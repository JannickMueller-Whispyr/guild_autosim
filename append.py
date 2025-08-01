import os
import sys
import argparse

# Define valid classes/specs for cloth and int
CLOTH_CLASSES = {"mage", "priest", "warlock"}
LEATHER_CLASSES = {"rogue", "druid", "monk", "demonhunter"}
MAIL_CLASSES = {"hunter", "shaman", "evoker"}
PLATE_CLASSES = {"warrior", "paladin", "deathknight"}
INT_SPECS = {
    "arcane", "fire", "frost", "balance", "restoration", "discipline", "holy", "shadow",
    "elemental", "affliction", "demonology", "destruction", "mistweaver",
    "devastation", "preservation", "augmentation"
}
AGI_SPECS = {
    "assassination", "outlaw", "subtlety", "feral", "guardian", "windwalker",
    "havoc", "vengeance", "beast_mastery", "marksmanship", "survival"
}
STR_SPECS = {
    "arms", "fury", "protection", "retribution", "blood", "frost", "unholy"
}
HERO_TALENTS = {
    "aldrachi_reaver", "deathbringer", "rider_of_the_apocalypse", "sanlayn", "felscarred",
    "druid_of_the_claw", "elunes_chosen", "keeper_of_the_grove", "wildstalker", "chronowarden", "flameshaper", "scalecommander",
    "dark_ranger", "pack_leader", "sentinel", "frostfire", "spellslinger", "sunfury", "conduit_of_the_celestials",
    "master_of_harmony", "shadopan", "herald_of_the_sun", "lightsmith", "templar", "archon", "oracle", "voidweaver",
    "deathstalker", "fatebound", "trickster", "farseer", "stormbringer", "totemic", "diabolist", "hellcaller",
    "soul_harvester", "colossus", "mountain_thane", "slayer"
}

def parse_append_file(txt_file):
    with open(txt_file, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]
    pairs = []
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith("#"):
            pairs.append((lines[i], lines[i+1]))
            i += 2
        else:
            i += 1
    return pairs

def should_append(filename, comment):
    fname = filename.lower()
    comment = comment.lower()
    # Armor type checks
    if "cloth" in comment:
        if not any(f"_{cls}_" in f"_{fname}_" for cls in CLOTH_CLASSES):
            return False
    if "leather" in comment:
        if not any(f"_{cls}_" in f"_{fname}_" for cls in LEATHER_CLASSES):
            return False
    if "mail" in comment:
        if not any(f"_{cls}_" in f"_{fname}_" for cls in MAIL_CLASSES):
            return False
    if "plate" in comment:
        if not any(f"_{cls}_" in f"_{fname}_" for cls in PLATE_CLASSES):
            return False
    # Stat type checks (same logic can be applied if needed)
    if "int" in comment:
        if not any(f"_{spec}_" in f"_{fname}_" for spec in INT_SPECS):
            return False
    if "agi" in comment:
        if not any(f"_{spec}_" in f"_{fname}_" for spec in AGI_SPECS):
            return False
    if "str" in comment:
        if not any(f"_{spec}_" in f"_{fname}_" for spec in STR_SPECS):
            return False
    return True

def format_copy_line(filename, comment):
    # Remove extension
    base_filename = os.path.splitext(filename)[0]
    # Remove '#' and extra spaces, replace spaces with underscores, lowercase
    x = comment.lstrip("#").strip().replace(" ", "_").lower()
    return f"profileset.\"{base_filename}_{x}\"+="

def append_to_simc_files(txt_file, folder="simc_inputs"):
    pairs = parse_append_file(txt_file)
    whitespace = "\n" * 20
    whitespace_with_ptr = whitespace + "\nptr=1\n"

    for filename in os.listdir(folder):
        if filename.endswith(".simc"):
            filepath = os.path.join(folder, filename)
            # Read file and remove previous appended info if present
            with open(filepath, "r", encoding="utf-8") as simc_file:
                content = simc_file.read()
            # Find the start of the appended section (20 consecutive newlines)
            append_marker = whitespace
            marker_index = content.find(append_marker)
            if marker_index != -1:
                # Remove everything from the marker onwards
                content = content[:marker_index].rstrip("\n")

            # Prepare new appended info
            to_append = []
            for comment, line in pairs:
                if should_append(filename, comment):
                    copy_line = format_copy_line(filename, comment)
                    to_append.append(comment)
                    to_append.append(f"{copy_line}{line}")
            if to_append:
                with open(filepath, "w", encoding="utf-8") as simc_file:
                    simc_file.write(content + whitespace_with_ptr + "\n".join(to_append) + "\n")
                print(f"Appended to: {filepath}")

def append_tier_set_bonuses(folder="simc_inputs"):
    whitespace = "\n" * 20
    for filename in os.listdir(folder):
        if filename.endswith(".simc"):
            filepath = os.path.join(folder, filename)
            with open(filepath, "r", encoding="utf-8") as simc_file:
                content = simc_file.read()
            marker_index = content.find(whitespace)
            if marker_index != -1:
                content = content[:marker_index].rstrip("\n")
            base_filename = os.path.splitext(filename)[0]
            hero_talent = None
            normalized_base = base_filename.replace("_", "").lower()
            for talent in HERO_TALENTS:
                normalized_talent = talent.replace("_", "").lower()
                if normalized_talent in normalized_base:
                    hero_talent = talent  # Use the original, with underscores
                    break
            if not hero_talent:
                hero_talent = "unknown"
            blocks = []
            # 2+2
            blocks.append(f"profileset.\"{base_filename}_2+2pc\"+=set_bonus=thewarwithin_season_2_2pc=1")
            blocks.append(f"profileset.\"{base_filename}_2+2pc\"+=set_bonus=thewarwithin_season_2_4pc=0")
            blocks.append(f"profileset.\"{base_filename}_2+2pc\"+=set_bonus=name=thewarwithin_season_3,pc=2,hero_tree={hero_talent},enable=1")
            blocks.append(f"profileset.\"{base_filename}_2+2pc\"+=set_bonus=name=thewarwithin_season_3,pc=4,hero_tree={hero_talent},enable=0")
            # 4pc
            blocks.append(f"profileset.\"{base_filename}_4pc\"+=set_bonus=thewarwithin_season_2_2pc=0")
            blocks.append(f"profileset.\"{base_filename}_4pc\"+=set_bonus=thewarwithin_season_2_4pc=0")
            blocks.append(f"profileset.\"{base_filename}_4pc\"+=set_bonus=name=thewarwithin_season_3,pc=2,hero_tree={hero_talent},enable=1")
            blocks.append(f"profileset.\"{base_filename}_4pc\"+=set_bonus=name=thewarwithin_season_3,pc=4,hero_tree={hero_talent},enable=1")
            set_bonus_block = "\n".join(blocks)
            with open(filepath, "w", encoding="utf-8") as simc_file:
                simc_file.write("ptr=1\n" + content + whitespace + set_bonus_block + "\n")
            print(f"Appended tier set bonuses to: {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_txt", nargs="?", help="Input .txt file to append")
    parser.add_argument("--tier", action="store_true", help="Append tier set bonuses instead of input file")
    args = parser.parse_args()

    if args.tier:
        append_tier_set_bonuses()
    elif args.input_txt:
        append_to_simc_files(args.input_txt)
    else:
        print("Usage: python append.py <input.txt> [--tier]")
        sys.exit(1)