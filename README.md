# File Path Record and Movement Log

A two-script toolkit for documenting folder structures and file movement history as static, shareable HTML — no runtime dependencies needed to view the output.

---

## Scripts Overview

### 1. `treeplot1.py` — Path & File Tree Reader

Reads all specified file paths and directories, then outputs a structured tree representation of the file system layout.

**What it does:**
- Accepts a list of hardcoded root paths to scan
- Recursively walks each path and collects all files and folders
- Outputs a visual tree structure (similar to the Unix `tree` command)
- Serves as the data source / discovery layer for `generate_tree_html.py`

**Usage:**
```bash
python treeplot1.py
```

> Paths are hardcoded inside the script. Edit the `PATHS` list at the top of the file to point to your target directories before running.

**Output:** Prints the tree to stdout. Pipe or redirect as needed:
```bash
python treeplot1.py > tree_output.txt
```

---

### 2. `generate_tree_html.py` — Static HTML Movement Log Generator

Generates a standalone, self-contained `.html` file that displays:
- The full folder/file tree structure
- A file movement log (source → destination records)

**Key design principle — no runtime required to view:**  
All paths and movement records are **hardcoded** directly into the script. The output `.html` file is fully self-contained and can be opened in any browser without running a server, installing dependencies, or executing any code.

**What it does:**
- Reads hardcoded path definitions and movement log entries within the script
- Generates a styled HTML page embedding the tree and movement history
- Writes the output to a `.html` file that anyone can double-click and open

**Usage:**
```bash
python generate_tree_html.py
```

This produces an `output.html` (or similarly named file) in the current directory.

**To update paths or movement records:**  
Open `generate_tree_html.py` and edit the hardcoded variables near the top of the file:
```python
# --- CONFIGURE THESE ---
ROOT_PATHS = [
    "C:/Projects/MyApp",
    "D:/Archives/2024",
]

MOVEMENT_LOG = [
    {"date": "2024-01-15", "file": "report.xlsx", "from": "D:/Archives/2024", "to": "C:/Projects/MyApp/reports"},
    # add more entries here
]
```

---

## Workflow

```
treeplot1.py          →    Discover & verify paths/files exist
      ↓
generate_tree_html.py →    Encode paths + movement log → output.html
      ↓
output.html           →    Share / open in any browser, no dependencies
```

---

## File Movement Log — What to Check

Before distributing the generated HTML, verify the movement log is accurate:

| Check | Description |
|---|---|
| **Source paths exist** | Confirm `from` paths in the log were real locations |
| **Destination paths correct** | Confirm `to` paths reflect where files actually landed |
| **Dates accurate** | Timestamps match actual move/copy operations |
| **No duplicates** | Each file entry appears once unless intentionally copied to multiple destinations |
| **Deleted files noted** | Files removed (not moved) should be flagged separately |

Run `treeplot1.py` first to cross-reference which files are currently present against what the movement log records — discrepancies indicate files that were moved but not yet logged, or logged but not yet moved.

---

## Output File

| File | Description |
|---|---|
| `output.html` | Self-contained HTML — open in any browser |

No installation required to **view** the output. Python 3.x is required only to **regenerate** it.

---

## Requirements

- Python 3.7+
- No external libraries (standard library only)
