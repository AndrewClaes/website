import os
from markdown import markdown
import re

# Define the HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Google Font -->
  <meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' https://fonts.googleapis.com;
    style-src 'self' https://fonts.googleapis.com;
    font-src 'self' https://fonts.gstatic.com;
  ">

  <!-- SEO: Meta Description -->
  <meta name="description" content="Andrew Claes - Music, Research, and Projects">

  <!-- SEO: Keywords from Markdown -->
  {meta_keywords}

  <!-- Open Graph -->
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="Explore the latest content from Andrew Claes.">
  <meta property="og:image" content="https://andrewclaes.github.io/website/images/preview.jpg">
  <meta property="og:url" content="https://andrewclaes.github.io/website//pages/{prefix}.html">
  <meta property="og:type" content="website">

  <title>{title}</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="icon" href="/images/favicon.ico" type="image/x-icon">
<link href="https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@100..900&display=swap" rel="stylesheet">
<body>
  <header>
    <nav>
      <ul id="menu">
        {menu_links}
      </ul>
    </nav>
  </header>

  <div class="layout">
    <!-- Dynamic left menu -->
    <aside class="dynamic-menu">
      <h3><a href="../pages/{prefix}.html">{menu_title}</a></h3>
      <ul>
        {dynamic_menu_links}
      </ul>
    </aside>

    <!-- Main content -->
    <main>
      <div class="nav-buttons">
        <button onclick="history.back()">← Back</button>
        <button onclick="history.forward()">Forward →</button>
      </div>
      {content}
    </main>
  </div>

  <footer>
    <p>© 2025 Macroheart. All rights reserved.</p>
  </footer>
