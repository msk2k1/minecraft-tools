import argparse, shutil, os, time, subprocess, sys

# constants from runtime arguments
try:
    parser = argparse.ArgumentParser()
    parser.add_argument('server', help="Path to the current server folder.")
    parser.add_argument('newJar', help="Path to the updated server.jar.")
    parser.add_argument('-i', '--show-public-ip', action='store_true', help="Fetch and print public IP address after migrating.")
    parser.add_argument('-k', '--keep-junk-files', action='store_true', help="Keep folder of items that are no longer necessary after upgrade. (Default behavior is to delete them.)")

    ARGS = parser.parse_args()

    # error condition: provided server file is not .jar
    if not (str(ARGS.newJar).endswith(".jar")): raise Exception("Server file must be a .jar file.")
except Exception as e: print(e); sys.exit(2)

# other constants
JUNK_FOLDER_NAME = os.path.join(ARGS.server, ("old_" + time.strftime("%Y%m%d-%H%M%S")))
TEMP_FOLDER_NAME = os.path.join(ARGS.server, "tmp")
TEMP_FILES = ["world", "banned-ips.json", "banned-players.json", "ops.json", "server.properties", "usercache.json", "whitelist.json"]
JUNK_FILES = ["logs", "eula.txt", "server.jar", "libraries", "versions"]

# main execution
try:

    # create tmp folder (files to restore after upgrade)
    print("Stashing files to keep...")
    for file in TEMP_FILES:
        try:
            shutil.move(
                os.path.join(ARGS.server, file), 
                os.path.join(ARGS.server, "tmp", file)
            )
        except Exception as e: raise Exception(f"Error attempting to move {file}: {e}")

    # Create junk folder (files which can be discarded after upgrade)
    print("Stashing files to discard...")
    for file in JUNK_FILES:
        try:
            shutil.move(
                os.path.join(ARGS.server, file), 
                os.path.join(JUNK_FOLDER_NAME, file)
            )
        except Exception as e: raise Exception(f"Error attempting to move {file}: {e}")

    # copy passed jar to server folder, renaming the copy to "server.jar"
    print("Copying over updated .jar...")
    try:
        activeJar = os.path.join(ARGS.server, "server.jar")
        shutil.copy(ARGS.newJar, activeJar)
    except Exception as e: raise(e)

    # run server.jar to create initial files, including the EULA
    print("Initializing new server.jar...")
    try:
        subprocess.run(
            ["java", "-jar", activeJar],    # run server jar using "java" command. 
            cwd=ARGS.server,                # changes working directory during execution so files are placed in the server folder.
            stdout=subprocess.DEVNULL,      # supress regular terminal output...
            stderr=subprocess.STDOUT)       # ...but not errors
        os.remove(os.path.join(ARGS.server, "server.properties")) # remove existing server.properties file to ensure the one from tmp is used
    except Exception as e: raise(e)

    # accept the EULA by editing the eula.txt.
    print("Agreeing to EULA...")
    try:
        eulaPath = os.path.join(ARGS.server, "eula.txt")
        with open(eulaPath,'r') as file: eulaContents = file.readlines()
        eulaContents[2] = "eula=true"
        with open(eulaPath,'w') as file: file.writelines(eulaContents)
    except Exception as e: raise(e)

    # restore files from tmp folder.
    try:
        print("Restoring existing server data...")
        for file in os.listdir(TEMP_FOLDER_NAME):
            shutil.move(
                os.path.join(TEMP_FOLDER_NAME, file),
                os.path.join(ARGS.server, file)
            )
    except Exception as e: raise(e)

    # delete tmp folder if it is empty
    if not os.listdir(TEMP_FOLDER_NAME): os.rmdir(TEMP_FOLDER_NAME)
    else: print("tmp folder could not be deleted because it still contains files.")

    print("\nServer upgrade complete.\n")

    # delete dump folder
    if ARGS.keep_junk_files:
        print(f"Files in {JUNK_FOLDER_NAME} can be safely deleted.")
    else:
        try: shutil.rmtree(JUNK_FOLDER_NAME)
        except Exception as e: print(f"Junk folder could not be deleted: {e}")

    # print IP address to give to friends
    if ARGS.show_public_ip:
        try:
            import urllib.request
            myIP = urllib.request.urlopen("https://checkip.amazonaws.com").read().decode('utf8').strip() + ":25565"
            print(f"\nServer address: {myIP}")
        except Exception as e:
            print(f"\nServer address could not be obtained: {e}")

except Exception as e: print(e); sys.exit(1)

sys.exit(0)