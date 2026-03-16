import os
import re

# Cache: maps root -> (mtime_snapshot, tree_string)
_tree_cache = {}

SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
    '.mp4', '.mp3', '.pdf', '.zip', '.tar', '.gz',
    '.exe', '.bin', '.lock', '.pyc'
}

# Rough token budget: ~4 chars per token, target ≤ 6000 tokens for context
MAX_CONTEXT_CHARS = 24_000


def _root_mtime(root):
    """Quick fingerprint of root dir modification time."""
    try:
        return os.path.getmtime(root)
    except OSError:
        return 0


def get_file_tree(root=".", max_depth=2):
    mtime = _root_mtime(root)
    cached = _tree_cache.get(root)
    if cached and cached[0] == mtime:
        return cached[1]

    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted([
            d for d in dirnames
            if not d.startswith('.')
            and d not in ('venv', 'node_modules', '__pycache__', '.git', 'dist', 'build')
        ])
        depth = dirpath.replace(root, '').count(os.sep)
        if depth > max_depth:
            continue
        indent = "  " * depth
        lines.append(f"{indent}{os.path.basename(dirpath)}/")
        for f in sorted(filenames):
            ext = os.path.splitext(f)[1].lower()
            if ext not in SKIP_EXTENSIONS:
                lines.append(f"{indent}  {f}")

    result = "\n".join(lines)
    _tree_cache[root] = (mtime, result)
    return result


def get_all_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception:
        return []


def extract_function(lines, name):
    """Extract a specific function or class by name. Handles blank lines correctly."""
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
            # Skip blank lines — don't use them to determine end of block
            if not line.strip():
                result.append(line)
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                break
            result.append(line)

    return ''.join(result) if result else None


def extract_line_range(lines, target_line, padding=15):
    """Extract lines around a specific line number."""
    start = max(0, target_line - padding - 1)
    end   = min(len(lines), target_line + padding)
    excerpt = ''.join(lines[start:end])
    return f"(lines {start+1}–{end})\n{excerpt}"


def detect_scope(question, lines):
    """
    Figure out what part of the file to load based on the question.
    Returns the relevant chunk of code.
    """
    q = question.lower()

    # Question mentions a specific function/class name
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

    # Question mentions a line number
    line_match = re.search(r'line\s*(\d+)', q)
    if line_match:
        target = int(line_match.group(1))
        return extract_line_range(lines, target)

    # Needs full file
    FULL_FILE_KEYWORDS = [
        'whole', 'entire', 'all', 'everything', 'file',
        'find bugs', 'review', 'improve', 'refactor',
        'explain', 'what does', 'overall'
    ]
    if any(k in q for k in FULL_FILE_KEYWORDS):
        return ''.join(lines)

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
            return ''.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines truncated)"
        return ''.join(lines)
    except Exception as e:
        return f"[Could not read file: {e}]"


def build_context(question, file_path=None, project_root=".", max_lines=0):
    parts = []

    tree = get_file_tree(project_root)
    tree_section = f"Project structure:\n```\n{tree}\n```"
    parts.append(tree_section)

    file_section = ""
    if file_path and os.path.exists(file_path):
        lines = get_all_lines(file_path)
        total = len(lines)

        if max_lines and total > max_lines:
            content = read_file(file_path, max_lines=max_lines)
        else:
            content = detect_scope(question, lines)

        file_section = f"File: {file_path} ({total} lines total)\n```\n{content}\n```"
        parts.append(file_section)

    parts.append(f"Question: {question}")

    full = "\n\n".join(parts)

    # Token budget guard: trim file content if context is too large
    if len(full) > MAX_CONTEXT_CHARS and file_section:
        budget = MAX_CONTEXT_CHARS - len(tree_section) - len(question) - 200
        if budget > 500:
            trimmed_content = content[:budget] + f"\n... [truncated to fit context window]"
            file_section = f"File: {file_path} ({total} lines total)\n```\n{trimmed_content}\n```"
        else:
            file_section = f"[File omitted — context too large. Ask about a specific function or line range.]"

        parts = [tree_section, file_section, f"Question: {question}"]
        full = "\n\n".join(parts)

    return full