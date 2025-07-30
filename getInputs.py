import requests
import sys
import os

VALID_CLASSES = [
    "hunter", "priest", "rogue", "warlock", "druid", "mage", "paladin",
    "shaman", "warrior", "deathknight", "demonhunter", "monk", "evoker"
]

def get_original_addon_input(report_id):
    url = f"https://www.raidbots.com/reports/{report_id}/data.json"
    print(f"Fetching: {url}")
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    response.raise_for_status()
    data = response.json()

    try:
        simbot = data["simbot"]
        addon_input = simbot["input"]
        id_active_hero_talent = simbot["meta"]["rawFormData"]["character"]["talentLoadouts"][0]["talents"]["activeSubtrees"][0]
        name_hero_talent1 = simbot["meta"]["rawFormData"]["character"]["talentLoadouts"][0]["talents"]["subTreeNodes"][0]["entries"][0]["name"]
        id_hero_talent1 = simbot["meta"]["rawFormData"]["character"]["talentLoadouts"][0]["talents"]["subTreeNodes"][0]["entries"][0]["traitSubTreeId"]
        name_hero_talent2 = simbot["meta"]["rawFormData"]["character"]["talentLoadouts"][0]["talents"]["subTreeNodes"][0]["entries"][1]["name"]
        id_hero_talent2 = simbot["meta"]["rawFormData"]["character"]["talentLoadouts"][0]["talents"]["subTreeNodes"][0]["entries"][1]["traitSubTreeId"]
    except KeyError:
        print("Could not find ['sim']['simbot']['input'] or activeSubtrees in JSON.")
        return None
    return addon_input, id_active_hero_talent, name_hero_talent1, id_hero_talent1, name_hero_talent2, id_hero_talent2

def extract_class_and_name(addon_input):
    for line in addon_input.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for class_name in VALID_CLASSES:
            if line.startswith(f"{class_name}="):
                char_name = line.split("=", 1)[1].replace('"', '')
                return class_name, char_name
        break  # Only check the first non-empty, non-comment line
    return None, None

def extract_spec(addon_input):
    for line in addon_input.splitlines():
        if line.startswith("spec="):
            return line.split("=", 1)[1].replace('"', '')
    return None

def get_active_hero_talent_name(id_active_hero_talent, id_hero_talent1, name_hero_talent1, id_hero_talent2, name_hero_talent2):
    if id_active_hero_talent == id_hero_talent1:
        return name_hero_talent1
    elif id_active_hero_talent == id_hero_talent2:
        return name_hero_talent2
    else:
        return "unknown_hero_talent"

if __name__ == "__main__":
    print("Script started")
    if len(sys.argv) < 2:
        print("Usage: python getInputs.py <report_ids.txt>")
        sys.exit(1)
    txt_file = sys.argv[1]
    output_folder = "simc_inputs"
    print(f"Creating folder (if needed): {os.path.abspath(output_folder)}")
    os.makedirs(output_folder, exist_ok=True)

    with open(txt_file, "r", encoding="utf-8") as f:
        report_ids = [line.strip() for line in f if line.strip()]

    for report_id in report_ids:
        print(f"Processing report ID: {report_id}")
        result = get_original_addon_input(report_id)
        if result is None:
            print(f"Skipping {report_id} due to missing data.")
            continue
        addon_input, id_active_hero_talent, name_hero_talent1, id_hero_talent1, name_hero_talent2, id_hero_talent2 = result
        char_class, char_name = extract_class_and_name(addon_input)
        spec = extract_spec(addon_input)
        active_hero_talent_name = get_active_hero_talent_name(
            id_active_hero_talent, id_hero_talent1, name_hero_talent1, id_hero_talent2, name_hero_talent2
        )
        safe_herotalent = active_hero_talent_name.replace(" ", "").lower() if active_hero_talent_name else "unknownherotalent"
        safe_class = char_class if char_class else "unknownclass"
        safe_spec = spec if spec else "unknownspec"
        safe_name = char_name if char_name else "unknownname"
        output_filename = f"{safe_class}_{safe_spec}_{safe_herotalent}_{safe_name}.simc"
        output_path = os.path.join(output_folder, output_filename)
        print(f"Saving file to: {os.path.abspath(output_path)}")
        with open(output_path, "w", encoding="utf-8") as outf:
            outf.write(addon_input)
        # Override the {class}= field in addon_input
        new_name = f"{safe_class}_{safe_spec}_{safe_herotalent}_{safe_name}"
        addon_input = "\n".join(
            [f"{safe_class}={new_name}" if line.startswith(f"{safe_class}=") else line for line in addon_input.splitlines()]
        )
        with open(output_path, "w", encoding="utf-8") as outf:
            outf.write(addon_input)