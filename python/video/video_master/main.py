import argparse
import json
import os
import sys
from typing import List, Dict

from core.duplicate_finder import DuplicateFinder
from core.utils import format_size

def print_banner():
    banner = """
==================================================
        Video Organizer & Duplicate Finder
==================================================
"""
    print(banner)

def report_duplicates(duplicates: List[Dict], output_json: str = None):
    """Print a clean, structured report of duplicates."""
    if not duplicates:
        print("🎉 No duplicate video files found.")
        return

    print(f"🔍 Found {len(duplicates)} groups of duplicate videos:\n")
    
    total_wasted_space = 0
    
    for idx, group in enumerate(duplicates, 1):
        size_str = format_size(group['size'])
        paths = group['paths']
        wasted_for_group = group['size'] * (len(paths) - 1)
        total_wasted_space += wasted_for_group
        
        print(f"Group #{idx} (Size: {size_str}, MD5: {group['hash']}):")
        for p in paths:
            print(f"  - {p}")
        print()

    print("=" * 50)
    print(f"Total potential space savings: {format_size(total_wasted_space)}")
    print("=" * 50)

    if output_json:
        try:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(duplicates, f, indent=4, ensure_ascii=False)
            print(f"\n📝 Detailed report saved to: {output_json}")
        except OSError as e:
            print(f"\n❌ Failed to save JSON report: {e}")

def handle_deletions_interactive(duplicates: List[Dict]):
    """Interactively ask the user which files to delete in each duplicate group."""
    print("\n🗑️  Entering interactive deletion mode...")
    print("For each duplicate group, you can select which file to KEEP.")
    print("The rest of the files in that group will be deleted. Press Enter to skip a group.\n")

    for idx, group in enumerate(duplicates, 1):
        size_str = format_size(group['size'])
        paths = group['paths']
        
        print(f"Group #{idx} (Size: {size_str}):")
        for i, path in enumerate(paths, 1):
            print(f"  [{i}] {path}")
            
        try:
            choice_str = input(f"Select the file index to KEEP (1-{len(paths)}) or press Enter to skip: ").strip()
            if not choice_str:
                print("Skipped group.\n")
                continue
                
            choice = int(choice_str)
            if 1 <= choice <= len(paths):
                keep_idx = choice - 1
                keep_path = paths[keep_idx]
                
                for i, path in enumerate(paths):
                    if i != keep_idx:
                        try:
                            os.remove(path)
                            print(f"  Deleted: {path}")
                        except OSError as e:
                            print(f"  ❌ Error deleting {path}: {e}")
                print(f"  Kept: {keep_path}\n")
            else:
                print("⚠️ Invalid choice. Skipped group.\n")
        except ValueError:
            print("⚠️ Invalid choice. Skipped group.\n")
        except KeyboardInterrupt:
            print("\nAborted deletion process.")
            break

def handle_deletions_keep_first(duplicates: List[Dict]):
    """Automatically keep the first file in each group, and delete the rest (with confirmation)."""
    total_files_to_delete = sum(len(group['paths']) - 1 for group in duplicates)
    total_wasted_space = sum(group['size'] * (len(group['paths']) - 1) for group in duplicates)
    
    print(f"\n⚠️  WARNING: You are about to automatically delete {total_files_to_delete} duplicate files.")
    print(f"This will reclaim {format_size(total_wasted_space)} of space.")
    print("In each group, the FIRST file listed will be KEPT, and all other duplicates will be deleted.")
    
    confirm = input("Are you absolutely sure you want to proceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Operation cancelled.")
        return

    print("\nStarting automatic deletion...")
    for group in duplicates:
        paths = group['paths']
        keep_path = paths[0]
        print(f"Keeping: {keep_path}")
        for path in paths[1:]:
            try:
                os.remove(path)
                print(f"  Deleted: {path}")
            except OSError as e:
                print(f"  ❌ Error deleting {path}: {e}")
        print()
    print("Automatic deletion complete.")

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Find duplicate video files in local directories.")
    parser.add_argument(
        '-d', '--dir', 
        nargs='+', 
        default=['.'], 
        help="One or more directories to scan (default: current directory)"
    )
    parser.add_argument(
        '--json', 
        type=str, 
        help="Path to save duplicate report as a JSON file"
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help="Fast mode: skip full MD5 verification (uses size + head/tail hash only)"
    )
    parser.add_argument(
        '--visual',
        action='store_true',
        help="Visual mode: find duplicates by visual content (handles watermark, ads, transcoding)"
    )
    
    # Exclusivity group for deletion strategy
    delete_group = parser.add_mutually_exclusive_group()
    delete_group.add_argument(
        '--delete-interactive', 
        action='store_true', 
        help="Interactively select which files to keep/delete"
    )
    delete_group.add_argument(
        '--delete-keep-first', 
        action='store_true', 
        help="Automatically keep the first file in each group and delete the rest"
    )
    
    args = parser.parse_args()
    
    # Resolve absolute paths of target directories
    target_dirs = [os.path.abspath(d) for d in args.dir]
    
    print(f"Scanning directories: {', '.join(target_dirs)}")
    if args.visual:
        print("👁️  Visual mode active: using dHash + ffmpeg to identify content duplicates.")
    elif args.fast:
        print("⚡ Fast mode active: skipping full MD5 verification.")
    
    finder = DuplicateFinder()
    duplicates = finder.find_duplicates(
        target_dirs, 
        show_progress=True, 
        fast_mode=args.fast,
        visual_mode=args.visual
    )
    
    report_duplicates(duplicates, output_json=args.json)
    
    if duplicates:
        if args.delete_interactive:
            handle_deletions_interactive(duplicates)
        elif args.delete_keep_first:
            handle_deletions_keep_first(duplicates)
        else:
            print("\n💡 Tip: Run with --delete-interactive to clean up duplicates.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
