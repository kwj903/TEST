import os
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from markupsafe import Markup

def build_site():
    # Setup directories
    content_dir = "content"
    template_dir = "templates"
    output_dir = "public"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html', 'xml']))

    try:
        template = env.get_template("base.html")
    except TemplateNotFound as e:
        print(f"Warning: Could not load template 'base.html'. Ensure it exists in {template_dir}/")
        print(f"Error: {e}")
        return

    # Initialize markdown instance once
    md = markdown.Markdown()

    # Process all markdown files
    for filename in os.listdir(content_dir):
        if filename.endswith(".md"):
            # Read markdown content
            file_path = os.path.join(content_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Convert to HTML
            html_content = md.convert(md_content)

            # Reset the markdown instance for the next use
            md.reset()

            # Render with template
            # For simplicity, we use the filename without extension as title if needed
            title = filename[:-3].replace("-", " ").title()
            final_html = template.render(title=title, content=Markup(html_content))

            # Write output
            output_filename = filename[:-3] + ".html"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_html)

            print(f"Built {output_filename}")

if __name__ == "__main__":
    build_site()
