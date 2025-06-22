import json, shutil, os, time, subprocess, sys, colorist

def choice(prompt: str):
    print(prompt, end=' ')
    while True:
        r = input()
        if r.upper() == 'Y': return True
        elif r.upper() == 'N': return False
        else: print('Please respond with "y" or "n":', end=' ')

def migrate_instance():

    # paths to "minecraft" folders
    src = SETTINGS['migration']['source_instance']
    dst = SETTINGS['migration']['destination_instance']

    # validate instance folders
    assert os.path.exists(src), "Source instance does not exist."
    assert os.path.exists(dst), "Destination instance not found. Ensure it exists and you've launched it at least once."
    assert src != dst, "Source and destination instances are the same."

    # migrate each subfolder
    for folder in SETTINGS['migration']['things_to_migrate']:

        # verify folder exists in source
        if not os.path.exists(os.path.join(src,folder)): 
            colorist.yellow(f"Folder does not exist in source instance: {folder}") 
        
        # perform migration
        else:
            print(f"Moving folder: {folder}")
            
            items = [os.path.join(src,folder,i) for i in os.listdir(os.path.join(src,folder))]
            migrate_dest = os.path.join(dst,folder)
            os.makedirs(migrate_dest, exist_ok=True)
            
            try:
                for i in items: 
                    shutil.move(i, migrate_dest)
                    # print(f"Moved item {os.path.basename(i)} to {migrate_dest}")
            except Exception as e: 
                colorist.red(f"Failed to move {os.path.basename(i)}: {e}")

    # copy over options.txt
    if SETTINGS['migration']['copy_game_options']:
        try:
            print("Copying game settings")
            os.remove(os.path.join(dst,"options.txt"))
            shutil.copy(
                os.path.join(src,"options.txt"),
                os.path.join(dst,"options.txt")
            )
        except Exception as e: 
            colorist.red(f"Failed to move options.txt: {e}")

    colorist.bg_green("\n Migration finished. Remember to install mod loader and update mods! \n")
    return

