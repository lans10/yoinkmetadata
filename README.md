# yoinkmetadata
Yoinkmetadata is a Python script designed to remove metadata from files. It can compare metadata between two files, and give a list of unique metadata tags that it encountered in it's runtime. It can enumerate and view/remove metadata tags from all files in a specified folder, and allows the user to compare it with backup or differing version of the same files. 
It also allows for cracking password for encrypted PDF files, and corrects file extensions if it does not match what the tools expect as the correct filetype.

## Requirements
- Python 3.x
- `exiftool`
- `PyPDF2`
- `qpdf`
- `mat2`
- `pdfcrack`
- RockYou wordlist: https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

```bash
pip install -r requirements.txt
```

## Usage 
```bash
python yoinkmetadata.py <action> <path>
```

- `<action>`: Specify the action to perform. Available actions include:
	- `view`: View metadata of a file.
	- `scrub` or `clean`: Clean metadata from a file.
	- `compare`: Compare metadata between two files.
	- `magic` or `both`: Perform metadata scrubbing and analysis on a directory.
	- `verify` or `test`: Test metadata comparison between two directories.
- `<path>`: Path to the file or directory.

## Examples
- View metadata of a file
```bash
python yoinkmetadata.py view /path/to/file
```
- View metadata of all files in a folder
```bash
python yoinkmetadata.py view /path/to/folder
```
- Clean metadata from a file
```bash
python yoinkmetadata.py scrub /path/to/file
```
- Clean metadata of all files in a folder
```bash
python yoinkmetadata.py scrub /path/to/folder
```
- Perform metadata scrubbing and analysis on a directory:
```bash
python yoinkmetadata.py magic /path/to/folder
```
- Test metadata comparison between two directories:
```bash
python yoinkmetadata.py test /path/to/folder
```s

## Note
- Ensure all necessary dependencies are installed and accessible in the system's PATH.
- For password cracking functionality, provide a custom wordlist file (rockyou.txt by default) and ensure the necessary tool pdfcrack is available.
- Skipping a tool's execution if it's not installed/present is a consideration for future releases. However, exiftool is the core of this script and is essential.
- The test method currently is hardcoded for a personal project.	





