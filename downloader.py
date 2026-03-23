import yt_dlp
import os
import subprocess

class AudioDownloader:
    def __init__(self, output_dir="temp_audio"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Look for custom paths in environment variables
        self.yt_dlp_path = os.getenv("YT_DLP_PATH", "yt-dlp")
        self.ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")

    def download_from_url(self, url):
        """Downloads audio from a URL using yt-dlp."""
        output_path = os.path.join(self.output_dir, "downloaded_audio.%(ext)s")
        ydl_opts = {
            'ffmpeg_location': self.ffmpeg_path if self.ffmpeg_path != "ffmpeg" else None,
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # If yt-dlp is not in path, we might need to use its exact location
            # However, yt-dlp library usually handles its own calls if possible.
            # But for the CLI/External calls, we use self.yt_dlp_path if needed.
            info = ydl.extract_info(url, download=True)
            # Find the actual filename (e.g., downloaded_audio.mp3)
            ext = info.get('ext', 'mp3')
            final_filename = os.path.join(self.output_dir, f"downloaded_audio.mp3")
            return final_filename

    def extract_from_local(self, input_path):
        """Extracts and compresses audio from a local video file using ffmpeg."""
        output_path = os.path.join(self.output_dir, "local_audio.mp3")
        
        # ffmpeg -i input.mp4 -vn -ar 16000 -ac 1 -b:a 32k audio.mp3
        command = [
            self.ffmpeg_path, '-y', '-i', input_path,
            '-vn',                # No video
            '-ar', '16000',      # Sample rate
            '-ac', '1',          # Mono
            '-b:a', '32k',       # Bitrate
            output_path
        ]
        
        try:
            subprocess.run(command, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {e.stderr.decode()}")
            return None

    def compress_audio(self, input_path):
        """Compresses existing audio file to meet Groq's size limits if possible."""
        compressed_path = os.path.join(self.output_dir, "compressed_audio.mp3")
        command = [
            self.ffmpeg_path, '-y', '-i', input_path,
            '-ar', '16000',
            '-ac', '1',
            '-b:a', '32k',
            compressed_path
        ]
        try:
            subprocess.run(command, check=True, capture_output=True)
            return compressed_path
        except subprocess.CalledProcessError as e:
            print(f"Error compressing audio: {e.stderr.decode()}")
            return input_path
