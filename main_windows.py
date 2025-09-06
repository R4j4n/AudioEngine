# Enhanced Windows Audio Scheduler with comprehensive features
import asyncio
import logging
import subprocess
import time
from datetime import datetime
from datetime import time as dtime
from functools import partial
from typing import Dict, List

import pygame
import schedule
import win32api
import win32con
import win32gui
import winsdk.windows.media.control as wmc
from prettytable import PrettyTable

from mapping_london import mapp


class AudioScheduler:
    def __init__(self):
        # Initialize pygame mixer for audio playbook
        pygame.mixer.init()

        # Dictionary to store schedule times and corresponding audio files by day
        self.schedule_dict = mapp
        self.validate_times()

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

        # Initialize logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

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
        """Update the current day with validation"""
        # Get current day using datetime
        current_day_datetime = datetime.now().strftime("%A").lower()

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
                        "Please use 24-hour format (HH:MM), e.g., '14:30' for 2:30 PM"
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
                    (
                        audio_file.split("\\")[-1]
                        if "\\" in audio_file
                        else audio_file.split("/")[-1]
                    ),  # Show only filename, not full path
                ]
            )

        print(f"\nSchedule for {day.capitalize()}:")
        print(table)

    def print_all_schedules(self):
        """Print schedules for all days"""
        for day in self.schedule_dict.keys():
            self.print_daily_schedule(day)
            print("\n" + "=" * 80 + "\n")  # Separator between days

    async def get_media_session(self):
        """Get the current media session"""
        try:
            sessions = (
                await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
            )
            current_session = sessions.get_current_session()
            return current_session
        except Exception as e:
            self.logger.error(f"Error getting media session: {e}")
            return None

    def get_chrome_windows(self):
        """Get all Chrome window handles"""
        chrome_windows = []

        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                class_name = win32gui.GetClassName(hwnd)
                window_text = win32gui.GetWindowText(hwnd)
                if "Chrome" in class_name or "chrome" in window_text.lower():
                    windows.append(hwnd)
            return True

        win32gui.EnumWindows(callback, chrome_windows)
        return chrome_windows

    async def check_media_playing(self):
        """Check if media is playing using Windows media controls"""
        try:
            session = await self.get_media_session()
            if session:
                playback_info = session.get_playback_info()
                return (
                    playback_info.playback_status
                    == wmc.GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING
                )
            return False
        except Exception as e:
            self.logger.error(f"Error checking media status: {e}")
            return False

    async def pause_media(self):
        """Pause media using Windows media controls"""
        success = False

        try:
            # Method 1: Try using Windows Media Control
            session = await self.get_media_session()
            if session:
                await session.try_pause_async()
                success = True
        except Exception as e:
            self.logger.warning(f"Windows Media Control pause failed: {e}")

        # Method 2: Fallback - Try sending media keys to Chrome windows
        if not success:
            try:
                chrome_windows = self.get_chrome_windows()
                for hwnd in chrome_windows:
                    win32gui.SetForegroundWindow(hwnd)
                    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                    win32api.keybd_event(
                        win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0
                    )
                    time.sleep(0.2)
                success = bool(chrome_windows)
            except Exception as e:
                self.logger.warning(f"Chrome window media key pause failed: {e}")

        # Method 3: Try sending spacebar to active Chrome window
        if not success:
            try:
                chrome_windows = self.get_chrome_windows()
                for hwnd in chrome_windows:
                    win32gui.SetForegroundWindow(hwnd)
                    win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
                    win32api.keybd_event(
                        win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0
                    )
                    time.sleep(0.2)
                success = bool(chrome_windows)
            except Exception as e:
                self.logger.warning(f"Chrome window spacebar pause failed: {e}")

        return success

    async def play_media(self):
        """Resume media using Windows media controls"""
        success = False

        try:
            # Method 1: Try using Windows Media Control
            session = await self.get_media_session()
            if session:
                await session.try_play_async()
                success = True
        except Exception as e:
            self.logger.warning(f"Windows Media Control play failed: {e}")

        # Method 2: Fallback - Try sending media keys to Chrome windows
        if not success:
            try:
                chrome_windows = self.get_chrome_windows()
                for hwnd in chrome_windows:
                    win32gui.SetForegroundWindow(hwnd)
                    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                    win32api.keybd_event(
                        win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0
                    )
                    time.sleep(0.2)
                success = bool(chrome_windows)
            except Exception as e:
                self.logger.warning(f"Chrome window media key play failed: {e}")

        # Method 3: Try sending spacebar to active Chrome window
        if not success:
            try:
                chrome_windows = self.get_chrome_windows()
                for hwnd in chrome_windows:
                    win32gui.SetForegroundWindow(hwnd)
                    win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
                    win32api.keybd_event(
                        win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0
                    )
                    time.sleep(0.2)
                success = bool(chrome_windows)
            except Exception as e:
                self.logger.warning(f"Chrome window spacebar play failed: {e}")

        return success

    async def play_scheduled_audio(self, audio_file: str, day: str):
        """Play the scheduled audio file"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            print(f"\nTriggering scheduled audio at {current_time}")
            print(f"Playing: {audio_file}")

            # Check if media is playing and store the original state
            media_was_playing = await self.check_media_playing()

            # If media is playing, try to pause it
            if media_was_playing:
                print("Media detected - attempting to pause...")
                if await self.pause_media():
                    print("Successfully paused media")
                    time.sleep(1)  # Wait for media to fully pause
                else:
                    print(
                        "Warning: Could not pause media. Continuing with audio playback..."
                    )
            else:
                print("No media playing - proceeding with scheduled audio...")

            # Set volume and play the audio file
            pygame.mixer.music.set_volume(0.65)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            # Wait for the audio to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            # Only resume media if it was playing before
            if media_was_playing:
                print("Attempting to resume previously playing media...")
                if await self.play_media():
                    print("Successfully resumed media")
                else:
                    print("Warning: Could not resume media")

            print("Audio playbook completed")

        except Exception as e:
            print(f"Error during audio playback: {e}")
            self.logger.error(f"Error during audio playback: {e}")

    def schedule_all_tasks(self):
        """Schedule all tasks for the current day"""
        current_day = self.get_current_day()
        if current_day not in self.schedule_dict:
            print(f"No schedule found for {current_day.capitalize()}")
            return

        # Clear any existing schedules
        schedule.clear()

        # Schedule tasks for the current day
        for time_str, audio_file in self.schedule_dict[current_day].items():
            schedule.every().day.at(time_str).do(
                partial(asyncio.run, self.play_scheduled_audio(audio_file, current_day))
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

            except KeyboardInterrupt:
                print("\nScheduler stopped by user.")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                self.logger.error(f"Error in main loop: {e}")
                # Log additional diagnostic information
                print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
                print(f"Current day: {current_day}")
                print(f"Scheduled jobs: {len(schedule.jobs)}")
                # Continue running despite errors
                time.sleep(5)  # Wait a bit before retrying


if __name__ == "__main__":
    try:
        scheduler = AudioScheduler()
        scheduler.run()
    except Exception as e:
        print(f"Failed to start scheduler: {e}")
        logging.error(f"Failed to start scheduler: {e}")
        input("Press Enter to exit...")
