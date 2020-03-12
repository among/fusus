import sys

from time import sleep
from subprocess import run, Popen


HELP = f"""
python3 build.py command

command:

-h
--help
help  : print help and exit

adocs    : build apidocs
docs     : serve docs locally
shipdocs : ship (publish) docs on GitHub
"""


def readArgs():
    args = sys.argv[1:]
    if not len(args) or args[0] in {"-h", "--help", "help"}:
        print(HELP)
        return (False, None, [])
    arg = args[0]
    if arg not in {
        "adocs",
        "docs",
        "shipdocs",
    }:
        print(HELP)
        return (False, None, [])
    return (arg, None, [])


def shipDocs():
    apidocs()
    run(["mkdocs", "gh-deploy"])


def serveDocs():
    apidocs()
    proc = Popen(["mkdocs", "serve"])
    sleep(3)
    run("open http://127.0.0.1:8000", shell=True)
    try:
        proc.wait()
    except KeyboardInterrupt:
        pass
    proc.terminate()


def apidocs():
    cmdLine = (
        "pdoc3"
        " --force"
        " --html"
        " --output-dir docs/apidocs/html"
        " programs/pipeline"
    )
    run(cmdLine, shell=True)


def main():
    (task, msg, remaining) = readArgs()
    if not task:
        return
    elif task == "adocs":
        apidocs()
    elif task == "docs":
        serveDocs()
    elif task == "shipdocs":
        shipDocs()


main()
