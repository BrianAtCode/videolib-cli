"""
Interactive CLI for VideoLib - Added 'q' key interrupt during background processing
Enhancement: Press 'q' to cancel operations and return to menu
"""
import sys
import os
import re
import threading
import time
import subprocess
import select
from pathlib import Path
from typing import Optional, List, Dict, Any
from .gif_commands import GifCommands
# Import the video processing library
try:
    import videolib
except ImportError:
    # If running from source, add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import videolib

class KeyboardListener:
    """Listen for keyboard input during background operations"""
    
    def __init__(self):
        self.should_quit = False
        self.listening = False
        self.listener_thread = None
        
    def start_listening(self):
        """Start listening for 'q' key press"""
        self.should_quit = False
        self.listening = True
        
        if sys.platform.startswith('win'):
            # Windows implementation
            self.listener_thread = threading.Thread(target=self._listen_windows, daemon=True)
        else:
            # Unix/Linux/macOS implementation
            self.listener_thread = threading.Thread(target=self._listen_unix, daemon=True)
        
        self.listener_thread.start()
    
    def stop_listening(self):
        """Stop listening for keyboard input"""
        self.listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=0.5)
    
    def _listen_windows(self):
        """Windows keyboard listener using msvcrt"""
        try:
            import msvcrt
            while self.listening and not self.should_quit:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if key == 'q':
                        self.should_quit = True
                        break
                time.sleep(0.1)
        except ImportError:
            # Fallback for Windows without msvcrt
            pass
    
    def _listen_unix(self):
        """Unix/Linux/macOS keyboard listener using select"""
        try:
            import termios
            import tty
            
            # Save terminal settings
            old_settings = termios.tcgetattr(sys.stdin)
            
            try:
                # Set terminal to raw mode
                tty.setraw(sys.stdin.fileno())
                
                while self.listening and not self.should_quit:
                    # Check if input is available
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1).lower()
                        if key == 'q':
                            self.should_quit = True
                            break
                    
            finally:
                # Restore terminal settings
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                
        except (ImportError, OSError):
            # Fallback for systems without termios/select
            pass

class FFmpegMonitor:
    """Monitor FFmpeg output for real-time statistics with interrupt support"""
    
    def __init__(self, keyboard_listener):
        self.stats = {
            'bitrate': '0kbits/s',
            'speed': '0x',
            'size': '0kB',
            'time': '00:00:00',
            'fps': '0',
            'drop': '0',
            'dup': '0'
        }
        self.running = False
        self.display_thread = None
        self.keyboard_listener = keyboard_listener
        
    def start_display(self, operation_name: str = "Processing"):
        """Start real-time statistics display with interrupt support"""
        self.running = True
        self.operation_name = operation_name
        self.display_thread = threading.Thread(target=self._display_stats, daemon=True)
        self.display_thread.start()
    
    def stop_display(self):
        """Stop statistics display"""
        self.running = False
        if self.display_thread:
            self.display_thread.join(timeout=1)
        print()  # New line after stats
    
    def parse_ffmpeg_line(self, line: str):
        """Parse FFmpeg progress line for statistics"""
        if not line:
            return
            
        try:
            # Parse frame rate
            if 'fps=' in line:
                fps_match = re.search(r'fps=\s*(\d+(?:\.\d+)?)', line)
                if fps_match:
                    self.stats['fps'] = fps_match.group(1)
            
            # Parse current time
            if 'time=' in line:
                time_match = re.search(r'time=(\d+:\d+:\d+\.\d+)', line)
                if time_match:
                    self.stats['time'] = time_match.group(1)[:8]  # Remove milliseconds
            
            # Parse bitrate
            if 'bitrate=' in line:
                bitrate_match = re.search(r'bitrate=\s*([\d.]+\w+)', line)
                if bitrate_match:
                    self.stats['bitrate'] = bitrate_match.group(1)
            
            # Parse speed
            if 'speed=' in line:
                speed_match = re.search(r'speed=\s*([\d.]+x)', line)
                if speed_match:
                    self.stats['speed'] = speed_match.group(1)
            
            # Parse size
            if 'size=' in line:
                size_match = re.search(r'size=\s*([\d.]+\w+)', line)
                if size_match:
                    self.stats['size'] = size_match.group(1)
            
            # Parse drop/dup frames
            if 'drop=' in line:
                drop_match = re.search(r'drop=(\d+)', line)
                if drop_match:
                    self.stats['drop'] = drop_match.group(1)
            
            if 'dup=' in line:
                dup_match = re.search(r'dup=(\d+)', line)
                if dup_match:
                    self.stats['dup'] = dup_match.group(1)
                    
        except Exception as e:
            # Ignore parsing errors to avoid interrupting the display
            pass
    
    def _display_stats(self):
        """Display real-time FFmpeg statistics with interrupt hint"""
        while self.running and not self.keyboard_listener.should_quit:
            stats_line = (
                f"\r{self.operation_name} -> "
                f"Time: {self.stats['time']} | "
                f"Size: {self.stats['size']} | "
                f"Bitrate: {self.stats['bitrate']} | "
                f"Speed: {self.stats['speed']} | "
                f"FPS: {self.stats['fps']} | Press 'q' to cancel"
            )
            
            # Truncate if too long for terminal
            if len(stats_line) > 120:
                stats_line = stats_line[:115] + "..."
            
            print(stats_line, end='', flush=True)
            time.sleep(0.5)

