# Minecraft Update Helper (minup)

I wrote this to manage local files for Minecraft: Java Edition:
- **Move** worlds, settings, etc. to new Minecraft instance
- Upgrading servers to new Minecraft versions

Python 3 and the [colorist](https://jakob-bagterp.github.io/colorist-for-python/getting-started/installation/) library are required to run this script.

## Configuration
When called, the script will use settings from the `minup-settings.json` file located in the same folder as the program.
The settings which can be defined are:
- Migration
    - `source_instance`: The `minecraft` or `.minecraft` folder for your existing version.
    - `destination_instance`: The `minecraft` or `.minecraft` folder for the new instance. The instance needs to be launched at least once for this folder to exist.
    - `things_to_migrate`: Subfolders in `minecraft` or `.minecraft` you would like moved over.
    - `copy_game_options`: Apply your existing game settings to the new instance.
- Server Upgrade
    - `server_folder`: The folder containing your Minecraft server data. It's assumed only one server's data is in this folder.
    - `new_jar`: The `.jar` server executable for the new Minecraft version. These can be obtained from the [Minecraft wiki](https://minecraft.wiki/).
    - `show_public_ip`: Fetch and print public IP address after migrating.
    - `keep_junk_files`: Keep folder of items that are no longer necessary after upgrade. If `false`, they will be deleted.

One or both of the actions can be performed in a single run; set `do` in the respective section of the settings file to `true` or `false`.

## Operation

### Instance Migration
Usually after I install a new Minecraft update, I have to manually copy over my worlds, mods, and texture packs. This script automates that process.

The files are **moved** to the new instance, **not** copied.

### Server Upgrade
This is to update self-hosted servers (which use `server.jar` to run) for new Minecraft versions, while preserving the world file, player data, and server properties. 
It follows steps based on [this tutorial](https://wiki.sportskeeda.com/minecraft/how-to-update-server-minecraft). 
Note that the upgrade is done **in-place**, as opposed to making a copy/backup of the server folder.

The steps done to upgrade a server are:
1. Files to keep after the update are stored in `<server root>/tmp`
2. Files which can be discarded after the update are moved to a different folder, `<server root>/old_<current date>`.
3. The new server.jar is copied into the server folder and launched for the first time.
4. The EULA is agreed to by modifying `eula.txt`.
5. Files from `<server root>/tmp` are moved back into the `<server root>`.