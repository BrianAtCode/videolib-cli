"""
Command implementations for CLI
"""
from typing import Dict, Any, List
import videolib

class CLICommands:
    """CLI command implementations"""
    
    def __init__(self, processor: videolib.VideoProcessor):
        self.processor = processor
    
    def download_video(self, url: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Download video command"""
        result = self.processor.download_video(url, output_path, **kwargs)
        return {
            'success': result.success,
            'output_file': result.output_file,
            'error': result.error_message,
            'file_size': result.file_size
        }
    
    def split_video(self, source_file: str, output_name: str, max_size: str, **kwargs) -> Dict[str, Any]:
        """Split video command"""
        result = self.processor.split_video_by_size(source_file, output_name, max_size, **kwargs)
        return {
            'success': result.success,
            'output_files': result.output_files,
            'oversized_files': result.oversized_files,
            'error': result.error_message
        }
    
    def create_clips(self, source_file: str, output_name: str, intervals: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Create clips command"""
        result = self.processor.create_clips(source_file, output_name, intervals, **kwargs)
        return {
            'success': result.success,
            'output_files': result.output_files,
            'failed_clips': result.failed_clips,
            'error': result.error_message
        }
    
    def process_batch(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process batch command"""
        return self.processor.process_batch(tasks)
    
    def get_media_info(self, file_path: str) -> Dict[str, Any]:
        """Get media info command"""
        media_info = self.processor.get_media_info(file_path)
        
        if not media_info:
            return {'success': False, 'error': 'Could not get media information'}
        
        return {
            'success': True,
            'duration': media_info.duration,
            'video_codec': media_info.video_codec,
            'audio_codec': media_info.audio_codec,
            'format': media_info.format_name,
            'size_bytes': media_info.size_bytes,
            'width': media_info.width,
            'height': media_info.height,
            'bitrate': media_info.bitrate
        }