class ProgressTracker:
    """Track and display progress for long-running operations with interrupt support"""
    
    def __init__(self, keyboard_listener):
        self.running = False
        self.thread = None
        self.progress = 0
        self.message = ""
        self.keyboard_listener = keyboard_listener
    
    def start(self, message: str = "Processing..."):
        """Start progress display with interrupt support"""
        self.message = message
        self.running = True
        self.progress = 0
        self.thread = threading.Thread(target=self._display_progress, daemon=True)
        self.thread.start()
    
    def update(self, progress: int, message: str = None):
        """Update progress (0-100)"""
        self.progress = min(100, max(0, progress))
        if message:
            self.message = message
    
    def stop(self):
        """Stop progress display"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print()  # New line after progress
    
    def _display_progress(self):
        """Display progress bar in separate thread with interrupt hint"""
        while self.running and not self.keyboard_listener.should_quit:
            bar_length = 25  # Shorter to make room for interrupt hint
            filled = int(bar_length * self.progress / 100)
            bar = '=' * filled + '-' * (bar_length - filled)
            
            progress_line = f"\r[{bar}] {self.progress:3d}% {self.message} | Press 'q' to cancel"
            print(progress_line, end='', flush=True)
            time.sleep(0.5)

class InteractiveCLI:
    """Interactive command-line interface with 'q' key interrupt support"""
    
    def __init__(self):
        self.processor = None
        self.running = True
        self.keyboard_listener = KeyboardListener()
        self.progress_tracker = ProgressTracker(self.keyboard_listener)
        self.ffmpeg_monitor = FFmpegMonitor(self.keyboard_listener)
        self.gif_commands = GifCommands()
        
    def initialize_processor(self):
        """Initialize video processor with custom FFmpeg paths if needed"""
        if self.processor is not None:
            return
        
        # Check for custom FFmpeg paths
        use_custom = self.get_yes_no("Do you want to specify custom FFmpeg/FFprobe paths?", False)
        
        if use_custom:
            ffmpeg_path = self.get_input("FFmpeg executable path", "ffmpeg")
            ffprobe_path = self.get_input("FFprobe executable path", "ffprobe")
            
            try:
                self.processor = videolib.create_processor(
                    ffmpeg_path=ffmpeg_path, 
                    ffprobe_path=ffprobe_path
                )
                print("-> Video processor initialized with custom paths")
            except Exception as e:
                print(f"X Failed to initialize with custom paths: {e}")
                print("-> Falling back to default paths...")
                self.processor = videolib.create_processor()
        else:
            try:
                self.processor = videolib.create_processor()
                print("-> Video processor initialized")
            except Exception as e:
                print(f"X Failed to initialize video processor: {e}")
                print("Please ensure FFmpeg and FFprobe are installed and in PATH")
                sys.exit(1)
    
    def show_menu(self):
        """Display main menu with simple symbols"""
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print("1. Download Video (Enhanced monitoring)")
        print("2. Split Video by Size") 
        print("3. Create Video Clips")
        print("4. Create Animated GIFs")
        print("5. Get Media Information")
        print("6. Batch Process from Config File")
        print("7. Settings")
        print("0. Exit")
        print("=" * 50)
        print("Tip: During operations, press 'q' to cancel and return to menu")
    
    def get_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get user input with optional default value"""
        if default:
            user_input = input(f"> {prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            while True:
                user_input = input(f"> {prompt}: ").strip()
                if user_input:
                    return user_input
                print("X This field is required. Please enter a value.")
    
    def get_yes_no(self, prompt: str, default: bool = False) -> bool:
        """Get yes/no input from user"""
        suffix = "[Y/n]" if default else "[y/N]"
        while True:
            response = input(f"? {prompt} {suffix}: ").strip().lower()
            
            if not response:
                return default
            
            if response in ['y', 'yes', '1', 'true']:
                return True
            elif response in ['n', 'no', '0', 'false']:
                return False
            else:
                print("X Please enter 'y' for yes or 'n' for no")
    
    def get_file_path(self, prompt: str, must_exist: bool = True) -> str:
        """Get file path input with validation"""
        while True:
            file_path = self.get_input(prompt)
            
            if must_exist:
                if os.path.exists(file_path):
                    return file_path
                else:
                    print(f"X File not found: {self.truncate_path(file_path)}")
                    retry = self.get_yes_no("Try again?", True)
                    if not retry:
                        raise KeyboardInterrupt("User cancelled file selection")
            else:
                # Check if directory exists for output files
                dir_path = os.path.dirname(file_path)
                if dir_path and not os.path.exists(dir_path):
                    create_dir = self.get_yes_no(f"Directory '{self.truncate_path(dir_path)}' doesn't exist. Create it?", True)
                    if create_dir:
                        try:
                            os.makedirs(dir_path, exist_ok=True)
                            print(f"-> Created directory: {self.truncate_path(dir_path)}")
                        except OSError as e:
                            print(f"X Failed to create directory: {e}")
                            continue
                    else:
                        continue
                return file_path
    
    def truncate_path(self, path: str, max_length: int = 40) -> str:
        """Truncate long paths for display"""
        if len(path) <= max_length:
            return path
        
        # For URLs
        if path.startswith(('http://', 'https://')):
            if len(path) <= max_length:
                return path
            return path[:max_length-3] + "..."
        
        # For file paths
        path_obj = Path(path)
        if len(str(path_obj)) <= max_length:
            return str(path_obj)
        
        # Try to show meaningful part
        name = path_obj.name
        if len(name) <= max_length - 4:  # Leave room for ".../ "
            return f".../{name}"
        else:
            return f".../{name[:max_length-7]}..."
    
    def truncate_filename(self, filename: str, max_length: int = 30) -> str:
        """Truncate filename for display"""
        if len(filename) <= max_length:
            return filename
        
        # Try to preserve extension
        if '.' in filename:
            name, ext = filename.rsplit('.', 1)
            available = max_length - len(ext) - 4  # 4 for "..." and "."
            if available > 0:
                return f"{name[:available]}...{ext}"
        
        return filename[:max_length-3] + "..."
    
    def pause_for_user(self, message: str = "Press Enter to continue..."):
        """Pause and wait for user input"""
        input(f"\n-> {message}")
    
    def download_video_interactive(self):
        """Interactive download video workflow with 'q' interrupt support"""
        print("\n" + "-" * 50)
        print("VIDEO DOWNLOAD WORKFLOW (Enhanced)")
        print("-" * 50)
        
        try:
            # Step 1: Get URL
            print("\nStep 1: Video URL")
            print("-" * 20)
            url = self.get_input("Enter video URL (http:// or https://)")
            
            if not videolib.FormatParser.is_valid_url(url):
                print("X Invalid URL format. URL must start with http:// or https://")
                return
            
            # Step 2: Get output filename  
            print("\nStep 2: Output Settings")
            print("-" * 25)
            
            # Suggest filename from URL and show truncated version
            suggested = videolib.FileManager.suggest_filename_from_url(url)
            print(f"-> Suggested from URL: {self.truncate_filename(suggested)}")
            output_filename = self.get_input("Output filename", suggested)
            
            # Step 3: Overwrite confirmation
            if os.path.exists(output_filename):
                overwrite = self.get_yes_no(f"File '{self.truncate_filename(output_filename)}' exists. Overwrite?", False)
                if not overwrite:
                    print("X Download cancelled")
                    return
            else:
                overwrite = True
            
            # Step 4: Confirm and execute
            print("\nStep 3: Confirmation")
            print("-" * 20)
            print(f"-> URL: {url}")  # Full URL in confirmation
            print(f"-> Output: {output_filename}")  # Full filename in confirmation
            print(f"-> Overwrite: {'Yes' if overwrite else 'No'}")
            
            confirm = self.get_yes_no("Proceed with download?", True)
            if not confirm:
                print("X Download cancelled")
                return
            
            # Execute download with interrupt support
            print("\n-> Starting download with real-time monitoring...")
            print("-> Press 'q' anytime during download to cancel and return to menu")
            print("-" * 50)
            
            try:
                # Start keyboard listener
                self.keyboard_listener.start_listening()
                
                # Use enhanced FFmpeg monitoring with interrupt support
                result = self._download_with_interrupt_support(url, output_filename, overwrite)
                
            except KeyboardInterrupt:
                print("\n-> Download cancelled by user (Ctrl+C)")
                return
            finally:
                # Always stop keyboard listener
                self.keyboard_listener.stop_listening()
                self.ffmpeg_monitor.stop_display()
            
            # Check for 'q' interrupt
            if self.keyboard_listener.should_quit:
                print("\n-> Download cancelled by user ('q' pressed)")
                print("-> Returning to main menu...")
                return
            
            if result and result.success:
                file_size = videolib.FormatParser.format_file_size(result.file_size) if result.file_size else "Unknown"
                print(f"\n-> Download completed successfully!")
                print(f"-> File: {result.output_file}")
                print(f"-> Size: {file_size}")
            else:
                error_msg = result.error_message if result else "Unknown error"
                print(f"\nX Download failed: {error_msg}")
            
        except KeyboardInterrupt:
            print("\n-> Download cancelled by user")
        except Exception as e:
            print(f"\nX Unexpected error: {e}")
        finally:
            # Cleanup
            self.keyboard_listener.stop_listening()
            self.ffmpeg_monitor.stop_display()
        
        self.pause_for_user()
    
    def _download_with_interrupt_support(self, url: str, output_filename: str, overwrite: bool):
        """Download with real-time FFmpeg statistics monitoring and interrupt support"""
        # Start FFmpeg monitoring
        self.ffmpeg_monitor.start_display("Download")
        
        try:
            # Create a custom FFmpeg command with progress output
            cmd = [
                self.processor.ffmpeg.ffmpeg_path,
                "-y" if overwrite else "-n",  # overwrite or no-overwrite
                "-i", url,
                "-c", "copy",  # stream copy for faster download
                "-progress", "pipe:1",  # Enable progress output to stdout
                "-loglevel", "info",    # Show info level logs
                output_filename
            ]
            
            # Execute with real-time monitoring and interrupt support
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr into stdout
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor output in real-time with interrupt checking
            while True:
                # Check for 'q' interrupt
                if self.keyboard_listener.should_quit:
                    print("\n-> Terminating FFmpeg process...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)  # Wait up to 5 seconds for graceful termination
                    except subprocess.TimeoutExpired:
                        print("-> Force killing FFmpeg process...")
                        process.kill()
                    break
                
                # Read FFmpeg output
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Parse FFmpeg output for statistics
                    self.ffmpeg_monitor.parse_ffmpeg_line(output.strip())
            
            # Get return code
            return_code = process.poll()
            
            # Stop monitoring
            self.ffmpeg_monitor.stop_display()
            
            # Check for user interruption
            if self.keyboard_listener.should_quit:
                return None  # User cancelled
            
            # Check result
            if return_code == 0 and os.path.exists(output_filename):
                file_size = os.path.getsize(output_filename)
                return type('Result', (), {
                    'success': True,
                    'output_file': output_filename,
                    'file_size': file_size,
                    'error_message': None
                })()
            else:
                return type('Result', (), {
                    'success': False,
                    'output_file': output_filename,
                    'file_size': None,
                    'error_message': f"FFmpeg process failed with code {return_code}"
                })()
                
        except Exception as e:
            self.ffmpeg_monitor.stop_display()
            return type('Result', (), {
                'success': False,
                'output_file': output_filename,
                'file_size': None,
                'error_message': str(e)
            })()
    
    def split_video_interactive(self):
        """Interactive split video workflow with 'q' interrupt support"""
        print("\n" + "-" * 50)
        print("VIDEO SPLIT WORKFLOW")
        print("-" * 50)
        
        try:
            # Step 1: Get source file
            print("\nStep 1: Source Video")
            print("-" * 20)
            source_file = self.get_file_path("Enter source video file path", must_exist=True)

            # Get media info with progress
            print("\n-> Analyzing video...")
            print("-> Press 'q' to cancel analysis")
            self.keyboard_listener.start_listening()
            self.progress_tracker.start("Analyzing video file...")
            
            try:
                media_info = self.processor.get_media_info(source_file)
            finally:
                self.progress_tracker.stop()
                self.keyboard_listener.stop_listening()
            
            # Check for user interrupt
            if self.keyboard_listener.should_quit:
                print("\n-> Analysis cancelled by user ('q' pressed)")
                return
        
            if media_info:
                duration = videolib.FormatParser.format_duration(media_info.duration) if media_info.duration else "Unknown"
                file_size = videolib.FormatParser.format_file_size(media_info.size_bytes) if media_info.size_bytes else "Unknown"
                print(f"-> Duration: {duration}")
                print(f"-> Current size: {file_size}")
                if media_info.video_codec:
                    print(f"-> Video codec: {media_info.video_codec}")
                if media_info.audio_codec:
                    print(f"-> Audio codec: {media_info.audio_codec}")
        
            # Step 2: Get target size
            print("\nStep 2: Target Size")
            print("-" * 20)
            target_size_str = self.get_input("Enter target size per segment (e.g. 500MB, 1GB)")
            
            # Parse target size
            try:
                target_size_bytes = videolib.FormatParser.parse_size(target_size_str)
            except Exception as e:
                print(f"X Invalid size format: {e}")
                print("-> Examples: 500MB, 1GB, 1024KB")
                return
            
            # Validate target size
            if media_info and media_info.size_bytes:
                if target_size_bytes >= media_info.size_bytes:
                    print(f"-> Note: Target size ({videolib.FormatParser.format_file_size(target_size_bytes)}) "
                        f"is larger than source ({file_size})")
                    proceed = self.get_yes_no("File is already smaller than target. Continue anyway?", False)
                    if not proceed:
                        print("X Split cancelled")
                        return
                else:
                    # Estimate number of segments
                    estimated_segments = int((media_info.size_bytes / target_size_bytes) + 0.5)
                    print(f"-> Estimated segments: ~{estimated_segments} segments")
            
            # Step 3: Output settings
            print("\nStep 3: Output Settings")
            print("-" * 25)
            
            # Suggest output name from source file
            suggested_name = os.path.splitext(os.path.basename(source_file))[0] + "_segment"
            output_name = self.get_input("Output name prefix (without extension)", suggested_name)
            
            # Get output extension (default to source extension)
            suggested_ext = os.path.splitext(source_file)[1][1:] if os.path.splitext(source_file)[1] else "mp4"
            output_extension = self.get_input("Output file extension", suggested_ext)
            
            # Normalize extension
            output_extension = videolib.FormatParser.normalize_extension(output_extension)
            
            # Step 4: Advanced settings (optional)
            print("\nStep 4: Advanced Settings (Optional)")
            print("-" * 35)
            use_advanced = self.get_yes_no("Configure advanced settings?", False)
            
            if use_advanced:
                safety_factor_str = self.get_input("Safety factor (0.8-0.99, lower = smaller segments)", "0.95")
                try:
                    safety_factor = float(safety_factor_str)
                    if not 0.5 <= safety_factor <= 0.99:
                        print("X Safety factor must be between 0.5 and 0.99, using default 0.95")
                        safety_factor = 0.95
                except ValueError:
                    print("X Invalid safety factor, using default 0.95")
                    safety_factor = 0.95
                
                max_rounds_str = self.get_input("Max split rounds for oversized segments (1-10)", "4")
                try:
                    max_rounds = int(max_rounds_str)
                    if not 1 <= max_rounds <= 10:
                        print("X Max rounds must be between 1 and 10, using default 4")
                        max_rounds = 4
                except ValueError:
                    print("X Invalid max rounds, using default 4")
                    max_rounds = 4
            else:
                safety_factor = 0.95
                max_rounds = 4
            
            # Step 5: Confirmation
            print("\nStep 5: Confirmation")
            print("-" * 20)
            print(f"-> Source: {self.truncate_path(source_file)}")
            print(f"-> Target size: {videolib.FormatParser.format_file_size(target_size_bytes)}")
            print(f"-> Output prefix: {output_name}")
            print(f"-> Output extension: {output_extension}")
            if media_info and media_info.size_bytes:
                estimated_segments = int((media_info.size_bytes / target_size_bytes) + 0.5)
                print(f"-> Estimated segments: ~{estimated_segments}")
            print(f"-> Safety factor: {safety_factor}")
            print(f"-> Max split rounds: {max_rounds}")
            
            confirm = self.get_yes_no("Proceed with video split?", True)
            if not confirm:
                print("X Split cancelled")
                return
            
            # Step 6: Execute split with interrupt support
            print("\n-> Starting video split...")
            print("-> Press 'q' anytime during processing to cancel and return to menu")
            print("-" * 50)
            
            # Start keyboard listener
            self.keyboard_listener.start_listening()
            self.progress_tracker.start("Splitting video...")
            
            try:
                # Use VideoSplitter from processor
                from videolib.core.splitter import SplitOptions
                
                options = SplitOptions(
                    source_file=source_file,
                    output_name=output_name,
                    output_extension=output_extension,
                    max_size_bytes=target_size_bytes,
                    safety_factor=safety_factor,
                    max_rounds=max_rounds
                )
                
                # Execute split
                result = self.processor.splitter.split_by_size(options)
                
            finally:
                self.progress_tracker.stop()
                self.keyboard_listener.stop_listening()
            
            # Check for user interrupt
            if self.keyboard_listener.should_quit:
                print("\n-> Split cancelled by user ('q' pressed)")
                print("-> Note: Partial output files may have been created")
                return
            
            # Display results using the improved __str__ method
            print("\n" + "=" * 50)
            print("VIDEO SPLIT RESULTS")
            print("=" * 50)
            
            if result.success:
                print(f"-> Successfully split video into {len(result.output_files)} segment(s)")
                
                if result.was_copied:
                    print("-> Note: File was already smaller than target size and was copied")
                
                # Show output files
                print("\n-> Output segments:")
                total_size = 0
                for i, output_file in enumerate(result.output_files, 1):
                    file_size = videolib.FileManager.get_file_size(output_file)
                    if file_size:
                        size_str = videolib.FormatParser.format_file_size(file_size)
                        total_size += file_size
                        
                        # Check if oversized
                        if file_size > target_size_bytes:
                            status = "[OVERSIZED]"
                        else:
                            status = ""
                        
                        print(f"   {i}. {os.path.basename(output_file)} ({size_str}) {status}")
                    else:
                        print(f"   {i}. {os.path.basename(output_file)} (Size unknown)")
                
                # Show total size
                if total_size > 0:
                    print(f"\n-> Total output size: {videolib.FormatParser.format_file_size(total_size)}")
                
                # Show oversized files warning
                if result.oversized_files:
                    print(f"\n-> Warning: {len(result.oversized_files)} file(s) exceeded target size:")
                    for oversized in result.oversized_files:
                        file_size = videolib.FileManager.get_file_size(oversized)
                        size_str = videolib.FormatParser.format_file_size(file_size) if file_size else "Unknown"
                        print(f"   - {os.path.basename(oversized)} ({size_str})")
                    print("-> Consider using a smaller target size or higher safety factor")
            
            else:
                print(f"X Split failed: {result.error_message}")

        except KeyboardInterrupt:
            print("\n-> Split cancelled by user")
        except Exception as e:
            print(f"\nX Unexpected error: {e}")
        finally:
            self.keyboard_listener.stop_listening()
        
        self.pause_for_user()
    
    def create_clips_interactive(self):
        """Interactive create clips workflow with 'q' interrupt support"""
        print("\n" + "-" * 50)
        print("VIDEO CLIP CREATION WORKFLOW")
        print("-" * 50)

        try:
            # Step 1: Get source file
            print("\nStep 1: Source Video")
            print("-" * 20)
            source_file = self.get_file_path("Enter source video file path", must_exist=True)

            # Get media info with progress
            print("\n-> Analyzing video...")
            self.keyboard_listener.start_listening()
            self.progress_tracker.start("Analyzing video file...")

            try:
                media_info = self.processor.get_media_info(source_file)
            finally:
                self.progress_tracker.stop()
                self.keyboard_listener.stop_listening()

            if self.keyboard_listener.should_quit:
                print("\n-> Analysis cancelled by user ('q' pressed)")
                return

            if media_info:
                duration = videolib.FormatParser.format_duration(media_info.duration) if media_info.duration else "Unknown"
                file_size = videolib.FormatParser.format_file_size(media_info.size_bytes) if media_info.size_bytes else "Unknown"
                print(f"-> Duration: {duration}")
                print(f"-> Current size: {file_size}")
                if media_info.video_codec:
                    print(f"-> Video codec: {media_info.video_codec}")
                if media_info.audio_codec:
                    print(f"-> Audio codec: {media_info.audio_codec}")

            # Step 2: Get output settings
            print("\nStep 2: Output Settings")
            print("-" * 25)

            # Output name (without extension)
            suggested_name = os.path.splitext(os.path.basename(source_file))[0] + "_clip"
            output_name = self.get_input("Output name prefix (without extension)", suggested_name)

            # Output extension
            suggested_ext = os.path.splitext(source_file)[1][1:] if os.path.splitext(source_file)[1] else "mp4"
            output_extension = self.get_input("Output file extension", suggested_ext)
            output_extension = videolib.FormatParser.normalize_extension(output_extension)

            # Step 3: Get clip intervals
            print("\nStep 3: Clip Intervals")
            print("-" * 25)
            print("-> Enter time intervals for clips")
            print("-> Time format: HH:MM:SS, MM:SS, or seconds")
            print(f"-> Video duration: {duration if media_info else 'Unknown'}")
            print("-> Enter 'done' when finished adding intervals")

            intervals = []
            interval_num = 1

            while True:
                print(f"\n-> Interval {interval_num}:")

                # Get start time
                start_time_str = self.get_input(f"  Start time (or 'q' to finish)")

                if start_time_str.lower() == 'q':
                    if len(intervals) == 0:
                        print("X At least one interval is required")
                        continue
                    break

                # Validate start time
                start_valid, start_error = videolib.InputValidator.validate_timecode(start_time_str)
                if not start_valid:
                    print(f"X {start_error}")
                    continue

                # Get end time
                end_time_str = self.get_input(f"  End time")

                # Validate end time
                end_valid, end_error = videolib.InputValidator.validate_timecode(end_time_str)
                if not end_valid:
                    print(f"X {end_error}")
                    continue

                # Parse to seconds
                start_seconds = videolib.FormatParser.parse_timecode(start_time_str)
                end_seconds = videolib.FormatParser.parse_timecode(end_time_str)

                # Validate interval
                if start_seconds >= end_seconds:
                    print("X Start time must be less than end time")
                    continue

                # Check against video duration if available
                if media_info and media_info.duration:
                    if end_seconds > media_info.duration:
                        print(f"X Warning: End time ({end_seconds}s) exceeds video duration ({media_info.duration}s)")
                        proceed = self.get_yes_no("Add this interval anyway?", False)
                        if not proceed:
                            continue

                # Add interval
                intervals.append({
                    'start': start_seconds,
                    'end': end_seconds,
                    'start_str': start_time_str,
                    'end_str': end_time_str
                })

                print(f"-> Added interval {interval_num}: {start_time_str} to {end_time_str}")
                interval_num += 1

            # Step 4: Codec settings
            print("\nStep 4: Codec Settings")
            print("-" * 25)
            print("-> Default: 'copy' (fast, no re-encoding)")
            print("-> Use 'libx264' for H.264 re-encoding")

            video_codec = self.get_input("Video codec", "copy")
            audio_codec = self.get_input("Audio codec", "copy")

            # Step 5: Confirmation
            print("\nStep 5: Confirmation")
            print("-" * 20)
            print(f"-> Source: {self.truncate_path(source_file)}")
            print(f"-> Output prefix: {output_name}")
            print(f"-> Output extension: {output_extension}")
            print(f"-> Number of clips: {len(intervals)}")
            print(f"-> Video codec: {video_codec}")
            print(f"-> Audio codec: {audio_codec}")
            print("\n-> Clip intervals:")
            for i, interval in enumerate(intervals):
                print(f"   {i+1}. {interval['start_str']} to {interval['end_str']}")

            confirm = self.get_yes_no("Proceed with clip creation?", True)
            if not confirm:
                print("X Clip creation cancelled")
                return

            # Step 6: Execute clip creation
            print("\n-> Starting clip creation...")
            print("-> Press 'q' anytime during processing to cancel and return to menu")
            print("-" * 50)

            # Create clips using VideoClipper
            from videolib.core.clipper import VideoClipper, ClipOptions, ClipInterval

            # Convert intervals to ClipInterval objects
            clip_intervals = []
            for interval in intervals:
                try:
                    clip_intervals.append(ClipInterval(
                        start_time=interval['start'],
                        end_time=interval['end']
                    ))
                except ValueError as e:
                    print(f"X Invalid interval: {e}")
                    continue

            if not clip_intervals:
                print("X No valid intervals to process")
                return

            # Create clip options
            options = ClipOptions(
                source_file=source_file,
                output_name=output_name,
                output_extension=output_extension,
                intervals=clip_intervals,
                video_codec=video_codec,
                audio_codec=audio_codec
            )

            # Execute with interrupt support
            self.keyboard_listener.start_listening()
            self.progress_tracker.start(f"Creating {len(clip_intervals)} clips...")

            try:
                # Use processor's clipper
                result = self.processor.clipper.create_clips(options)
            finally:
                self.progress_tracker.stop()
                self.keyboard_listener.stop_listening()

            # Check for user interruption
            if self.keyboard_listener.should_quit:
                print("\n-> Clip creation cancelled by user ('q' pressed)")
                print("-> Returning to main menu...")
                return

            # Display results
            print("\n" + "=" * 50)
            print("CLIP CREATION RESULTS")
            print("=" * 50)

            if result.success:
                print(f"-> Successfully created {len(result.output_files)} clips")
                print("\n-> Output files:")
                for i, output_file in enumerate(result.output_files):
                    file_size = videolib.FileManager.get_file_size(output_file)
                    size_str = videolib.FormatParser.format_file_size(file_size) if file_size else "Unknown"
                    print(f"   {i+1}. {os.path.basename(output_file)} ({size_str})")
            else:
                print(f"X Clip creation failed: {result.error_message}")

            # Show failed clips if any
            if result.failed_clips:
                print(f"\n-> Failed clips: {len(result.failed_clips)}")
                for clip_num, error in result.failed_clips:
                    print(f"   X Clip {clip_num}: {error}")

        except KeyboardInterrupt:
            print("\n-> Clip creation cancelled by user")
        except Exception as e:
            print(f"\nX Unexpected error: {e}")
        finally:
            self.keyboard_listener.stop_listening()
            self.pause_for_user()
    
    def get_media_info_interactive(self):
        """Interactive media info workflow with 'q' interrupt support"""
        print("\n" + "-" * 50)
        print("MEDIA INFORMATION")
        print("-" * 50)
        
        try:
            # Get file path
            file_path = self.get_file_path("Enter media file path", must_exist=True)
            
            print("\n-> Analyzing media file...")
            print("-> Press 'q' to cancel analysis")
            
            self.keyboard_listener.start_listening()
            self.progress_tracker.start("Reading media information...")
            
            try:
                media_info = self.processor.get_media_info(file_path)
            finally:
                self.progress_tracker.stop()
                self.keyboard_listener.stop_listening()
            
            if self.keyboard_listener.should_quit:
                print("\n-> Analysis cancelled by user ('q' pressed)")
                return
            
            if not media_info:
                print("X Could not get media information for this file")
                return
            
            print("\n" + "=" * 50)
            print(f"Media Information: {Path(file_path).name}")
            print("=" * 50)
            
            if media_info.duration:
                print(f"-> Duration: {videolib.FormatParser.format_duration(media_info.duration)}")
            
            if media_info.video_codec:
                print(f"-> Video codec: {media_info.video_codec}")
            
            if media_info.audio_codec:
                print(f"-> Audio codec: {media_info.audio_codec}")
            
            if media_info.format_name:
                print(f"-> Format: {media_info.format_name}")
            
            if media_info.width and media_info.height:
                print(f"-> Resolution: {media_info.width}x{media_info.height}")
            
            if media_info.size_bytes:
                print(f"-> File size: {videolib.FormatParser.format_file_size(media_info.size_bytes)}")
            
            if media_info.bitrate:
                bitrate_mbps = media_info.bitrate / 1_000_000
                print(f"-> Bitrate: {bitrate_mbps:.2f} Mbps ({media_info.bitrate:,} bps)")
            
        except KeyboardInterrupt:
            print("\n-> Media info cancelled by user")
        except Exception as e:
            print(f"\nX Unexpected error: {e}")
        finally:
            self.keyboard_listener.stop_listening()
        
        self.pause_for_user()
    
    def batch_process_interactive(self):
        """Interactive batch processing workflow with 'q' interrupt support"""
        print("\n" + "-" * 50)
        print("BATCH PROCESSING FROM CONFIG FILE")
        print("-" * 50)
        
        try:
            # Get config file
            config_file = self.get_file_path("Enter JSON config file path", must_exist=True)
            
            # Validate config first
            print("\n-> Validating configuration...")
            print("-> Press 'q' to cancel validation")
            
            self.keyboard_listener.start_listening()
            self.progress_tracker.start("Validating config file...")
            
            try:
                manager = videolib.ConfigurationManager()
                is_valid, errors = manager.validate_config_file(config_file)
            finally:
                self.progress_tracker.stop()
                self.keyboard_listener.stop_listening()
            
            if self.keyboard_listener.should_quit:
                print("\n-> Validation cancelled by user ('q' pressed)")
                return
            
            if not is_valid:
                print("X Configuration validation failed:")
                for error in errors:
                    print(f"   -> {error}")
                return
            
            print("-> Configuration is valid")
            
            # Load config
            config = videolib.load_config_from_file(config_file)
            
            # Show config summary
            print("\n-> Configuration Summary:")
            print(f"-> Total tasks: {len(config.tasks)}")
            
            task_counts = {}
            for task in config.tasks:
                task_counts[task.task_type] = task_counts.get(task.task_type, 0) + 1
            
            for task_type, count in task_counts.items():
                print(f"   -> {task_type}: {count}")
            
            if config.global_settings:
                print(f"-> Global settings: {len(config.global_settings)} items")
            
            # Confirm execution
            confirm = self.get_yes_no("Proceed with batch processing?", True)
            if not confirm:
                print("X Batch processing cancelled")
                return
            
            # Convert config to task list for batch processing
            tasks = []
            for task in config.tasks:
                merged_params = config.get_merged_params(config.tasks.index(task))
                tasks.append({
                    'type': task.task_type,
                    'parameters': merged_params
                })
            
            # Execute batch with interrupt support
            print("\n-> Starting batch processing...")
            print("-> Press 'q' anytime during processing to cancel and return to menu")
            
            self.keyboard_listener.start_listening()
            self.progress_tracker.start("Processing batch tasks...")
            
            try:
                result = self.processor.process_batch(tasks)
            finally:
                self.progress_tracker.stop()
                self.keyboard_listener.stop_listening()
            
            if self.keyboard_listener.should_quit:
                print("\n-> Batch processing cancelled by user ('q' pressed)")
                return
            
            # Show results
            print("\n" + "=" * 50)
            print("BATCH PROCESSING RESULTS")
            print("=" * 50)
            print(f"-> Total tasks: {result['total_tasks']}")
            print(f"-> Successful: {result['successful_tasks']}")
            print(f"-> Failed: {result['failed_tasks']}")
            print(f"-> Success rate: {result['success_rate']:.1f}%")
            
            # Show individual results
            if result['results']:
                print("\n-> Task Details:")
                for task_result in result['results']:
                    task_num = task_result['task_index'] + 1
                    task_type = task_result['task_type']
                    success = getattr(task_result['result'], 'success', task_result['result'].get('success', False))
                    
                    status_icon = "->" if success else "X"
                    print(f"   {status_icon} Task {task_num} ({task_type}): {'SUCCESS' if success else 'FAILED'}")
            
        except KeyboardInterrupt:
            print("\n-> Batch processing cancelled by user")
        except Exception as e:
            print(f"\nX Unexpected error: {e}")
        finally:
            self.keyboard_listener.stop_listening()
        
        self.pause_for_user()
    
    def settings_menu(self):
        """Settings and configuration menu"""
        print("\n" + "-" * 50)
        print("SETTINGS")
        print("-" * 50)
        
        while True:
            print("\n-> Settings Menu:")
            print("1. Reinitialize Processor")
            print("2. Check FFmpeg Version")
            print("3. Test Media File")
            print("0. Back to Main Menu")
            
            try:
                choice = self.get_input("Select option").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self.processor = None
                    self.initialize_processor()
                elif choice == '2':
                    self.check_ffmpeg_version()
                elif choice == '3':
                    self.test_media_file()
                else:
                    print("X Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n-> Settings menu cancelled")
                break
    
    def check_ffmpeg_version(self):
        """Check FFmpeg version"""
        print("\n-> Checking FFmpeg version...")
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Get first line which contains version info
                version_line = result.stdout.split('\n')[0]
                print(f"-> {version_line}")
            else:
                print("X FFmpeg not found or not working")
        except FileNotFoundError:
            print("X FFmpeg executable not found in PATH")
        except subprocess.TimeoutExpired:
            print("X FFmpeg version check timed out")
        except Exception as e:
            print(f"X Error checking FFmpeg: {e}")
        
        self.pause_for_user()
    
    def test_media_file(self):
        """Test a media file with interrupt support"""
        print("\n-> Test Media File")
        try:
            file_path = self.get_file_path("Enter media file to test", must_exist=True)
            
            print("\n-> Testing file...")
            print("-> Press 'q' to cancel test")
            
            self.keyboard_listener.start_listening()
            self.progress_tracker.start("Testing media file...")
            
            try:
                media_info = self.processor.get_media_info(file_path)
            finally:
                self.progress_tracker.stop()
                self.keyboard_listener.stop_listening()
            
            if self.keyboard_listener.should_quit:
                print("\n-> Test cancelled by user ('q' pressed)")
                return
            
            if media_info:
                print("-> File is readable by FFmpeg")
                print(f"-> Duration: {videolib.FormatParser.format_duration(media_info.duration) if media_info.duration else 'Unknown'}")
            else:
                print("X File is not readable or not a valid media file")
                
        except KeyboardInterrupt:
            print("\n-> Test cancelled")
        except Exception as e:
            print(f"\nX Test error: {e}")
        finally:
            self.keyboard_listener.stop_listening()
        
        self.pause_for_user()
    
    def run(self):
        """Main program loop with while loop and return to menu"""
        try:
            self.initialize_processor()
            
            while self.running:
                # Reset keyboard listener state for each menu iteration
                self.keyboard_listener.should_quit = False
                
                self.show_menu()
                
                try:
                    choice = self.get_input("Select option").strip()
                    
                    if choice == '0':
                        print("\n-> Thank you for using VideoLib!")
                        self.running = False
                    elif choice == '1':
                        self.download_video_interactive()
                    elif choice == '2':
                        self.split_video_interactive()
                    elif choice == '3':
                        self.create_clips_interactive()
                    elif choice == '4':
                        self.gif_commands.create_gif_clips_interactive()
                    elif choice == '5':
                        self.get_media_info_interactive()
                    elif choice == '6':
                        self.batch_process_interactive()
                    elif choice == '7':
                        self.settings_menu()
                    else:
                        print("X Invalid option. Please try again.")
                        self.pause_for_user("Press Enter to continue...")
                        
                except KeyboardInterrupt:
                    print("\n\n-> Operation cancelled. Returning to main menu...")
                    continue
                    
        except KeyboardInterrupt:
            print("\n\n-> Goodbye!")
        except Exception as e:
            print(f"\n! Unexpected error: {e}")
            print("Please report this issue.")
        finally:
            # Final cleanup
            self.keyboard_listener.stop_listening()

def main():
    """Entry point for interactive CLI"""
    cli = InteractiveCLI()
    cli.run()

if __name__ == '__main__':
    main()