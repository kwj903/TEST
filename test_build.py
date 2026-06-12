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
