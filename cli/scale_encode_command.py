"""
Scale & Encode Command - Inherits from CLICommands base class

This module implements the Scale & Encode workflow by extending the base
CLICommands class with specialized functionality for video scaling and
audio encoding operations.
"""

import os
from typing import Dict, Any, List, Optional, Tuple

import videolib
from .commands import CLICommands
from .ui import MenuHandler, InputHandler, DisplayHandler, UIHelper

from videolib.config.scale_encode_presets import (
    RESOLUTION_PRESETS_DESKTOP, RESOLUTION_PRESETS_VR,
    VIDEO_CODEC_OPTIONS, VIDEO_PROFILE_OPTIONS,
    VIDEO_LEVEL_OPTIONS, FRAME_RATE_OPTIONS,
    AUDIO_CODEC_OPTIONS, SAMPLE_RATE_OPTIONS, CHANNEL_OPTIONS
)

class ScaleEncodeCommand(CLICommands):
    """
    Scale & Encode command - complete workflow with all messages.
    
    Inherits from CLICommands to maintain consistent command interface
    and leverage base command handling patterns.
    """
    
    # Message constants - all user-facing text content
    MESSAGES = {
        'workflow_title': 'SCALE & ENCODE WORKFLOW',
        'step_1a': 'Input File Selection',
        'step_1b': 'Video Settings',
        'step_1c': 'Audio Settings',
        'step_2': 'Output File Selection',
        'resolution_type_title': 'Resolution Type Selection',
        'resolution_select': 'Resolution Selection',
        'codec_select': '{} Codec Selection',
        'profile_select': 'Video Profile Selection',
        'level_select': 'Video Level Selection',
        'frame_rate_select': 'Frame Rate Selection',
        'sample_rate_select': 'Audio Sample Rate Selection',
        'channels_select': 'Audio Channels Selection',
        'video_bitrate_select': 'Video Bitrate Selection',
        'audio_bitrate_select': 'Audio Bitrate Selection',
        'settings_summary': 'CONFIGURATION SUMMARY',
        'confirm_proceed': 'Proceed with encoding',
        'error_file_not_found': 'File not found',
        'error_empty_path': 'File path cannot be empty',
        'error_no_file': 'No file selected',
        'error_no_output': 'No output file specified',
        'error_cancelled': 'Encoding cancelled by user',
        'error_interrupted': 'Encoding interrupted',
        'success_complete': 'Scale & Encode completed successfully',
        'success_output': 'Output file',
        'failed_complete': 'Scale & Encode did not complete',
        'cancelled_by_user': 'Encoding cancelled by user',
    }
    
    def __init__(self, processor: videolib.VideoProcessor, keyboard_listener, progress_tracker):
        """
        Initialize Scale Encode Command.
        
        Args:
            processor: VideoProcessor instance
            keyboard_listener: For interrupt handling
            progress_tracker: For progress display
        """
        # Call parent constructor
        super().__init__(processor)
        
        # Store additional dependencies
        self.keyboard_listener = keyboard_listener
        self.progress_tracker = progress_tracker
        
        # Initialize UI components
        self.config = processor.config
        self.video_setting = videolib.interfaces.scale_encode_interface.VideoSettings()
        self.audio_setting = videolib.interfaces.scale_encode_interface.AudioSettings()
        self.ui_helper = UIHelper()
        self.menu = MenuHandler(self.ui_helper)
        self.input_handler = InputHandler(self.ui_helper)
        self.display = DisplayHandler(self.ui_helper)
    
    def execute_workflow(self) -> bool:
        """
        Execute complete scale & encode workflow.
        
        This is the main entry point for the scale & encode command.
        It orchestrates the entire workflow from input file selection
        through encoding execution.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.display.display_section(self.MESSAGES['workflow_title'])
            
            # Step 1a: Get input file
            input_file = self._get_input_file()
            if not input_file:
                self.display.display_error(self.MESSAGES['error_no_file'])
                return False
            
            # Step 2: Detect properties
            detected_props = self._detect_properties(input_file)
            self._display_detected_properties(detected_props)
            
            # Step 3: Collect video settings
            self._collect_video_settings(detected_props)
            
            # Step 4: Collect audio settings
            self._collect_audio_settings(detected_props)
            
            # Step 5: Display settings summary
            self._display_settings_summary()
            
            # Step 6: Get output file
            output_file = self._get_output_file()
            if not output_file:
                self.display.display_error(self.MESSAGES['error_no_output'])
                return False
            
            # Step 7: Confirm and execute
            if not self.input_handler.get_confirmation(self.MESSAGES['confirm_proceed']):
                self.display.display_warning(self.MESSAGES['cancelled_by_user'])
                return False
            
            # Execute encoding
            return self._execute_encoding(input_file, output_file)
            
        except KeyboardInterrupt:
            self.display.display_warning(self.MESSAGES['error_interrupted'])
            return False
        except Exception as e:
            self.display.display_error(f"Error in workflow: {e.with_traceback.format_exc()}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== Workflow Methods ==========
    
    def _get_input_file(self) -> Optional[str]:
        """
        Get and validate input file from user.
        
        Returns:
            File path if valid, None otherwise
        """
        self.display.display_step(self.MESSAGES['step_1a'])
        
        while True:
            file_path = self.input_handler.get_file_path("Enter input video file", must_exist=True)
            if file_path:
                return file_path
            
            retry = self.input_handler.get_confirmation("Try again", default=True)
            if not retry:
                return None
    
    def _detect_properties(self, input_file: str) -> Dict[str, Any]:
        """
        Detect input file properties using FFprobe.
        
        Args:
            input_file: Path to input video file
        
        Returns:
            Dictionary with detected video and audio properties
        """
        self.display.display_info("FFprobe analyzing video...")
        self.keyboard_listener.start_listening()
        self.progress_tracker.start("Detecting properties...")
        
        try:
            detected_props = self.processor.detect_advance_media_properties(input_file)
            return detected_props if detected_props else {'video': {}, 'audio': {}}
        finally:
            self.progress_tracker.stop()
            self.keyboard_listener.stop_listening()
            
            if self.keyboard_listener.should_quit:
                raise KeyboardInterrupt("User cancelled")
    
    def _display_detected_properties(self, properties: Dict[str, Any]) -> None:
        """
        Display detected input file properties.
        
        Args:
            properties: Dictionary with detected properties
        """
        print("\nCurrent Input Video Information:")
        
        video = properties.get('video', {})
        print(f"- Codec: {video.get('codec', 'unknown')}")
        print(f"- Profile: {video.get('profile', 'unknown')}")
        print(f"- Level: {video.get('level', 'unknown')}")
        print(f"- Bitrate: {video.get('bitrate', 'unknown')}")
        print(f"- Frame Rate: {video.get('frame_rate', 'unknown')} fps")
        print(f"- Resolution: {video.get('width')}x{video.get('height')}")
        
        audio = properties.get('audio', {})
        print(f"\n- Audio Codec: {audio.get('codec', 'unknown')}")
        print(f"- Sample Rate: {audio.get('sample_rate', 'unknown')} Hz")
        print(f"- Channels: {audio.get('channels', 'unknown')}")
        print(f"- Audio Bitrate: {audio.get('bitrate', 'unknown')}")
    
    def _collect_video_settings(self, detected_props: Dict[str, Any]) -> None:
        """
        Collect video settings from user with optimization.
        
        Optimization: If user selects detected codec, automatically use "copy" 
        to skip re-encoding and improve processing speed.
        
        Args:
            detected_props: Dictionary with detected properties
        """
        from videolib.config.scale_encode_presets import (
            RESOLUTION_PRESETS_DESKTOP, RESOLUTION_PRESETS_VR,
            VIDEO_CODEC_OPTIONS, VIDEO_PROFILE_OPTIONS,
            VIDEO_LEVEL_OPTIONS, FRAME_RATE_OPTIONS
        )
        
        self.display.display_step(self.MESSAGES['step_1b'])
        
        # Resolution type
        print(f"\n{self.MESSAGES['resolution_type_title']}:")
        print("  1. Desktop")
        print("  2. VR")
        
        res_type = input("\n> Select type (1-2): ").strip()
        self.config.scale_resolution_type = "vr" if res_type == "2" else "desktop"
        
        # Resolution
        width, height, default_br = self._select_resolution(
            self.config.scale_resolution_type
        )
        self.config.scale_width = width
        self.video_setting.width = width
        
        self.config.scale_height = height
        self.video_setting.height = height

        # ========== OPTIMIZATION: Video Codec Selection ==========
        detected_codec = detected_props.get('video', {}).get('codec')
        selected_codec_index = self._select_codec_index("video", detected_codec)

        # Determine actual codec to use
        if selected_codec_index == "detected":
            print("detected")
            # User selected detected codec → Use "copy" for optimization
            self.config.video_codec = "copy"
            self.video_setting.codec = "copy"
            
            # ✅ FAST PATH: Skip profile, level, frame rate, bitrate when using copy
            print("\n[Optimized: Using codec 'copy' - no re-encoding, processing speed improved]")
            
            # Keep profile/level/fps/bitrate as defaults (won't be used with copy)
            self.config.video_profile = detected_props.get('video', {}).get('profile', 'high')
            #self.video_setting.profile = detected_props.get('video', {}).get('profile', 'high')

            self.config.video_level = detected_props.get('video', {}).get('level', '4.1')
            #self.video_setting.level = detected_props.get('video', {}).get('level', '4.1')

            self.config.video_frame_rate = detected_props.get('video', {}).get('frame_rate', 30)
            #self.video_setting.frame_rate = detected_props.get('video', {}).get('frame_rate', 30)

            self.config.video_bitrate = detected_props.get('video', {}).get('bitrate', '5000k')
            #self.video_setting.bitrate = detected_props.get('video', {}).get('bitrate', '5000k')
        
        else:
            # User selected custom codec → Full re-encoding with all settings
            self.config.video_codec = selected_codec_index
            self.video_setting.codec = selected_codec_index
            
            # Profile
            detected_profile = detected_props.get('video', {}).get('profile')
            self.config.video_profile = self._select_profile(detected_profile)
            self.video_setting.profile = self.config.video_profile
            
            # Level
            detected_level = detected_props.get('video', {}).get('level')
            self.config.video_level = self._select_level(detected_level)
            self.video_setting.level = self.config.video_level
            
            # Frame rate
            detected_fps = detected_props.get('video', {}).get('frame_rate')
            self.config.video_frame_rate = self._select_frame_rate(detected_fps)
            self.video_setting.frame_rate = self.config.video_frame_rate
            
            # Bitrate
            detected_br = detected_props.get('video', {}).get('bitrate')
            self.config.video_bitrate = self._select_video_bitrate(detected_br, default_br)
            self.video_setting.bitrate = self.config.video_bitrate
    
    def _collect_audio_settings(self, detected_props: Dict[str, Any]) -> None:
        """
        Collect audio settings from user with optimization.
        
        Optimization: If user selects detected codec, automatically use "copy"
        to skip re-encoding and improve processing speed.
        
        Args:
            detected_props: Dictionary with detected properties
        """
        from videolib.config.scale_encode_presets import (
            SAMPLE_RATE_OPTIONS, CHANNEL_OPTIONS
        )
        
        self.display.display_step(self.MESSAGES['step_1c'])
        
        # ========== OPTIMIZATION: Audio Codec Selection ==========
        detected_audio_codec = detected_props.get('audio', {}).get('codec')
        selected_audio_codec_index = self._select_codec_index("audio", detected_audio_codec)
        
        # Determine actual codec to use
        if selected_audio_codec_index == "detected":
            # User selected detected codec → Use "copy" for optimization
            self.config.audio_codec = "copy"
            self.audio_setting.codec = "copy"
            
            # ✅ FAST PATH: Skip profile, sample rate, channels, bitrate when using copy
            print("\n[Optimized: Using codec 'copy' - no re-encoding, processing speed improved]")
            
            # Keep audio settings as detected (won't be used with copy)
            self.config.audio_profile = detected_props.get('audio', {}).get('profile', 'aac_low')
            self.config.audio_sample_rate = int(detected_props.get('audio', {}).get('sample_rate', 44100))
            self.config.audio_channels = int(detected_props.get('audio', {}).get('channels', 2))
            self.config.audio_channel_layout = detected_props.get('audio', {}).get('channel_layout', 'stereo')
            self.config.audio_bitrate = detected_props.get('audio', {}).get('bitrate', '192k')
        
        else:
            # User selected custom codec → Full re-encoding with all settings
            self.config.audio_codec = selected_audio_codec_index
            self.audio_setting.codec = selected_audio_codec_index
            
            # Sample rate
            detected_sr = detected_props.get('audio', {}).get('sample_rate')
            self.config.audio_sample_rate = self._select_sample_rate(detected_sr)
            self.audio_setting.audio_sample_rate = self.config.audio_sample_rate
            
            # Channels
            detected_ch = detected_props.get('audio', {}).get('channels')
            channels, layout = self._select_channels(detected_ch)

            self.config.audio_channels = channels
            self.audio_setting.channels = channels

            self.config.audio_channel_layout = layout
            self.audio_setting.channel_layout = layout
            
            # Audio bitrate
            detected_abr = detected_props.get('audio', {}).get('bitrate')
            self.config.audio_bitrate = self._select_audio_bitrate(detected_abr, channels)
            self.audio_setting.bitrate = self.config.audio_bitrate

    def _select_codec_index(self, codec_type: str, detected: str = None) -> str:
        """
        Get codec selection from user - returns "detected" or actual codec name.
        
        Enhanced version that removes old "copy" option and provides
        optimized "Keep detected" option for faster processing.
        
        User Experience:
        - Option 1-N: Select from available codecs (libx264, libx265, aac, etc.)
        - Option N+1: Keep detected (uses copy codec for 5-10x speed improvement)
        - Option N+2: Custom codec
        
        Args:
            codec_type: 'video' or 'audio'
            detected: Detected codec name (e.g., 'h264', 'aac')
        
        Returns:
            "detected" - User wants to use detected codec (will trigger "copy")
            codec_name - User selected specific codec
        """
        from videolib.config.scale_encode_presets import (
            VIDEO_CODEC_OPTIONS, AUDIO_CODEC_OPTIONS
        )
        
        print(f"\n{self.MESSAGES['codec_select'].format(codec_type.title())}:")
        
        options = VIDEO_CODEC_OPTIONS if codec_type == "video" else AUDIO_CODEC_OPTIONS
        
        # Display standard codec options (without old "copy" option)
        for i, (codec, info) in enumerate(options.items(), 1):
            marker = " (detected)" if detected and detected in codec else ""
            print(f"  {i}. {codec}{marker} - {info['desc']}")
        
        # Add optimized "Keep detected" option if we have a detected codec
        if detected:
            next_option = len(options) + 1
            print(f"  {next_option}. Keep detected ({detected}) - Optimized (copy, faster) ⚡")
            print(f"  {next_option + 1}. Custom")
            max_choices = len(options) + 2
        else:
            next_option = len(options) + 1
            print(f"  {next_option}. Custom")
            max_choices = len(options) + 1
        
        # Get user selection
        choice = self.menu.get_selection("Select codec", max_choices, allow_custom=True)
        
        codec_list = list(options.keys())
        
        if choice.isdigit():
            choice_int = int(choice)
            
            # ========== USER SELECTED "KEEP DETECTED" ==========
            # This triggers the optimization path (codec="copy")
            if detected and choice_int == len(options) + 1:
                return "detected"
            
            # ========== USER SELECTED "CUSTOM" ==========
            custom_option = len(options) + 2 if detected else len(options) + 1
            if choice_int == custom_option:
                custom_codec = self.input_handler.get_string("Enter custom codec", required=True)
                return custom_codec
            
            # ========== USER SELECTED STANDARD CODEC ==========
            if 1 <= choice_int <= len(codec_list):
                selected_codec = codec_list[choice_int - 1]
                return selected_codec
        
        # Default fallback
        return "detected" if detected else ("libx264" if codec_type == "video" else "aac")
        
    
    def _display_settings_summary(self) -> None:
        """Display complete configuration summary"""
        print("\n" + "=" * 60)
        print("VIDEO SETTINGS")
        print("=" * 60)
        print(f"Resolution: {self.config.scale_width}x{self.config.scale_height}")
        print(f"Codec: {self.config.video_codec}")
        print(f"Profile: {self.config.video_profile}")
        print(f"Level: {self.config.video_level}")
        print(f"Frame Rate: {self.config.video_frame_rate} fps")
        print(f"Bitrate: {self.config.video_bitrate}")
        
        print("\n" + "=" * 60)
        print("AUDIO SETTINGS")
        print("=" * 60)
        print(f"Codec: {self.config.audio_codec}")
        print(f"Profile: {self.config.audio_profile}")
        print(f"Sample Rate: {self.config.audio_sample_rate} Hz")
        print(f"Channels: {self.config.audio_channels} ({self.config.audio_channel_layout})")
        print(f"Bitrate: {self.config.audio_bitrate}")
        print("=" * 60)
    
    def _get_output_file(self) -> Optional[str]:
        """
        Get output file path from user.
        
        Returns:
            Output file path if valid, None otherwise
        """
        self.display.display_step(self.MESSAGES['step_2'])
        
        output_file = self.input_handler.get_string("Enter output file name", default="video_scaled.mp4")
        
        if os.path.exists(output_file):
            overwrite = self.input_handler.get_confirmation(f"File '{output_file}' exists. Overwrite", default=False)
            if not overwrite:
                return None
        
        return output_file
    
    def _execute_encoding(self, input_file: str, output_file: str) -> bool:
        """
        Execute the actual encoding operation.
        
        Args:
            input_file: Input video file path
            output_file: Output video file path
        
        Returns:
            True if successful, False otherwise
        """
        self.display.display_info("Processing...")
        
        self.keyboard_listener.start_listening()
        #self.keyboard_listener.start_display("Encoding video...")
        self.progress_tracker.start("Encoding video...")
        
        try:
            result = self.processor.scale_and_encode(input_file, output_file, self.video_setting, self.audio_setting)
            
            if result.success:
                self.display.display_success(self.MESSAGES['success_complete'])
                print(f"-> {self.MESSAGES['success_output']}: {output_file}")
                return True
            else:
                self.display.display_error(self.MESSAGES['failed_complete'])
                print(f"-> Error: {result.error_message}")
                return False
        finally:
            self.progress_tracker.stop()
            self.keyboard_listener.stop_listening()
            
            if self.keyboard_listener.should_quit:
                self.display.display_warning(self.MESSAGES['cancelled_by_user'])
                return False
    
    # ========== Menu Selection Helper Methods ==========
    
    def _select_resolution(self, res_type: str) -> Tuple[int, int, str]:
        """Get resolution selection from user"""
        
        presets = (RESOLUTION_PRESETS_DESKTOP if res_type == "desktop" 
                  else RESOLUTION_PRESETS_VR)
        
        print(f"\n{self.MESSAGES['resolution_select']}:")
        for i, (name, specs) in enumerate(presets.items(), 1):
            print(f"  {i}. {name} ({specs['width']}x{specs['height']})")
        print(f"  {len(presets) + 1}. Custom")
        
        choice = self.menu.get_selection("Select resolution", len(presets), allow_custom=True)
        
        preset_list = list(presets.items())
        if choice.isdigit() and 1 <= int(choice) <= len(preset_list):
            name, specs = preset_list[int(choice) - 1]
            return (specs['width'], specs['height'], specs['default_bitrate'])
        elif choice == str(len(presets) + 1):
            width = self.input_handler.get_integer("Enter width", min_val=64, max_val=16384)
            height = self.input_handler.get_integer("Enter height", min_val=64, max_val=16384)
            bitrate = self.input_handler.get_string("Enter bitrate (e.g., 8000k)", required=True)
            return (width, height, bitrate)
        
        return (1920, 1080, "6000k")
    
    def _select_codec(self, codec_type: str, detected: str = None) -> str:
        """
        Get codec selection from user (backward compatible).
        
        Note: For optimized collection, use _select_codec_index instead.
        
        Args:
            codec_type: 'video' or 'audio'
            detected: Detected codec name
        
        Returns:
            Selected codec name
        """
        selected = self._select_codec_index(codec_type, detected)
        
        # If optimization selected, return the detected codec
        # (actual "copy" will be set in _collect_video_settings/_collect_audio_settings)
        if selected == "detected":
            return detected or ("libx264" if codec_type == "video" else "aac")
        
        return selected
    
    def _select_profile(self, detected: str = None) -> str:
        """Get profile selection from user"""
        print(f"\n{self.MESSAGES['profile_select']}:")
        
        for i, profile in enumerate(VIDEO_PROFILE_OPTIONS, 1):
            print(f"  {i}. {profile}")
        
        # Add "copy" option with detected value
        copy_option = len(VIDEO_PROFILE_OPTIONS) + 1
        if detected:
            print(f"  {copy_option}. copy ({detected})")
            print(f"  {copy_option + 1}. Custom")
            max_choice = len(VIDEO_PROFILE_OPTIONS) + 2
        else:
            print(f"  {copy_option}. Custom")
            max_choice = len(VIDEO_PROFILE_OPTIONS) + 1
        
        choice = self.menu.get_selection("Select profile", max_choice, allow_custom=True)
        
        if choice.isdigit():
            choice_int = int(choice)
            
            # User selected "copy"
            if detected and choice_int == copy_option:
                return "copy"
            
            # User selected standard option
            if 1 <= choice_int <= len(VIDEO_PROFILE_OPTIONS):
                return VIDEO_PROFILE_OPTIONS[choice_int - 1]
            
            # User selected custom
            if (detected and choice_int == copy_option + 1) or (not detected and choice_int == copy_option):
                return self.input_handler.get_string("Enter custom profile", required=True)
        
        return "high"

    
    def _select_level(self, detected: str = None) -> str:
        """Get level selection from user"""
        print(f"\n{self.MESSAGES['level_select']}:")
        
        for i, level in enumerate(VIDEO_LEVEL_OPTIONS, 1):
            print(f"  {i}. {level}")
        
        # Add "copy" option with detected value
        copy_option = len(VIDEO_LEVEL_OPTIONS) + 1
        if detected:
            print(f"  {copy_option}. copy ({detected})")
            print(f"  {copy_option + 1}. Custom")
            max_choice = len(VIDEO_LEVEL_OPTIONS) + 2
        else:
            print(f"  {copy_option}. Custom")
            max_choice = len(VIDEO_LEVEL_OPTIONS) + 1
        
        choice = self.menu.get_selection("Select level", max_choice, allow_custom=True)
        
        if choice.isdigit():
            choice_int = int(choice)
            
            # User selected "copy"
            if detected and choice_int == copy_option:
                return "copy"
            
            # User selected standard option
            if 1 <= choice_int <= len(VIDEO_LEVEL_OPTIONS):
                return VIDEO_LEVEL_OPTIONS[choice_int - 1]
            
            # User selected custom
            if (detected and choice_int == copy_option + 1) or (not detected and choice_int == copy_option):
                return self.input_handler.get_string("Enter custom level", required=True)
        
        return "4.1"

    def _select_frame_rate(self, detected: float = None) -> int:
        """Get frame rate selection from user"""
        print(f"\n{self.MESSAGES['frame_rate_select']}:")
        
        for i, fps in enumerate(FRAME_RATE_OPTIONS, 1):
            print(f"  {i}. {fps}")
        
        # Add "copy" option with detected value
        copy_option = len(FRAME_RATE_OPTIONS) + 1
        if detected:
            print(f"  {copy_option}. copy ({detected})")
            print(f"  {copy_option + 1}. Custom")
            max_choice = len(FRAME_RATE_OPTIONS) + 2
        else:
            print(f"  {copy_option}. Custom")
            max_choice = len(FRAME_RATE_OPTIONS) + 1
        
        choice = self.menu.get_selection("Select frame rate", max_choice, allow_custom=True)
        
        if choice.isdigit():
            choice_int = int(choice)
            
            # User selected "copy"
            if detected and choice_int == copy_option:
                return "copy"
            
            # User selected standard option
            if 1 <= choice_int <= len(FRAME_RATE_OPTIONS):
                return int(FRAME_RATE_OPTIONS[choice_int - 1])
            
            # User selected custom
            if (detected and choice_int == copy_option + 1) or (not detected and choice_int == copy_option):
                return self.input_handler.get_integer("Enter custom frame rate", min_val=1)
        
        return 30
    
    def _select_channels(self, detected: int = None) -> Tuple[int, str]:
        """Get channel selection from user"""
        print(f"\n{self.MESSAGES['channels_select']}:")
        
        for key, info in CHANNEL_OPTIONS.items():
            print(f"  {key}. {info['desc']}")
        
        # Add "copy" option with detected value
        if detected:
            print(f"  5. copy ({detected} channels)")
            print("  6. Custom")
            max_choice = "6"
        else:
            print("  5. Custom")
            max_choice = "5"
        
        choice = input(f"\n> Select channels (1-{max_choice}): ").strip()
        
        # User selected "copy"
        if detected and choice == "5":
            return (detected, "copy")
        
        # User selected standard option
        if choice in CHANNEL_OPTIONS:
            cfg = CHANNEL_OPTIONS[choice]
            return (cfg['channels'], cfg['layout'])
        
        # User selected custom
        custom_option = "6" if detected else "5"
        if choice == custom_option:
            ch = self.input_handler.get_integer("Enter channel count", min_val=1)
            layout = self.input_handler.get_string("Enter channel layout", required=True)
            return (ch, layout)
        
        return (2, "stereo")
    
    def _select_video_bitrate(self, detected: str = None, recommended: str = None) -> str:
        """Get video bitrate selection from user"""
        print(f"\n{self.MESSAGES['video_bitrate_select']}:")
        
        print(f"  1. Use recommended bitrate ({recommended})")
        
        # Add "copy" option with detected value
        if detected:
            print(f"  2. copy ({detected})")
            print("  3. Custom")
            max_choice = 3
        else:
            print("  2. Custom")
            max_choice = 2
        
        choice = input(f"\n> Select bitrate (1-{max_choice}): ").strip()
        
        if choice == "1":
            return recommended or "5000k"
        elif detected and choice == "2":
            return "copy"
        elif (detected and choice == "3") or (not detected and choice == "2"):
            return self.input_handler.get_string("Enter custom bitrate (e.g., 8000k)", required=True)
        
        return recommended or "5000k"

    def _select_sample_rate(self, detected: int = None) -> int:
        """
        Get sample rate selection from user.
        
        Offers "copy" option with detected value for faster processing
        when user wants to keep detected sample rate.
        
        Args:
            detected: Detected sample rate in Hz
            
        Returns:
            Sample rate value or "copy" string
        """
        print(f"\n{self.MESSAGES['sample_rate_select']}:")
        
        # Display sample rate options WITHOUT (detected) marker
        for i, sr in enumerate(SAMPLE_RATE_OPTIONS, 1):
            print(f"  {i}. {sr} Hz")
        
        # Add "copy" option with detected value
        copy_option = len(SAMPLE_RATE_OPTIONS) + 1
        if detected:
            print(f"  {copy_option}. copy ({detected} Hz)")
            print(f"  {copy_option + 1}. Custom")
            max_choice = len(SAMPLE_RATE_OPTIONS) + 2
        else:
            print(f"  {copy_option}. Custom")
            max_choice = len(SAMPLE_RATE_OPTIONS) + 1
        
        choice = self.menu.get_selection("Select sample rate", max_choice, allow_custom=True)
        
        if choice.isdigit():
            choice_int = int(choice)
            
            # User selected "copy"
            if detected and choice_int == copy_option:
                return detected
            
            # User selected standard option
            if 1 <= choice_int <= len(SAMPLE_RATE_OPTIONS):
                return SAMPLE_RATE_OPTIONS[choice_int - 1]
            
            # User selected custom
            if (detected and choice_int == copy_option + 1) or (not detected and choice_int == copy_option):
                return self.input_handler.get_integer("Enter custom sample rate (Hz)", min_val=8000)
        
        return 44100

    
    def _select_audio_bitrate(self, detected: str = None, channels: int = 2) -> str:
        """Get audio bitrate selection from user"""
        default_abr = "192k" if channels == 2 else ("96k" if channels == 1 else "384k")
        
        print(f"\n{self.MESSAGES['audio_bitrate_select']}:")
        
        print(f"  1. Use recommended bitrate ({default_abr})")
        
        # Add "copy" option with detected value
        if detected:
            print(f"  2. copy ({detected})")
            print("  3. Custom")
            max_choice = 3
        else:
            print("  2. Custom")
            max_choice = 2
        
        choice = input(f"\n> Select bitrate (1-{max_choice}): ").strip()
        
        if choice == "1":
            return default_abr
        elif detected and choice == "2":
            return "copy"
        elif (detected and choice == "3") or (not detected and choice == "2"):
            return self.input_handler.get_string("Enter custom bitrate (e.g., 192k)", required=True)
        
        return default_abr

