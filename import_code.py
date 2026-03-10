import os
import re


def extract_files(input_filepath: str, output_dir: str = "extracted_files"):
    """
    Parses a monolithic text file and splits it into individual files
    based on the 'FILE: <filename>' header format.
    """
    # 1. Ensure the main output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 2. Read the entire monolithic file
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{input_filepath}'")
        return

    # 3. Regex to match the exact header block
    # Matches: (start of string or newline) + (===...) + (FILE: name) + (===...)
    pattern = r'(?:^|\n)=+\nFILE:\s*(.+?)\n=+\n'

    # re.split returns a list: [text_before, filename1, content1, filename2, content2, ...]
    parts = re.split(pattern, content)

    # 4. Loop through the extracted filename and content pairs
    # We start at index 1 and step by 2 to grab each (filename, content) pair
    files_created = 0
    for i in range(1, len(parts), 2):
        filename = parts[i].strip()
        # Strip leading/trailing whitespace to clean up extra blank lines,
        # but ensure the file ends with a single newline
        file_content = parts[i + 1].strip() + '\n'

        output_path = os.path.join(output_dir, filename)

        # 5. Create subdirectories if the filename contains them
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 6. Write the content to the new file
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(file_content)

        print(f"Created: {output_path}")
        files_created += 1

    print(f"\nSuccess: Extracted {files_created} files into the '{output_dir}' directory.")


# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    # Define the name of the big text file containing your combined code
    INPUT_FILE = "all_python_files.txt"

    # Define where you want the split files to go
    OUTPUT_FOLDER = "match3_source"

    # Run the function
    extract_files(INPUT_FILE, output_dir=OUTPUT_FOLDER)
