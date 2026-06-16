# layer_11/reactions.py
import os

# Maps file extension to a task template
# {path} and {filename} are substituted at runtime
REACTIONS: dict[str, str] = {
    ".py": (
        "Review the Python file at '{path}'. "
        "Check for bugs, style issues, and improvements. "
        "Save your feedback to '{filename}.review.md'."
    ),
    ".txt": (
        "Read the file at '{path}' and write a concise summary. "
        "Save the summary to '{filename}.summary.md'."
    ),
    ".md": (
        "Read the markdown file at '{path}'. "
        "Check for clarity, structure, and completeness. "
        "Save suggestions to '{filename}.suggestions.md'."
    ),
    ".json": (
        "Read the JSON file at '{path}'. "
        "Describe its structure and contents in plain English. "
        "Save the description to '{filename}.description.md'."
    ),
    ".csv": (
        "Read the CSV file at '{path}'. "
        "Summarize the data: how many rows, what columns, any patterns. "
        "Save the analysis to '{filename}.analysis.md'."
    ),
    ".js": (
        "Review the JavaScript file at '{path}'. "
        "Check for bugs and modern best practices. "
        "Save feedback to '{filename}.review.md'."
    ),
    ".ts": (
        "Review the TypeScript file at '{path}'. "
        "Check for bugs and modern best practices. "
        "Save feedback to '{filename}.review.md'."
    ),
}

DEFAULT_REACTION = (
    "A new file '{filename}' appeared at '{path}'. "
    "Describe what type of file it is and what it might contain. "
    "Save your notes to '{filename}.notes.md'."
)

def get_reaction(filepath: str) -> str:
    """Return the task string for a given file path."""
    ext = os.path.splitext(filepath)[1].lower()
    filename = os.path.basename(filepath)
    path = filepath

    template = REACTIONS.get(ext, DEFAULT_REACTION)
    return template.format(path=path, filename=filename)