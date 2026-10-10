"""
Controlled read/write helpers for agent-generated artifacts.

These are plain functions (not exposed as CrewAI @tool by default)
used by services that need to persist an agent's deliverable to disk,
e.g. exporting a final report. Per Section 13, this is a "write"
category operation, not "external/irreversible" -- it never leaves
the local filesystem.
"""
import io
import os
import re
import zipfile

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated_deliverables")

# Agents are prompted (see crews/task_factory.py) to wrap each file of a
# multi-file deliverable in this exact marker format. This regex is the
# other half of that contract.
_FILE_BLOCK_RE = re.compile(
    r"===FILE:\s*(?P<path>[^\n=]+?)\s*===\s*\n(?P<content>.*?)(?:\n)?===END FILE===",
    re.DOTALL,
)


def parse_files_from_output(output: str, fallback_filename: str) -> list[tuple[str, str]]:
    """
    Turns one agent's raw text output into a list of (relative_path, content)
    files.

    If the agent used the ===FILE: ...=== / ===END FILE=== markers (because
    its deliverable was genuinely multiple files -- e.g. source code), this
    returns one entry per file, preserving whatever folder structure the
    agent specified in the path. Otherwise the WHOLE output is treated as a
    single file, using fallback_filename -- so a plain report or strategy
    document still downloads as one real file instead of forcing every
    deliverable into an artificial multi-file shape.
    """
    matches = list(_FILE_BLOCK_RE.finditer(output or ""))
    if not matches:
        return [(fallback_filename, output or "")]

    files = []
    for m in matches:
        # Guard against path traversal -- an agent-provided path is
        # untrusted input, never trust it to stay inside the output dir.
        raw_path = m.group("path").strip().lstrip("/")
        safe_parts = [p for p in raw_path.split("/") if p not in ("", ".", "..")]
        safe_path = "/".join(safe_parts) or fallback_filename
        files.append((safe_path, m.group("content")))
    return files


def save_deliverable(project_id: int, filename: str, content: str) -> str:
    project_dir = os.path.join(OUTPUT_DIR, str(project_id))
    os.makedirs(project_dir, exist_ok=True)
    path = os.path.join(project_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def build_zip(files: list[tuple[str, str]], root_folder: str | None = None) -> bytes:
    """
    Builds a .zip file in memory from a list of (relative_path, content)
    files and returns the raw bytes -- used by the download endpoints so
    nothing has to be written to disk just to serve a download.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files:
            arcname = f"{root_folder}/{path}" if root_folder else path
            zf.writestr(arcname, content)
    return buffer.getvalue()
