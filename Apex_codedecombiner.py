#!/usr/bin/env python3
"""
Splits a combined Markdown file back into individual source files.
Created with enhancements by apexcoderz
"""
import argparse
import logging
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Configure logging for professional CLI output
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def detect_format(content: str) -> str:
    """
    Detects which format the file uses: 'markdown' or 'c_comment'.
    Returns None if no format is detected.
    """
    # Check for markdown format (## filename)
    markdown_pattern = r'^##\s+.+?\s*\n```'
    if re.search(markdown_pattern, content, re.MULTILINE):
        return 'markdown'
    
    # Check for C-style comment format (/* ===... MODULE: name ... ===*/)
    c_comment_pattern = r'/\*\s*={10,}\s*\*?\s*MODULE:\s*.+?\s*\*?\s*={10,}\s*\*/'
    if re.search(c_comment_pattern, content, re.MULTILINE | re.DOTALL):
        return 'c_comment'
    
    return None

def split_markdown_format(content: str) -> List[Tuple[str, str]]:
    """
    Splits content in markdown format.
    Returns list of (filename, content) tuples.
    """
    pattern = r'^##\s+(.+?)\s*\n```(?:\w+)?\n(.*?)```'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    results = []
    for filename, file_content in matches:
        filename = filename.strip()
        # Clean up content
        if file_content.endswith('\n\n'):
            file_content = file_content[:-1]
        elif not file_content.endswith('\n'):
            file_content += '\n'
        results.append((filename, file_content))
    
    return results

def split_c_comment_format(content: str) -> List[Tuple[str, str]]:
    """
    Splits content in C-style comment format.
    Returns list of (filename, content) tuples.
    """
    header_pattern = r'/\*\s*(={10,})\s*\*?\s*MODULE:\s*(.+?)\s*\*?\s*={10,}\s*\*/'
    
    headers = []
    for match in re.finditer(header_pattern, content, re.MULTILINE | re.DOTALL):
        module_name = match.group(2).strip()
        start_pos = match.end()
        headers.append((module_name, start_pos))
    
    if not headers:
        return []
    
    results = []
    
    for i, (module_name, start_pos) in enumerate(headers):
        if i < len(headers) - 1:
            next_separator_pattern = r'/\*\s*={10,}'
            next_match = re.search(next_separator_pattern, content[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = len(content)
        else:
            closing_pattern = r'/\*\s*={10,}\s*\*/'
            closing_match = re.search(closing_pattern, content[start_pos:])
            if closing_match:
                end_pos = start_pos + closing_match.start()
            else:
                end_pos = len(content)
        
        file_content = content[start_pos:end_pos].strip()
        
        if file_content and not file_content.endswith('\n'):
            file_content += '\n'
        
        results.append((module_name, file_content))
    
    return results

def split_program_file(input_file: Path, output_folder: Path) -> bool:
    """
    Splits a combined file into individual source files.
    Supports both markdown and C-style comment formats.
    Maintains directory structure from the file paths.
    """
    if not input_file.exists():
        logging.error(f"Input file not found: {input_file}")
        return False
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    try:
        content = input_file.read_text(encoding='utf-8')
    except Exception as e:
        logging.error(f"Failed to read input file: {e}")
        return False
    
    # Detect format
    format_type = detect_format(content)
    
    if format_type is None:
        logging.error("Unable to detect file format (markdown or c_comment)")
        return False
    
    logging.info(f"Detected format: {format_type}")
    
    # Split based on format
    if format_type == 'markdown':
        file_list = split_markdown_format(content)
    else:
        file_list = split_c_comment_format(content)
    
    if not file_list:
        logging.error("No valid file blocks found in the input file")
        return False
    
    created_files = []
    
    for filename, file_content in file_list:
        output_path = output_folder / filename
        
        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            output_path.write_text(file_content, encoding='utf-8')
            created_files.append(str(output_path))
            logging.info(f"Created: {output_path}")
        except Exception as e:
            logging.error(f"Failed to write file '{filename}': {e}")
    
    if created_files:
        logging.info(f"Successfully split {len(created_files)} files into '{output_folder}'")
        return True
    else:
        logging.warning("No files were created")
        return False

def main() -> None:
    """CLI entry point utilizing argparse for robust flag handling."""
    parser = argparse.ArgumentParser(
        description="Split a combined Markdown file back into individual source files.",
        epilog="Built with apexcoderz enhancements"
    )
    parser.add_argument("input_file", type=Path, help="Input Markdown file to split")
    parser.add_argument("output_folder", type=Path, help="Output directory for split files")
    
    args = parser.parse_args()
    
    success = split_program_file(args.input_file, args.output_folder)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
