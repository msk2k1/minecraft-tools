import os, shutil, json

def getSelection(choices: list, promptFor: str):
    while True:
        index = input(f"Enter numerical index of {promptFor} instance: ")
        try:
            index = int(index)
            break
        except:
            print("Invalid selection.")
    return choices[index]

if not os.path.exists("migrate-instances-config.json"):
    print("migrate-instances-config.json not found in script's folder.")
    quit()
else:
    with open("migrate-instances-config.json", 'r') as f: args = json.load(f)

# detect instances (top-level folders in root); prompt for choice
root = os.path.realpath(args["instances-root"])
instances = next(os.walk(root))[1]
for num, i in enumerate(instances): print(f'{num:02d}', "|", i )
src = os.path.realpath(os.path.join(root, getSelection(instances, "source"), ".minecraft"))
dst = os.path.realpath(os.path.join(root, getSelection(instances, "destination"), ".minecraft"))

# selection integrity checks
if (not os.path.exists(src)) or (not os.path.exists(dst)):
    print("At least one of the folders given detected as not a minecraft instance: no .minecraft folder")
    quit()
if src == dst:
    print("Source and destination instances are the same.")
    quit()

# migrate folders from src to dst
for folder in args["folders"]:
    print("\nMigrating folder:", folder)
    if not os.path.exists(os.path.join(src,folder)): print("### Folder does not exist in source instance:", folder) # verify folder exists in source
    else:
        items = [os.path.join(src,folder,i) for i in os.listdir(os.path.join(src,folder))]
        try:
            migrateDest = os.path.join(dst,folder)
            os.makedirs(migrateDest, exist_ok=True)
            for i in items: 
                shutil.move(i, migrateDest)
                print("Moved:",os.path.basename(i), "to", migrateDest)
        except Exception as e: print("### Move failed for", os.path.basename(i), "...", e)

# copy over options.txt
if args["copy-options"]:
    try:
        print("Copying options.txt")
        os.remove(os.path.join(dst,"options.txt"))
        shutil.copy(
            os.path.join(src,"options.txt"),
            os.path.join(dst,"options.txt")
        )
    except Exception as e: print("### Move failed for options.txt...", e)

print("\nExecution finished")
print("Remember to install mod loader and update mods")