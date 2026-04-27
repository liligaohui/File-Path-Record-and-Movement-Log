from __future__ import annotations

import csv
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent.resolve()

DEFAULT_OLD_CSV = SCRIPT_DIR / "original_hierarchy.csv"
DEFAULT_NEW_CSV = SCRIPT_DIR / "test_updated_hierarchy3.csv"
OUTPUT_HTML = SCRIPT_DIR / "alltest_Folder_Structure_Viewer3.html"

# --- HTML Template ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Folder Structure Viewer</title>
    <style>
        :root {
            --bg-color: #f8f9fa;
            --sidebar-width: 450px;
            --border-color: #dee2e6;
            --primary-color: #0d6efd;
            --hover-color: #e9ecef;
            --selected-color: #cfe2ff;
            --row-height: 28px;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        body {
            margin: 0;
            font-family: var(--font-family);
            display: flex;
            height: 100vh;
            overflow: hidden;
            font-size: 14px;
            color: #212529;
        }

        #main-container {
            display: flex;
            flex: 1;
            height: 100%;
            width: 100%;
        }

        #tree-pane {
            flex: 0 0 var(--sidebar-width);
            display: flex;
            flex-direction: column;
            border-right: 1px solid var(--border-color);
            background: white;
            resize: horizontal;
            overflow: hidden;
            min-width: 200px;
            max-width: 80%;
        }

        #detail-pane {
            flex: 1;
            padding: 40px;
            background: var(--bg-color);
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        #toolbar {
            padding: 10px;
            border-bottom: 1px solid var(--border-color);
            background: #f1f3f5;
            display: flex;
            gap: 8px;
        }

        #search-box {
            flex: 1;
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            outline: none;
        }

        #search-box:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(13,110,253,.25);
        }

        #virtual-scroller {
            flex: 1;
            overflow-y: auto;
            overflow-x: auto;
            position: relative;
            will-change: transform;
        }

        #scroll-content {
            position: relative;
        }

        .tree-row {
            position: absolute;
            left: 0;
            right: 0;
            height: var(--row-height);
            display: flex;
            align-items: center;
            cursor: pointer;
            box-sizing: border-box;
            white-space: nowrap;
            padding-right: 10px;
            user-select: none;
        }

        .tree-row:hover {
            background-color: var(--hover-color);
        }

        .tree-row.selected {
            background-color: var(--selected-color);
        }

        .row-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            margin-right: 5px;
            color: #6c757d;
        }

        .row-expander {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            cursor: pointer;
            color: #495057;
            font-weight: bold;
        }

        .row-expander:hover {
            color: black;
        }

        .row-text {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .icon-folder { fill: #FFC107; }
        .icon-file { fill: #6c757d; }

        .info-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        h2 {
            margin-top: 0;
            color: #343a40;
            font-weight: 600;
        }

        .field-group {
            margin-bottom: 20px;
        }

        .field-label {
            display: block;
            font-size: 12px;
            font-weight: 700;
            color: #6c757d;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .field-value {
            font-family: "Consolas", "Monaco", monospace;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
            word-break: break-all;
            font-size: 13px;
            line-height: 1.5;
        }

        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            color: white;
            background-color: #6c757d;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: white;
            border: 1px solid #ced4da;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        }

        .btn:hover {
            background: #e9ecef;
            border-color: #adb5bd;
        }

        .btn:active {
            transform: translateY(1px);
        }

        #toast {
            visibility: hidden;
            min-width: 250px;
            background-color: #323232;
            color: #fff;
            text-align: center;
            border-radius: 4px;
            padding: 12px 24px;
            position: fixed;
            z-index: 999;
            left: 50%;
            bottom: 30px;
            transform: translateX(-50%);
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        #toast.show {
            visibility: visible;
            animation: fadein 0.5s, fadeout 0.5s 2.5s;
        }

        @keyframes fadein {
            from { bottom: 0; opacity: 0; }
            to { bottom: 30px; opacity: 1; }
        }

        @keyframes fadeout {
            from { bottom: 30px; opacity: 1; }
            to { bottom: 0; opacity: 0; }
        }
    </style>
</head>
<body>

<div id="main-container">
    <div id="tree-pane">
        <div id="toolbar">
            <input type="text" id="search-box" placeholder="Search files and folders...">
        </div>
        <div id="virtual-scroller">
            <div id="scroll-content"></div>
        </div>
    </div>

    <div id="detail-pane">
        <div class="info-card">
            <h2 id="det-name">Select a file</h2>

            <div class="field-group">
                <span class="field-label">Type</span>
                <span id="det-type" class="badge">-</span>
            </div>

            <div class="field-group">
                <span class="field-label">Original Path</span>
                <div style="display:flex; gap: 10px; align-items: flex-start;">
                    <div class="field-value" style="flex:1" id="det-old">-</div>
                    <button class="btn" onclick="copyText('det-old')">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        Copy
                    </button>
                </div>
            </div>

            <div class="field-group">
                <span class="field-label">New Path</span>
                <div style="display:flex; gap: 10px; align-items: flex-start;">
                    <div class="field-value" style="flex:1" id="det-new">-</div>
                    <button class="btn" onclick="copyText('det-new')">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        Copy
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<div id="toast">Copied to clipboard</div>

<script>
    const flatData = __DATA_PLACEHOLDER__;

    const expandedIds = new Set();
    let visibleRows = [];
    let selectedId = null;
    let searchQuery = "";

    const rowHeight = 28;
    const buffer = 10;

    const scroller = document.getElementById('virtual-scroller');
    const content = document.getElementById('scroll-content');
    const searchBox = document.getElementById('search-box');

    function init() {
        recalcVisibleRows();
        scroller.addEventListener('scroll', render);
        window.addEventListener('resize', render);
        render();
    }

    function recalcVisibleRows() {
        if (searchQuery) {
            visibleRows = flatData.filter(item =>
                item.name.toLowerCase().includes(searchQuery)
            );
        } else {
            visibleRows = [];
            let skipUntilDepth = -1;

            for (let i = 0; i < flatData.length; i++) {
                const item = flatData[i];

                if (skipUntilDepth !== -1) {
                    if (item.depth > skipUntilDepth) {
                        continue;
                    } else {
                        skipUntilDepth = -1;
                    }
                }

                visibleRows.push(item);

                if (item.type === 'folder' && !expandedIds.has(item.id)) {
                    skipUntilDepth = item.depth;
                }
            }
        }

        content.style.height = `${visibleRows.length * rowHeight}px`;
        render();
    }

    function render() {
        const scrollTop = scroller.scrollTop;
        const viewportHeight = scroller.clientHeight;

        const startIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - buffer);
        const endIndex = Math.min(visibleRows.length, Math.ceil((scrollTop + viewportHeight) / rowHeight) + buffer);

        let html = '';
        for (let i = startIndex; i < endIndex; i++) {
            const item = visibleRows[i];
            const top = i * rowHeight;
            const isSelected = item.id === selectedId;
            const isExpanded = expandedIds.has(item.id);
            const indent = searchQuery ? 0 : (item.depth * 20);

            let iconSvg = '';
            if (item.type === 'folder') {
                iconSvg = `<svg class="row-icon icon-folder" viewBox="0 0 24 24"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" fill="#FFC107"></path></svg>`;
            } else {
                iconSvg = `<svg class="row-icon icon-file" viewBox="0 0 24 24"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" fill="none" stroke="currentColor" stroke-width="2"></path></svg>`;
            }

            let expanderHtml = `<span class="row-expander"></span>`;
            if (item.type === 'folder' && !searchQuery) {
                const arrow = isExpanded ? '&#9660;' : '&#9654;';
                expanderHtml = `<span class="row-expander" onclick="toggleExpand(event, ${item.id})">${arrow}</span>`;
            }

           html += `
                <div class="tree-row ${isSelected ? 'selected' : ''}" style="top: ${top}px" onclick="selectItem(${item.id})">
                    <span style="display:inline-flex; align-items:center; padding-left:${indent}px; width:100%; box-sizing:border-box;">
                        ${expanderHtml}
                        ${iconSvg}
                         <span class="row-text">${item.name}</span>
                     </span>
                 </div>
            `;
        }

        content.innerHTML = html;
    }

    window.toggleExpand = function(e, id) {
        e.stopPropagation();
        if (expandedIds.has(id)) {
            expandedIds.delete(id);
        } else {
            expandedIds.add(id);
        }
        recalcVisibleRows();
    }

    window.selectItem = function(id) {
        selectedId = id;
        const item = flatData.find(x => x.id === id);
        if (!item) return;

        render();

        document.getElementById('det-name').textContent = item.name;
        document.getElementById('det-type').textContent = item.type.toUpperCase();
        document.getElementById('det-old').textContent = item.old_path || '-';
        document.getElementById('det-new').textContent = item.new_path || '-';
    }

    searchBox.addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase();
        scroller.scrollTop = 0;
        recalcVisibleRows();
    });

    window.copyText = function(elementId) {
        const text = document.getElementById(elementId).textContent;
        if (text && text !== '-') {
            navigator.clipboard.writeText(text).then(() => {
                const x = document.getElementById("toast");
                x.className = "show";
                setTimeout(function() {
                    x.className = x.className.replace("show", "");
                }, 3000);
            });
        }
    }

    init();
