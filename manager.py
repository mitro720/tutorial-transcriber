import os
import json
from datetime import datetime

class SessionManager:
    def __init__(self, base_output_dir=None):
        if not base_output_dir:
            # Interactive prompt if not provided
            default_base = os.path.join(os.getcwd(), "output")
            print(f"\n--- Output Configuration ---")
            user_input = input(f"Where should this session be saved? [Press Enter for default: {default_base}]: ").strip()
            self.base_dir = user_input if user_input else default_base
        else:
            self.base_dir = base_output_dir

        # Create session-specific folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(self.base_dir, f"session_{timestamp}")
        self.visuals_dir = os.path.join(self.session_dir, "visuals")
        self.temp_dir = os.path.join(self.session_dir, "temp")
        
        self.ensure_dirs()
        
        self.start_time = datetime.now()
        self.metadata = {
            "run_timestamp": self.start_time.isoformat(),
            "output_dir": self.session_dir,
            "steps": {}
        }

    def ensure_dirs(self):
        """Creates the necessary subdirectories."""
        for d in [self.session_dir, self.visuals_dir, self.temp_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

    def get_path(self, filename, category="session"):
        """Returns the absolute path for a file based on its category."""
        if category == "visuals":
            return os.path.join(self.visuals_dir, filename)
        elif category == "temp":
            return os.path.join(self.temp_dir, filename)
        return os.path.join(self.session_dir, filename)

    def log_step(self, step_name, status, duration=None, extra=None):
        """Logs step-specific metadata."""
        self.metadata["steps"][step_name] = {
            "status": status,
            "duration_seconds": duration,
            **(extra or {})
        }

    def save_metadata(self, final_stats=None):
        """Saves the accumulated metadata to metadata.json."""
        if final_stats:
            self.metadata.update(final_stats)
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        self.metadata["total_duration_seconds"] = total_duration
        
        metadata_path = self.get_path("metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=4)
        return metadata_path
