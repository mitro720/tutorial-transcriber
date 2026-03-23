# 📝 TutorialToText

TutorialToText is a powerful AI-driven tool that converts video tutorials and audio recordings into clean, structured Markdown reading guides. Whether you're a student, developer, or lifelong learner, TutorialToText helps you digest educational content faster by generating logical, step-by-step summaries instead of raw transcripts.

## 🚀 Features

-   **High-Speed Transcription**: Powered by the Groq Whisper-v3 API for near-instant results.
-   **YouTube Integration**: Automatically downloads and extracts audio from YouTube URLs using `yt-dlp`.
-   **AI Formatting**: Uses Llama-3 (via Groq) to restructure raw transcripts into professional documentation with Key Takeaways and clean headers.
-   **Local Fallback**: Includes a built-in fallback to local `openai-whisper` for offline use or when an API key is missing.
-   **Unlimited File Size**: Automatically chunks large audio files into segments to bypass API limits.

## 🛠️ Installation

### 1. Prerequisites
-   **Python 3.10+**
-   **FFmpeg**: Required for audio processing. (If on Windows, you can install via WinGet: `winget install Gyan.FFmpeg`)

### 2. Clone the Repository
```bash
git clone https://github.com/mitro720/tutorial-transcriber.git
cd tutorial-transcriber
```

### 3. Set Up Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment
Create a `.env` file in the root directory (use `.env.template` as a guide):
```env
GROQ_API_KEY=your_groq_api_key_here
FFMPEG_PATH=C:\path\to\ffmpeg.exe
```

## 📖 Usage

### Transcribe a YouTube Video
```bash
python main.py "https://www.youtube.com/watch?v=EXAMPLE"
```

### Transcribe a Local Video/Audio File
```bash
python main.py "path/to/my_tutorial.mp4" --local
```

### Use Local Whisper (No API)
```bash
python main.py "https://www.youtube.com/watch?v=EXAMPLE" --local-whisper
```

## 📂 Project Structure

-   `main.py`: Entry point for the application.
-   `transcriber.py`: Core logic for API and local transcription.
-   `downloader.py`: Handles YouTube downloads and audio extraction via FFmpeg.
-   `formatter.py`: LLM-based post-processing for better readability.
-   `local_transcriber.py`: Encapsulation for the offline Whisper model.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
