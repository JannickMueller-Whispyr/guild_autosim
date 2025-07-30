import subprocess
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <report_ids.txt>")
        sys.exit(1)
    txt_file = sys.argv[1]

    # Run getInputs.py with the txt file
    print(f"Running getInputs.py for report IDs in: {txt_file}")
    subprocess.run(["python", "getInputs.py", txt_file], check=True)

    # Run cleanInputs.py
    print("Running cleanInputs.py to clean all .simc files...")
    subprocess.run(["python", "cleanInputs.py"], check=True)

if __name__ == "__main__":
    main()