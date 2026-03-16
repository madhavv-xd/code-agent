import os
import re

_tree_cache = {}

SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
    '.mp4', '.mp3', '.pdf', '.zip', '.tar', '.gz',
    '.exe', '.bin', '.lock', '.pyc'
}

def get_file_tree(root=".", max_depth=2):
    if root in _tree_cache:
        return _tree_cache[root]
    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith('.')
            and d not in ('venv', 'node_modules', '__pycache__', '.git', 'dist', 'build')
        ]
        depth = dirpath.replace(root, '').count(os.sep)
        if depth > max_depth:
            continue
        indent = "  " * depth
        lines.append(f"{indent}{os.path.basename(dirpath)}/")
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext not in SKIP_EXTENSIONS:
                lines.append(f"{indent}  {f}")
    result = "\n".join(lines)
    _tree_cache[root] = result
    return result

def get_all_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        return []

def extract_function(lines, name):
    """Extract a specific function or class by name."""
    result = []
    inside = False
    base_indent = None

    for line in lines:
        if re.match(rf'^\s*(def|class|async def|function|const|let)\s+{re.escape(name)}', line):
            inside = True
            base_indent = len(line) - len(line.lstrip())
            result.append(line)
            continue

        if inside:
            current_indent = len(line) - len(line.lstrip())
            # stop when we return to base indent (end of function)
            if line.strip() and current_indent <= base_indent:
                break
            result.append(line)

    return ''.join(result) if result else None

def extract_line_range(lines, target_line, padding=10):
    """Extract lines around a specific line number."""
    start = max(0, target_line - padding - 1)
    end   = min(len(lines), target_line + padding)
    excerpt = ''.join(lines[start:end])
    return f"(lines {start+1}-{end})\n{excerpt}"

def detect_scope(question, lines):
    """
    Figure out what part of the file to load based on the question.
    Returns the relevant chunk of code.
    """
    q = question.lower()

    # question mentions a specific function/class name
    func_match = re.search(
        r'(function|method|class|def)\s+["\']?(\w+)["\']?|'
        r'["\'](\w+)["\']?\s+(function|method|class)|'
        r'`(\w+)`',
        q
    )
    if func_match:
        name = next(g for g in func_match.groups() if g and g not in
                    ('function', 'method', 'class', 'def'))
        extracted = extract_function(lines, name)
        if extracted:
            return f"Relevant section ({name}):\n{extracted}"

    # question mentions a line number
    line_match = re.search(r'line\s*(\d+)', q)
    if line_match:
        target = int(line_match.group(1))
        return extract_line_range(lines, target)

    # needs full file — broad questions
    FULL_FILE_KEYWORDS = [
        'whole', 'entire', 'all', 'everything', 'file',
        'find bugs', 'review', 'improve', 'refactor',
        'explain', 'what does', 'overall'
    ]
    if any(k in q for k in FULL_FILE_KEYWORDS):
        return ''.join(lines)

    # default — send full file
    return ''.join(lines)

def read_file(filepath, max_lines=0):
    """Simple full file read with optional hard limit."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in SKIP_EXTENSIONS:
        return "[binary file skipped]"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if max_lines and len(lines) > max_lines:
            return ''.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
        return ''.join(lines)
    except Exception as e:
        return f"[Could not read file: {e}]"

def build_context(question, file_path=None, project_root=".", max_lines=0):
    parts = []

    tree = get_file_tree(project_root)
    parts.append(f"Project structure:\n```\n{tree}\n```")

    if file_path and os.path.exists(file_path):
        lines = get_all_lines(file_path)
        total = len(lines)

        if max_lines and total > max_lines:
            # hard limit set by user — respect it
            content = read_file(file_path, max_lines=max_lines)
        else:
            # smart load — only what the question needs
            content = detect_scope(question, lines)

        parts.append(f"File: {file_path} ({total} lines total)\n```\n{content}\n```")

    parts.append(f"Question: {question}")
    return "\n\n".join(parts)
