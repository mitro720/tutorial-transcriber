import os
from dotenv import load_dotenv
from downloader import AudioDownloader

def test_extraction():
    load_dotenv()
    # Ensure our found path is used if not in .env
    if not os.getenv("YT_DLP_PATH"):
        os.environ["YT_DLP_PATH"] = r"C:\Users\derrick\AppData\Roaming\Python\Python313\Scripts\yt-dlp.exe"
    
    downloader = AudioDownloader()
    print(f"Using yt-dlp path: {downloader.yt_dlp_path}")
    print(f"Using ffmpeg path: {downloader.ffmpeg_path}")
    
    # Test with a very short video (e.g., a 1-second silence video or similar)
    # Using a common short URL for testing if possible.
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # Me at the zoo (short)
    
    try:
        print("Starting test download...")
        audio_path = downloader.download_from_url(test_url)
        print(f"Success! Audio saved to: {audio_path}")
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    test_extraction()
