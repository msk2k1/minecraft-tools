import os, shutil, sys

# constants
INSTANCES_FOLDER = os.path.realpath("/media/matt/games/PrismLauncher/instances/")
MIGRATE = ["resourcepacks", "saves", "screenshots", "mods", "shaderpacks"]
COPY_OPTIONS = True

# pick a Minecraft instance and verify its integrity.
# returns minecraft/.minecraft folder path for the chosen instance.
def pick_instance(choices: list, prompt_is_for: str):

    # selection prompt
    while True:
        index = input(f"Enter numerical index of {prompt_is_for} instance: ")
        try: selection = os.path.join(INSTANCES_FOLDER, choices[int(index)]); break
        except: print("Invalid selection.")

    # confirm there is not both a "minecraft" and ".minecraft" folder for the instance.
    if os.path.exists(os.path.join(selection, "minecraft")) and os.path.exists(os.path.join(selection, ".minecraft")):
        raise Exception("both a 'minecraft' and '.minecraft' folder exist in this instance. Delete one and try again.")
    
    # confirm existence of 'minecraft' or '.minecraft' folder. Check for '.minecraft' first.
    if os.path.exists(os.path.join(selection, ".minecraft")):
        return os.path.join(selection, ".minecraft")
    elif os.path.exists(os.path.join(selection, "minecraft")):
        return os.path.exists(os.path.join(selection, "minecraft"))
    else:
        raise Exception("Folder not detected as a minecraft instance. (No 'minecraft' or '.minecraft' subfolder)")

### main execution starts here ###

# get migration source and destination instances
instances = next(os.walk(INSTANCES_FOLDER))[1]
for index, name in enumerate(instances): print(f"{index:02d} | {name}") # list available instances
try:
    src = pick_instance(instances, "source")
    dst = pick_instance(instances, "destination")
    if src == dst: raise Exception("Source and destination instances are the same.")
except Exception as e: print(f"Error selecting instances: {e}"); sys.exit(1)

# migrate each subfolder in MIGRATE list
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