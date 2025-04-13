import argparse, shutil, os, time, subprocess, sys

# given server folder and path to new server.jar
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('server', help="Path to the current server folder.")
    parser.add_argument('newJar', help="Path to the updated server.jar.")
    parser.add_argument('-i', '--show-public-ip', action='store_true', help="Fetch and print public IP address after migrating.")
    parser.add_argument('-k', '--keep-temp-files', action='store_true', help="Keep folder of items that are no longer necessary after upgrade. (Default behavior is to delete them.)")

    output = parser.parse_args()

    if not (str(output.newJar).endswith(".jar")): # error condition: provided server file is not .jar
        raise Exception("Server file must be a .jar file.")
    else: return output

# move "items" in "root" into a subfolder "subfolder".
def stashFiles(root: str, items: str, subfolder: str):
    print("Preparing", subfolder, "stash...")
    for i in items:
        try:
            shutil.move(
                os.path.join(root, i), 
                os.path.join(root, subfolder, i)
            )
        except Exception as e:
            raise Exception(f"Error attempting to move {i}: {e}")
    return

# copy over give server.jar, run it for the first time, and accept the EULA. Rerturns the path to the copied jar to be used for the server.
# jar: the jar file given as parameter to script.
def initServer(jar: str, root: str):
    try:
        print("copying over", jar, "...")
        activeJar = os.path.join(root, "server.jar")
        shutil.copy(jar, activeJar)
    except Exception as e: raise(e)

    try:
        print("initializing server.jar...")
        subprocess.run(
            ["java", "-jar", activeJar],    # run server jar using "java" command. 
            cwd=ARGS["server"],             # changes working directory during execution so files are placed in the server folder.
            stdout=subprocess.DEVNULL,      # supress regular terminal output...
            stderr=subprocess.STDOUT)       # ...but not errors
        
        os.remove(os.path.join(root, "server.properties")) # remove existing server.properties file to ensure the one from tmp is used
    except Exception as e: raise(e)

    return activeJar

# accept the EULA by editing the eula.txt.
def acceptEULA(root: str):
    try:
        print("agreeing to EULA...")
        eulaPath = os.path.join(root, "eula.txt")
        with open(eulaPath,'r') as file: eulaContents = file.readlines()
        eulaContents[2] = "eula=true"
        with open(eulaPath,'w') as file: file.writelines(eulaContents)
    except Exception as e: raise(e)
    return

# copy the files out of tmp folder and attempt to delete it.
def restoreTmp(root: str):
    folder = os.path.join(ARGS["server"], "tmp")
    try:
        print("Restoring existing serverreturn  data...")
        for i in os.listdir(folder):
            shutil.move(
                os.path.join(folder, i),
                os.path.join(root, i)
            )
    except Exception as e: raise(e)

    # delete tmp folder if it is empty
    if not os.listdir(folder): os.rmdir(os.path.join(ARGS["server"], "tmp"))
    else: print("tmp folder could not be deleted because it still contains files.")

    return

### main execution starts here ###
try:
    ARGS = getArgs()
    # serverRoot = ARGS.server
    print(ARGS.server)
    quit()

    # tmp folder: files to transfer after upgrade
    tmpFolder = os.path.join(serverRoot, "tmp")
    tmpItems = ["world", "banned-ips.json", "banned-players.json", "ops.json", "server.properties", "usercache.json", "whitelist.json"]
    stashFiles(serverRoot, tmpItems, tmpFolder)

    # dump folder: files which can be discarded after upgrade. For safety reasons, the script doesn't delete them itself.
    dumpName = "dump_" + time.strftime("%Y%m%d-%H%M%S")
    dumpFolder = os.path.join(serverRoot, dumpName)
    dumpItems = ["logs", "eula.txt", "server.jar", "libraries", "versions"]
    stashFiles(serverRoot, dumpItems, dumpFolder)

    initServer(ARGS["newJar"], serverRoot)
    acceptEULA(serverRoot)
    restoreTmp(serverRoot)

    # delete dump folder
    print("Server upgrade complete.")
    print(f"To launch, run: \ncd {serverRoot}; java -jar ./server.jar --nogui\n")
    if ARGS.keep_temp_files:
        print(f"Files in {dumpName} can be safely deleted.")
    else:
        try: os.rmdir(dumpFolder)
        except Exception as e: print(f"dump folder could not be deleted: {e}")

    # print IP address to give to friends
    if ARGS.show_public_ip:
        try:
            import urllib.request
            myIP = urllib.request.urlopen("https://checkip.amazonaws.com").read().decode('utf8').strip() + ":25565"
            print(f"Server address: {myIP}")
        except Exception as e:
            print(f"Public IP could not be obtained: {e}")
except Exception as e: 
    print(e)
    sys.exit(1)

sys.exit(0)