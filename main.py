#!/usr/bin/env python3
"""
VideoLib CLI - Main Entry Point

A command-line interface for the VideoLib video processing library.
Provides interactive menu and batch processing capabilities.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for local development
# Remove this if videolib is installed via pip
parent_dir = Path(__file__).parent.parent
if parent_dir.exists():
    sys.path.insert(0, str(parent_dir))

def check_requirements():
    """Check if all required components are present"""
    current_dir = Path(__file__).parent
    
    # Check for videolib package
    videolib_path = current_dir / "videolib"
    if not videolib_path.exists():
        print("X VideoLib package not found!")
        print(f"Expected location: {videolib_path}")
        return False
    
    # Check for enhanced CLI with 'q' interrupt support
    cli_path = current_dir / "cli" / "interactive_main.py"
    if not cli_path.exists():
        print("X Enhanced Interactive CLI with 'q' interrupt not found!")
        print(f"Expected location: {cli_path}")
        return False
    
    return True

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
    
    print("! FFmpeg not found in PATH")
    print("Please install FFmpeg from: https://ffmpeg.org/download.html")
    print("Or specify custom paths in the application settings")
    return False

# Validation and Import CLI modules
def main():
    """Main entry point for VideoLib CLI"""
    print("VideoLib - Video Processing Tool (Enhanced with 'q' interrupt)")
    print("=" * 65)
    
    # Check requirements
    if not check_requirements():
        print("\nX Requirements check failed")
        sys.exit(1)
    
    # Check FFmpeg (warning only)
    ffmpeg_available = check_ffmpeg()
    if not ffmpeg_available:
        print("\nContinuing anyway - you can configure FFmpeg paths later...")
        input("Press Enter to continue...")
    
    
    # Add paths and launch enhanced CLI
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
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
