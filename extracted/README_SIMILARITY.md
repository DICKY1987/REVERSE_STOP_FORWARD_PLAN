# File Similarity Comparison

This directory contains a script to compare file contents and identify files with high similarity.

## Overview

The `compare_file_similarity.py` script analyzes all text files in the current directory and subdirectories, comparing each pair of files to identify those with 90% or more similar content.

## Usage

### Basic Usage

Run the script from the extracted directory:

```bash
cd extracted
python3 compare_file_similarity.py
```

The script will:
1. Scan all text files in the directory recursively
2. Compare each pair of files using sequence matching
3. Display results showing files with 90% or more similarity

### Output

The script outputs:
- Number of files scanned
- Progress indicator during comparison
- List of file pairs with 90%+ similarity
- Similarity percentage for each pair

### Features

- **Smart File Detection**: Automatically identifies text files vs binary files
- **Efficient Comparison**: Uses Python's `difflib.SequenceMatcher` for accurate similarity calculation
- **Recursive Scanning**: Searches all subdirectories
- **Progress Indicator**: Shows comparison progress for large directories
- **Exclusions**: Automatically excludes common directories like `.git`, `__pycache__`, `node_modules`, etc.

## Results for This Directory

Last run results are saved in `similarity_report.txt`.

**Summary of findings:**
- **Total text files scanned**: Varies based on files present (typically 90+)
- **Files with 90%+ similarity**: 1 pair

**Identified similar files:**
- `spec_project/tests/acceptance/user_creates_order.feature` and `order_research/tests/acceptance/user_creates_order.feature` (100.00% identical)

## Technical Details

### Similarity Algorithm

The script uses Python's `difflib.SequenceMatcher` which:
- Compares files character by character
- Returns a similarity ratio between 0.0 (completely different) and 1.0 (identical)
- Uses the Ratcliff/Obershelp algorithm for pattern matching

### File Type Detection

Text files are identified by:
1. MIME type detection
2. Common text file extensions (`.py`, `.txt`, `.md`, `.json`, etc.)
3. Fallback text read test

### Performance

- Comparison complexity: O(n²) where n is the number of files
- Memory usage: Reads two files at a time, memory-efficient for large directories
- Progress indicators adapt to terminal vs. non-terminal output

## Customization

To modify the similarity threshold, edit the script or use it as a module:

```python
from compare_file_similarity import compare_files
from pathlib import Path

# Use 80% threshold instead of 90%
similar_pairs = compare_files(Path.cwd(), similarity_threshold=0.80)
```

## Requirements

- Python 3.6 or higher
- Standard library only (no external dependencies)
