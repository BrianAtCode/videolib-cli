"""
UI utilities for CLI
"""
import sys
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
        print(f"⚠️  {message}")
    
    @staticmethod
    def info(message: str) -> None:
        """Print info message"""
        print(f"ℹ️  {message}")
    
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

def confirm(message: str, default: bool = False) -> bool:
    """Ask for user confirmation"""
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{message} {suffix}: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes', '1', 'true']

def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default"""
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    else:
        return input(f"{prompt}: ").strip()
