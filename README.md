# VideoLib CLI

**Interactive Command-Line Interface for VideoLib**

A user-friendly CLI application built on top of the [VideoLib](https://github.com/USERNAME/videolib) library. Process videos through an interactive menu system or batch configuration files.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)

## Features

- 🎯 **Interactive Menu**: Step-by-step guided interface for all operations
- ⌨️ **Keyboard Interrupts**: Press 'q' anytime during processing to cancel
- 📊 **Progress Tracking**: Real-time progress bars for long operations
- 📝 **Batch Processing**: Run multiple tasks from JSON configuration files
- ✅ **Input Validation**: Comprehensive validation with helpful error messages
- 🎨 **Clean UI**: Well-formatted output with clear visual hierarchy

## Screenshots

```
╔═══════════════════════════════════════════════════════════╗
║                   VIDEOLIB PROCESSOR                      ║
║            Interactive Video Processing Tool              ║
╚═══════════════════════════════════════════════════════════╝

MAIN MENU:
--------------------------------------------------
1. Download video from URL
2. Split video by size
3. Create video clips
4. Batch process from config file
5. View FFmpeg/FFprobe info
0. Exit

> Your choice: _
```

## Installation

### Prerequisites

1. **FFmpeg** must be installed:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`

2. **VideoLib** library must be installed:
   ```bash
   pip install git+https://github.com/USERNAME/videolib.git
   ```

### Install VideoLib CLI

```bash
# Clone the repository
git clone https://github.com/USERNAME/videolib-cli.git
cd videolib-cli

# Install dependencies
pip install -r requirements.txt

# Run the CLI
python main.py
```

## Quick Start

### Interactive Mode

Simply run the main script and follow the interactive prompts:

```bash
python main.py
```

The CLI will guide you through:
1. Selecting an operation (download, split, clip, or batch)
2. Entering required parameters with validation
3. Confirming settings before processing
4. Monitoring progress with real-time updates
5. Viewing results with file details

### Batch Processing Mode

Create a configuration file (e.g., `tasks.json`):

```json
{
  "output_dir": "./output",
  "temp_dir": "./temp",
  "tasks": [
    {
      "type": "download",
      "url": "https://youtube.com/watch?v=VIDEO_ID",
      "output_name": "my_video",
      "output_extension": "mp4"
    },
    {
      "type": "split",
      "source_file": "large_video.mp4",
      "target_size_mb": 500,
      "output_name": "segment",
      "output_extension": "mp4"
    }
  ]
}
```

Then run batch processing through the menu (option 4).

## Features Overview

### 1. Download Video from URL

Download videos from YouTube and other platforms:

```
VIDEO DOWNLOAD WORKFLOW
--------------------------------------------------

Step 1: Video URL
> Enter video URL: https://youtube.com/watch?v=VIDEO_ID

Step 2: Output Settings
> Output name: my_video
> Output extension [mp4]: mp4

Step 3: Quality Settings
> Video quality [best]: best

Step 4: Confirmation
-> URL: https://youtube.com/watch?v=VIDEO_ID
-> Output: my_video.mp4
-> Quality: best

? Proceed with download? [Y/n]: y

-> Starting download...
-> Press 'q' anytime to cancel
[████████████████████] 100% Downloading... | Press 'q' to cancel

✓ Download complete!
-> Output file: my_video.mp4 (45.2 MB)
```

### 2. Split Video by Size

Split large videos into smaller segments:

```
VIDEO SPLIT WORKFLOW
--------------------------------------------------

Step 1: Source Video
> Enter source video file path: large_video.mp4

-> Analyzing video...
-> Duration: 01:30:45
-> Current size: 2.1 GB

Step 2: Target Size
> Enter target size per segment: 500MB

-> Estimated segments: 5 segments

Step 3: Output Settings
> Output name prefix: segment
> Output extension [mp4]: mp4

Step 4: Confirmation
? Proceed with splitting? [Y/n]: y

-> Splitting into 5 segments...
[████████████████████] 100% Processing... | Press 'q' to cancel

✓ Successfully created 5 segments:
   1. segment_001.mp4 (500.0 MB)
   2. segment_002.mp4 (500.0 MB)
   3. segment_003.mp4 (500.0 MB)
   4. segment_004.mp4 (500.0 MB)
   5. segment_005.mp4 (120.0 MB)
```

### 3. Create Video Clips

Extract specific time intervals:

```
VIDEO CLIP CREATION WORKFLOW
--------------------------------------------------

Step 1: Source Video
> Enter source video file path: movie.mp4

-> Duration: 02:15:30
-> Size: 1.5 GB

Step 2: Output Settings
> Output name prefix: clip
> Output extension [mp4]: mp4

Step 3: Clip Intervals
-> Enter time intervals (HH:MM:SS, MM:SS, or seconds)
-> Enter 'done' when finished

-> Interval 1:
>   Start time: 0:30
>   End time: 1:45
-> Added interval: 0:30 to 1:45

-> Interval 2:
>   Start time: 2:00
>   End time: 3:30
-> Added interval: 2:00 to 3:30

-> Interval 3:
>   Start time: done

Step 4: Codec Settings
> Video codec [copy]: copy
> Audio codec [copy]: copy

Step 5: Confirmation
-> Source: movie.mp4
-> Intervals: 2 clips
   1. 0:30 to 1:45
   2. 2:00 to 3:30

? Proceed with clip creation? [Y/n]: y

-> Creating 2 clips...
[████████████████████] 100% Processing... | Press 'q' to cancel

✓ Successfully created 2 clips:
   1. clip_001.mp4 (25.0 MB)
   2. clip_002.mp4 (30.0 MB)
```

### 4. Batch Processing

Process multiple tasks from a configuration file:

```
BATCH PROCESSING WORKFLOW
--------------------------------------------------

Step 1: Configuration File
> Enter config file path: tasks.json

-> Loading configuration...
-> Found 3 tasks

Step 2: Review Tasks
1. Download: https://youtube.com/watch?v=VIDEO_ID
2. Split: large_video.mp4 (target: 500MB)
3. Clip: movie.mp4 (2 intervals)

? Proceed with batch processing? [Y/n]: y

-> Processing task 1/3: Download
[████████████████████] 100% | Press 'q' to cancel
✓ Task 1 complete

-> Processing task 2/3: Split
[████████████████████] 100% | Press 'q' to cancel
✓ Task 2 complete

-> Processing task 3/3: Clip
[████████████████████] 100% | Press 'q' to cancel
✓ Task 3 complete

==================================================
BATCH PROCESSING RESULTS
==================================================
✓ 3 of 3 tasks completed successfully
-> Total output files: 8 files
```

## Keyboard Shortcuts

- **'q'**: Cancel current operation and return to menu
- **Ctrl+C**: Emergency exit
- **Enter**: Confirm default values

## Project Structure

```
videolib-cli/
├── main.py                  # Entry point
├── cli/                     # CLI modules
│   ├── __init__.py
│   ├── interactive_main.py  # Interactive menu system
│   ├── commands.py          # Command implementations
│   └── ui.py                # UI formatting utilities
├── docs/                    # Documentation
│   ├── FILE_STRUCTURE.md
│   ├── sample_config.json
│   └── USAGE.md
├── run_simple.py            # Simple launcher
├── run_videolib.bat         # Windows batch launcher
├── requirements.txt         # Dependencies
└── README.md
```

## Configuration File Format

See [sample_config.json](docs/sample_config.json) for a complete example.

Basic structure:

```json
{
  "output_dir": "./output",
  "temp_dir": "./temp",
  "tasks": [
    {
      "type": "download|split|clip",
      // ... task-specific parameters
    }
  ]
}
```

## Development

### Local Development with VideoLib

To develop with a local copy of VideoLib:

```bash
# Clone both repositories
git clone https://github.com/USERNAME/videolib.git
git clone https://github.com/USERNAME/videolib-cli.git

# Install videolib in editable mode
cd videolib
pip install -e .

# Run the CLI
cd ../videolib-cli
python main.py
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/
```

## Troubleshooting

### FFmpeg Not Found

**Error**: `FFmpeg not found in system PATH`

**Solution**: Install FFmpeg and add it to your system PATH:
- Windows: Add FFmpeg bin directory to PATH environment variable
- Linux/macOS: FFmpeg should be in `/usr/local/bin` or `/usr/bin`

### VideoLib Not Found

**Error**: `ModuleNotFoundError: No module named 'videolib'`

**Solution**: Install the VideoLib library:
```bash
pip install git+https://github.com/USERNAME/videolib.git
```

### Permission Denied

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solution**: Check write permissions for output directory or run with appropriate privileges.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Related Projects

- [VideoLib](https://github.com/USERNAME/videolib) - Core video processing library

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📝 [Documentation](https://github.com/USERNAME/videolib-cli#readme)
- 🐛 [Issue Tracker](https://github.com/USERNAME/videolib-cli/issues)
- 💬 [Discussions](https://github.com/USERNAME/videolib-cli/discussions)

## Author

Your Name - [@yourhandle](https://github.com/USERNAME)

Project Link: [https://github.com/USERNAME/videolib-cli](https://github.com/USERNAME/videolib-cli)
