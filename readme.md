These are small scripts I've written to manage local files for Minecraft: Java Edition.

Python is required to run these scripts. Python versions prior to 3.12.5 are untested. No external libraries are needed.

---
# migrate-instances
Usually after I install a new Minecraft update, I have to manually copy over my worlds, mods, and texture packs. This script automates that process. The script automatically detects all Minecraft instances, and prompts the user to select the old and new ones. It's assumed the new instance has already been created and launched at least once. `migrate-instances-config.json` should be stored in the same folder as the script, and contains settings intended to be user-defined:
- Folder containing all Minecraft instances
- subfolders in instance's .minecraft whose contents should be migrated
- enable/disable copying options.txt from the source instance.

After this script runs, the old instance is safe to delete.

Note that installing a mod loader and updating mods must still be done manually.

---
# update-server
This is intended to update self-hosted servers (which use `server.jar` to run) for new Minecraft versions, while preserving the world file, player data, and server properties. It follows steps based on [this tutorial](https://wiki.sportskeeda.com/minecraft/how-to-update-server-minecraft). 

**Usage:** The script requires paths to the server folder and updated server.jar passed at runtime.

The actions this script performs are:
1. Files to keep after the update are stored in `<server root>/tmp`
2. Files which can be discarded after the update are moved to a different folder, `<server root>/dump_<current date>`.
3. The new server.jar is copied into the server folder and launched for the first time.
4. The EULA is agreed to by modifying `eula.txt`.
5. Files from `<server root>/tmp` are moved back into the `<server root>`.
6. By default, the "dump" folder is deleted. (Pass `-k` at runtime to preserve this folder)