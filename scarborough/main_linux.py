import subprocess
import time
import os
from datetime import datetime

import pygame
import schedule


# Scarborough schedule mapping with updated color order:
# pink, yellow, orange, green, teal/aqua, silver, brown, blue, red
SCHEDULE = {
    "sunday": {
        "10:30": "audio/pink.wav",
        "10:45": "audio/yellow.wav",
        "11:00": "audio/orange.wav",
        "11:15": "audio/green.wav",
        "11:30": "audio/aqua.wav",
        "11:45": "audio/silver.wav",
        "12:00": "audio/brown.wav",
        "12:15": "audio/blue.wav",
        "12:30": "audio/red.wav",
        "12:45": "audio/pink.wav",
        "13:00": "audio/yellow.wav",
        "13:15": "audio/orange.wav",
        "13:30": "audio/green.wav",
        "13:45": "audio/aqua.wav",
        "14:00": "audio/silver.wav",
        "14:15": "audio/brown.wav",
        "14:30": "audio/blue.wav",
        "14:45": "audio/red.wav",
        "15:00": "audio/pink.wav",
        "15:15": "audio/yellow.wav",
        "15:30": "audio/orange.wav",
        "15:45": "audio/green.wav",
        "16:00": "audio/aqua.wav",
        "16:15": "audio/silver.wav",
        "16:30": "audio/brown.wav",
        "16:45": "audio/blue.wav",
        "17:00": "audio/red.wav",
        "17:15": "audio/pink.wav",
        "17:30": "audio/yellow.wav",
        "17:45": "audio/orange.wav",
        "18:00": "audio/green.wav",
        "18:15": "audio/aqua.wav",
        "18:30": "audio/silver.wav",
        "18:45": "audio/brown.wav",
        "19:00": "audio/blue.wav",
        "19:15": "audio/red.wav",
        "19:30": "audio/pink.wav",
        "19:45": "audio/yellow.wav",
    },
    "monday": {
        "10:30": "audio/pink.wav",
        "10:45": "audio/yellow.wav",
        "11:00": "audio/orange.wav",
        "11:15": "audio/green.wav",
        "11:30": "audio/aqua.wav",
        "11:45": "audio/silver.wav",
        "12:00": "audio/brown.wav",
        "12:15": "audio/blue.wav",
        "12:30": "audio/red.wav",
        "12:45": "audio/pink.wav",
        "13:00": "audio/yellow.wav",
        "13:15": "audio/orange.wav",
        "13:30": "audio/green.wav",
        "13:45": "audio/aqua.wav",
        "14:00": "audio/silver.wav",
        "14:15": "audio/brown.wav",
        "14:30": "audio/blue.wav",
        "14:45": "audio/red.wav",
        "15:00": "audio/pink.wav",
        "15:15": "audio/yellow.wav",
        "15:30": "audio/orange.wav",
        "15:45": "audio/green.wav",
        "16:00": "audio/aqua.wav",
        "16:15": "audio/silver.wav",
        "16:30": "audio/brown.wav",
        "16:45": "audio/blue.wav",
        "17:00": "audio/red.wav",
        "17:15": "audio/pink.wav",
        "17:30": "audio/yellow.wav",
        "17:45": "audio/orange.wav",
        "18:00": "audio/green.wav",
        "18:15": "audio/aqua.wav",
        "18:30": "audio/silver.wav",
        "18:45": "audio/brown.wav",
        "19:00": "audio/blue.wav",
        "19:15": "audio/red.wav",
        "19:30": "audio/pink.wav",
        "19:45": "audio/yellow.wav",
    },
    "tuesday": {
        "10:30": "audio/pink.wav",
        "10:45": "audio/yellow.wav",
        "11:00": "audio/orange.wav",
        "11:15": "audio/green.wav",
        "11:30": "audio/aqua.wav",
        "11:45": "audio/silver.wav",
        "12:00": "audio/brown.wav",
        "12:15": "audio/blue.wav",
        "12:30": "audio/red.wav",
        "12:45": "audio/pink.wav",
        "13:00": "audio/yellow.wav",
        "13:15": "audio/orange.wav",
        "13:30": "audio/green.wav",
        "13:45": "audio/aqua.wav",
        "14:00": "audio/silver.wav",
        "14:15": "audio/brown.wav",
        "14:30": "audio/blue.wav",
        "14:45": "audio/red.wav",
        "15:00": "audio/pink.wav",
        "15:15": "audio/yellow.wav",
        "15:30": "audio/orange.wav",
        "15:45": "audio/green.wav",
        "16:00": "audio/aqua.wav",
        "16:15": "audio/silver.wav",
        "16:30": "audio/brown.wav",
        "16:45": "audio/blue.wav",
        "17:00": "audio/red.wav",
        "17:15": "audio/pink.wav",
        "17:30": "audio/yellow.wav",
        "17:45": "audio/orange.wav",
        "18:00": "audio/green.wav",
        "18:15": "audio/aqua.wav",
        "18:30": "audio/silver.wav",
        "18:45": "audio/brown.wav",
        "19:00": "audio/blue.wav",
        "19:15": "audio/red.wav",
        "19:30": "audio/pink.wav",
        "19:45": "audio/yellow.wav",
    },
    "wednesday": {
        "10:30": "audio/pink.wav",
        "10:45": "audio/yellow.wav",
        "11:00": "audio/orange.wav",
        "11:15": "audio/green.wav",
        "11:30": "audio/aqua.wav",
        "11:45": "audio/silver.wav",
        "12:00": "audio/brown.wav",
        "12:15": "audio/blue.wav",
        "12:30": "audio/red.wav",
        "12:45": "audio/pink.wav",
        "13:00": "audio/yellow.wav",
        "13:15": "audio/orange.wav",
        "13:30": "audio/green.wav",
        "13:45": "audio/aqua.wav",
        "14:00": "audio/silver.wav",
        "14:15": "audio/brown.wav",
        "14:30": "audio/blue.wav",
        "14:45": "audio/red.wav",
        "15:00": "audio/pink.wav",
        "15:15": "audio/yellow.wav",
        "15:30": "audio/orange.wav",
        "15:45": "audio/green.wav",
        "16:00": "audio/aqua.wav",
        "16:15": "audio/silver.wav",
        "16:30": "audio/brown.wav",
        "16:45": "audio/blue.wav",
        "17:00": "audio/red.wav",
        "17:15": "audio/pink.wav",
        "17:30": "audio/yellow.wav",
        "17:45": "audio/orange.wav",
        "18:00": "audio/green.wav",
        "18:15": "audio/aqua.wav",
        "18:30": "audio/silver.wav",
        "18:45": "audio/brown.wav",
        "19:00": "audio/blue.wav",
        "19:15": "audio/red.wav",
        "19:30": "audio/pink.wav",
        "19:45": "audio/yellow.wav",
    },
    "thursday": {
        "10:30": "audio/pink.wav",
        "10:45": "audio/yellow.wav",
        "11:00": "audio/orange.wav",
        "11:15": "audio/green.wav",
        "11:30": "audio/aqua.wav",
        "11:45": "audio/silver.wav",
        "12:00": "audio/brown.wav",
        "12:15": "audio/blue.wav",
        "12:30": "audio/red.wav",
        "12:45": "audio/pink.wav",
        "13:00": "audio/yellow.wav",
        "13:15": "audio/orange.wav",
        "13:30": "audio/green.wav",
        "13:45": "audio/aqua.wav",
        "14:00": "audio/silver.wav",
        "14:15": "audio/brown.wav",
        "14:30": "audio/blue.wav",
        "14:45": "audio/red.wav",
        "15:00": "audio/pink.wav",
        "15:15": "audio/yellow.wav",
        "15:30": "audio/orange.wav",
        "15:45": "audio/green.wav",
        "16:00": "audio/aqua.wav",
        "16:15": "audio/silver.wav",
        "16:30": "audio/brown.wav",
        "16:45": "audio/blue.wav",
        "17:00": "audio/red.wav",
        "17:15": "audio/pink.wav",
        "17:30": "audio/yellow.wav",
        "17:45": "audio/orange.wav",
        "18:00": "audio/green.wav",
        "18:15": "audio/aqua.wav",
        "18:30": "audio/silver.wav",
        "18:45": "audio/brown.wav",
        "19:00": "audio/blue.wav",
        "19:15": "audio/red.wav",
        "19:30": "audio/pink.wav",
        "19:45": "audio/yellow.wav",
    },
    "friday": {
        "10:30": "audio/pink.wav",
        "10:45": "audio/yellow.wav",
        "11:00": "audio/orange.wav",
        "11:15": "audio/green.wav",
        "11:30": "audio/aqua.wav",
        "11:45": "audio/silver.wav",
        "12:00": "audio/brown.wav",
        "12:15": "audio/blue.wav",
        "12:30": "audio/red.wav",
        "12:45": "audio/pink.wav",
        "13:00": "audio/yellow.wav",
        "13:15": "audio/orange.wav",
        "13:30": "audio/green.wav",
        "13:45": "audio/aqua.wav",
        "14:00": "audio/silver.wav",
        "14:15": "audio/brown.wav",
        "14:30": "audio/blue.wav",
        "14:45": "audio/red.wav",
        "15:00": "audio/pink.wav",
        "15:15": "audio/yellow.wav",
        "15:30": "audio/orange.wav",
        "15:45": "audio/green.wav",
        "16:00": "audio/aqua.wav",
        "16:15": "audio/silver.wav",
        "16:30": "audio/brown.wav",
        "16:45": "audio/blue.wav",
        "17:00": "audio/red.wav",
        "17:15": "audio/pink.wav",
        "17:30": "audio/yellow.wav",
        "17:45": "audio/orange.wav",
        "18:00": "audio/green.wav",
        "18:15": "audio/aqua.wav",
        "18:30": "audio/silver.wav",
        "18:45": "audio/brown.wav",
        "19:00": "audio/blue.wav",
        "19:15": "audio/red.wav",
        "19:30": "audio/pink.wav",
        "19:45": "audio/yellow.wav",
        "20:00": "audio/orange.wav",
        "20:15": "audio/green.wav",
        "20:30": "audio/aqua.wav",
        "20:45": "audio/silver.wav",
        "21:00": "audio/brown.wav",
        "21:15": "audio/blue.wav",
        "21:30": "audio/red.wav",
        "21:45": "audio/pink.wav",
        "22:00": "audio/yellow.wav",
    },
    "saturday": {
        "10:30": "audio/pink.wav",
        "10:45": "audio/yellow.wav",
        "11:00": "audio/orange.wav",
        "11:15": "audio/green.wav",
        "11:30": "audio/aqua.wav",
        "11:45": "audio/silver.wav",
        "12:00": "audio/brown.wav",
        "12:15": "audio/blue.wav",
        "12:30": "audio/red.wav",
        "12:45": "audio/pink.wav",
        "13:00": "audio/yellow.wav",
        "13:15": "audio/orange.wav",
        "13:30": "audio/green.wav",
        "13:45": "audio/aqua.wav",
        "14:00": "audio/silver.wav",
        "14:15": "audio/brown.wav",
        "14:30": "audio/blue.wav",
        "14:45": "audio/red.wav",
        "15:00": "audio/pink.wav",
        "15:15": "audio/yellow.wav",
        "15:30": "audio/orange.wav",
        "15:45": "audio/green.wav",
        "16:00": "audio/aqua.wav",
        "16:15": "audio/silver.wav",
        "16:30": "audio/brown.wav",
        "16:45": "audio/blue.wav",
        "17:00": "audio/red.wav",
        "17:15": "audio/pink.wav",
        "17:30": "audio/yellow.wav",
        "17:45": "audio/orange.wav",
        "18:00": "audio/green.wav",
        "18:15": "audio/aqua.wav",
        "18:30": "audio/silver.wav",
        "18:45": "audio/brown.wav",
        "19:00": "audio/blue.wav",
        "19:15": "audio/red.wav",
        "19:30": "audio/pink.wav",
        "19:45": "audio/yellow.wav",
        "20:00": "audio/orange.wav",
        "20:15": "audio/green.wav",
        "20:30": "audio/aqua.wav",
        "20:45": "audio/silver.wav",
        "21:00": "audio/brown.wav",
        "21:15": "audio/blue.wav",
        "21:30": "audio/red.wav",
        "21:45": "audio/pink.wav",
        "22:00": "audio/yellow.wav",
    },
}


