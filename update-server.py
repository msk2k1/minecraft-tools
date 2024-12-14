import argparse, shutil, os, time, subprocess, urllib.request, sys

# given server folder and path to new server.jar
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('server', help="Path to the current server folder.")
    parser.add_argument('newJar', help="Path to the updated server.jar.")

    contents = parser.parse_args()
    output = {
        "server": os.path.realpath(contents.server),
        "newJar": os.path.realpath(contents.newJar)
    }

    if not output["newJar"].endswith(".jar"): # error condition: provided server file is not .jar
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
            cwd=args["server"],             # changes working directory during execution so files are placed in the server folder.
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
    folder = os.path.join(args["server"], "tmp")
    try:
        print("Restoring existing server data...")
        for i in os.listdir(folder):
            shutil.move(
                os.path.join(folder, i),
                os.path.join(root, i)
            )
    except Exception as e: raise(e)

    # delete tmp folder if it is empty
    if not os.listdir(folder): os.rmdir(os.path.join(args["server"], "tmp"))
    else: print("tmp folder could not be deleted because it still contains files.")

    return

### main execution starts here ###
try:
    args = getArgs()
    serverRoot = args["server"]

    # tmp folder: files to transfer after upgrade
    tmpFolder = os.path.join(serverRoot, "tmp")
    tmpItems = ["world", "banned-ips.json", "banned-players.json", "ops.json", "server.properties", "usercache.json", "whitelist.json"]
    stashFiles(serverRoot, tmpItems, tmpFolder)

    # dump folder: files which can be discarded after upgrade. For safety reasons, the script doesn't delete them itself.
    dumpFolder = os.path.join(serverRoot, ("dump_" + time.strftime("%Y%m%d-%H%M%S")))
    dumpItems = ["logs", "eula.txt", "server.jar", "libraries", "versions"]
    stashFiles(serverRoot, dumpItems, dumpFolder)

    initServer(args["newJar"], serverRoot)
    acceptEULA(serverRoot)
    restoreTmp(serverRoot)

    print(f"\nServer upgrade complete. Files in 'dump_' folder can be deleted.")
    print(f"To launch, run: \ncd {serverRoot}; java -jar ./server.jar --nogui\n")

    # print IP address to give to friends
    ipSite = "https://checkip.amazonaws.com"
    try:
        myIP = urllib.request.urlopen(ipSite).read().decode('utf8').strip() + ":25565"
        input("To reveal public IP address, press enter. Otherwise EXIT the program with Ctrl+C or close terminal window.")
        print("Public server address is:", myIP)
    except:
        print(f"Visit {ipSite} to get you public IP. Give this to friends, including :25565 after it.")

except Exception as e: 
    print(e)
    sys.exit(-1)

sys.exit(0)