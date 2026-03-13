import os

def get_file_tree(root=".", max_depth=2):
    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith('.')
            and d not in ('venv', 'node_modules', '__pycache__', '.git')
        ]
        depth = dirpath.replace(root, '').count(os.sep)
        if depth > max_depth:
            continue
        indent = "  " * depth
        lines.append(f"{indent}{os.path.basename(dirpath)}/")
        for f in filenames:
            lines.append(f"{indent}  {f}")
    return "\n".join(lines)

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Could not read file: {e}]"

def build_context(question, file_path=None, project_root="."):
    parts = []

    tree = get_file_tree(project_root)
    parts.append(f"Project structure:\n```\n{tree}\n```")

    if file_path and os.path.exists(file_path):
        content = read_file(file_path)
        parts.append(f"File: {file_path}\n```\n{content}\n```")

    parts.append(f"Question: {question}")
    return "\n\n".join(parts)