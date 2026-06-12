# Source Code Decombiner

A robust Python-based Command-Line Interface (CLI) utility designed to split and extract a single aggregated repository file (`program.md` or a C-comment based file) back into its original individual component files, complete with directory tree reconstruction.

## Architecture & Workflow
1. **Input Stream Analysis:** Sequentially reads the target aggregate file utilizing secure UTF-8 encoding.
2. **Automated Detection Engine:** Utilizes pre-compiled Regular Expression (`re`) engines to detect Markdown delimiters (`## path`) or C-style Header Blocks.
3. **Path Reconstruction:** Recursively isolates relative file path names.
4. **Clean I/O Isolation:** Dynamically recreates missing wrapper subdirectories prior to flushing the source code to physical storage.

## Installation
This application purely utilizes the standard built-in libraries of Python 3.6 and above (No external dependencies).
```bash
# Clone the repository
git clone [https://github.com/apexcoderz/Apex-Program-Decombiner](https://github.com/apexcoderz/Apex-Program-Decombiner.git)
cd Apex-Program-Decombiner

# Grant execution permissions to the script
chmod +x src/Apex_codedecombiner.py
```

## Usage
Run the utility by providing the path to the target aggregate file along with the destination directory for extraction:

```bash
# Standard extraction of the program.md document
python3 src/Apex_codedecombiner.py program.md ./src_extracted

# Using the executable script directly
./src/Apex_codedecombiner.py combined_project.txt ./output_directory
```

## Contributing
We highly appreciate contributions from the open-source community:
1. Fork this repository.
2. Create a new feature branch (`git checkout -b feature/support-new-syntax`).
3. Commit your changes following the Semantic Commit Messages guidelines.
4. Submit a Pull Request (PR) for a comprehensive review by the Maintainer.
```

#### Directory Tree Layout
```text
source-decombiner/
├── .gitignore
├── LICENSE
├── README.md
├── docs/
│   └── architecture_spec.md
└── src/
    └── Apex_codedecombiner.py
```

#### Semantic Commit Guidelines
* **`refactor: pre-compile regular expression objects for parsing speed`** (Improves text block search performance).
* **`feat: add dynamic directory path generation inside split handler`** (Adds automatic folder creation functionality).
* **`fix: handle potential UnicodeDecodeError with structural fallback safely`** (Fixes non-UTF8 file reading failures).

#### License Recommendation
**Apache 2.0 License**
*Justification:* The Apache 2.0 License is recommended because, in addition to providing free rights to use, modify, and redistribute like the MIT license, it also provides formal legal protection regarding patent rights (grant of patent rights) from contributors to application users. Highly ideal for repository management utilities.