"""
UI utilities for CLI
"""

import sys
import os
import time
from typing import Optional, List, Dict

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
    
# ============================================================================
# Scale & Encode UI Components (Add to end of ui.py)
# ============================================================================

class MenuHandler:
    """Reusable menu selection handler for CLI"""
    
    def __init__(self, ui_helper: UIHelper = None):
        """
        Initialize MenuHandler.
        
        Args:
            ui_helper: Optional UIHelper instance
        """
        self.ui_helper = ui_helper or UIHelper()
    
    def display_options(self, options: List[str], title: str = None) -> None:
        """
        Display menu options.
        
        Args:
            options: List of option strings
            title: Optional title to display before options
        """
        if title:
            self.ui_helper.print_step(title)
        
        for option in options:
            print(option)
    
    def get_selection(self, prompt: str, max_option: int, allow_custom: bool = False) -> str:
        """
        Get user menu selection.
        
        Args:
            prompt: Prompt text
            max_option: Maximum option number
            allow_custom: If True, allow entering custom value
        
        Returns:
            User selection as string
        """
        while True:
            try:
                choice = input(f"\n> {prompt}: ").strip()
                
                if choice.isdigit():
                    if 1 <= int(choice) <= max_option:
                        return choice
                    elif allow_custom and int(choice) == max_option + 1:
                        return choice
                
                print(f"X Invalid selection. Please enter 1-{max_option}")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"X Error: {e}")


class InputHandler:
    """Reusable user input handler for CLI"""
    
    def __init__(self, ui_helper: UIHelper = None):
        """
        Initialize InputHandler.
        
        Args:
            ui_helper: Optional UIHelper instance
        """
        self.ui_helper = ui_helper or UIHelper()
    
    def get_file_path(self, prompt: str = "Enter file path", must_exist: bool = True) -> Optional[str]:
        """
        Get file path from user.
        
        Args:
            prompt: Prompt text
            must_exist: If True, file must exist
        
        Returns:
            File path or None if cancelled
        """
        while True:
            try:
                file_path = input(f"> {prompt}: ").strip()
                
                if not file_path:
                    print("X File path cannot be empty")
                    continue
                
                if must_exist and not os.path.exists(file_path):
                    print(f"X File not found: {file_path}")
                    retry = input("? Try again? [Y/n]: ").strip().lower()
                    if retry != 'n':
                        continue
                    return None
                
                return file_path
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"X Error: {e}")
    
    def get_integer(self, prompt: str, min_val: int = None, max_val: int = None) -> Optional[int]:
        """
        Get integer input from user.
        
        Args:
            prompt: Prompt text
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        
        Returns:
            Integer value or None if invalid
        """
        while True:
            try:
                value = int(input(f"> {prompt}: ").strip())
                
                if min_val is not None and value < min_val:
                    print(f"X Value must be >= {min_val}")
                    continue
                
                if max_val is not None and value > max_val:
                    print(f"X Value must be <= {max_val}")
                    continue
                
                return value
            except ValueError:
                print("X Please enter a valid integer")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"X Error: {e}")
    
    def get_string(self, prompt: str, default: str = None, required: bool = True) -> Optional[str]:
        """
        Get string input from user.
        
        Args:
            prompt: Prompt text
            default: Default value if user enters nothing
            required: If True, cannot be empty
        
        Returns:
            String value or None
        """
        try:
            if default:
                response = input(f"> {prompt} [{default}]: ").strip()
                return response if response else default
            else:
                while True:
                    response = input(f"> {prompt}: ").strip()
                    if response or not required:
                        return response
                    print("X Input cannot be empty")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"X Error: {e}")
    
    def get_confirmation(self, prompt: str, default: bool = True) -> bool:
        """
        Get yes/no confirmation from user.
        
        Args:
            prompt: Prompt text
            default: Default value
        
        Returns:
            True for yes, False for no
        """
        suffix = "[Y/n]" if default else "[y/N]"
        response = input(f"? {prompt} {suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', '1', 'true']


class DisplayHandler:
    """Reusable display handler for CLI output"""
    
    def __init__(self, ui_helper: UIHelper = None):
        """
        Initialize DisplayHandler.
        
        Args:
            ui_helper: Optional UIHelper instance
        """
        self.ui_helper = ui_helper or UIHelper()
    
    def display_section(self, title: str) -> None:
        """Display section header"""
        self.ui_helper.print_header(title)
    
    def display_step(self, step_text: str) -> None:
        """Display step header"""
        self.ui_helper.print_step(step_text)
    
    def display_list(self, items: List[str], title: str = None) -> None:
        """
        Display list of items.
        
        Args:
            items: List of strings to display
            title: Optional title
        """
        if title:
            self.display_step(title)
        
        for item in items:
            print(item)
    
    def display_key_value(self, data: Dict[str, str], title: str = None) -> None:
        """
        Display key-value pairs.
        
        Args:
            data: Dictionary of key-value pairs
            title: Optional title
        """
        if title:
            self.display_step(title)
        
        for key, value in data.items():
            print(f"  {key}: {value}")
    
    def display_success(self, message: str) -> None:
        """Display success message"""
        self.ui_helper.print_success(message)
    
    def display_error(self, message: str) -> None:
        """Display error message"""
        self.ui_helper.print_error(message)
    
    def display_warning(self, message: str) -> None:
        """Display warning message"""
        self.ui_helper.print_warning(message)
    
    def display_info(self, message: str) -> None:
        """Display info message"""
        self.ui_helper.print_info(message)
    
    def display_divider(self, char: str = "-", length: int = 50) -> None:
        """Display divider line"""
        self.ui_helper.print_divider(char, length)