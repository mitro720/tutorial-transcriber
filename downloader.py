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
        self.aria2c_path = os.getenv("ARIA2C_PATH", "aria2c")

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
            info = ydl.extract_info(url, download=True)
            final_filename = os.path.join(self.output_dir, "downloaded_audio.mp3")
            return final_filename

    def download_video(self, url):
        """Downloads high-quality 720p video using aria2c and concurrent fragments."""
        output_tmpl = os.path.join(self.output_dir, "downloaded_video.%(ext)s")
        ydl_opts = {
            'ffmpeg_location': self.ffmpeg_path if self.ffmpeg_path != "ffmpeg" else None,
            # Best 720p mp4 for visual clarity + efficiency
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
            'outtmpl': output_tmpl,
            'external_downloader': self.aria2c_path if self.aria2c_path != "aria2c" else 'aria2c',
            'external_downloader_args': [
                '--min-split-size=1M',
                '--max-connection-per-server=16',
                '--max-concurrent-downloads=16',
                '--split=16'
            ],
            'concurrent_fragment_downloads': 16,
            'retries': 10,
            'fragment_retries': 10,
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get('ext', 'mp4')
            final_filename = os.path.join(self.output_dir, f"downloaded_video.{ext}")
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
