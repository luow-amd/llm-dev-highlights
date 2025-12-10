import sys
import re
from pathlib import Path
from datetime import datetime

def process_file(file_path):
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"File not found: {file_path}")
            return

        content = path.read_text(encoding='utf-8')
        
        # Check if already has front matter
        if content.startswith('---'):
            print(f"Skipping {file_path}: already has front matter")
            return

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

[<< Back to Home]({{{{ site.baseurl }}}}/)

"""
        new_content = front_matter + content
        path.write_text(new_content, encoding='utf-8')
        print(f"Successfully added Front Matter to {file_path}")
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_front_matter.py <file_path>")
        sys.exit(1)
    
    process_file(sys.argv[1])
