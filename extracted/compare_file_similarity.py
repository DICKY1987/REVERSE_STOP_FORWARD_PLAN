#!/usr/bin/env python3
"""
File Similarity Comparator

Compares all files in the current directory and subdirectories to identify
files with 90% or more similar content.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Set
from difflib import SequenceMatcher
import mimetypes


def is_text_file(file_path: Path) -> bool:
    """
    Check if a file is likely a text file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file appears to be text, False otherwise
    """
    # Check by extension first
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith('text'):
        return True
    
    # Check common text extensions
    text_extensions = {
        '.py', '.txt', '.md', '.json', '.yaml', '.yml', '.xml', '.html',
        '.css', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
        '.sh', '.bash', '.ps1', '.csv', '.sql', '.go', '.rs', '.rb',
        '.php', '.pl', '.swift', '.kt', '.scala', '.r', '.m', '.lua',
        '.vim', '.ini', '.cfg', '.conf', '.toml', '.feature'
    }
    
    if file_path.suffix.lower() in text_extensions:
        return True
    
    # Try to read as text
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Try to read first 1KB
        return True
    except (UnicodeDecodeError, PermissionError):
        return False


def calculate_similarity(file1_path: Path, file2_path: Path) -> float:
    """
    Calculate similarity between two files.
    
    Args:
        file1_path: Path to first file
        file2_path: Path to second file
        
    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    try:
        with open(file1_path, 'r', encoding='utf-8', errors='ignore') as f1:
            content1 = f1.read()
        
        with open(file2_path, 'r', encoding='utf-8', errors='ignore') as f2:
            content2 = f2.read()
        
        # Use SequenceMatcher to calculate similarity
        similarity = SequenceMatcher(None, content1, content2).ratio()
        return similarity
        
    except Exception as e:
        print(f"Error comparing {file1_path} and {file2_path}: {e}", file=sys.stderr)
        return 0.0


def get_all_files(root_dir: Path, exclude_dirs: Set[str] = None) -> List[Path]:
    """
    Get all text files in the directory recursively.
    
    Args:
        root_dir: Root directory to search
        exclude_dirs: Set of directory names to exclude
        
    Returns:
        List of file paths
    """
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 
                       '.venv', 'venv', 'dist', 'build', '.tox'}
    
    files = []
    
    for item in root_dir.rglob('*'):
        # Skip if in excluded directory
        if any(excluded in item.parts for excluded in exclude_dirs):
            continue
        
        # Only process files
        if item.is_file():
            # Check if it's a text file
            if is_text_file(item):
                files.append(item)
    
    return files


def compare_files(root_dir: Path, similarity_threshold: float = 0.90) -> List[Tuple[Path, Path, float]]:
    """
    Compare all files in the directory and find similar pairs.
    
    Args:
        root_dir: Root directory to search
        similarity_threshold: Minimum similarity ratio to report
        
    Returns:
        List of tuples (file1, file2, similarity_ratio) for similar files
    """
    print(f"Scanning files in {root_dir}...")
    files = get_all_files(root_dir)
    print(f"Found {len(files)} text files to compare")
    
    similar_pairs = []
    total_comparisons = len(files) * (len(files) - 1) // 2
    comparisons_done = 0
    
    print(f"\nComparing files (total comparisons: {total_comparisons})...")
    
    # Compare each pair of files
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            comparisons_done += 1
            
            # Progress indicator
            if comparisons_done % 100 == 0 or comparisons_done == total_comparisons:
                if sys.stdout.isatty():
                    print(f"Progress: {comparisons_done}/{total_comparisons} comparisons", end='\r')
                    sys.stdout.flush()
                else:
                    # For non-interactive output, print periodic updates
                    if comparisons_done % 1000 == 0 or comparisons_done == total_comparisons:
                        print(f"Progress: {comparisons_done}/{total_comparisons} comparisons")
            
            file1 = files[i]
            file2 = files[j]
            
            similarity = calculate_similarity(file1, file2)
            
            if similarity >= similarity_threshold:
                similar_pairs.append((file1, file2, similarity))
    
    print()  # New line after progress
    return similar_pairs


def main():
    """Main function to run the file similarity comparison."""
    # Get the directory to scan (current directory by default)
    root_dir = Path(__file__).parent.resolve()
    
    print("=" * 80)
    print("File Similarity Comparator")
    print("=" * 80)
    print(f"Searching for files with 90% or more similar content")
    print(f"Root directory: {root_dir}")
    print("=" * 80)
    print()
    
    # Find similar files
    similar_pairs = compare_files(root_dir, similarity_threshold=0.90)
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if not similar_pairs:
        print("\nNo files with 90% or more similarity found.")
    else:
        print(f"\nFound {len(similar_pairs)} pair(s) of files with 90% or more similarity:\n")
        
        for file1, file2, similarity in sorted(similar_pairs, key=lambda x: x[2], reverse=True):
            # Get relative paths from root
            try:
                rel_path1 = file1.relative_to(root_dir)
                rel_path2 = file2.relative_to(root_dir)
            except ValueError:
                rel_path1 = file1
                rel_path2 = file2
            
            print(f"Similarity: {similarity * 100:.2f}%")
            print(f"  File 1: {rel_path1}")
            print(f"  File 2: {rel_path2}")
            print()
    
    print("=" * 80)
    print("Comparison complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