class AudioScheduler:
    def __init__(self):
        # Get the directory where this script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        pygame.mixer.init()
        self.schedule_dict = SCHEDULE
        self.valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        self.validate_schedule()
        self.check_dependencies()

    def check_dependencies(self):
        """Check if required system tools are installed"""
        try:
            subprocess.run(["which", "playerctl"], check=True, capture_output=True, timeout=2)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            raise SystemError("playerctl not installed. Install with: sudo apt-get install playerctl")

    def validate_schedule(self):
        """Validate schedule configuration"""
        for day in self.schedule_dict.keys():
            if day.lower() not in self.valid_days:
                raise ValueError(f"Invalid day: {day}")

            for time_str, audio_file in self.schedule_dict[day].items():
                try:
                    hour, minute = map(int, time_str.split(":"))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError(f"Invalid time: {time_str}")
                except ValueError:
                    raise ValueError(f"Invalid time format for {day}: {time_str}. Use HH:MM")

                # Convert relative path to absolute path
                audio_path = os.path.join(self.script_dir, audio_file)
                if not os.path.exists(audio_path):
                    raise FileNotFoundError(f"Audio file not found: {audio_path}")

    def check_media_playing(self):
        """Check if media is currently playing"""
        try:
            result = subprocess.run(
                ["playerctl", "status"],
                capture_output=True,
                text=True,
                timeout=1
            )
            return result.returncode == 0 and result.stdout.strip().lower() == "playing"
        except (subprocess.TimeoutExpired, Exception):
            return False

    def pause_media(self):
        """Pause currently playing media"""
        try:
            result = subprocess.run(
                ["playerctl", "pause"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False

    def play_media(self):
        """Resume paused media"""
        try:
            result = subprocess.run(
                ["playerctl", "play"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False

    def play_scheduled_audio(self, audio_file: str):
        """Play scheduled announcement, pausing and resuming media if needed"""
        media_was_playing = False

        try:
            # Convert relative path to absolute path
            audio_path = os.path.join(self.script_dir, audio_file)

            if not os.path.exists(audio_path):
                print(f"Error: Audio file not found: {audio_path}")
                return

            media_was_playing = self.check_media_playing()

            if media_was_playing:
                if not self.pause_media():
                    print("Warning: Failed to pause media")
                time.sleep(0.5)

            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()

        except Exception as e:
            print(f"Error playing audio: {e}")
        finally:
            if media_was_playing:
                time.sleep(0.3)
                if not self.play_media():
                    print("Warning: Failed to resume media")

    def schedule_all_tasks(self):
        """Schedule all tasks for the current day"""
        current_day = datetime.now().strftime("%A").lower()

        if current_day not in self.schedule_dict:
            print(f"No schedule for {current_day.capitalize()}")
            return

        schedule.clear()

        for time_str, audio_file in self.schedule_dict[current_day].items():
            schedule.every().day.at(time_str).do(self.play_scheduled_audio, audio_file)

        print(f"Loaded {len(self.schedule_dict[current_day])} scheduled items for {current_day.capitalize()}")

    def run(self):
        """Run the scheduler"""
        print("Scarborough Audio Scheduler Started")

        current_day = datetime.now().strftime("%A").lower()
        print(f"Current day: {current_day.capitalize()}")
        print(f"Current time: {datetime.now().strftime('%H:%M:%S')}\n")

        self.schedule_all_tasks()

        last_day = current_day

        try:
            while True:
                schedule.run_pending()

                now = datetime.now()
                new_day = now.strftime("%A").lower()

                if new_day != last_day:
                    print(f"\nDay changed to {new_day.capitalize()}")
                    self.schedule_all_tasks()
                    last_day = new_day

                time.sleep(1)

        except KeyboardInterrupt:
            print("\nScheduler stopped")
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    scheduler = AudioScheduler()
    scheduler.run()
