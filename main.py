import os
import argparse
import time
import sys
from datetime import datetime
from groq import Groq
import json
from dotenv import load_dotenv

from extractor import AudioDownloader
from transcriber import AudioTranscriber
from formatter import TextFormatter
from detector import FrameDetector
from manager import SessionManager

def main():
    # Force unbuffered output for real-time progress in Windows terminals
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(line_buffering=True)
        
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    parser = argparse.ArgumentParser(description="TutorialToText: Convert video/audio to Markdown guides.")
    parser.add_argument("input", nargs="?", help="URL of the video or path to a local file. If omitted, a file picker will open.")
    parser.add_argument("-o", "--output", help="Output filename (default: guide.md)", default="guide.md")
    parser.add_argument("-d", "--dir", help="Base output directory (will prompt if not provided).")
    parser.add_argument("--local", action="store_true", help="Flag to indicate input is a local file.")
    parser.add_argument("--local-whisper", action="store_true", help="Use local Whisper model instead of Groq API.")
    parser.add_argument("--clips", action="store_true", help="Capture mini-video clips for high-confidence moments.")
    
    args = parser.parse_args()

    # Initialize Session Manager
    session = SessionManager(args.dir)
    
    # GUI File Picker if no input provided
    if not args.input:
        print("\n[No input provided] Opening file picker...")
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        selected_file = filedialog.askopenfilename(
            title="Select Video/Audio for Dissection",
            filetypes=[
                ("Media Files", "*.mp4 *.mkv *.avi *.mov *.m4v *.mp3 *.wav *.m4a"),
                ("All Files", "*.*")
            ]
        )
        root.destroy()
        
        if not selected_file:
            print("Error: No file selected. Exiting.")
            return
        
        args.input = selected_file
        args.local = True # Automatically treat picked file as local
    
    print(f"\n[Session Started: {session.session_dir}]")

    if not api_key and not args.local_whisper:
        print("Error: GROQ_API_KEY not found. Required for Groq-based transcription and formatting.")
        return

    try:
        # 1. Extraction
        start_time = time.time()
        print(f"\n[1/5] Extracting audio from {args.input}...")
        # Use session's temp directory
        downloader = AudioDownloader(output_dir=session.temp_dir)
        
        if args.local or os.path.exists(args.input):
            audio_path = downloader.extract_from_local(args.input)
            video_path = args.input if not args.input.endswith((".mp3", ".wav", ".m4a")) else None
        else:
            print("  > Downloading video for dissection...")
            video_path = downloader.download_video(args.input)
            print("  > Extracting audio for transcription...")
            audio_path = downloader.extract_from_local(video_path)

        if not audio_path or not os.path.exists(audio_path):
            raise FileNotFoundError("Audio extraction failed.")

        duration = time.time() - start_time
        print(f"  [OK] done ({duration:.1f}s)")
        session.log_step("Extraction", "Success", duration, {"video_path": video_path})

        # 2. Transcription
        start_time = time.time()
        print(f"\n[2/5] Transcribing audio ({'Local' if args.local_whisper else 'Groq Whisper'})...")
        transcriber = AudioTranscriber(api_key, use_local=args.local_whisper)
        transcription_result = transcriber.transcribe(audio_path)
        
        if not transcription_result or not transcription_result.get("text"):
            raise ValueError("Transcription failed to return text.")

        raw_transcript = transcription_result["text"]
        segments = transcription_result["segments"]
        
        duration = time.time() - start_time
        print(f"  [OK] done ({duration:.1f}s, {len(raw_transcript.split())} words)")
        session.log_step("Transcription", "Success", duration, {"word_count": len(raw_transcript.split())})

        # 3. Visual Detection
        visuals = None
        if video_path:
            start_time = time.time()
            print(f"\n[3/5] Detecting important moments & {'clips' if args.clips else 'frames'}...")
            # Use session's visuals directory
            detector = FrameDetector(output_dir=session.visuals_dir)
            visuals = detector.detect_important_frames(video_path, segments, capture_clips=args.clips)
            
            duration = time.time() - start_time
            print(f"  [OK] done ({duration:.1f}s, {len(visuals)} moments captured)")
            session.log_step("Detection", "Success", duration, {"moments_count": len(visuals)})

        # 4. Formatting
        start_time = time.time()
        if api_key:
            print(f"\n[4/5] Formatting into Markdown (Groq Llama-3)...")
            formatter = TextFormatter(api_key)
            markdown_guide = formatter.format_transcript(raw_transcript, visuals=visuals)
            duration = time.time() - start_time
            print(f"  [OK] done ({duration:.1f}s)")
            session.log_step("Formatting", "Success", duration)
        else:
            print("\n[4/5] Skipping Formatting (GROQ_API_KEY missing)...")
            markdown_guide = raw_transcript
            session.log_step("Formatting", "Skipped")

        # 5. Save Output
        start_time = time.time()
        output_guide_path = session.get_path(args.output)
        print(f"\n[5/5] Saving final guide to {os.path.basename(output_guide_path)}...")
        with open(output_guide_path, "w", encoding="utf-8") as f:
            f.write(markdown_guide)
        
        with open(session.get_path("transcript_raw.txt"), "w", encoding="utf-8") as f:
            f.write(raw_transcript)

        duration = time.time() - start_time
        print(f"  [OK] done")
        session.log_step("Saving", "Success", duration)

        # Final Metadata & Cleanup
        meta_path = session.save_metadata({
            "source_url": args.input if not args.local else "local_file",
            "models_used": {
                "transcription": "whisper-large-v3" if not args.local_whisper else "local-whisper",
                "llm": "llama-3.3-70b-versatile"
            }
        })

        print(f"\nSuccess! Total output is ready in:")
        print(f"  > {session.session_dir}")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        session.log_step("Pipeline", "Failed", extra={"error": str(e)})
        session.save_metadata()
        return

if __name__ == "__main__":
    main()
