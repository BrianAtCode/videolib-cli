import os
import time
from typing import List, Tuple, Optional

from videolib import VideoProcessor, create_gif_clips
from .ui import UIHelper, Colors, ProgressReporter

class GifCommands:
    """GIF conversion commands for CLI interface"""
    
    def __init__(self):
        self.processor = VideoProcessor()
        self.ui = UIHelper()
        self.progress = ProgressReporter()
    
    def create_gif_clips_interactive(self):
        """Interactive GIF creation workflow"""
        try:
            self.ui.print_header("VIDEO TO GIF CONVERSION WORKFLOW")
            
            # Step 1: Get source video
            source_file = self._get_source_video()
            if not source_file:
                return
            
            # Get video info
            self.ui.print_info("Analyzing video file...")
            media_info = self.processor.get_media_info(source_file)
            if not media_info:
                self.ui.print_error("Could not analyze video file")
                return
            
            self._display_video_info(media_info)
            
            # Step 2: Choose GIF creation method
            method = self._choose_gif_method()
            
            if method == "1":  # Auto-generate clips
                self._auto_generate_clips(source_file, media_info.duration)
            elif method == "2":  # Manual intervals
                self._manual_intervals(source_file, media_info.duration)
                
        except KeyboardInterrupt:
            self.ui.print_info("\n-> GIF creation cancelled by user")
        except Exception as e:
            self.ui.print_error(f"Error during GIF creation: {e}")
    
    def _get_source_video(self) -> Optional[str]:
        """Get and validate source video file"""
        self.ui.print_step("Step 1: Source Video")
        
        while True:
            source_file = self.ui.get_input("Enter source video file path")
            
            if not source_file:
                continue
                
            if not os.path.exists(source_file):
                self.ui.print_error("File not found. Please try again.")
                continue
            
            return source_file
    
    def _display_video_info(self, media_info):
        """Display video information"""
        duration_str = self.ui.format_duration(media_info.duration)
        size_str = self.ui.format_file_size(media_info.size_bytes)
        
        print(f"-> Duration: {Colors.colorize(duration_str, Colors.GREEN)}")
        print(f"-> Size: {Colors.colorize(size_str, Colors.GREEN)}")
        print(f"-> Video codec: {Colors.colorize(media_info.video_codec, Colors.CYAN)}")
        print(f"-> Audio codec: {Colors.colorize(media_info.audio_codec, Colors.CYAN)}")
        print()
    
    def _choose_gif_method(self) -> str:
        """Choose GIF creation method"""
        self.ui.print_step("Step 2: GIF Creation Method")
        
        print("1. Auto-generate clips (specify number and duration)")
        print("2. Manual time intervals")
        print()
        
        while True:
            choice = self.ui.get_input("Select method (1, 2)")
            if choice in ["1", "2"]:
                return choice
            self.ui.print_error("Please enter 1, 2")
    
    def _auto_generate_clips(self, source_file: str, total_duration: float):
        """Auto-generate GIF clips with equal spacing"""
        self.ui.print_step("Step 3: Auto-Generate Settings")
        
        # Get number of clips
        while True:
            try:
                num_clips_input = self.ui.get_input("Number of GIF clips to create")
                num_clips = int(num_clips_input)
                if num_clips > 0:
                    break
                self.ui.print_error("Please enter a positive number")
            except ValueError:
                self.ui.print_error("Please enter a valid number")
        
        # Get clip duration
        while True:
            try:
                clip_duration_input = self.ui.get_input("Duration of each clip (seconds)")
                clip_duration = float(clip_duration_input)
                if 0 < clip_duration <= total_duration:
                    break
                self.ui.print_error(f"Duration must be between 0 and {total_duration} seconds")
            except ValueError:
                self.ui.print_error("Please enter a valid number")
        
        # Get output settings
        output_name = self.ui.get_input("Output name prefix", "gif_clip")
        
        # Get basic quality settings
        fps = self._get_fps_setting()
        scale_width = self._get_scale_setting()
        
        # Create thumbnails option
        create_thumbnails = self.ui.confirm_action("Create thumbnail images?", default=True)
        
        # Confirmation
        self.ui.print_step("Step 4: Confirmation")
        print(f"-> Source: {Colors.colorize(source_file, Colors.YELLOW)}")
        print(f"-> Number of clips: {Colors.colorize(str(num_clips), Colors.GREEN)}")
        print(f"-> Clip duration: {Colors.colorize(f'{clip_duration}s', Colors.GREEN)}")
        print(f"-> Output prefix: {Colors.colorize(output_name, Colors.CYAN)}")
        print(f"-> FPS: {Colors.colorize(str(fps), Colors.BLUE)}")
        print(f"-> Scale width: {Colors.colorize(f'{scale_width}px', Colors.BLUE)}")
        print(f"-> Create thumbnails: {Colors.colorize('Yes' if create_thumbnails else 'No', Colors.MAGENTA)}")
        print()
        
        if not self.ui.confirm_action("Proceed with GIF creation?"):
            return
        
        # Execute conversion
        self.ui.print_info("Starting GIF creation...")
        self.ui.print_info("Press 'q' anytime to cancel")
        
        # Start progress tracking
        self.progress.start(num_clips, "Creating GIF clips...")
        
        result = create_gif_clips(
            source_file=source_file,
            total_duration=total_duration,
            num_clips=num_clips,
            clip_duration=clip_duration,
            output_name=output_name,
            fps=fps,
            scale_width=scale_width,
            create_thumbnails=create_thumbnails
        )
        
        self.progress.finish("GIF creation completed!")
        self._display_gif_results(result)
    
    def _manual_intervals(self, source_file: str, total_duration: float):
        """Manual time interval specification"""
        self.ui.print_step("Step 3: Manual Time Intervals")
        
        duration_str = self.ui.format_duration(total_duration)
        print(f"-> Video duration: {Colors.colorize(duration_str, Colors.GREEN)}")
        print("-> Enter time intervals (HH:MM:SS, MM:SS, or seconds)")
        print("-> Enter 'done' when finished")
        print()
        
        intervals = []
        interval_num = 1
        
        while True:
            print(f"-> Interval {interval_num}:")
            
            # Get start time
            start_input = self.ui.get_input("Start time")
            if start_input.lower() == 'done':
                break
            
            try:
                start_time = self.ui.parse_time_input(start_input)
                print(start_time)
                if start_time < 0 or start_time >= total_duration:
                    self.ui.print_error(f"Start time must be between 0 and {duration_str}")
                    continue
            except ValueError:
                self.ui.print_error("Invalid time format. Use HH:MM:SS, MM:SS, or seconds")
                continue
            
            # Get end time
            end_input = self.ui.get_input("End time")
            try:
                print(end_input)
                end_time = self.ui.parse_time_input(end_input)
                print(end_time)
                if end_time <= start_time or end_time > total_duration:
                    self.ui.print_error(f"End time must be greater than start time and <= {duration_str}")
                    continue
            except ValueError:
                self.ui.print_error("Invalid time format. Use HH:MM:SS, MM:SS, or seconds")
                continue
            
            intervals.append((start_time, end_time))
            start_str = self.ui.format_duration(start_time)
            end_str = self.ui.format_duration(end_time)
            print(f"-> Added interval: {Colors.colorize(f'{start_str} to {end_str}', Colors.GREEN)}")
            print()
            
            interval_num += 1
        
        if not intervals:
            self.ui.print_info("No intervals specified")
            return
        
        # Get output settings and proceed with conversion
        self._finalize_gif_creation(source_file, intervals)
    
    def _get_fps_setting(self) -> int:
        """Get FPS setting from user"""
        while True:
            fps_input = self.ui.get_input("FPS (frames per second)", "10")
            if not fps_input:
                return 10
            try:
                fps = int(fps_input)
                if 1 <= fps <= 30:
                    return fps
                self.ui.print_error("FPS must be between 1 and 30")
            except ValueError:
                self.ui.print_error("Please enter a valid number")
    
    def _get_scale_setting(self) -> int:
        """Get scale width setting from user"""
        while True:
            scale_input = self.ui.get_input("Scale width in pixels", "320")
            if not scale_input:
                return 320
            try:
                scale = int(scale_input)
                if 100 <= scale <= 1920:
                    return scale
                self.ui.print_error("Scale width must be between 100 and 1920 pixels")
            except ValueError:
                self.ui.print_error("Please enter a valid number")
    
    def _finalize_gif_creation(self, source_file: str, intervals: List[Tuple[float, float]]):
        """Finalize and execute GIF creation"""
        # Get output settings
        output_name = self.ui.get_input("Output name prefix", "gif_clip")
        fps = self._get_fps_setting()
        scale_width = self._get_scale_setting()
        create_thumbnails = self.ui.confirm_action("Create thumbnail images?", default=True)
        
        # Confirmation
        self.ui.print_step("Step 4: Confirmation")
        print(f"-> Source: {Colors.colorize(source_file, Colors.YELLOW)}")
        print(f"-> Intervals: {Colors.colorize(str(len(intervals)), Colors.GREEN)} clips")
        for i, (start, end) in enumerate(intervals, 1):
            start_str = self.ui.format_duration(start)
            end_str = self.ui.format_duration(end)
            print(f"   {i}. {Colors.colorize(f'{start_str} to {end_str}', Colors.CYAN)}")
        print()
        
        if not self.ui.confirm_action("Proceed with GIF creation?"):
            return
        
        # Execute conversion
        self.ui.print_info("Creating GIF clips...")
        
        # Start progress tracking
        self.progress.start(len(intervals), "Processing intervals...")
        
        result = self.processor.create_gif_clips(
            source_file=source_file,
            intervals=intervals,
            output_name=output_name,
            fps=fps,
            scale_width=scale_width,
            create_thumbnails=create_thumbnails
        )
        
        self.progress.finish("GIF creation completed!")
        self._display_gif_results(result)
    
    def _display_gif_results(self, result):
        """Display GIF conversion results"""
        if result.success:
            self.ui.print_header("GIF CREATION RESULTS")
            self.ui.print_success(f"Successfully created {len(result.gif_files)} GIF(s)")
            print()
            
            print("-> GIF files:")
            for i, gif_file in enumerate(result.gif_files, 1):
                size = self.ui.get_file_size(gif_file) if os.path.exists(gif_file) else 0
                size_str = self.ui.format_file_size(size)
                print(f"   {i}. {Colors.colorize(gif_file, Colors.GREEN)} ({Colors.colorize(size_str, Colors.BLUE)})")
            
            if result.thumbnail_files:
                print()
                print("-> Thumbnail files:")
                for i, thumb_file in enumerate(result.thumbnail_files, 1):
                    print(f"   {i}. {Colors.colorize(thumb_file, Colors.CYAN)}")
            
            print()
            print(f"-> Total duration: {Colors.colorize(self.ui.format_duration(result.total_duration), Colors.YELLOW)}")
            print(f"-> Processing time: {Colors.colorize(f'{result.processing_time:.1f}s', Colors.YELLOW)}")
            
        else:
            self.ui.print_error("GIF creation failed")
            if result.error_message:
                print(f"Error: {Colors.colorize(result.error_message, Colors.RED)}")
        
        self.ui.wait_for_enter()
