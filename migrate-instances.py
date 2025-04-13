import os, shutil, sys

# function: prompt for selection given a list of choices.
def getSelection(choices: list, prompt_is_for: str):
    while True:
        index = input(f"Enter numerical index of {prompt_is_for} instance: ")
        try: index = int(index); break
        except: print("Invalid selection.")
    return choices[index]

# constants
INSTANCES_FOLDER = os.path.realpath("/media/matt/games/PrismLauncher/instances/")
MIGRATE = ["resourcepacks", "saves", "screenshots", "mods", "shaderpacks"]
COPY_OPTIONS = True

### main execution starts here ###

# detect instances (top-level folders in root); prompt for choice
instances = next(os.walk(INSTANCES_FOLDER))[1]
for index, name in enumerate(instances): print(f'{index:02d}', "|", name)
src = os.path.realpath(os.path.join(INSTANCES_FOLDER, getSelection(instances, "source"), ".minecraft"))
dst = os.path.realpath(os.path.join(INSTANCES_FOLDER, getSelection(instances, "destination"), ".minecraft"))

# selection integrity checks
try:
    if (not os.path.exists(src)) or (not os.path.exists(dst)): raise Exception("At least one of the folders given detected as not a minecraft instance: no .minecraft folder")
    if src == dst: raise Exception("Source and destination instances are the same.")
except Exception as e: print(e); sys.exit(1)

# migrate folders from src to dst
for folder in MIGRATE:
    print(f"Migrating folder: {folder}...")
    if not os.path.exists(os.path.join(src,folder)): print("### Folder does not exist in source instance:", folder) # verify folder exists in source
    else:
        items = [os.path.join(src,folder,i) for i in os.listdir(os.path.join(src,folder))]
        try:
            migrateDest = os.path.join(dst,folder)
            os.makedirs(migrateDest, exist_ok=True)
            for i in items: 
                shutil.move(i, migrateDest)
                print(f"Moved item {os.path.basename(i)} to {migrateDest}")
        except Exception as e: print(f"### Failed to move {os.path.basename(i)}: {e}")

# copy over options.txt
if COPY_OPTIONS:
    try:
        print("Copying options.txt...")
        os.remove(os.path.join(dst,"options.txt"))
        shutil.copy(
            os.path.join(src,"options.txt"),
            os.path.join(dst,"options.txt")
        )
    except Exception as e: print(f"### Failed to move options.txt: {e}")

print("\nMigration finished. Remember to install mod loader and update mods!")
sys.exit(0)