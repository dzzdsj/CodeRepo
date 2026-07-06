import hashlib
import os

def calculate_md5(file_path: str, block_size: int = 65536) -> str:
    """Calculate the full MD5 hash of a file.
    
    Args:
        file_path: Absolute path to the file.
        block_size: Buffer size for reading the file.
        
    Returns:
        The MD5 hex digest string.
    """
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

def calculate_partial_hash(file_path: str, sample_size: int = 65536) -> str:
    """Calculate a quick hash based on the head and tail of the file.
    
    This is useful for quickly filtering out non-duplicate files of the same size
    without reading the entire file.
    
    Args:
        file_path: Absolute path to the file.
        sample_size: Number of bytes to read from head and tail.
        
    Returns:
        A hash string representing the head and tail of the file.
    """
    file_size = os.path.getsize(file_path)
    md5 = hashlib.md5()
    
    with open(file_path, 'rb') as f:
        if file_size <= sample_size * 2:
            # File is small, read the entire file
            md5.update(f.read())
        else:
            # Read head
            md5.update(f.read(sample_size))
            # Read tail
            f.seek(file_size - sample_size)
            md5.update(f.read(sample_size))
            
    # Include file size in the hash to prevent collisions where head/tail are same
    # but sizes are different (though sizes are checked beforehand anyway)
    md5.update(str(file_size).encode('utf-8'))
    return md5.hexdigest()

def format_size(size_in_bytes: int) -> str:
    """Convert bytes to human-readable size string.
    
    Args:
        size_in_bytes: Size in bytes.
        
    Returns:
        Formatted string (e.g., '1.25 GB').
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"
