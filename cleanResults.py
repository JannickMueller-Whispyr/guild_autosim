import os
import json
import csv

def process_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = []
    # Get baseline profile
    try:
        baseline_mean = data["sim"]["players"][0]["collected_data"]["dps"]["mean"]
        baseline_name = data["sim"]["players"][0]["name"]
        if baseline_mean is not None and baseline_name is not None:
            combined = f"{baseline_mean}_{baseline_name}"
            combined = combined.replace("_", ",")
            results.append(combined)
    except (KeyError, TypeError):
        pass
    # Get alternate profiles
    try:
        profilesets = data["sim"]["profilesets"]["results"]
        for entry in profilesets:
            mean = entry.get("mean")
            name = entry.get("name")
            if mean is not None and name is not None:
                combined = f"{mean}_{name}"
                combined = combined.replace("_", ",")
                results.append(combined)
    except (KeyError, TypeError):
        pass
    return results

def main():
    results_folder = "results"
    all_lines = []
    for filename in os.listdir(results_folder):
        if filename.endswith(".json"):
            filepath = os.path.join(results_folder, filename)
            lines = process_json_file(filepath)
            all_lines.extend(lines)
    # Write to results.csv
    with open("results.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for line in all_lines:
            writer.writerow([value.strip() for value in line.split(",")])
    print("results.csv created.")

if __name__ == "__main__":
    main()