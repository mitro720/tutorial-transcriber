from pydub import AudioSegment
from pydub.generators import Sine
import os

def create_sample_audio(filename="sample_test.wav"):
    print(f"Generating sample audio: {filename}")
    # Create a 5-second sine wave at 440Hz
    tone = Sine(440).to_audio_segment(duration=5000)
    tone.export(filename, format="wav")
    print("Done.")

if __name__ == "__main__":
    create_sample_audio()
