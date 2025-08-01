import subprocess
import sys

def main():
    # Use default file if no argument provided
    if len(sys.argv) > 1:
        txt_file = sys.argv[1]
    else:
        txt_file = "report_ids.txt"
    
    # Run getInputs.py with the txt file
    print(f"Running getInputs.py for report IDs in: {txt_file}")
    subprocess.run(["python", "getInputs.py", txt_file], check=True)

    # Run cleanInputs.py
    print("Running cleanInputs.py to clean all .simc files...")
    subprocess.run(["python", "cleanInputs.py"], check=True)

    # Run append.py --tier
    print("Running append.py --tier...")
    subprocess.run(["python", "append.py", "--tier"], check=True)

    # Run api.py --batch
    print("Running api.py --batch...")
    subprocess.run(["python", "api.py", "--batch"], check=True)
    
    # Run cleanResults.py
    print("Running cleanResults.py...")
    subprocess.run(["python", "cleanResults.py"], check=True)

if __name__ == "__main__":
    main()