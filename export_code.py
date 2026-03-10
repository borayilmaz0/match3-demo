import os

def write_python_files_to_txt(source_folder: str, output_file: str):
    with open(output_file, "w", encoding="utf-8") as out:
        for filename in os.listdir(source_folder):
            if filename.endswith(".py"):
                file_path = os.path.join(source_folder, filename)

                out.write(f"\n{'='*80}\n")
                out.write(f"FILE: {filename}\n")
                out.write(f"{'='*80}\n\n")

                with open(file_path, "r", encoding="utf-8") as f:
                    out.write(f.read())
                    out.write("\n")

# Example usage
write_python_files_to_txt("./", "all_python_files.txt")
