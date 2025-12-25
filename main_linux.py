import subprocess
import time
import os
from datetime import datetime

import pygame
import schedule

from mapping import mapp


class AudioScheduler:
    def __init__(self):
        pygame.mixer.init()
        self.schedule_dict = mapp
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

                if not os.path.exists(audio_file):
                    raise FileNotFoundError(f"Audio file not found: {audio_file}")

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
            if not os.path.exists(audio_file):
                print(f"Error: Audio file not found: {audio_file}")
                return

            media_was_playing = self.check_media_playing()

            if media_was_playing:
                if not self.pause_media():
                    print("Warning: Failed to pause media")
                time.sleep(0.5)

            pygame.mixer.music.load(audio_file)
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
        print("Audio Scheduler Started")

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
