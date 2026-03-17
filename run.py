import subprocess
import argparse
import sys

## This script orchestrates the entire simulation pipeline by running each step in sequence.
## It also accepts command-line arguments to control which steps to run and which input files to use
## Usage examples:
##      python run.py report_ids.txt --trinket  # Run with trinket bonuses instead of tier set bonuses
##      python run.py report_ids.txt             # Run with tier set bonuses (default)

def main():
    parser = argparse.ArgumentParser(description="Run the simulation pipeline.")
    # The txt_file argument is optional and defaults to "report_ids.txt"
    parser.add_argument("txt_file", nargs="?", default="report_ids.txt", help="Path to the report IDs file")

    # Optional Arguments to control which steps to run
    parser.add_argument("--trinket", action="store_true", help="Run append.py with the trinket input file instead of tier set bonuses")
    args = parser.parse_args()
    txt_file = args.txt_file
    
    # Run getInputs.py with the txt file
    print(f"Running getInputs.py for report IDs in: {txt_file}")
    subprocess.run(["python", "getInputs.py", txt_file], check=True)

    # Run cleanInputs.py
    print("Running cleanInputs.py to clean all .simc files...")
    subprocess.run(["python", "cleanInputs.py"], check=True)

    # Run append.py --tier or --trinket
    if args.trinket:
        print("Running append.py --trinket...")
        subprocess.run(["python", "append.py", "--trinket"], check=True)
    else:
        print("Running append.py --tier...")
        subprocess.run(["python", "append.py", "--tier"], check=True)

    # Run api.py --batch
    print("Running api.py --batch...")
    subprocess.run(["python", "api.py", "--batch"], check=True)
    
    # Run cleanResults.py
    print("Running cleanResults.py...")
    subprocess.run(["python", "cleanResults.py"], check=True)
    
    # Run reshapeResults.py
    if args.trinket:
        print("Running reshapeResults.py for trinkets...")
        subprocess.run(["python", "reshapeResults.py", "--gear"], check=True)
    else:
        print("Running reshapeResults.py...")
        subprocess.run(["python", "reshapeResults.py"], check=True)

if __name__ == "__main__":
    main()