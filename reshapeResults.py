import csv
import sys
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

def reshape_tier_sets():
    """Reshape for tier set comparison (0pc, 2pc, 4pc)"""
    data = defaultdict(dict)
    
    with open("results.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 4:
                dps = row[0]
                class_name = row[1]
                
                # Find spec position (handle beast_mastery special case)
                spec = None
                spec_index = -1
                for i in range(2, len(row)):
                    if row[i].lower() in ALL_SPECS:
                        spec = row[i]
                        spec_index = i
                        break
                    elif (i < len(row) - 1 and 
                          row[i].lower() == "beast" and 
                          row[i + 1].lower() == "mastery"):
                        spec = "beast_mastery"
                        spec_index = i + 1
                        break
                
                if spec is None:
                    continue
                
                # Find name (first uppercase word after spec)
                name = None
                name_index = -1
                for i in range(spec_index + 1, len(row)):
                    if row[i] and row[i][0].isupper():
                        name = row[i]
                        name_index = i
                        break
                
                if name is None:
                    continue
                
                # Combine hero talent (everything between spec and name)
                hero_talent_parts = row[spec_index + 1:name_index]
                hero_talent = "_".join(hero_talent_parts) if hero_talent_parts else "unknown"
                
                # Profile is everything after name, or "0pc" if empty
                profile_parts = row[name_index + 1:]
                profile = "".join(profile_parts) if profile_parts and any(profile_parts) else "0pc"
                
                # Create unique key for each character
                key = (class_name, spec, hero_talent, name)
                data[key][profile] = dps
    
    # Write reshaped data
    with open("results.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Class", "Spec", "Hero Talent", "Name", "0pc", "2pc", "4pc"])
        
        for (class_name, spec, hero_talent, name), profiles in data.items():
            row = [
                class_name, spec, hero_talent, name,
                profiles.get("0pc", ""),
                profiles.get("2pc", ""),
                profiles.get("4pc", "")
            ]
            writer.writerow(row)
    
    print("Reshaped tier set results saved to results.csv")

def reshape_gear():
    """Reshape for gear comparison (baseline vs individual items in different slots)"""
    data = defaultdict(lambda: defaultdict(dict))
    
    with open("results.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 5:
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
                    elif (i < len(row) - 1 and 
                          row[i].lower() == "beast" and 
                          row[i + 1].lower() == "mastery"):
                        spec = "beast_mastery"
                        spec_index = i + 1
                        break
                
                if spec is None:
                    continue
                
                # Find name
                name = None
                name_index = -1
                for i in range(spec_index + 1, len(row)):
                    if row[i] and row[i][0].isupper():
                        name = row[i]
                        name_index = i
                        break
                
                if name is None:
                    continue
                
                # Combine hero talent
                hero_talent_parts = row[spec_index + 1:name_index]
                hero_talent = "_".join(hero_talent_parts) if hero_talent_parts else "unknown"
                
                # Process gear info after name
                gear_parts = row[name_index + 1:]
                
                # Create unique key for each character
                char_key = (class_name, spec, hero_talent, name)
                
                if not gear_parts or not any(gear_parts):
                    # Baseline case - store in all item entries
                    data[char_key]["baseline"]["baseline"] = dps
                else:
                    # Remove stat and armor type indicators
                    filtered_parts = []
                    for part in gear_parts:
                        if part.lower() not in ["agi", "str", "int", "cloth", "leather", "mail", "plate"]:
                            filtered_parts.append(part)
                    
                    if not filtered_parts:
                        continue
                    
                    # Find slot (trinket1, trinket2, etc.)
                    slot = None
                    slot_index = -1
                    for i, part in enumerate(filtered_parts):
                        if part.lower().startswith(("trinket", "ring", "neck", "weapon", "head", "chest", 
                                                  "legs", "feet", "hands", "waist", "wrist", "shoulder", 
                                                  "back", "main_hand", "off_hand")):
                            slot = part.lower()
                            slot_index = i
                            break
                    
                    if slot is None:
                        continue
                    
                    # Combine item name (everything after slot)
                    item_parts = filtered_parts[slot_index + 1:]
                    item_name = "_".join(item_parts) if item_parts else "unknown_item"
                    
                    # Store DPS for this item and slot combination
                    data[char_key][item_name][slot] = dps
    
    # Write reshaped data
    with open("results.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(["Class", "Spec", "Hero Talent", "Name", "Baseline", "Trinket_Name", "Trinket1", "Trinket2"])
        
        # Write data rows
        for (class_name, spec, hero_talent, name), items in data.items():
            baseline_dps = items.get("baseline", {}).get("baseline", "")
            
            # Get all unique items (excluding baseline)
            trinket_items = {item for item in items.keys() if item != "baseline"}
            
            for item_name in sorted(trinket_items):
                trinket_data = items[item_name]
                row = [
                    class_name,
                    spec, 
                    hero_talent,
                    name,
                    baseline_dps,
                    item_name,
                    trinket_data.get("trinket1", ""),
                    trinket_data.get("trinket2", "")
                ]
                writer.writerow(row)
    
    print("Reshaped gear results saved to results.csv")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--gear":
        reshape_gear()
    else:
        reshape_tier_sets()

if __name__ == "__main__":
    main()