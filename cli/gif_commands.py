import os
import time
from typing import List, Tuple, Optional

from videolib import VideoProcessor, create_gif_clips
from .ui import UIHelper, Colors, ProgressReporter


class GifCommands:
    """Enhanced GIF conversion commands for CLI interface"""

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
                self._auto_generate_clips_enhanced(source_file, media_info.duration)
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

        print("1. Auto-generate clips (specify number, duration, and gap)")
        print("2. Manual time intervals")
        print()

        while True:
            choice = self.ui.get_input("Select method (1, 2)")
            if choice in ["1", "2"]:
                return choice
            self.ui.print_error("Please enter 1 or 2")

    def _auto_generate_clips_enhanced(self, source_file: str, total_duration: float):
        """Enhanced auto-generate GIF clips with time gap control and merging"""
        self.ui.print_step("Step 3: Enhanced Auto-Generate Settings")

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

        # Get GIF duration (length of each clip)
        while True:
            try:
                gif_duration_input = self.ui.get_input("Duration of each GIF clip (seconds)")
                gif_duration = float(gif_duration_input)
                if gif_duration > 0:
                    break
                self.ui.print_error("Duration must be greater than 0")
            except ValueError:
                self.ui.print_error("Please enter a valid number")

        # Get time gap between clips
        while True:
            try:
                time_gap_input = self.ui.get_input("Time gap between clips (seconds)", "0")
                time_gap = float(time_gap_input)
                if time_gap >= 0:
                    break
                self.ui.print_error("Time gap must be 0 or greater")
            except ValueError:
                self.ui.print_error("Please enter a valid number")

        # Calculate total time needed and show warning if necessary
        total_time_needed = (num_clips * gif_duration) + ((num_clips - 1) * time_gap)
        if total_time_needed > total_duration:
            self.ui.print_warning(f"Total time needed ({self.ui.format_duration(total_time_needed)}) exceeds video duration ({self.ui.format_duration(total_duration)})")
            if not self.ui.confirm_action("Continue anyway? Some clips may be incomplete."):
                return

        # Get output settings
        output_name = self.ui.get_input("Output name prefix", "auto_clip")

        # Get quality settings
        fps = self._get_fps_setting()
        scale_width = self._get_scale_setting()
        quality_level = self._get_quality_setting()

        # Enhanced options
        create_thumbnails = self.ui.confirm_action("Create thumbnail images?", default=True)
        create_grid = self.ui.confirm_action("Create thumbnail grid with media info?", default=True)
        merge_gifs = self.ui.confirm_action("Merge all GIFs into one file?", default=True)

        # Additional enhanced option: cleanup individual thumbnails
        create_thumbnails = self.ui.confirm_action("Create thumbnails from video clips?", default=True)
        create_grid = False
        cleanup_individual_thumbs = False
        
        if create_thumbnails:
            create_grid = self.ui.confirm_action("Create thumbnail grid with media info?", default=True)
            
            # Ask about individual thumbnail cleanup
            if create_grid:
                print()
                print("📂 File Management Options:")
                print("   Individual thumbnails are used to create the grid.")
                print("   After the grid is created, you can choose to:")
                print("   • Keep individual thumbnails (for detailed inspection)")
                print("   • Remove individual thumbnails (cleaner output directory)")
                print()
                
                cleanup_individual_thumbs = self.ui.confirm_action(
                    "Remove individual thumbnails after grid creation?", 
                    default=False
                )

        # Confirmation
        self.ui.print_step("Step 4: Confirmation")
        print(f"-> Source: {Colors.colorize(source_file, Colors.YELLOW)}")
        print(f"-> Number of clips: {Colors.colorize(str(num_clips), Colors.GREEN)}")
        print(f"-> GIF duration: {Colors.colorize(f'{gif_duration}s', Colors.GREEN)}")
        print(f"-> Time gap: {Colors.colorize(f'{time_gap}s', Colors.GREEN)}")
        print(f"-> Output prefix: {Colors.colorize(output_name, Colors.CYAN)}")
        print(f"-> FPS: {Colors.colorize(str(fps), Colors.BLUE)}")
        print(f"-> Scale width: {Colors.colorize(f'{scale_width}px', Colors.BLUE)}")
        print(f"-> Quality: {Colors.colorize(quality_level, Colors.BLUE)}")
        print(f"-> Create thumbnails: {Colors.colorize('Yes' if create_thumbnails else 'No', Colors.MAGENTA)}")
        print(f"-> Create grid: {Colors.colorize('Yes' if create_grid else 'No', Colors.MAGENTA)}")
        print(f"-> Merge GIFs: {Colors.colorize('Yes' if merge_gifs else 'No', Colors.MAGENTA)}")

        # cleanup option to confirmation display
        if create_grid:
            print(f"-> Create grid: {Colors.colorize('Yes' if create_grid else 'No', Colors.MAGENTA)}")
            if cleanup_individual_thumbs:
                print(f"-> Cleanup individual thumbs: {Colors.colorize('Yes (keep grid only)', Colors.YELLOW)}")
            else:
                print(f"-> Cleanup individual thumbs: {Colors.colorize('No (keep all)', Colors.GREEN)}")

        # Show timeline preview
        print(f"\n-> Timeline Preview:")
        for i in range(min(num_clips, 5)):  # Show first 5 clips
            start_time = i * (gif_duration + time_gap)
            end_time = start_time + gif_duration
            start_str = self.ui.format_duration(start_time)
            end_str = self.ui.format_duration(end_time)
            print(f"   Clip {i+1}: {Colors.colorize(f'{start_str} - {end_str}', Colors.CYAN)}")

        if num_clips > 5:
            print(f"   ... and {num_clips - 5} more clips")
        print()

        if not self.ui.confirm_action("Proceed with enhanced GIF creation?"):
            return

        # Execute conversion
        self.ui.print_info("Starting enhanced GIF creation...")
        self.ui.print_info("Press 'q' anytime to cancel")

        # Start progress tracking
        self.progress.start(num_clips + 2, "Creating GIF clips with enhancements...")

        try:
            result = self.processor.create_auto_gif_clips(
                source_file=source_file,
                num_clips=num_clips,
                gif_duration=gif_duration,
                time_gap=time_gap,
                output_name=output_name,
                fps=fps,
                scale_width=scale_width,
                quality_level=quality_level,
                create_thumbnails=create_thumbnails,
                create_grid=create_grid,
                merge_gifs=merge_gifs,
                cleanup_individual_thumbs=cleanup_individual_thumbs
            )

            self.progress.finish("GIF creation completed!")
            self._display_enhanced_gif_results(result)

        except Exception as e:
            self.progress.finish("GIF creation failed!")
            self.ui.print_error(f"Error during GIF creation: {e}")

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
                if start_time < 0 or start_time >= total_duration:
                    self.ui.print_error(f"Start time must be between 0 and {duration_str}")
                    continue
            except ValueError:
                self.ui.print_error("Invalid time format. Use HH:MM:SS, MM:SS, or seconds")
                continue

            # Get end time
            end_input = self.ui.get_input("End time")
            try:
                end_time = self.ui.parse_time_input(end_input)
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

    def _get_quality_setting(self) -> str:
        """Get quality level setting from user"""
        while True:
            print("Quality levels:")
            print("1. Low (smaller files, faster processing)")
            print("2. Medium (balanced quality and size)")
            print("3. High (best quality, larger files)")
            print()

            choice = self.ui.get_input("Select quality level (1-3)", "2")
            if choice == "1":
                return "low"
            elif choice == "2":
                return "medium"
            elif choice == "3":
                return "high"
            else:
                self.ui.print_error("Please enter 1, 2, or 3")

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
        """Display standard GIF conversion results"""
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

    def _display_enhanced_gif_results(self, result):
        """Display GIF conversion results with media info and merged files"""
        if result.success:
            self.ui.print_header("GIF CREATION RESULTS")
            
            # Show media info if available
            if result.media_info:
                print("-> Video Information:")
                info = result.media_info
                print(f"   Format: {Colors.colorize(info.get('format', 'Unknown'), Colors.CYAN)}")
                print(f"   Duration: {Colors.colorize(self._format_duration_from_str(info.get('duration', '0')), Colors.CYAN)}")
                resolution_str = f"{info.get('width', '0')}x{info.get('height', '0')}"
                print(f"   Resolution: {Colors.colorize(resolution_str, Colors.CYAN)}")
                print()
            
            self.ui.print_success(f"Successfully created {len(result.gif_files)} file(s)")
            print()

            # Separate individual GIFs from merged files
            individual_gifs = [f for f in result.gif_files if not f.endswith('_merged.gif')]
            merged_gifs = [f for f in result.gif_files if f.endswith('_merged.gif')]
            
            individual_thumbs = [f for f in result.thumbnail_files if not f.endswith('_grid.png')]
            grid_thumbs = [f for f in result.thumbnail_files if f.endswith('_grid.png')]

            # Display individual GIF clips
            if individual_gifs:
                print("-> Individual GIF clips:")
                for i, gif_file in enumerate(individual_gifs, 1):
                    size = self.ui.get_file_size(gif_file) if os.path.exists(gif_file) else 0
                    size_str = self.ui.format_file_size(size)
                    print(f"   {i}. {Colors.colorize(gif_file, Colors.GREEN)} ({Colors.colorize(size_str, Colors.BLUE)})")

            # Display merged GIF
            if merged_gifs:
                print("\n-> Merged GIF file:")
                for gif_file in merged_gifs:
                    size = self.ui.get_file_size(gif_file) if os.path.exists(gif_file) else 0
                    size_str = self.ui.format_file_size(size)
                    print(f"   {Colors.colorize(gif_file, Colors.YELLOW)} ({Colors.colorize(size_str, Colors.BLUE)})")

            # Display grid thumbnail
            if grid_thumbs:
                print("\n-> Thumbnail grid with media info:")
                for thumb_file in grid_thumbs:
                    size = self.ui.get_file_size(thumb_file) if os.path.exists(thumb_file) else 0
                    size_str = self.ui.format_file_size(size)
                    print(f"   {Colors.colorize(thumb_file, Colors.MAGENTA)} ({Colors.colorize(size_str, Colors.BLUE)})")

            # Display individual thumbnails
            if individual_thumbs:
                print("\n-> Individual thumbnails:")
                for i, thumb_file in enumerate(individual_thumbs, 1):
                    print(f"   {i}. {Colors.colorize(thumb_file, Colors.CYAN)}")
            elif grid_thumbs:
                print(f"\n-> Individual thumbnails: {Colors.colorize('Cleaned up (removed)', Colors.YELLOW)}")

            print()
            print(f"-> Total GIF duration: {Colors.colorize(self.ui.format_duration(result.total_duration), Colors.YELLOW)}")
            print(f"-> Processing time: {Colors.colorize(f'{result.processing_time:.1f}s', Colors.YELLOW)}")

        else:
            self.ui.print_error("Enhanced GIF creation failed")
            if result.error_message:
                print(f"Error: {Colors.colorize(result.error_message, Colors.RED)}")

        self.ui.wait_for_enter()

    def _format_duration_from_str(self, duration_str: str) -> str:
        """Format duration from string seconds to HH:MM:SS"""
        try:
            seconds = float(duration_str)
            return self.ui.format_duration(seconds)
        except:
            return duration_str
