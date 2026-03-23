import os
from groq import Groq
from pydub import AudioSegment
import math
try:
    from local_transcriber import LocalTranscriber
except ImportError:
    LocalTranscriber = None

class AudioTranscriber:
    def __init__(self, api_key=None, use_local=False):
        self.client = Groq(api_key=api_key) if api_key else None
        self.max_file_size_mb = 25
        self.use_local = use_local
        self.local_model = None

    def transcribe(self, audio_path):
        """Transcribes the audio file, using local fallback if requested or if API fails."""
        if self.use_local:
            return self._transcribe_locally(audio_path)
        
        if not self.client:
            print("Groq API key missing. Attempting local transcription...")
            return self._transcribe_locally(audio_path)

        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        
        try:
            if file_size_mb <= self.max_file_size_mb:
                result = self._transcribe_file(audio_path)
            else:
                print(f"File size ({file_size_mb:.2f}MB) exceeds limits. Chunking...")
                result = self._transcribe_chunks(audio_path)
            
            return {
                "text": result.get("text", ""),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            print(f"Groq transcription failed: {e}. Falling back to local...")
            return self._transcribe_locally(audio_path)

    def _transcribe_locally(self, audio_path):
        """Helper to use local Whisper model."""
        if LocalTranscriber is None:
            print("Error: openai-whisper\ntorch\nopencv-python\n is not installed. Local transcription unavailable.")
            return None
        
        if not self.local_model:
            self.local_model = LocalTranscriber()
        
        return self.local_model.transcribe(audio_path)


    def _transcribe_file(self, file_path, retries=3):
        """Helper to transcribe a single file with exponential backoff on rate limits."""
        import time
        for attempt in range(retries):
            try:
                with open(file_path, "rb") as file:
                    transcription = self.client.audio.transcriptions.create(
                        file=(os.path.basename(file_path), file.read()),
                        model="whisper-large-v3",
                        response_format="verbose_json",
                        language="en", 
                        temperature=0.0
                    )
                    return {
                        "text": transcription.text,
                        "segments": transcription.segments
                    }
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e) and attempt < retries - 1:
                    wait_time = (2 ** attempt) + 1
                    print(f"  ! Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                else:
                    raise e
        return None

    def _transcribe_chunks(self, audio_path):
        """Chunks audio file into 10-minute segments and transcribes each."""
        audio = AudioSegment.from_file(audio_path)
        # 10 minutes in milliseconds
        chunk_length_ms = 10 * 60 * 1000 
        chunks = math.ceil(len(audio) / chunk_length_ms)
        
        full_text = []
        all_segments = []
        
        for i in range(chunks):
            start_ms = i * chunk_length_ms
            chunk = audio[start_ms : (i + 1) * chunk_length_ms]
            
            chunk_name = f"chunk_{i}.mp3"
            chunk.export(chunk_name, format="mp3")
            
            try:
                print(f"  > Transcribing chunk {i+1}/{chunks}...")
                result = self._transcribe_file(chunk_name)
                
                if result:
                    # Offset timestamps for segments
                    offset_seconds = start_ms / 1000.0
                    for segment in result.get("segments", []):
                        segment["start"] += offset_seconds
                        segment["end"] += offset_seconds
                        all_segments.append(segment)
                    
                    full_text.append(result.get("text", ""))
                else:
                    print(f"  ! Warning: Chunk {i+1} failed to transcribe.")
            finally:
                if os.path.exists(chunk_name):
                    os.remove(chunk_name)
                    
        return {
            "text": " ".join(full_text),
            "segments": all_segments
        }
