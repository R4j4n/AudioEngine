import subprocess
import time
from datetime import datetime
from datetime import time as dtime
from typing import Dict, List

import dbus
import pygame
import schedule
from prettytable import PrettyTable

from mapping import mapp


class AudioScheduler:
    def __init__(self):
        pygame.mixer.init()
        self.schedule_dict = mapp
        self.validate_times()
        self.check_dependencies()

        # Validate the days in the schedule
        self.valid_days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        self.validate_days()

        # Store current day information
        self._current_day = None
        self.update_current_day()

    def check_dependencies(self):
        """Check if required system tools are installed"""
        try:
            subprocess.run(["which", "xdotool"], check=True, capture_output=True)
            subprocess.run(["which", "playerctl"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise SystemError(
                "Required tools not installed. Please install them using:\n"
                "sudo apt-get install xdotool playerctl"
            )

    def validate_days(self):
        """Validate that all days in schedule_dict are correct"""
        for day in self.schedule_dict.keys():
            if day.lower() not in self.valid_days:
                raise ValueError(f"Invalid day in schedule: {day}")

        # Verify all days are present
        missing_days = set(self.valid_days) - set(
            k.lower() for k in self.schedule_dict.keys()
        )
        if missing_days:
            raise ValueError(f"Missing days in schedule: {missing_days}")

    def update_current_day(self):
        """Update the current day with multiple validation methods"""
        # Get current day using multiple methods for redundancy
        current_day_datetime = datetime.now().strftime("%A").lower()
        current_day_time = time.strftime("%A").lower()

        # Validate that both methods agree
        if current_day_datetime != current_day_time:
            print(
                f"Warning: Day detection mismatch - datetime: {current_day_datetime}, time: {current_day_time}"
            )
            # Log additional system time information for debugging
            print(f"System time details:")
            print(f"Datetime now: {datetime.now()}")
            print(f"Time strftime: {time.strftime('%c')}")

        self._current_day = current_day_datetime

        # Verify the day is valid
        if self._current_day not in self.valid_days:
            raise ValueError(f"Invalid day detected: {self._current_day}")

        print(f"Current day validated: {self._current_day.capitalize()}")
        return self._current_day

    def get_current_day(self):
        """Get the current day with validation"""
        # Update current day if not set
        if self._current_day is None:
            self.update_current_day()

        # Double-check the stored day matches current day
        actual_day = datetime.now().strftime("%A").lower()
        if self._current_day != actual_day:
            print(
                f"Day mismatch detected. Stored: {self._current_day}, Actual: {actual_day}"
            )
            self.update_current_day()

        return self._current_day

    def validate_times(self):
        """Validate that all times in schedule_dict are in correct 24-hour format"""
        for day, times in self.schedule_dict.items():
            for time_str in times.keys():
                try:
                    hour, minute = map(int, time_str.split(":"))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError(f"Invalid time format: {time_str}")
                    dtime(hour, minute)
                except ValueError as e:
                    raise ValueError(
                        f"Invalid time format in schedule for {day}: {time_str}. "
                        "Please use 24-hour format (HH:MM)"
                    )

    def print_daily_schedule(self, day: str = None):
        """Print the schedule for a specific day or current day in a pretty format"""
        if day is None:
            day = datetime.now().strftime("%A").lower()

        if day not in self.schedule_dict:
            print(f"No schedule found for {day.capitalize()}")
            return

        table = PrettyTable()
        table.field_names = ["Time (24hr)", "Time (12hr)", "Audio File"]
        table.align = "l"  # Left align all columns

        # Get the schedule for the day and sort by time
        daily_schedule = self.schedule_dict[day]
        sorted_times = sorted(
            daily_schedule.keys(), key=lambda x: datetime.strptime(x, "%H:%M")
        )

        for time_str in sorted_times:
            audio_file = daily_schedule[time_str]
            table.add_row(
                [
                    time_str,
                    self.convert_to_12hr(time_str),
                    audio_file.split("/")[-1],  # Show only filename, not full path
                ]
            )

        print(f"\nSchedule for {day.capitalize()}:")
        print(table)

    def print_all_schedules(self):
        """Print schedules for all days"""
        for day in self.schedule_dict.keys():
            self.print_daily_schedule(day)
            print("\n" + "=" * 80 + "\n")  # Separator between days

    def get_chrome_window_ids(self):
        """Get all Chrome window IDs"""
        try:
            cmd = "xdotool search --class 'chrome'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except:
            return []

    def check_media_playing(self):
        """Check if media is playing using multiple methods"""
        try:
            # Method 1: Check using playerctl
            try:
                result = subprocess.run(
                    ["playerctl", "--player=chromium,chrome", "status"],
                    capture_output=True,
                    text=True,
                )
                if result.stdout.strip().lower() == "playing":
                    return True
            except:
                pass

            # Method 2: Check using pactl
            cmd = "pactl list sink-inputs | grep -c 'RUNNING'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return int(result.stdout.strip()) > 0
        except:
            return False

    def pause_media(self):
        """Pause media using multiple methods"""
        success = False

        # Method 1: Try using playerctl
        try:
            subprocess.run(
                ["playerctl", "--player=chromium,chrome", "pause"],
                check=True,
                capture_output=True,
            )
            success = True
        except:
            pass

        # Method 2: Try using xdotool
        if not success:
            try:
                window_ids = self.get_chrome_window_ids()
                for window_id in window_ids:
                    subprocess.run(["xdotool", "windowfocus", window_id], check=True)
                    subprocess.run(["xdotool", "key", "space"], check=True)
                    time.sleep(0.2)
                success = True
            except:
                pass

        # Method 3: Try using D-Bus
        if not success:
            try:
                bus = dbus.SessionBus()
                for service in bus.list_names():
                    if "chrome" in service.lower():
                        proxy = bus.get_object(service, "/org/mpris/MediaPlayer2")
                        interface = dbus.Interface(
                            proxy, "org.mpris.MediaPlayer2.Player"
                        )
                        interface.Pause()
                        success = True
                        break
            except:
                pass

        return success

    def play_media(self):
        """Resume media using multiple methods"""
        success = False

        try:
            subprocess.run(
                ["playerctl", "--player=chromium,chrome", "play"],
                check=True,
                capture_output=True,
            )
            success = True
        except:
            try:
                window_ids = self.get_chrome_window_ids()
                for window_id in window_ids:
                    subprocess.run(["xdotool", "windowfocus", window_id], check=True)
                    subprocess.run(["xdotool", "key", "space"], check=True)
                    time.sleep(0.2)
                success = True
            except:
                pass

        return success

    def play_scheduled_audio(self, audio_file: str, day: str):
        """Play the scheduled audio file"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            print(f"\nTriggering scheduled audio at {current_time}")
            print(f"Playing: {audio_file}")

            # Check if media is playing and store the original state
            media_was_playing = self.check_media_playing()

            # If media is playing, try to pause it
            if media_was_playing:
                print("Media detected - attempting to pause...")
                if self.pause_media():
                    print("Successfully paused media")
                    time.sleep(1)  # Wait for media to fully pause
                else:
                    print(
                        "Warning: Could not pause media. Continuing with audio playback..."
                    )
            else:
                print("No media playing - proceeding with scheduled audio...")

            # Play the audio file
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            # Wait for the audio to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            # Only resume media if it was playing before
            if media_was_playing:
                print("Attempting to resume previously playing media...")
                if self.play_media():
                    print("Successfully resumed media")
                else:
                    print("Warning: Could not resume media")

            print("Audio playback completed")

        except Exception as e:
            print(f"Error during audio playback: {e}")

    def schedule_all_tasks(self):
        """Schedule all tasks for the current day"""
        current_day = datetime.now().strftime("%A").lower()
        if current_day not in self.schedule_dict:
            print(f"No schedule found for {current_day.capitalize()}")
            return

        # Clear any existing schedules
        schedule.clear()

        # Schedule tasks for the current day
        for time_str, audio_file in self.schedule_dict[current_day].items():
            schedule.every().day.at(time_str).do(
                self.play_scheduled_audio, audio_file, current_day
            )
            print(
                f"Scheduled: {time_str} ({self.convert_to_12hr(time_str)}) - {audio_file}"
            )

    def convert_to_12hr(self, time_24hr: str) -> str:
        """Convert 24-hour time to 12-hour format for display"""
        try:
            hour, minute = map(int, time_24hr.split(":"))
            return datetime.strptime(f"{hour}:{minute}", "%H:%M").strftime("%I:%M %p")
        except ValueError:
            return time_24hr  # Return original if conversion fails

    def run(self):
        """Run the scheduler"""
        print("\nAudio scheduler starting...")

        # Initial day setup with validation
        current_day = self.get_current_day()
        last_day_check = datetime.now()

        print(f"\nInitial day validated as: {current_day.capitalize()}")
        self.print_daily_schedule(current_day)

        self.schedule_all_tasks()

        print("\nScheduler is now running. Press Ctrl+C to exit.")
        print(f"Schedule loaded for: {current_day.capitalize()}")
        print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")

        while True:
            try:
                # Check if day has changed every minute
                now = datetime.now()
                if (now - last_day_check).seconds >= 60:
                    new_day = self.get_current_day()
                    if new_day != current_day:
                        print(
                            f"\nDay change detected: {current_day.capitalize()} → {new_day.capitalize()}"
                        )
                        print(f"Time of change: {now.strftime('%H:%M:%S')}")
                        current_day = new_day
                        self.schedule_all_tasks()
                        self.print_daily_schedule(current_day)
                    last_day_check = now

                schedule.run_pending()
                time.sleep(1)

            except Exception as e:
                print(f"Error in main loop: {e}")
                # Log additional diagnostic information
                print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
                print(f"Current day: {current_day}")
                print(f"Scheduled jobs: {len(schedule.jobs)}")
                # Continue running despite errors
                time.sleep(5)  # Wait a bit before retrying


if __name__ == "__main__":
    scheduler = AudioScheduler()
    scheduler.run()
