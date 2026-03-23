import whisper
import os

class LocalTranscriber:
    def __init__(self, model_name="base"):
        """
        Initializes the local Whisper model.
        Common models: tiny, base, small, medium, large
        """
        print(f"Loading local Whisper model '{model_name}'... (This may take a moment)")
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path):
        """Transcribes the audio file using the local Whisper model."""
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found at {audio_path}")
            return None
        
        print(f"Transcribing locally: {audio_path}")
        result = self.model.transcribe(audio_path)
        return result["text"]
