import os

def clean_simc_file_inplace(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        if line.startswith("name="):
            break
        if line.strip().startswith("#"):
            continue
        cleaned_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

if __name__ == "__main__":
    folder = "simc_inputs"
    for filename in os.listdir(folder):
        if filename.endswith(".simc"):
            filepath = os.path.join(folder, filename)
            clean_simc_file_inplace(filepath)
            print(f"Cleaned: {filepath}")