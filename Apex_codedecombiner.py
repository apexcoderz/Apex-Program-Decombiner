#!/usr/bin/env python3
import argparse
import logging
import re
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[96m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_MAGENTA = "\033[95m"
COLOR_DIM = "\033[2m"

MARKDOWN_HEADER_PATTERN = r'^##\s+.+?\s*\n```'
C_COMMENT_HEADER_PATTERN = r'/\*\s*={10,}\s*\*?\s*MODULE:\s*.+?\s*\*?\s*={10,}\s*\*/'


def supports_color() -> bool:
    return sys.stdout.isatty()


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{COLOR_RESET}" if supports_color() else text


def print_banner() -> None:
    banner = r"""
    ___    ____     __________  ____  ______   ____  ________________  __  _______  _____   ____________
   /   |  / __ \   / ____/ __ \/ __ \/ ____/  / __ \/ ____/ ____/ __ \/  |/  / __ )/  _/ | / / ____/ __ \
  / /| | / /_/ /  / /   / / / / / / / __/    / / / / __/ / /   / / / / /|_/ / __  |/ //  |/ / __/ / /_/ /
 / ___ |/ ____/  / /___/ /_/ / /_/ / /___   / /_/ / /___/ /___/ /_/ / /  / / /_/ // // /|  / /___/ _, _/
/_/  |_/_/       \____/\____/_____/_____/  /_____/_____/\____/\____/_/  /_/_____/___/_/ |_/_____/_/ |_|
"""
    print(colorize(banner, COLOR_CYAN))
    print(colorize("  Source Code Decombiner  ·  aditya projects.id   ·   apexcoderz ", COLOR_DIM))


def print_easter_egg() -> None:
    art = r'''
      .-""""""-.
    .'          '.
   /   O      O   \      "Code with love."
  :                 :
  |                 |     built by  apexcoderz x AP
  :    \        /   :     for       Everyone
   \    '.____.'    /
    '.            .'
      '-.......-'
'''
    print(colorize(art, COLOR_MAGENTA))


def render_progress(current: int, total: int, label: str, width: int = 30) -> None:
    ratio = current / total if total else 1
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    line = f"\r  [{colorize(bar, COLOR_GREEN)}] {current}/{total}  {colorize(label, COLOR_DIM)}"
    pad = max(0, shutil.get_terminal_size((80, 20)).columns - len(line) + 20)
    sys.stdout.write(line + " " * pad)
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")


def detect_format(content: str) -> Optional[str]:
    if re.search(MARKDOWN_HEADER_PATTERN, content, re.MULTILINE):
        return 'markdown'
    if re.search(C_COMMENT_HEADER_PATTERN, content, re.MULTILINE | re.DOTALL):
        return 'c_comment'
    return None


def split_markdown_format(content: str) -> List[Tuple[str, str]]:
    pattern = r'^##\s+(.+?)\s*\n```(?:\w+)?\n(.*?)```'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    results = []
    for filename, file_content in matches:
        filename = filename.strip()
        if file_content.endswith('\n\n'):
            file_content = file_content[:-1]
        elif not file_content.endswith('\n'):
            file_content += '\n'
        results.append((filename, file_content))

    return results


def split_c_comment_format(content: str) -> List[Tuple[str, str]]:
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
            end_pos = start_pos + next_match.start() if next_match else len(content)
        else:
            closing_pattern = r'/\*\s*={10,}\s*\*/'
            closing_match = re.search(closing_pattern, content[start_pos:])
            end_pos = start_pos + closing_match.start() if closing_match else len(content)

        file_content = content[start_pos:end_pos].strip()
        if file_content and not file_content.endswith('\n'):
            file_content += '\n'

        results.append((module_name, file_content))

    return results


def split_program_file(input_file: Path, output_folder: Path) -> bool:
    if not input_file.exists():
        logging.error(f"Input file not found: {input_file}")
        return False

    output_folder.mkdir(parents=True, exist_ok=True)

    try:
        content = input_file.read_text(encoding='utf-8')
    except Exception as e:
        logging.error(f"Failed to read input file: {e}")
        return False

    format_type = detect_format(content)
    if format_type is None:
        logging.error("Unable to detect file format (markdown or c_comment)")
        return False

    logging.info(colorize(f"Detected format: {format_type}", COLOR_YELLOW))

    file_list = split_markdown_format(content) if format_type == 'markdown' else split_c_comment_format(content)

    if not file_list:
        logging.error("No valid file blocks found in the input file")
        return False

    created_files = []

    for index, (filename, file_content) in enumerate(file_list, start=1):
        render_progress(index, len(file_list), filename)
        output_path = output_folder / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            output_path.write_text(file_content, encoding='utf-8')
            created_files.append(str(output_path))
        except Exception as e:
            logging.error(f"Failed to write file '{filename}': {e}")
        time.sleep(0.02)

    if created_files:
        logging.info(colorize(f"Successfully split {len(created_files)} files into '{output_folder}'", COLOR_GREEN))
        return True

    logging.warning("No files were created")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split a combined Markdown file back into individual source files.",
        epilog="aditya projects.id"
    )
    parser.add_argument("input_file", type=Path, nargs='?', help="Input Markdown file to split")
    parser.add_argument("output_folder", type=Path, nargs='?', help="Output directory for split files")
    parser.add_argument("--credits", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.credits or (args.input_file and str(args.input_file) in ("42", "apexcoderz", "aditya")):
        print_easter_egg()
        sys.exit(0)

    if args.input_file is None or args.output_folder is None:
        parser.error("the following arguments are required: input_file, output_folder")

    print_banner()
    success = split_program_file(args.input_file, args.output_folder)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
