import subprocess
import os
from io import BytesIO
from PIL import Image

FFPROBE_PATH = "ffprobe"
FFMPEG_PATH = "ffmpeg"

def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe.
    
    Args:
        video_path: Path to the video file.
        
    Returns:
        Duration of the video in seconds, or 0.0 if failed.
    """
    cmd = [
        FFPROBE_PATH,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        return float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError, FileNotFoundError, subprocess.TimeoutExpired):
        return 0.0

def extract_video_frame(video_path: str, timestamp_sec: float) -> Image.Image:
    """Extract a single frame from a video at the given timestamp using ffmpeg.
    
    Uses ffmpeg fast seek (-ss before -i) to efficiently grab a frame without
    decoding the entire video from the start.
    
    Args:
        video_path: Path to the video file.
        timestamp_sec: Position in seconds to extract the frame.
        
    Returns:
        A PIL Image object, or None if extraction failed.
    """
    cmd = [
        FFMPEG_PATH,
        "-ss", f"{timestamp_sec:.3f}",
        "-y",
        "-i", video_path,
        "-vframes", "1",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-"
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        if result.returncode != 0:
            return None
        
        img_bytes = result.stdout
        if not img_bytes:
            return None
            
        # Pillow loads lazily, so we force-load it in memory using .load()
        # to ensure it's fully read before returning and closing the stream.
        img = Image.open(BytesIO(img_bytes))
        img.load()
        return img
    except (subprocess.SubprocessError, FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None
