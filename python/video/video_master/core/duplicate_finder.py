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
from core.video_info import get_video_duration, extract_video_frame
from core.visual_hash import calculate_dhash, hamming_distance

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

    def find_duplicates(self, target_dirs: List[str], show_progress: bool = True, fast_mode: bool = False, visual_mode: bool = False) -> List[Dict]:
        """Find duplicate video files across specified directories.
        
        Supports two major modes:
        1. Byte-based matching (default): fast and exact byte-level matching.
        2. Visual-based matching (visual_mode=True): scans frame contents (useful if 
           videos have different names, resolutions, or appended/prepended ads).
           
        Args:
            target_dirs: List of directories to scan.
            show_progress: Whether to show progress bars using tqdm.
            fast_mode: (Byte mode only) If True, skips full MD5 calculation (Phase 2/2) 
                       and assumes files are duplicate if size and head/tail hashes match.
            visual_mode: If True, uses visual fingerprinting (dHash) to match video contents.
            
        Returns:
            A list of duplicate groups, where each group is a dict containing:
            - 'hash': The hash of the duplicate files.
            - 'size': The representative size of each file in bytes.
            - 'paths': List of absolute paths of duplicate files.
        """
        if visual_mode:
            return self._find_visual_duplicates(target_dirs, show_progress)
        else:
            return self._find_byte_duplicates(target_dirs, show_progress, fast_mode)

    def _find_byte_duplicates(self, target_dirs: List[str], show_progress: bool, fast_mode: bool) -> List[Dict]:
        """Core logic for byte-based exact/fast duplicate detection."""
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
                if size > 0:
                    size_groups[size].append(filepath)
            except OSError:
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
            for (size, p_hash), files in candidate_partials.items():
                if len(files) > 1:
                    files.sort()
                    duplicates.append({
                        'hash': f"quick_{p_hash}",
                        'size': size,
                        'paths': files
                    })
        else:
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
                    files.sort()
                    duplicates.append({
                        'hash': f_hash,
                        'size': size,
                        'paths': files
                    })
        
        duplicates.sort(key=lambda x: x['size'], reverse=True)
        return duplicates

    def _find_visual_duplicates(self, target_dirs: List[str], show_progress: bool) -> List[Dict]:
        """Core logic for content-aware visual duplicate detection (using ffmpeg + dHash)."""
        # Step 1: Scan all directories and collect video files
        all_files: Set[str] = set()
        for directory in target_dirs:
            if not os.path.isdir(directory):
                continue
            scanned = self.scan_directory(directory)
            all_files.update(scanned)

        if not all_files:
            return []

        # Step 2: Extract duration and compute dHash for each file
        video_metadata_list = []
        
        pbar_desc = "Extracting video fingerprints"
        if show_progress:
            pbar = tqdm(total=len(all_files), desc=pbar_desc, unit="file")
        else:
            pbar = None

        for filepath in all_files:
            try:
                duration = get_video_duration(filepath)
                size = os.path.getsize(filepath)
                
                # Ignore extremely short videos (e.g. < 2 seconds)
                if duration < 2.0:
                    if pbar:
                        pbar.update(1)
                    continue
                
                # Determine absolute sampling parameters
                # Long videos (duration >= 15s): start at 10s, step 5s, up to 24 frames
                # Short videos (duration < 15s): start at 2s, step 2s, up to 10 frames
                if duration >= 15.0:
                    start_sec = 10.0
                    step_sec = 5.0
                    max_frames = 24
                else:
                    start_sec = 2.0
                    step_sec = 2.0
                    max_frames = 10
                
                timestamps = [start_sec + i * step_sec for i in range(max_frames)]
                timestamps = [ts for ts in timestamps if ts < duration - (step_sec / 2.0)]
                
                hashes = []
                for ts in timestamps:
                    frame = extract_video_frame(filepath, ts)
                    if frame:
                        h = calculate_dhash(frame)
                        hashes.append(h)
                    else:
                        hashes.append("")
                
                # Only keep files that have at least some fingerprints successfully extracted
                if any(hashes):
                    video_metadata_list.append({
                        'path': filepath,
                        'size': size,
                        'duration': duration,
                        'hashes': hashes
                    })
            except Exception:
                pass
            finally:
                if pbar:
                    pbar.update(1)
        if pbar:
            pbar.close()

        if not video_metadata_list:
            return []

        # Step 3: Match videos based on duration proximity and dHash Hamming distance
        visited: Set[str] = set()
        duplicates = []
        
        # Sort by duration to optimize pair comparisons
        video_metadata_list.sort(key=lambda x: x['duration'])
        
        for i, video_a in enumerate(video_metadata_list):
            if video_a['path'] in visited:
                continue
                
            group = [video_a['path']]
            
            for j in range(i + 1, len(video_metadata_list)):
                video_b = video_metadata_list[j]
                if video_b['path'] in visited:
                    continue
                
                # Check if duration difference is within bounds (e.g., max 45s difference or 25% of duration)
                # This allows matching videos even with prepended/appended ads or slight editing
                dur_diff = abs(video_a['duration'] - video_b['duration'])
                max_allowed_diff = max(45.0, 0.25 * min(video_a['duration'], video_b['duration']))
                
                if dur_diff <= max_allowed_diff:
                    # Perform visual similarity comparison using sliding window alignment
                    if self._is_visual_match(video_a, video_b):
                        group.append(video_b['path'])
                        visited.add(video_b['path'])
                        
            if len(group) > 1:
                visited.add(video_a['path'])
                group.sort()
                
                # Get the middle frame's hash as the representative hash
                repr_hash = video_a['hashes'][len(video_a['hashes']) // 2] if video_a['hashes'] else "visual"
                
                duplicates.append({
                    'hash': f"visual_{repr_hash}",
                    'size': os.path.getsize(group[0]),
                    'paths': group
                })

        # Sort duplicate groups by size descending
        duplicates.sort(key=lambda x: x['size'], reverse=True)
        return duplicates

    def _is_visual_match(self, video_a: Dict, video_b: Dict, threshold: int = 4) -> bool:
        """Compare hashes of two videos using a sliding window alignment.
        
        This aligns sequences of hashes to handle temporal shifts (e.g. prepended ads).
        """
        # If they fall into different duration categories (long vs short), they don't match
        is_a_long = video_a['duration'] >= 15.0
        is_b_long = video_b['duration'] >= 15.0
        if is_a_long != is_b_long:
            return False
            
        hashes_a = video_a['hashes']
        hashes_b = video_b['hashes']
        
        len_a = len(hashes_a)
        len_b = len(hashes_b)
        
        if len_a < 3 or len_b < 3:
            return False
            
        # We slide hashes_b relative to hashes_a.
        # Max shift is capped (e.g. max 12 steps, which corresponds to 60s for 5s step, or 24s for 2s step)
        max_shift = min(12, max(len_a, len_b) - 2)
        if max_shift < 0:
            max_shift = 0
            
        best_match_count = 0
        best_match_ratio = 0.0
        best_overlap_len = 0
        
        for shift in range(-max_shift, max_shift + 1):
            overlap_a_start = max(0, -shift)
            overlap_a_end = min(len_a, len_b - shift)
            
            overlap_len = overlap_a_end - overlap_a_start
            if overlap_len < 3:
                continue
                
            match_count = 0
            for idx_a in range(overlap_a_start, overlap_a_end):
                idx_b = idx_a + shift
                h_a = hashes_a[idx_a]
                h_b = hashes_b[idx_b]
                if h_a and h_b:
                    dist = hamming_distance(h_a, h_b)
                    if dist <= threshold:
                        match_count += 1
                        
            ratio = match_count / overlap_len
            if match_count > best_match_count or (match_count == best_match_count and ratio > best_match_ratio):
                best_match_count = match_count
                best_match_ratio = ratio
                best_overlap_len = overlap_len
                
        # Define match criteria based on overlapping length
        if best_overlap_len >= 5:
            # At least 4 matched frames AND at least 65% matching ratio
            return best_match_count >= 4 and best_match_ratio >= 0.65
        else:
            # For short overlaps (3 or 4 frames), we require at least 3 matches AND 75% ratio
            return best_match_count >= 3 and best_match_ratio >= 0.75
