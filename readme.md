These are small scripts I've written to manage local files for Minecraft: Java Edition.

Python is required to run these scripts. Python versions prior to 3.12.3 are untested. No external libraries are needed for either program.

---
# migrate-instances
Usually after I install a new Minecraft update, I have to manually copy over my worlds, mods, and texture packs. This script automates that process.

**Usage**: No commandline parameters are used. When started, script lists Minecraft instances and prompts for migration source and destination. **It's assumed the new instance has already been created and launched at least once.** Note that installing a mod loader and updating mods must still be done manually.

---
# update-server
This is intended to update self-hosted servers (which use `server.jar` to run) for new Minecraft versions, while preserving the world file, player data, and server properties. It follows steps based on [this tutorial](https://wiki.sportskeeda.com/minecraft/how-to-update-server-minecraft). 

**Usage:** The script requires paths to the server folder and updated server.jar passed at runtime. **This script edits the server contents without making a backup copy. Back up the server folder yourself before running this script.** If execution fails partway through, you will need to manually restore the original folder structure.

In addition, these runtime parameters are accepted:
- `-h, --help           `: show help message and exit
- `-i, --show-public-ip `: Fetch and print public IP address after migrating.
- `-k, --keep-junk-files`: Keep folder of items that are no longer necessary after upgrade. (Default behavior is to delete them.)

The actions this script performs are:
1. Files to keep after the update are stored in `<server root>/tmp`
2. Files which can be discarded after the update are moved to a different folder, `<server root>/dump_<current date>`.
3. The new server.jar is copied into the server folder and launched for the first time.
4. The EULA is agreed to by modifying `eula.txt`.
5. Files from `<server root>/tmp` are moved back into the `<server root>`.
6. By default, the "dump" folder is deleted. (Pass `-k` at runtime to preserve this folder)