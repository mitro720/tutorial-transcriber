import os
import argparse
from groq import Groq
import json
from dotenv import load_dotenv
from downloader import AudioDownloader
from transcriber import AudioTranscriber
from formatter import TextFormatter
from detector import FrameDetector

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    parser = argparse.ArgumentParser(description="TutorialToText: Convert video/audio to Markdown guides.")
    parser.add_argument("input", help="URL of the video or path to a local file.")
    parser.add_argument("-o", "--output", help="Output filename (default: guide.md)", default="guide.md")
    parser.add_argument("--local", action="store_true", help="Flag to indicate input is a local file.")
    parser.add_argument("--local-whisper", action="store_true", help="Use local Whisper model instead of Groq API.")
    
    args = parser.parse_args()

    if not api_key and not args.local_whisper:
        print("Error: GROQ_API_KEY not found in environment or .env file.")
        print("Required for Groq-based transcription and formatting.")
        return

    # 1. Extraction
    print(f"--- Step 1: Extracting audio from {args.input} ---")
    downloader = AudioDownloader()
    
    if args.local or os.path.exists(args.input):
        audio_path = downloader.extract_from_local(args.input)
    else:
        audio_path = downloader.download_from_url(args.input)

    if not audio_path or not os.path.exists(audio_path):
        print("Failed to obtain audio file.")
        return

    # 2. Transcription
    print(f"--- Step 2: Transcribing audio ({'Local' if args.local_whisper else 'Groq Whisper'}) ---")
    transcriber = AudioTranscriber(api_key, use_local=args.local_whisper)
    transcription_result = transcriber.transcribe(audio_path)
    
    if not transcription_result or not transcription_result.get("text"):
        print("Transcription failed.")
        return

    raw_transcript = transcription_result["text"]
    segments = transcription_result["segments"]
    
    # 2.5 Visual Detection (New!)
    visuals = None
    # We only run detection if it's a video file or if we have a way to access the frames.
    # yt-dlp might have deleted the video, but if it exists, we use it.
    video_path = args.input if os.path.exists(args.input) and not args.input.endswith((".mp3", ".wav", ".m4a")) else None
    
    if video_path:
        print("--- Step 2.5: Detecting important frames and visuals ---")
        detector = FrameDetector()
        visuals = detector.detect_important_frames(video_path, segments)
        print(f"Captured {len(visuals)} important moments.")
    
    # 3. Formatting
    if api_key:
        print("--- Step 3: Formatting into Markdown (Groq Llama-3) ---")
        formatter = TextFormatter(api_key)
        markdown_guide = formatter.format_transcript(raw_transcript, visuals=visuals)
    else:
        print("--- Step 3: Skipping Formatting (GROQ_API_KEY missing) ---")
        markdown_guide = raw_transcript

    # 4. Save Output
    print(f"--- Final Step: Saving guide to {args.output} ---")
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(markdown_guide)

    print("\nSuccess! Your tutorial guide is ready.")
    
    # Cleanup (Optional)
    # if os.path.exists(audio_path):
    #     os.remove(audio_path)

if __name__ == "__main__":
    main()
