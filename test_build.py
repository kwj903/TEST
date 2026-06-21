import os
import shutil
import pytest
from build import build_site

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup test directories and files
    os.makedirs("content", exist_ok=True)
    os.makedirs("templates", exist_ok=True)

    # We will just clean up public directory before test to ensure it runs clean
    if os.path.exists("public"):
        shutil.rmtree("public")

    yield

    # Teardown logic if needed (we'll leave the generated files for inspection)

def test_build_site():
    # Run the build function
    build_site()

    # Verify the output files are created
    assert os.path.exists("public/index.html"), "index.html was not generated"
    assert os.path.exists("public/about.html"), "about.html was not generated"

    # Verify the content of the generated files
    with open("public/index.html", "r", encoding="utf-8") as f:
        content = f.read()

        # Check if Jinja template is applied (should have the header)
        assert "<title>Index</title>" in content
        assert "My Static Blog" in content

        # Check if markdown is converted to HTML
        assert "<h1>Hello World</h1>" in content
        assert "<strong>Markdown</strong>" in content

    with open("public/about.html", "r", encoding="utf-8") as f:
        content = f.read()
        assert "<title>About</title>" in content
        assert "<h1>About Me</h1>" in content

def test_xss_in_title():
    # Create a malicious markdown file using a safe filename (e.g., using an ampersand and single quotes)
    # Characters like <, >, and " are invalid on Windows filesystems.
    malicious_filename = "xss-&-'test'.md"
    os.makedirs("content", exist_ok=True)
    malicious_path = os.path.join("content", malicious_filename)

    with open(malicious_path, "w", encoding="utf-8") as f:
        f.write("# Malicious Content\nThis is a test.")

    # Run the build function
    build_site()

    # Verify the output file is created
    output_filename = "xss-&-'test'.html"
    output_path = os.path.join("public", output_filename)

    assert os.path.exists(output_path), "The file was not generated"

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if the title is properly escaped
    # The original filename is "xss-&-'test'.md"
    # title = filename[:-3].replace("-", " ").title() -> "Xss & 'Test'"
    # Expected escaped HTML: Xss &amp; &#39;Test&#39;
    assert "&amp;" in content, "The ampersand was not properly escaped!"
    assert "&#39;" in content, "The single quote was not properly escaped!"

    # Clean up
    os.remove(malicious_path)

def test_build_site_missing_template(monkeypatch, capsys):
    from jinja2 import Environment

    def mock_get_template(self, name):
        raise Exception("Mocked template not found")

    monkeypatch.setattr(Environment, "get_template", mock_get_template)

    build_site()

    captured = capsys.readouterr()
    assert "Warning: Could not load template 'base.html'." in captured.out
    assert "Mocked template not found" in captured.out