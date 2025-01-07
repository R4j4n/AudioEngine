import subprocess
import time
from datetime import datetime
from datetime import time as dtime

import dbus
import pygame
import schedule

from mapping import mapp


class AudioScheduler:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        # Dictionary to store schedule times and corresponding audio files by day
        self.schedule_dict = mapp
        # Validate time format
        self.validate_times()

        # Check if required tools are installed
        self.check_dependencies()

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
                        "Please use 24-hour format (HH:MM), e.g., '14:30' for 2:30 PM"
                    )

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

        # Method 1: Try using playerctl
        try:
            subprocess.run(
                ["playerctl", "--player=chromium,chrome", "play"],
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

        return success

    def play_scheduled_audio(self, audio_file):
        """Play the scheduled audio file"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            print(f"\nTriggering scheduled audio at {current_time}")

            # Check if media is playing and store the original state
            media_was_playing = self.check_media_playing()

            # If media is playing, try to pause it
            if media_was_playing:
                print("Media detected - attempting to pause...")
                if self.pause_media():
                    print("Successfully paused media")
                    time.sleep(1)  # Wait a bit longer for media to fully pause
                else:
                    print(
                        "Warning: Could not pause media. Continuing with audio playback..."
                    )
            else:
                print("No media playing - proceeding with scheduled audio...")

            # # Play the scheduled audio
            # print(f"Playing scheduled audio: {audio_file}")
            # pygame.mixer.music.load(audio_file)
            # pygame.mixer.music.play()

            # Play the scheduled audio twice
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            # Wait for the audio to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

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
        """Schedule all tasks from the dictionary"""
        for day, times in self.schedule_dict.items():
            for time_str, audio_file in times.items():
                if day.lower() == datetime.now().strftime("%A").lower():
                    schedule.every().day.at(time_str).do(
                        self.play_scheduled_audio, audio_file
                    )
                    print(
                        f"Scheduled audio {audio_file} for {day.capitalize()} at {time_str}"
                    )

    def run(self):
        """Run the scheduler"""
        print("\nAudio scheduler starting...")
        self.schedule_all_tasks()
        print("\nScheduler is now running. Scheduled times:")
        for day, times in self.schedule_dict.items():
            print(f"{day.capitalize()}:")
            for time_str in sorted(times.keys()):
                print(f"  - {time_str} ({self.convert_to_12hr(time_str)})")

        while True:
            schedule.run_pending()
            time.sleep(1)

    def convert_to_12hr(self, time_24hr):
        """Convert 24-hour time to 12-hour format for display"""
        hour, minute = map(int, time_24hr.split(":"))
        return datetime.strptime(f"{hour}:{minute}", "%H:%M").strftime("%I:%M %p")


if __name__ == "__main__":
    scheduler = AudioScheduler()
    scheduler.run()
