import sys
import re
from pathlib import Path
from datetime import datetime

BACK_LINK = "[<< Back to vLLM Reports]({{ site.baseurl }}/logs/vllm/)"


def escape_liquid_braces(text):
    """
    Escape {{ sequences in text that would break Jekyll/Liquid templating.

    Preserves:
    - Content already inside {%- raw -%}...{%- endraw -%} blocks.
    - {{ site.baseurl }} used by the back-navigation link added by this script.

    All other {{ occurrences (e.g. code examples, issue descriptions) are wrapped
    in {% raw %}...{% endraw %} so Liquid renders them verbatim.
    """
    # Protect {{ site.baseurl }} with a unique placeholder so it survives escaping
    placeholder = "\x00SITE_BASEURL\x00"
    text = text.replace("{{ site.baseurl }}", placeholder)

    # Split on existing {% raw %}...{% endraw %} blocks; only escape outside them
    raw_block = re.compile(
        r'\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}', re.DOTALL
    )
    segments = []
    last_end = 0
    for m in raw_block.finditer(text):
        segment = text[last_end:m.start()]
        segments.append(segment.replace("{{", "{% raw %}{{{% endraw %}"))
        segments.append(m.group())  # keep raw block unchanged
        last_end = m.end()
    remaining = text[last_end:]
    segments.append(remaining.replace("{{", "{% raw %}{{{% endraw %}"))

    return "".join(segments).replace(placeholder, "{{ site.baseurl }}")


def process_file(file_path):
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"File not found: {file_path}")
            return

        content = path.read_text(encoding='utf-8')

        if content.startswith('---'):
            # File already has front matter (e.g. committed with it pre-included).
            # We still need to sanitize {{ in the body so Jekyll can build the page.
            fm_end = content.find('\n---\n', 3)
            if fm_end == -1:
                print(f"Skipping {file_path}: malformed front matter")
                return

            front_matter_block = content[:fm_end + 5]  # up to and including ---\n
            body = content[fm_end + 5:]

            escaped_body = escape_liquid_braces(body)
            if escaped_body == body:
                print(f"Skipping {file_path}: already up to date")
                return

            path.write_text(front_matter_block + escaped_body, encoding='utf-8')
            print(f"Sanitized Liquid braces in {file_path}")
            return

        # No front matter yet — extract title/date, escape content, prepend front matter
        lines = content.splitlines()
        title = "vLLM Daily Report"
        # Default to today if extraction fails
        date_str = datetime.now().strftime('%Y-%m-%d')

        # Try to find title line (starts with # )
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                # Try to extract date from title or filename
                # Title format: "vLLM 开发动态报告 - 2025-12-10"
                match = re.search(r'(\d{4}-\d{2}-\d{2})', title)
                if match:
                    date_str = match.group(1)
                break

        # If date not in title, try filename
        if date_str == datetime.now().strftime('%Y-%m-%d'):
            match = re.search(r'report-(\d{4}-\d{2}-\d{2})', path.name)
            if match:
                date_str = match.group(1)

        front_matter = f"""---
title: {title}
date: {date_str}
layout: default
---

{BACK_LINK}

"""
        escaped_content = escape_liquid_braces(content)
        new_content = front_matter + escaped_content
        path.write_text(new_content, encoding='utf-8')
        print(f"Successfully added front matter to {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_front_matter.py <file_path>")
        sys.exit(1)

    process_file(sys.argv[1])
