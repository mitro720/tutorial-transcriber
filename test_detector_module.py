import cv2
import numpy as np
import os
from detector import FrameDetector

def create_test_video(path, duration_sec=5, fps=10):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, (640, 480))
    
    for i in range(duration_sec * fps):
        # Frame 0-19: Black
        if i < 20:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Frame 20-39: White (Scene Change at 2s)
        elif i < 40:
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        # Frame 40-50: High Text Density (Noise/Lines)
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            for _ in range(100):
                x1, y1 = np.random.randint(0, 640), np.random.randint(0, 480)
                x2, y2 = np.random.randint(0, 640), np.random.randint(0, 480)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
        
        out.write(frame)
    out.release()

def test_detector():
    video_path = "test_video.mp4"
    create_test_video(video_path)
    
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Starting the tutorial."},
        {"start": 2.1, "end": 4.0, "text": "Now look at this screen here."}, # Trigger word "look", "this", "here"
        {"start": 4.1, "end": 5.0, "text": "The result is shown."} # Trigger word "result"
    ]
    
    detector = FrameDetector(output_dir="test_visuals")
    moments = detector.detect_important_frames(video_path, segments)
    
    print("\n--- Detection Results ---")
    for m in moments:
        print(f"Time: {m['timestamp']}s | Signals: {m['signals']} | Conf: {m['confidence']}")
    
    if len(moments) > 0:
        print("\nSUCCESS: Detected important moments!")
    else:
        print("\nFAILURE: No moments detected.")

if __name__ == "__main__":
    test_detector()
