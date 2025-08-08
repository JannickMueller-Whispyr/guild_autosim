import csv
from collections import defaultdict

# Spec lists from append.py
INT_SPECS = {
    "arcane", "fire", "frost", "discipline", "holy", "shadow", "affliction", 
    "demonology", "destruction", "balance", "restoration", "devastation", 
    "preservation", "augmentation", "elemental", "enhancement"
}
AGI_SPECS = {
    "assassination", "outlaw", "subtlety", "feral", "guardian", "windwalker",
    "havoc", "vengeance", "beast_mastery", "marksmanship", "survival"
}
STR_SPECS = {
    "arms", "fury", "protection", "retribution", "blood", "frost", "unholy"
}
ALL_SPECS = INT_SPECS | AGI_SPECS | STR_SPECS

def reshape_results():
    data = defaultdict(dict)
    
    with open("results.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 4:
                dps = row[0]
                class_name = row[1]
                
                # Find spec position
                spec = None
                spec_index = -1
                for i in range(2, len(row)):
                    if row[i].lower() in ALL_SPECS:
                        spec = row[i]
                        spec_index = i
                        break
                
                if spec is None:
                    continue  # Skip if we can't find a valid spec
                
                # Find name (first uppercase word after spec)
                name = None
                name_index = -1
                for i in range(spec_index + 1, len(row)):
                    if row[i] and row[i][0].isupper():
                        name = row[i]
                        name_index = i
                        break
                
                if name is None:
                    continue  # Skip if we can't find a name
                
                # Combine hero talent (everything between spec and name)
                hero_talent_parts = row[spec_index + 1:name_index]
                hero_talent = "_".join(hero_talent_parts) if hero_talent_parts else "unknown"
                
                # Profile is everything after name, or "0pc" if empty
                profile_parts = row[name_index + 1:]
                profile = "".join(profile_parts) if profile_parts and any(profile_parts) else "0pc"
                
                # Create unique key for each character
                key = (class_name, spec, hero_talent, name)
                data[key][profile] = dps
    
    # Write reshaped data (overwrite results.csv)
    with open("results.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(["Class", "Spec", "Hero Talent", "Name", "0pc", "2pc", "4pc"])
        
        # Write data rows
        for (class_name, spec, hero_talent, name), profiles in data.items():
            row = [
                class_name,
                spec, 
                hero_talent,
                name,
                profiles.get("0pc", ""),
                profiles.get("2pc", ""),
                profiles.get("4pc", "")
            ]
            writer.writerow(row)
    
    print("Reshaped results saved to results.csv")

if __name__ == "__main__":
    reshape_results()