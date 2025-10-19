#!/usr/bin/env python3
"""
VideoLib CLI - Main Entry Point

A command-line interface for the VideoLib video processing library.
Provides interactive menu and batch processing capabilities.
"""
import sys
import os
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("X FFmpeg not found in System PATH")
    print("Please install FFmpeg from: https://ffmpeg.org/download.html")
    print("Or specify custom paths in the application settings")
    return False

def check_current_files_integrity():
    """Check all required files are present in the current directory"""
    required_files = [
        "main.py", 
        "cli/__init__.py", 
        "cli/interactive_main.py", 
        "cli/commands.py",
        "cli/ui.py"
    ]
    current_dir = Path(__file__).parent
    for file in required_files:
        if not (current_dir / file).exists():
            return False
    return True

def check_videolib_environment():
    """Check if VideoLib library is installed in the environment"""
    try:
        import videolib
        return True
    except ImportError:
        return False

def path_exists(path: str) -> bool:
    """Check if a given path exists"""
    return Path(path).exists()

def check_requirements():
    """Check if VideoLib library is installed"""

    # Get current directory
    current_dir = Path(__file__).parent
    
    # Check for videolib package
    videolib_path = current_dir / "videolib"

    # Check for CLI module
    if not check_current_files_integrity():
        return 1
    
    if not path_exists(videolib_path) and not check_videolib_environment():
        return 2
    else:
        return 0
        

# Validation and Import CLI modules
def main():
    """Main entry point for VideoLib CLI"""
    print("╔" + "=" * 64 + "╗")
    print("║                      VIDEOLIB PROCESSOR                        ║")
    print("║              Interactive Video Processing Tool                 ║")
    print("╚" + "=" * 64 + "╝")
    
    # Check FFmpeg (warning only)
    ffmpeg_available = check_ffmpeg()
    if not ffmpeg_available:
        print("\nContinuing anyway - you can configure FFmpeg paths later...")
        input("Press Enter to continue...")
    
    # Check VideoLib library (fatal)
    if check_requirements() == 1:
        print("X FileIntegrityError: Missing required CLI files")
        print("Please ensure all files are present")
        print("More info: https://github.com/BrianAtCode/videolib-cli.git")
        sys.exit(1)
    elif check_requirements() == 2:
        print("X ModuleNotFoundError: No module named 'videolib'")
        print("Please install VideoLib from: https://github.com/BrianAtCode/videolib.git")
        sys.exit(1)
        
    # Add parent directory to path for local development (sibling videolib repo)
    parent_dir = Path(__file__).parent.parent
    if parent_dir.exists():
        p = str(parent_dir)
        if p not in sys.path:
            sys.path.insert(0, p)

    # Ensure project root (so 'cli' package is importable when running main.py)
    current_dir = Path(__file__).parent
    proj = str(current_dir)
    if proj not in sys.path:
        sys.path.insert(0, proj)
    
    try:
        from cli.interactive_main import InteractiveCLI
        cli = InteractiveCLI()
        cli.run()
    except ImportError as e:
        print(f"\nX Import error: {e}")
        print("Make sure the VideoLib package is properly installed")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n-> Goodbye!")
    except Exception as e:
        print(f"\n! Unexpected error: {e}")
        print("Please report this issue")
        sys.exit(1)

if __name__ == "__main__":
    main()
