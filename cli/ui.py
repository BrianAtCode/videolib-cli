"""
UI utilities for CLI
"""

import sys
import os
import time
from typing import Optional

class CLIFormatter:
    """CLI output formatting utilities"""
    
    @staticmethod
    def success(message: str) -> None:
        """Print success message"""
        print(f"✅ {message}")
    
    @staticmethod
    def error(message: str) -> None:
        """Print error message"""
        print(f"❌ {message}", file=sys.stderr)
    
    @staticmethod
    def warning(message: str) -> None:
        """Print warning message"""
        print(f"⚠️ {message}")
    
    @staticmethod
    def info(message: str) -> None:
        """Print info message"""
        print(f"ℹ️ {message}")
    
    @staticmethod
    def progress(message: str) -> None:
        """Print progress message"""
        print(f"⏳ {message}")

class ProgressReporter:
    """Simple progress reporter for CLI"""
    
    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
        self.current_step = 0
        self.total_steps = 0
    
    def start(self, total_steps: int, message: str = "") -> None:
        """Start progress reporting"""
        if not self.show_progress:
            return
        
        self.total_steps = total_steps
        self.current_step = 0
        
        if message:
            print(f"🚀 {message}")
    
    def update(self, step: Optional[int] = None, message: str = "") -> None:
        """Update progress"""
        if not self.show_progress:
            return
        
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        progress_percent = (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
        progress_bar = "█" * int(progress_percent // 5)
        status = f"[{progress_bar:<20}] {progress_percent:.1f}%"
        
        if message:
            status += f" - {message}"
        
        print(f"\r{status}", end="", flush=True)
    
    def finish(self, message: str = "Completed") -> None:
        """Finish progress reporting"""
        if not self.show_progress:
            return
        
        print(f"\r✅ {message}" + " " * 50)  # Clear any remaining progress bar

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text"""
        return f"{color}{text}{cls.END}"

class UIHelper:
    """Enhanced UI helper that combines existing functionality with additional methods"""
    
    def __init__(self):
        self.formatter = CLIFormatter()
        self.progress = ProgressReporter()
    
    # Method delegation to maintain compatibility
    def print_success(self, message: str) -> None:
        """Print success message"""
        self.formatter.success(message)
    
    def print_error(self, message: str) -> None:
        """Print error message"""
        self.formatter.error(message)
    
    def print_warning(self, message: str) -> None:
        """Print warning message"""
        self.formatter.warning(message)
    
    def print_info(self, message: str) -> None:
        """Print info message"""
        self.formatter.info(message)
    
    def print_progress(self, message: str) -> None:
        """Print progress message"""
        self.formatter.progress(message)
    
    # Additional methods needed by gif_commands.py
    def print_header(self, title: str) -> None:
        """Print section header with formatting"""
        divider = "=" * len(title)
        print(f"\n{divider}")
        print(Colors.colorize(title.upper(), Colors.BOLD + Colors.CYAN))
        print(divider)
    
    def print_step(self, step_text: str) -> None:
        """Print step header"""
        print(f"\n{Colors.colorize('→', Colors.BLUE)} {Colors.colorize(step_text, Colors.BOLD)}")
        print("-" * len(step_text))
    
    def print_divider(self, char: str = "-", length: int = 50) -> None:
        """Print a divider line"""
        print(char * length)
    
    def confirm_action(self, message: str, default: bool = True) -> bool:
        """Ask for user confirmation"""
        suffix = "[Y/n]" if default else "[y/N]"
        response = input(f"? {message} {suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', '1', 'true']
    
    def get_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get user input with optional default"""
        if default:
            response = input(f"> {prompt} [{default}]: ").strip()
            return response if response else default
        else:
            return input(f"> {prompt}: ").strip()
    
    def wait_for_enter(self, message: str = "Press Enter to continue...") -> None:
        """Wait for user to press Enter"""
        input(f"\n-> {message}")
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes:02d}:{secs:02d}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in bytes to human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        size_index = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and size_index < len(size_names) - 1:
            size /= 1024.0
            size_index += 1
        
        return f"{size:.1f} {size_names[size_index]}"
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            return 0
    
    def parse_time_input(self, time_str: str) -> float:
        """Parse time input string to seconds"""
        time_str = time_str.strip()
        
        # Try to parse as plain seconds first
        try:
            return float(time_str)
        except ValueError:
            pass
        
        # Parse HH:MM:SS or MM:SS format
        parts = time_str.split(':')
        
        if len(parts) == 2:  # MM:SS
            try:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            except ValueError:
                raise ValueError("Invalid time format")
        
        elif len(parts) == 3:  # HH:MM:SS
            try:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            except ValueError:
                raise ValueError("Invalid time format")
        
        else:
            raise ValueError("Invalid time format. Use HH:MM:SS, MM:SS, or seconds")

def confirm(message: str, default: bool = False) -> bool:
    """Ask for user confirmation - standalone function for backward compatibility"""
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{message} {suffix}: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes', '1', 'true']

def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default - standalone function for backward compatibility"""
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    else:
        return input(f"{prompt}: ").strip()
