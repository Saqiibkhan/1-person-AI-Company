"""
Tests the file/folder deliverable feature: parsing an agent's raw
output into real (path, content) files, and the download endpoints
that zip them up.
"""
import zipfile
import io

from app.tools.file_tools import parse_files_from_output, build_zip


def test_single_document_output_becomes_one_fallback_file():
    output = "# Market Research\n\nSome findings here."
    files = parse_files_from_output(output, "market-research.md")
    assert files == [("market-research.md", output)]


def test_multi_file_marker_format_is_parsed_into_separate_files():
    output = """
Here is the implementation.

===FILE: src/main.py===
print("hello")
===END FILE===

===FILE: README.md===
# My Project
===END FILE===
""".strip()
    files = parse_files_from_output(output, "fallback.md")
    assert files == [
        ("src/main.py", 'print("hello")'),
        ("README.md", "# My Project"),
    ]


def test_path_traversal_in_file_marker_is_sanitized():
    output = "===FILE: ../../etc/passwd===\nmalicious\n===END FILE==="
    files = parse_files_from_output(output, "fallback.md")
    path, content = files[0]
    assert ".." not in path
    assert path == "etc/passwd"


def test_build_zip_produces_a_valid_archive_with_expected_entries():
    files = [("a.txt", "hello"), ("nested/b.txt", "world")]
    zip_bytes = build_zip(files, root_folder="myproject")

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        assert "myproject/a.txt" in names
        assert "myproject/nested/b.txt" in names
        assert zf.read("myproject/a.txt").decode() == "hello"
