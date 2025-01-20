import asyncio
import logging
import subprocess
import time
from datetime import datetime
from datetime import time as dtime
from functools import partial

import pygame
import schedule
import win32api
import win32con
import win32gui
import winsdk.windows.media.control as wmc

from mapping_london import mapp


class AudioScheduler:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        # Dictionary to store schedule times and corresponding audio files by day
        self.schedule_dict = mapp
        # Validate time format
        self.validate_times()

        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

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
                if "Chrome" in class_name:
                    windows.append(hwnd)
            return True

        win32gui.EnumWindows(callback, chrome_windows)
        return chrome_windows

    async def check_media_playing(self):
        """Check if media is playing using Windows media controls"""
        try:
            session = await self.get_media_session()
            if session:
                info = await session.try_get_media_properties_async()
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
        try:
            session = await self.get_media_session()
            if session:
                await session.try_pause_async()
                return True

            # Fallback: Try sending media keys to Chrome windows
            chrome_windows = self.get_chrome_windows()
            for hwnd in chrome_windows:
                win32gui.SetForegroundWindow(hwnd)
                win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                win32api.keybd_event(
                    win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0
                )
                time.sleep(0.2)

            return bool(chrome_windows)
        except Exception as e:
            self.logger.error(f"Error pausing media: {e}")
            return False

    async def play_media(self):
        """Resume media using Windows media controls"""
        try:
            session = await self.get_media_session()
            if session:
                await session.try_play_async()
                return True

            # Fallback: Try sending media keys to Chrome windows
            chrome_windows = self.get_chrome_windows()
            for hwnd in chrome_windows:
                win32gui.SetForegroundWindow(hwnd)
                win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                win32api.keybd_event(
                    win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0
                )
                time.sleep(0.2)

            return bool(chrome_windows)
        except Exception as e:
            self.logger.error(f"Error playing media: {e}")
            return False

    async def play_scheduled_audio(self, audio_file):
        """Play the scheduled audio file"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            self.logger.info(f"\nTriggering scheduled audio at {current_time}")

            # Check if media is playing and store the original state
            media_was_playing = await self.check_media_playing()

            # If media is playing, try to pause it
            if media_was_playing:
                self.logger.info("Media detected - attempting to pause...")
                if await self.pause_media():
                    self.logger.info("Successfully paused media")
                    time.sleep(1)
                else:
                    self.logger.warning(
                        "Could not pause media. Continuing with audio playback..."
                    )
            else:
                self.logger.info(
                    "No media playing - proceeding with scheduled audio..."
                )

            pygame.mixer.music.set_volume(0.65)
                    
            # Play the scheduled audio twice
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            # Only resume media if it was playing before
            if media_was_playing:
                self.logger.info("Attempting to resume previously playing media...")
                if await self.play_media():
                    self.logger.info("Successfully resumed media")
                else:
                    self.logger.warning("Could not resume media")

            self.logger.info("Audio playback completed")

        except Exception as e:
            self.logger.error(f"Error during audio playback: {e}")


    def schedule_all_tasks(self):
        """Schedule all tasks from the dictionary"""
        for day, times in self.schedule_dict.items():
            if day.lower() == datetime.now().strftime("%A").lower():
                for time_str, audio_file in times.items():
                    schedule.every().day.at(time_str).do(
                        partial(asyncio.run, self.play_scheduled_audio(audio_file))
                    )
                    self.logger.info(
                        f"Scheduled audio {audio_file} for {day.capitalize()} at {time_str}"
                    )

    def run(self):
        """Run the scheduler"""
        self.logger.info("\nAudio scheduler starting...")
        self.schedule_all_tasks()
        self.logger.info("\nScheduler is now running. Scheduled times:")
        for day, times in self.schedule_dict.items():
            print(f"{day.capitalize()}:")
            for time_str in sorted(times.keys()):
                print(f"  - {time_str} ({self.convert_to_12hr(time_str)})")

        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
            
    def convert_to_12hr(self, time_24hr):
        """Convert 24-hour time to 12-hour format for display"""
        hour, minute = map(int, time_24hr.split(":"))
        return datetime.strptime(f"{hour}:{minute}", "%H:%M").strftime("%I:%M %p")


if __name__ == "__main__":
    scheduler = AudioScheduler()
    scheduler.run()