</body>
</html>
"""


# Define a processing pipeline
def process_pipeline(md_content, pipeline):
    """
    Processes the markdown content through a sequence of pipeline functions.
    """
    for func in pipeline:
        md_content = func(md_content)
    return md_content

# Define a function for processing custom images
def process_custom_images(md_content):
    """
    Converts custom Markdown image syntax to HTML with CSS classes.
    """
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)-(\w+)'  # Matches ![Alt text](path)-size
    def replacer(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        size = match.group(3)
        css_class = f"{size}-image" if size in ['small', 'medium', 'large', 'full'] else "default-image"
        return f'<img src="{image_path}" alt="{alt_text}" class="{css_class}">'
    return re.sub(pattern, replacer, md_content)

# Define a function for replacing Markdown links
def replace_md_links(md_content):
    """
    Replaces all links pointing to .md files with .html links.
    """
    return re.sub(r'\(([^)]+)\.md\)', r'(\1.html)', md_content)

# Add other processing functions here
def extract_keywords(md_content, output_dir, page_name):
    """
    Extracts inline #keywords from Markdown content, converts them to HTML links,
    and ensures `home-tags-keyword.html` pages exist with back-references.
    """
    lines = md_content.split("\n")
    keywords = set()  # Store unique keywords
    processed_content = []  # Store updated content

    for line in lines:
        # Ignore Markdown headings (start with '#' followed by a space)
        if not re.match(r"^\s*#+\s", line):
            # Find inline hashtags (e.g., #project, #music)
            found_keywords = re.findall(r"#([\w\d_]+)", line)
            keywords.update(found_keywords)  # Add unique keywords

            # Replace #keyword with a clickable link
            for keyword in found_keywords:
                link = f"<a href='../website/pages/home-tags-{keyword}.html'>{keyword}</a>"
                line = line.replace(f"#{keyword}", link)

        processed_content.append(line)  # Store modified line

    # Generate meta tag
    meta_tag = f'<meta name="keywords" content="{", ".join(keywords)}">' if keywords else ""

    # Define static menu items (same for all tag pages)
    menu_links = """
        <li><a href='../pages/home.html'>Home</a></li>
        <li><a href='../pages/blog.html'>Blog</a></li>
        <li><a href='../pages/music.html'>Music</a></li>
        <li><a href='../pages/research.html'>Research</a></li>
        <li><a href='../pages/concerts.html'>Concerts</a></li>
        <li><a href='../pages/links.html'>Links</a></li>
        <li><a href='../pages/store.html'>Store</a></li>
    """

    # Generate a dynamic menu with all tag files (home-tags-*.html) in /pages/
    tag_files = [
        f for f in os.listdir(output_dir) if f.startswith("home-tags-") and f.endswith(".html")
    ]
    dynamic_menu_links = "\n".join(
        f'<li><a href="/pages/{tag_file}">{tag_file.replace("home-tags-", "").replace(".html", "")}</a></li>'
        for tag_file in sorted(tag_files)
    )

    # Ensure each tag page exists and update it
    for keyword in keywords:
        tag_file = os.path.join(output_dir, f"home-tags-{keyword}.html")
        tag_title = f"Tag: {keyword}"

        # Load existing content or create a new list
        existing_links = set()
        if os.path.exists(tag_file):
            with open(tag_file, "r", encoding="utf-8") as file:
                content = file.read()
                # Extract existing links to prevent duplicates
                existing_links.update(re.findall(r'<a href="../pages/(.*?)\.html">', content))

        # Add the new page reference if it doesn't exist
        if page_name not in existing_links:
            existing_links.add(page_name)

        # Generate updated content for the tag page
        tag_links = "\n".join(f'<li><a href="../pages/{link}.html">{link}</a></li>' for link in sorted(existing_links))
        tag_content = HTML_TEMPLATE.format(
            title=tag_title,
            meta_keywords=f'<meta name="keywords" content="{keyword}">',
            content=f"<h1>{tag_title}</h1><ul>{tag_links}</ul>",
            menu_links=menu_links,  # Static menu for all pages
            dynamic_menu_links=dynamic_menu_links,  # Dynamic list of all tag pages
            menu_title="Tags",
            prefix=f"home-tags-{keyword}"
        )

        # Write or update the tag file
        with open(tag_file, "w", encoding="utf-8") as file:
            file.write(tag_content)

    return "\n".join(processed_content), meta_tag  # Return updated content + meta tag

def process_tables(md_content):
    """
    Converts Markdown tables to HTML <table>, <tr>, <th>, and <td> elements.
    Handles empty cells, proper column alignment, and Markdown links in table cells.
    """
    def convert_links(cell):
        """
        Converts Markdown-style links [text](url) to HTML <a> tags.
        """
        pattern = r"\[([^\]]+)\]\(([^)]+)\)"  # Matches [linkname](link)
        return re.sub(pattern, r"<a href='\2'>\1</a>", cell)

    lines = md_content.split("\n")
    html_output = []
    inside_table = False
    column_count = 0  # Track the number of columns in the table for alignment

    for line in lines:
        # Detect a table row (rows with pipes `|`)
        if "|" in line:
            # Remove leading/trailing pipes and split by pipes
            cells = [convert_links(cell.strip()) for cell in line.strip("|").split("|")]

            # Skip rows that are empty or just contain pipes
            if not any(cells):
                continue

            # Handle divider rows (e.g., |---|---|---|)
            if all(cell.startswith("-") and cell.endswith("-") for cell in cells):
                continue

            # Start a new table if not already inside one
            if not inside_table:
                html_output.append("<table>")
                inside_table = True

            # Calculate column count based on the first valid row
            if column_count == 0:
                column_count = len(cells)

            # Handle header row (first row of the table)
            if html_output[-1] == "<table>":  # Header row is right after <table>
                html_output.append(
                    "<tr>" +
                    "".join(f"<th>{cell}</th>" for cell in cells[:column_count]) +
                    "</tr>"
                )
            else:  # Handle data rows
                html_output.append(
                    "<tr>" +
                    "".join(f"<td>{cell}</td>" for cell in cells[:column_count]) +
                    "</tr>"
                )
        else:
            # If the current line is not part of a table, close the table
            if inside_table:
                html_output.append("</table>")
                inside_table = False

            # Append non-table lines as-is
            html_output.append(line)

    # Close any unclosed table at the end of the content
    if inside_table:
        html_output.append("</table>")

    return "\n".join(html_output)

def links_in_tab(html_content):
    """
    Adds target="_blank" to all <a> tags within the <main> section of the HTML content.
    """
    # Match the <main> tag and extract its content
    main_pattern = r"(<main.*?>)(.*?)(</main>)"
    match = re.search(main_pattern, html_content, re.DOTALL)
    
    if match:
        opening_main, main_content, closing_main = match.groups()
        
        # Add target="_blank" to <a> tags within the extracted <main> content
        updated_main_content = re.sub(
            r'<a\s+([^>]*?href=["\'].*?["\'])([^>]*)>',
            r'<a \1 target="_blank" rel="noopener noreferrer" \2>',
            main_content
        )
        
        # Reassemble the <main> section
        html_content = html_content.replace(
            match.group(0),
            f"{opening_main}{updated_main_content}{closing_main}"
        )

    return html_content

def convert_line_breaks(md_content):
    """
    Converts single line breaks to <br> tags while preserving paragraph breaks.
    """
    # Split content into paragraphs (double newlines indicate paragraphs)
    paragraphs = md_content.split("\n\n")
    
    # Process each paragraph separately
    processed_paragraphs = []
    for para in paragraphs:
        # Replace single line breaks with <br>
        processed_para = para.replace("\n", " <br>\n")
        processed_paragraphs.append(processed_para)
    
    # Rejoin paragraphs with double newlines to maintain separation
    return "\n\n".join(processed_paragraphs)

# Menu generation
def generate_menu():
    """
    Generates the main static menu HTML.
    Returns clean HTML without unnecessary attributes.
    """
    menu_items = [
        ("home", "Home"),
        ("blog", "Blog"),
        ("music", "Music"),
        ("research", "Research"),
        ("concerts", "Concerts"),
        ("links", "Links"),
        ("store", "Store"),
    ]
    # Generate clean <li> and <a> elements
    menu_html = "\n".join(
        [f"<li><a href='../pages/{item[0]}.html'>{item[1]}</a></li>" for item in menu_items]
    )
    return menu_items, menu_html

def determine_prefix(page_name, menu_items):
    """
    Determine the prefix and menu title dynamically from the menu items.
    """
    for prefix, title in menu_items:
        if page_name.startswith(prefix):
            return prefix, title
    return "", "Related Pages"  # Default if no match


def generate_dynamic_menu(output_dir, current_prefix):
    """
    Generate a dynamic menu for related pages based on the current prefix.
    Show only files with exactly one additional suffix after the current prefix.
    Sorts the files alphabetically.
    """
    menu_items = []

    for filename in os.listdir(output_dir):
        filename_lower = filename.lower()
        # Ensure the file starts with the current prefix and ends with .html
        if filename_lower.startswith(current_prefix + "-") and filename_lower.endswith(".html"):
            # Extract the part after the current prefix
            remaining = filename_lower[len(current_prefix) + 1:].split("-")
            if len(remaining) == 1:  # Only include files with exactly one additional suffix
                title = remaining[0].replace(".html", "")
                menu_items.append((filename_lower, title))

    # Sort items alphabetically by the title
    menu_items.sort(key=lambda item: item[1])

    # Generate the dynamic menu links
    dynamic_menu_links = "".join(
        f"<li><a href='../pages/{filename}'>{title}</a></li>" for filename, title in menu_items
    )
    return dynamic_menu_links


def update_dynamic_menu(output_dir, page_name):
    """
    Generate the dynamic menu for related pages at the current depth.
    Handles pages with any number of prefixes (e.g., home-contact-number-details.html).
    """
    # Split the page name into parts based on dashes
    suffix_parts = page_name.split("-")
    current_prefix = "-".join(suffix_parts)  # Start with the full page name

    # Check if we are at the base level
    if len(suffix_parts) == 1:  # At the static menu level
        return generate_dynamic_menu(output_dir, current_prefix)

    # Otherwise, move one level up in the hierarchy
    # Combine all prefixes up to the current depth
    parent_prefix = "-".join(suffix_parts[:-1])  # Remove the last part of the suffix
    return generate_dynamic_menu(output_dir, parent_prefix)


# Find links in the Markdown content
def find_links(md_content):
    return re.findall(r"\[.*?\]\((.*?\.html)\)", md_content)

# Markdown to HTML conversion
def convert_markdown_to_html(md_file, output_dir, menu_items, pipeline):
    with open(md_file, "r", encoding="utf-8") as file:
        markdown_content = file.read()

    # Process the Markdown content through the pipeline
    markdown_content = process_pipeline(markdown_content, pipeline)

    # Extract page name from file
    page_name = os.path.basename(md_file).lower().replace(".md", "").replace(".html", "")

    # Extract keywords, replace #keywords with links, and generate tag pages
    markdown_content, meta_keywords = extract_keywords(markdown_content, output_dir, page_name)

    # Convert Markdown to HTML
    html_content = markdown(markdown_content)

    # Extract title from first header
    title = "Andrew Claes"
    if markdown_content.strip().startswith("#"):
        title = markdown_content.splitlines()[0].replace("#", "").strip()

    # Ensure meta_keywords is always a string (avoid None)
    meta_keywords = meta_keywords or ""

    # Determine the prefix and menu title for the dynamic menu
    prefix, menu_title = determine_prefix(page_name, menu_items)

    # Menu generation
    _, menu_links = generate_menu()

    # Dynamic menu for related pages
    dynamic_menu_links = update_dynamic_menu(output_dir, page_name)

    # Format the HTML
    final_html = HTML_TEMPLATE.format(
        title=title,
        meta_keywords=meta_keywords,  # ✅ Injects meta tag correctly
        content=html_content,  # ✅ Ensures main content is included
        menu_links=menu_links,
        dynamic_menu_links=dynamic_menu_links,
        menu_title=menu_title,
        prefix=prefix
    )

    # Save the output (ensure filename is lowercase)
    output_file = os.path.join(output_dir, page_name + ".html")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(final_html)

    print(f"Converted: {md_file} -> {output_file}")

# Main function
def main():
    input_dir = "website/markdown"
    output_dir = "website/pages"
    os.makedirs(output_dir, exist_ok=True)

    # Generate menu items dynamically
    menu_items, _ = generate_menu()
    

    # Define the processing pipeline
    pipeline = [
        process_custom_images,
        replace_md_links,
        process_tables,
        convert_line_breaks  
        ]

    # Convert Markdown to HTML
    for filename in os.listdir(input_dir):
        if filename.endswith(".md"):
            md_file = os.path.join(input_dir, filename)
            convert_markdown_to_html(md_file, output_dir, menu_items, pipeline)

if __name__ == "__main__":
    main()
