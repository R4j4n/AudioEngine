# Scarborough Audio Scheduler

## Overview
Standalone audio scheduler for Scarborough location with updated wristband color sequence.

## Color Order
Pink → Yellow → Orange → Green → Aqua → Silver → Brown → Blue → Red

## Features
- ✓ Bulletproof error handling with detailed status messages
- ✓ Automatic media pause/resume functionality
- ✓ Self-contained (no external mapping file needed)
- ✓ Comprehensive validation on startup
- ✓ Heartbeat messages every 60 seconds
- ✓ Auto-restart on critical errors
- ✓ Detailed logging for all operations

## Requirements
```bash
sudo apt-get install playerctl
pip install pygame schedule
```

## Running
```bash
cd /Users/Rajan/Documents/GitHub/AudioEngine/scarborough
python3 main_linux.py
```

## What You'll See

### On Startup
```
============================================================
SCARBOROUGH AUDIO SCHEDULER - INITIALIZATION
============================================================
Script directory: /path/to/scarborough

Initializing pygame mixer...
✓ Pygame mixer initialized successfully

Validating schedule and audio files...
✓ Sunday: 38 time slots validated
✓ Monday: 38 time slots validated
...
✓ Validated 7 days with 266 total scheduled audio files

Checking system dependencies...
Checking for playerctl...
✓ playerctl found: /usr/bin/playerctl

✓ Initialization complete
============================================================
```

### During Operation
```
============================================================
[14:30:00] SCHEDULED ANNOUNCEMENT TRIGGERED
============================================================
Audio file: blue.wav
Full path: /path/to/audio/blue.wav

Checking media playback status...
✓ Media is playing - attempting to pause...
✓ Media paused successfully

▶ Playing announcement: blue.wav
✓ Announcement playback completed

Attempting to resume media...
✓ Media resumed successfully
============================================================
```

### Heartbeat
```
[15:00:00] Scheduler active - 38 jobs scheduled
```

## Error Handling
The scheduler will:
1. Show detailed error messages with stack traces
2. Validate all files exist before starting
3. Continue running even if individual announcements fail
4. Attempt auto-restart on critical errors
5. Clean up properly on Ctrl+C

## Audio Files
All audio files are in the `audio/` folder as `.wav` files.
