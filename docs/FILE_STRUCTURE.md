# VideoLib - Complete File Structure

## 📁 Project Directory Structure

```
project-root/
├── videolib/                           # Main library package
│   ├── __init__.py                     # Library main interface with quick functions
│   │
│   ├── core/                           # Core processing modules
│   │   ├── __init__.py                 # Core package exports
│   │   ├── ffmpeg_wrapper.py           # FFmpeg/FFprobe wrapper with commands
│   │   ├── video_processor.py          # Main video processor orchestrator
│   │   ├── downloader.py               # Video downloader (OOP)
│   │   ├── splitter.py                 # Video splitter by size (OOP)
│   │   └── clipper.py                  # Video clipper by intervals (OOP)
│   │
│   ├── utils/                          # Utility modules
│   │   ├── __init__.py                 # Utils package exports
│   │   ├── file_manager.py             # File operations utilities
│   │   ├── format_parser.py            # Size/time format parsing
│   │   ├── path_builder.py             # Path construction helpers
│   │   └── validators.py               # Input/config validation
│   │
│   ├── config/                         # Configuration management
│   │   ├── __init__.py                 # Config package exports
│   │   ├── config_manager.py           # Configuration manager
│   │   └── task_definitions.py         # Task templates & workflow builder
│   │
│   └── interfaces/                     # Abstract interfaces (optional)
│       ├── __init__.py                 # Interfaces package exports
│       ├── base_interface.py           # Base abstract interfaces
│       └── task_interface.py           # Task-specific interfaces
│
├── cli/                                # CLI front-end implementations
│   ├── __init__.py                     # CLI package marker
│   ├── interactive_main.py             # CLI interact with functions of video lib folder
│   ├── main.py                         # Command-line argument parser
│   ├── commands.py                     # CLI command implementations
│   └── ui.py                           # CLI formatting utilities
│
├── docs/                               # Documentation
│   ├── FILE_STRUCTURE.md               # File Architecture
│   ├── sample_config.json              # Batch Processing Json Configuration Sample
│
├── tests/                              # Unit tests (skeleton)
│   └── __init__.py
│
├── videolib_launcher.py                # launcher
│
├── run_simple.py                       # Simple launcher script
└── run_videolib.bat                    # Windows batch launcher

```