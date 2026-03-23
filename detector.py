import cv2
import os
import subprocess
import json

class FrameDetector:
    def __init__(self, output_dir="captured_visuals"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.trigger_words = [
            "here", "this", "look", "see", "notice",
            "command", "run", "execute", "type",
            "install", "output", "result", "error",
            "diagram", "architecture", "structure"
        ]

    def is_scene_change(self, frame1, frame2, threshold=0.6):
        """Signal 1: Detects significant visual transitions."""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return score < threshold

    def has_high_text_density(self, frame, threshold=0.15):
        """Signal 2: Detects frames with high edge density (likely slides or code)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        density = edges.sum() / (edges.shape[0] * edges.shape[1] * 255)
        return density > threshold

    def has_trigger_word(self, timestamp, segments):
        """Signal 3: Checks if the transcript contains a trigger word at this time."""
        for segment in segments:
            if segment["start"] <= timestamp <= segment["end"]:
                text = segment["text"].lower()
                if any(word in text for word in self.trigger_words):
                    return True, segment["text"]
        return False, ""

    def detect_important_frames(self, video_path, segments, sample_rate_fps=1):
        """Main detection loop using multiple signals."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # We sample at a lower rate to avoid redundant processing
        frame_interval = int(fps / sample_rate_fps) if sample_rate_fps > 0 else 1
        
        important_moments = []
        prev_frame = None
        
        print(f"Analyzing video: {os.path.basename(video_path)} ({total_frames} frames)...")
        
        for frame_idx in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_idx / fps
            signals = []
            
            # 1. Scene Change
            if prev_frame is not None:
                if self.is_scene_change(prev_frame, frame):
                    signals.append("scene_change")
            
            # 2. Text Density
            if self.has_high_text_density(frame):
                signals.append("text_density")
            
            # 3. Transcript Anchor
            triggered, context = self.has_trigger_word(timestamp, segments)
            if triggered:
                signals.append("trigger_word")
            
            # Decision Logic: Flag if high confidence (2+ signals) or unique visual change
            # We prioritize Transcript Anchors as they give context
            if len(signals) >= 2 or ("trigger_word" in signals and "text_density" in signals):
                confidence = "high" if len(signals) >= 2 else "medium"
                
                # Capture frame
                frame_name = f"frame_{int(timestamp)}.png"
                frame_path = os.path.join(self.output_dir, frame_name)
                cv2.imwrite(frame_path, frame)
                
                important_moments.append({
                    "timestamp": float(round(timestamp, 2)),
                    "screenshot": frame_name,
                    "signals": signals,
                    "confidence": confidence,
                    "transcript_context": context
                })
                
            prev_frame = frame.copy()
            
        cap.release()
        return important_moments

    def save_miniclip(self, video_path, timestamp, output_name, before=3, after=7):
        """Option B: Captures a short video clip around a timestamp."""
        start = max(0, timestamp - before)
        duration = before + after
        output_path = os.path.join(self.output_dir, output_name)
        
        command = [
            "ffmpeg", "-y", "-ss", str(start),
            "-i", video_path,
            "-t", str(duration),
            "-c", "copy",
            output_path
        ]
        subprocess.run(command, capture_output=True)
        return output_path
