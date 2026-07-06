import os
from collections import defaultdict
from typing import Dict, List, Set, Tuple
try:
    from tqdm import tqdm
except ImportError:
    # Fallback dummy class if tqdm is not installed
    class tqdm:
        def __init__(self, total=None, desc="", unit="", **kwargs):
            self.total = total
            self.desc = desc
            self.n = 0
            if desc:
                print(f"{desc}...", end=" ", flush=True)

        def update(self, n=1):
            self.n += n

        def close(self):
            if self.desc:
                print("Done.")


from core.utils import calculate_md5, calculate_partial_hash

DEFAULT_VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v', 
    '.mpg', '.mpeg', '.3gp', '.rmvb', '.ts', '.vob'
}

class DuplicateFinder:
    """Class to scan and find duplicate video files."""

    def __init__(self, extensions: Set[str] = None):
        self.extensions = extensions if extensions is not None else DEFAULT_VIDEO_EXTENSIONS
        # Convert extensions to lowercase for case-insensitive matching
        self.extensions = {ext.lower() for ext in self.extensions}

    def scan_directory(self, target_dir: str) -> List[str]:
        """Recursively scan a directory for video files.
        
        Args:
            target_dir: The directory to scan.
            
        Returns:
            A list of absolute paths to video files.
        """
        video_files = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in self.extensions:
                    full_path = os.path.abspath(os.path.join(root, file))
                    video_files.append(full_path)
        return video_files

    def find_duplicates(self, target_dirs: List[str], show_progress: bool = True, fast_mode: bool = False) -> List[Dict]:
        """Find duplicate video files across specified directories.
        
        Uses a multi-stage filtering algorithm:
        1. Group by file size.
        2. Group by partial hash (head + tail of file) for files with the same size.
        3. (Optional) Group by full MD5 hash for files with the same size and partial hash.
        
        Args:
            target_dirs: List of directories to scan.
            show_progress: Whether to show progress bars using tqdm.
            fast_mode: If True, skips full MD5 calculation (Phase 2/2) and assumes
                       files are duplicate if size and head/tail hashes match.
                       This is much faster but slightly less accurate.
            
        Returns:
            A list of duplicate groups, where each group is a dict containing:
            - 'hash': The hash (full MD5 or quick partial hash) of the duplicate files.
            - 'size': The size of each file in bytes.
            - 'paths': List of absolute paths of duplicate files.
        """
        # Step 1: Scan all directories and collect video files
        all_files: Set[str] = set()
        for directory in target_dirs:
            if not os.path.isdir(directory):
                continue
            scanned = self.scan_directory(directory)
            all_files.update(scanned)

        if not all_files:
            return []

        # Step 2: Group files by size
        size_groups = defaultdict(list)
        for filepath in all_files:
            try:
                size = os.path.getsize(filepath)
                # Ignore zero-byte files
                if size > 0:
                    size_groups[size].append(filepath)
            except OSError:
                # Handle permission errors or broken symlinks
                continue

        # Filter out sizes that only have one file
        candidate_sizes = {size: files for size, files in size_groups.items() if len(files) > 1}
        if not candidate_sizes:
            return []

        # Calculate total files to process in next stages for progress bar
        total_size_candidates = sum(len(files) for files in candidate_sizes.values())
        
        # Step 3: Compute partial hashes for candidate files
        partial_hash_groups = defaultdict(list)
        
        pbar_desc = "Phase 1/2: Quick hashing" if not fast_mode else "Scanning: Quick hashing"
        if show_progress:
            pbar = tqdm(total=total_size_candidates, desc=pbar_desc, unit="file")
        else:
            pbar = None

        for size, files in candidate_sizes.items():
            for filepath in files:
                try:
                    p_hash = calculate_partial_hash(filepath)
                    # Key by (size, partial_hash) to avoid collision between files of different sizes
                    partial_hash_groups[(size, p_hash)].append(filepath)
                except OSError:
                    pass
                finally:
                    if pbar:
                        pbar.update(1)
        if pbar:
            pbar.close()

        # Filter out groups that only have one file
        candidate_partials = {key: files for key, files in partial_hash_groups.items() if len(files) > 1}
        if not candidate_partials:
            return []

        # Step 4: Compute full MD5 hashes or bypass if fast_mode is enabled
        duplicates = []

        if fast_mode:
            # Skip Phase 2, use partial hash results directly
            for (size, p_hash), files in candidate_partials.items():
                if len(files) > 1:
                    files.sort()
                    duplicates.append({
                        'hash': f"quick_{p_hash}",
                        'size': size,
                        'paths': files
                    })
        else:
            # Full Verification Mode
            total_full_candidates = sum(len(files) for files in candidate_partials.values())
            full_hash_groups = defaultdict(list)

            pbar_desc = "Phase 2/2: Full verification"
            if show_progress:
                pbar = tqdm(total=total_full_candidates, desc=pbar_desc, unit="file")
            else:
                pbar = None

            for (size, p_hash), files in candidate_partials.items():
                for filepath in files:
                    try:
                        f_hash = calculate_md5(filepath)
                        # Key by (size, full_hash) just to be absolutely safe
                        full_hash_groups[(size, f_hash)].append(filepath)
                    except OSError:
                        pass
                    finally:
                        if pbar:
                            pbar.update(1)
            if pbar:
                pbar.close()

            # Format and return the final duplicate groups
            for (size, f_hash), files in full_hash_groups.items():
                if len(files) > 1:
                    # Sort paths to keep the output deterministic and clean
                    files.sort()
                    duplicates.append({
                        'hash': f_hash,
                        'size': size,
                        'paths': files
                    })
        
        # Sort duplicate groups by file size descending
        duplicates.sort(key=lambda x: x['size'], reverse=True)
        return duplicates