def update_server():

    # validate input
    SERVER_FOLDER = SETTINGS['server_update']['server_folder']
    NEW_JAR = SETTINGS['server_update']['new_jar']
    assert NEW_JAR.endswith(".jar"), "Server file must be a .jar file."
    assert os.path.exists(SERVER_FOLDER), "Instance folder does not exist."
    assert os.path.exists(NEW_JAR), "New server .jar does not exist."

    # local constants
    TEMP_FOLDER = os.path.join(SERVER_FOLDER, "tmp")
    TEMP_FILES = ["world", "banned-ips.json", "banned-players.json", "ops.json", "server.properties", "usercache.json", "whitelist.json"]
    JUNK_FOLDER = os.path.join(SERVER_FOLDER, ("old_" + time.strftime("%Y%m%d-%H%M%S")))
    JUNK_FILES = ["logs", "eula.txt", "server.jar", "libraries", "versions"]

    # create tmp folder (files to restore after upgrade)
    print("Stashing files to keep...")
    for file in TEMP_FILES:
        try:
            shutil.move(
                os.path.join(SERVER_FOLDER, file), 
                os.path.join(SERVER_FOLDER, "tmp", file)
            )
        except Exception as e: raise Exception(f"Error attempting to move {file}: {e}")

    # Create junk folder (files which can be discarded after upgrade)
    print("Stashing files to discard...")
    for file in JUNK_FILES:
        try:
            shutil.move(
                os.path.join(SERVER_FOLDER, file), 
                os.path.join(JUNK_FOLDER, file)
            )
        except Exception as e: raise Exception(f"Error attempting to move {file}: {e}")

    # copy passed jar to server folder, renaming the copy to "server.jar"
    print("Copying over updated .jar...")
    active_jar = os.path.join(SERVER_FOLDER, "server.jar")
    try: shutil.copy(NEW_JAR, active_jar)
    except Exception as e: raise(e)

    # run server.jar to create initial files, including the EULA
    print("Initializing new server.jar...")
    try:
        subprocess.run(
            ["java", "-jar", active_jar],   # run server jar using "java" command. 
            cwd=SERVER_FOLDER,              # changes working directory during execution so files are placed in the server folder.
            stdout=subprocess.DEVNULL,      # supress regular terminal output...
            stderr=subprocess.STDOUT)       # ...but not errors
        os.remove(os.path.join(SERVER_FOLDER, "server.properties")) # remove existing server.properties file to ensure the one from tmp is used
    except Exception as e: raise(e)

    # accept the EULA by editing the eula.txt.
    print("Agreeing to EULA...")
    try:
        eula_path = os.path.join(SERVER_FOLDER, "eula.txt")
        with open(eula_path,'r') as file: eula_contents = file.readlines()
        eula_contents[2] = "eula=true"
        with open(eula_path,'w') as file: file.writelines(eula_contents)
    except Exception as e: raise(e)

    # restore files from tmp folder.
    try:
        print("Restoring existing server data...")
        for file in os.listdir(TEMP_FOLDER):
            shutil.move(
                os.path.join(TEMP_FOLDER, file),
                os.path.join(SERVER_FOLDER, file)
            )
    except Exception as e: raise(e)

    # delete tmp folder if it is empty
    if not os.listdir(TEMP_FOLDER): os.rmdir(TEMP_FOLDER)
    else: print("tmp folder could not be deleted because it still contains files.")

    colorist.bg_green("\n Server upgrade complete! \n")

    # things beyond this point can fail but the server will still have been upgraded

    # delete dump folder
    try:
        if SETTINGS['server_update']['keep_junk_files']:
            print(f"Files in {JUNK_FOLDER} can be safely deleted.")
        else: shutil.rmtree(JUNK_FOLDER)
    except Exception as e: 
        colorist.yellow(f"Junk folder could not be deleted: {e}")

    # print IP address to give to friends
    try:
        if SETTINGS['server_update']['show_public_ip']:
            import urllib.request
            my_ip = urllib.request.urlopen("https://checkip.amazonaws.com").read().decode('utf8').strip() + ":25565"
            print(f"Server address is {my_ip}")
    except Exception as e: colorist.yellow(f"Server address could not be obtained: {e}")

    print(f"\nRun to start server: \n  cd {SERVER_FOLDER}; javaw -jar ./server.jar\n")
    
    return


################## main execution starts here ##################


# get settings
settings_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'minup-settings.json'
)
try: 
    with open(settings_file) as file: SETTINGS = json.load(file)
except Exception as e: 
    print(f"Settings file {os.path.dirname(os.path.realpath(__file__))}/{settings_file} not found.")
    sys.exit(9)

# show settings that will be used
print("\nThe actions listed below will be performed:\n")
if SETTINGS['migration']['do']:
    print(f"{colorist.Color.BLACK}{colorist.BgColor.YELLOW} Instance Migration {colorist.Color.OFF}")
    for key, value in SETTINGS['migration'].items(): print(f"  {colorist.Color.YELLOW}{key}{colorist.Color.OFF}: {value}")
    if SETTINGS['server_update']['do']: print("")
if SETTINGS['server_update']['do']:
    print(f"{colorist.Color.BLACK}{colorist.BgColor.YELLOW} Server Update {colorist.Color.OFF}")
    for key, value in SETTINGS['server_update'].items(): print(f"  {colorist.Color.YELLOW}{key}{colorist.Color.OFF}: {value}")
    if SETTINGS['server_update']['show_public_ip']: 
        colorist.bg_red("\n Your public IP address will be shown in this terminal window. ")
print("")

# attempt actions
if choice('ok?'):
    if SETTINGS['migration']['do']: 
        try: migrate_instance()
        except Exception as e: 
            colorist.red(f"\nFailure during instance migration: {e}\n")
            sys.exit(1)
    
    if SETTINGS['server_update']['do']:
        try: update_server()
        except Exception as e: 
            colorist.red(f"\nFailure during server upgrade: {e}\n")
            sys.exit(1)
    
    sys.exit(0)
else: 
    print(f"Open file to change settings: \n{settings_file}\n")
    sys.exit(0)