</script>
</body>
</html>
"""


def normalize_path(value: str) -> str:
    if not value:
        return ""
    return str(value).strip().replace("\\", "/").rstrip("/").lower()


def normalize_item_type(value: str) -> str:
    v = (value or "").strip().lower()
    if v in {"directory", "folder"}:
        return "folder"
    return "file"


def get_display_type(value: str) -> str:
    return "folder" if normalize_item_type(value) == "folder" else "file"


def get_name_from_row(row: Dict[str, str]) -> str:
    relative_path = (row.get("relative_path") or "").strip().replace("\\", "/").rstrip("/")
    if relative_path:
        parts = [p for p in relative_path.split("/") if p]
        if parts:
            return parts[-1]
    full_path = (row.get("full_path") or "").strip().replace("\\", "/").rstrip("/")
    if full_path:
        parts = [p for p in full_path.split("/") if p]
        if parts:
            return parts[-1]
    return ""


def build_unique_name_type_map(rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], Dict[str, str]]:
    grouped = defaultdict(list)
    for row in rows:
        key = (get_name_from_row(row).lower(), normalize_item_type(row.get("item_type", "")))
        grouped[key].append(row)

    unique_map = {}
    for key, items in grouped.items():
        if len(items) == 1:
            unique_map[key] = items[0]
    return unique_map


def build_lookup(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Dict[str, str]]]:
    stable_id_columns = [
        "id", "file_id", "folder_id", "item_id", "object_id", "resource_id",
        "drive_id", "document_id", "doc_id", "guid", "uuid"
    ]

    by_stable_id = {}
    by_full_path = {}
    by_relative_path = {}

    for row in rows:
        for col in stable_id_columns:
            val = (row.get(col) or "").strip()
            if val:
                by_stable_id[f"{col}:{val.lower()}"] = row

        full_path = normalize_path(row.get("full_path", ""))
        if full_path and full_path not in by_full_path:
            by_full_path[full_path] = row

        rel_path = normalize_path(row.get("relative_path", ""))
        if rel_path and rel_path not in by_relative_path:
            by_relative_path[rel_path] = row

    by_unique_name_type = build_unique_name_type_map(rows)

    return {
        "by_stable_id": by_stable_id,
        "by_full_path": by_full_path,
        "by_relative_path": by_relative_path,
        "by_unique_name_type": by_unique_name_type,
    }


def find_matching_new_row(old_row: Dict[str, str], new_lookup: Dict[str, Dict]) -> Optional[Dict[str, str]]:
    stable_id_columns = [
        "id", "file_id", "folder_id", "item_id", "object_id", "resource_id",
        "drive_id", "document_id", "doc_id", "guid", "uuid"
    ]

    for col in stable_id_columns:
        val = (old_row.get(col) or "").strip()
        if val:
            key = f"{col}:{val.lower()}"
            match = new_lookup["by_stable_id"].get(key)
            if match:
                return match

    full_path = normalize_path(old_row.get("full_path", ""))
    if full_path:
        match = new_lookup["by_full_path"].get(full_path)
        if match:
            return match

    rel_path = normalize_path(old_row.get("relative_path", ""))
    if rel_path:
        match = new_lookup["by_relative_path"].get(rel_path)
        if match:
            return match

    name_type_key = (
        get_name_from_row(old_row).lower(),
        normalize_item_type(old_row.get("item_type", "")),
    )
    return new_lookup["by_unique_name_type"].get(name_type_key)


def enrich_old_rows_with_comparison(
    old_rows: List[Dict[str, str]],
    new_rows: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    new_lookup = build_lookup(new_rows)
    enriched = []

    for old_row in old_rows:
        row = dict(old_row)
        match = find_matching_new_row(old_row, new_lookup)

        row["old_path_for_viewer"] = old_row.get("full_path", "") or old_row.get("relative_path", "")

        if match:
            row["new_path_for_viewer"] = match.get("full_path", "") or match.get("relative_path", "")
        else:
            row["new_path_for_viewer"] = ""

        enriched.append(row)

    return enriched


def generate_tree_data(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    root = {"name": "ROOT", "children": {}, "data": None, "depth": -1}

    print("Building tree structure...")

    for row in rows:
        relative_path = (row.get("relative_path") or "").strip().replace("\\", "/")
        if not relative_path:
            continue

        parts = [p for p in relative_path.split("/") if p]
        item_type = normalize_item_type(row.get("item_type") or "file")

        current = root
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)

            if part not in current["children"]:
                current["children"][part] = {
                    "name": part,
                    "children": {},
                    "depth": i,
                    "type": "folder",
                    "data": None
                }

            current = current["children"][part]

            if is_last:
                current["type"] = "folder" if item_type == "folder" else "file"
                current["data"] = row

    flat_list = []
    _id_counter = 0

    def traverse(node, parent_id):
        nonlocal _id_counter

        sorted_keys = sorted(node["children"].keys(), key=lambda k: k.lower())

        for key in sorted_keys:
            child = node["children"][key]
            current_id = _id_counter
            _id_counter += 1

            row_data = child["data"]
            old_path = ""
            new_path = ""

            if row_data:
                old_path = row_data.get("old_path_for_viewer", "")
                new_path = row_data.get("new_path_for_viewer", "")

            item = {
                "id": current_id,
                "parentId": parent_id,
                "name": child["name"],
                "type": child["type"],
                "depth": child["depth"],
                "old_path": old_path,
                "new_path": new_path,
            }

            flat_list.append(item)
            traverse(child, current_id)

    traverse(root, None)
    return flat_list


def read_csv_rows(csv_path: Path) -> List[Dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    print(f"Reading CSV: {csv_path}...")
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def generate_html(old_csv_path: Path, new_csv_path: Path):
    old_rows = read_csv_rows(old_csv_path)
    new_rows = read_csv_rows(new_csv_path)

    print(f"Loaded old CSV rows: {len(old_rows)}")
    print(f"Loaded new CSV rows: {len(new_rows)}")

    merged_rows = enrich_old_rows_with_comparison(old_rows, new_rows)

    print("Processing tree from old CSV...")
    flat_data = generate_tree_data(merged_rows)
    print(f"Generated {len(flat_data)} tree nodes.")

    json_data = json.dumps(flat_data)
    final_html = HTML_TEMPLATE.replace("__DATA_PLACEHOLDER__", json_data)

    # Use OUTPUT_HTML directly (already a Path)
    with OUTPUT_HTML.open("w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"Successfully generated: {OUTPUT_HTML.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate standalone HTML Folder Viewer by comparing an old CSV and a new CSV."
    )
    parser.add_argument("--old-csv", type=Path, default=DEFAULT_OLD_CSV, help="Old CSV file")
    parser.add_argument("--new-csv", type=Path, default=DEFAULT_NEW_CSV, help="New CSV file")
    args = parser.parse_args()

    generate_html(args.old_csv, args.new_csv)