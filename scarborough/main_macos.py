import os
import subprocess
import time
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
        print("=" * 60)
        print("SCARBOROUGH AUDIO SCHEDULER - INITIALIZATION (macOS)")
        print("=" * 60)

        # Get the directory where this script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Script directory: {self.script_dir}")

        print("\nInitializing pygame mixer...")
        try:
            pygame.mixer.init()
            print("✓ Pygame mixer initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize pygame mixer: {e}")
            raise

        self.schedule_dict = SCHEDULE
        self.valid_days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

        print("\nValidating schedule and audio files...")
        self.validate_schedule()

        print("\nChecking system dependencies...")
        self.check_dependencies()

        print("\n✓ Initialization complete")
        print("=" * 60)

    def check_dependencies(self):
        """Check if required system tools are available (macOS uses AppleScript)"""
        print("Checking for osascript (AppleScript)...")
        try:
            result = subprocess.run(
                ["which", "osascript"], check=True, capture_output=True, timeout=2
            )
            osascript_path = result.stdout.decode().strip()
            print(f"✓ osascript found: {osascript_path}")
        except subprocess.CalledProcessError:
            print("✗ osascript not found")
            raise SystemError(
                "osascript not available. This should be available on all macOS systems."
            )
        except subprocess.TimeoutExpired:
            print("✗ osascript check timed out")
            raise SystemError("Failed to check for osascript")

    def validate_schedule(self):
        """Validate schedule configuration"""
        total_files = 0
        days_validated = 0

        for day in self.schedule_dict.keys():
            if day.lower() not in self.valid_days:
                print(f"✗ Invalid day: {day}")
                raise ValueError(f"Invalid day: {day}")

            time_slots = 0
            for time_str, audio_file in self.schedule_dict[day].items():
                try:
                    hour, minute = map(int, time_str.split(":"))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        print(f"✗ Invalid time: {time_str}")
                        raise ValueError(f"Invalid time: {time_str}")
                except ValueError:
                    print(f"✗ Invalid time format for {day}: {time_str}")
                    raise ValueError(
                        f"Invalid time format for {day}: {time_str}. Use HH:MM"
                    )

                # Convert relative path to absolute path
                audio_path = os.path.join(self.script_dir, audio_file)
                if not os.path.exists(audio_path):
                    print(f"✗ Audio file not found: {audio_path}")
                    raise FileNotFoundError(f"Audio file not found: {audio_path}")

                time_slots += 1
                total_files += 1

            days_validated += 1
            print(f"✓ {day.capitalize()}: {time_slots} time slots validated")

        print(
            f"\n✓ Validated {days_validated} days with {total_files} total scheduled audio files"
        )

    def check_media_playing(self):
        """Check if media is currently playing using AppleScript"""
        try:
            # Check common macOS media players
            script = """
            tell application "System Events"
                set musicPlaying to false
                set spotifyPlaying to false

                -- Check Music app
                if exists process "Music" then
                    tell application "Music"
                        if player state is playing then
                            set musicPlaying to true
                        end if
                    end tell
                end if

                -- Check Spotify
                if exists process "Spotify" then
                    tell application "Spotify"
                        if player state is playing then
                            set spotifyPlaying to true
                        end if
                    end tell
                end if

                return musicPlaying or spotifyPlaying
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=2
            )
            return result.returncode == 0 and result.stdout.strip().lower() == "true"
        except (subprocess.TimeoutExpired, Exception):
            return False

    def pause_media(self):
        """Pause currently playing media using AppleScript"""
        try:
            script = """
            tell application "System Events"
                -- Pause Music app
                if exists process "Music" then
                    tell application "Music"
                        if player state is playing then
                            pause
                        end if
                    end tell
                end if

                -- Pause Spotify
                if exists process "Spotify" then
                    tell application "Spotify"
                        if player state is playing then
                            pause
                        end if
                    end tell
                end if
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False

    def play_media(self):
        """Resume paused media using AppleScript"""
        try:
            script = """
            tell application "System Events"
                -- Resume Music app
                if exists process "Music" then
                    tell application "Music"
                        if player state is paused then
                            play
                        end if
                    end tell
                end if

                -- Resume Spotify
                if exists process "Spotify" then
                    tell application "Spotify"
                        if player state is paused then
                            play
                        end if
                    end tell
                end if
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False

    def play_scheduled_audio(self, audio_file: str):
        """Play scheduled announcement, pausing and resuming media if needed"""
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"\n{'='*60}")
        print(f"[{current_time}] SCHEDULED ANNOUNCEMENT TRIGGERED")
        print(f"{'='*60}")

        media_was_playing = False

        try:
            # Convert relative path to absolute path
            audio_path = os.path.join(self.script_dir, audio_file)
            filename = os.path.basename(audio_file)

            print(f"Audio file: {filename}")
            print(f"Full path: {audio_path}")

            if not os.path.exists(audio_path):
                print(f"✗ Error: Audio file not found: {audio_path}")
                return

            # Check if media is playing
            print("\nChecking media playback status...")
            media_was_playing = self.check_media_playing()

            if media_was_playing:
                print("✓ Media is playing - attempting to pause...")
                if self.pause_media():
                    print("✓ Media paused successfully")
                else:
                    print("⚠ Warning: Failed to pause media, continuing anyway...")
                time.sleep(0.5)
            else:
                print("• No media currently playing")

            # Play announcement
            print(f"\n▶ Playing announcement: {filename}")
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()
            print("✓ Announcement playback completed")

        except Exception as e:
            print(f"✗ Error during playback: {e}")
            import traceback

            traceback.print_exc()
        finally:
            # Resume media if it was playing
            if media_was_playing:
                print("\nAttempting to resume media...")
                time.sleep(0.3)
                if self.play_media():
                    print("✓ Media resumed successfully")
                else:
                    print("⚠ Warning: Failed to resume media")

            print(f"{'='*60}\n")

    def schedule_all_tasks(self):
        """Schedule all tasks for the current day"""
        current_day = datetime.now().strftime("%A").lower()

        print(f"\n{'='*60}")
        print(f"LOADING SCHEDULE FOR {current_day.upper()}")
        print(f"{'='*60}")

        if current_day not in self.schedule_dict:
            print(f"✗ No schedule found for {current_day.capitalize()}")
            return

        schedule.clear()

        scheduled_times = []
        for time_str, audio_file in self.schedule_dict[current_day].items():
            schedule.every().day.at(time_str).do(self.play_scheduled_audio, audio_file)
            scheduled_times.append((time_str, os.path.basename(audio_file)))

        # Sort and display upcoming schedules
        scheduled_times.sort()
        print(f"✓ Loaded {len(scheduled_times)} scheduled announcements\n")

        # Show next 5 upcoming schedules
        current_time = datetime.now().strftime("%H:%M")
        upcoming = [t for t in scheduled_times if t[0] >= current_time]

        if upcoming:
            print("Next upcoming announcements:")
            for i, (time_str, filename) in enumerate(upcoming[:5], 1):
                print(f"  {i}. {time_str} - {filename}")
            if len(upcoming) > 5:
                print(f"  ... and {len(upcoming) - 5} more")
        else:
            print("No more announcements scheduled for today")

        print(f"{'='*60}\n")

    def run(self):
        """Run the scheduler"""
        print("\n" + "=" * 60)
        print("SCARBOROUGH AUDIO SCHEDULER - STARTING")
        print("=" * 60)

        current_day = datetime.now().strftime("%A").lower()
        current_time = datetime.now().strftime("%H:%M:%S")

        print(f"\nCurrent day: {current_day.capitalize()}")
        print(f"Current time: {current_time}")
        print(f"System time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")

        self.schedule_all_tasks()

        last_day = current_day
        loop_count = 0

        print("✓ Scheduler is running - Press Ctrl+C to stop\n")
        print("Waiting for scheduled times...\n")

        try:
            while True:
                schedule.run_pending()

                now = datetime.now()
                new_day = now.strftime("%A").lower()

                # Check for day change
                if new_day != last_day:
                    print(f"\n{'='*60}")
                    print(
                        f"DAY CHANGED: {last_day.capitalize()} → {new_day.capitalize()}"
                    )
                    print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"{'='*60}")
                    self.schedule_all_tasks()
                    last_day = new_day

                # Print heartbeat every 60 seconds to show it's alive
                loop_count += 1
                if loop_count % 60 == 0:
                    current_time = now.strftime("%H:%M:%S")
                    pending_count = len(schedule.jobs)
                    print(
                        f"[{current_time}] Scheduler active - {pending_count} jobs scheduled"
                    )

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("SCHEDULER STOPPED BY USER")
            print("=" * 60)
            pygame.mixer.quit()
            print("✓ Cleanup completed")
        except Exception as e:
            print("\n" + "=" * 60)
            print(f"CRITICAL ERROR: {e}")
            print("=" * 60)
            import traceback

            traceback.print_exc()
            print("\nAttempting to restart in 5 seconds...")
            time.sleep(5)
            print("Restarting scheduler...")
            self.run()  # Attempt to restart


if __name__ == "__main__":
    try:
        scheduler = AudioScheduler()
        scheduler.run()
    except Exception as e:
        print("\n" + "=" * 60)
        print("FATAL ERROR DURING INITIALIZATION")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        print("\nPlease check:")
        print("  1. All audio files exist in the audio/ folder")
        print("  2. pygame is installed (pip install pygame)")
        print("  3. schedule is installed (pip install schedule)")
        print("=" * 60)
