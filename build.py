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
ship msg : push repo and publish docs on GitHub
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
        "ship",
    }:
        print(HELP)
        return (False, None, [])

    if arg in {'ship'} and len(args) < 2:
        print(HELP)
        print("Provide a commit message")
        return (False, None, [])
    return (arg, None, [" ".join(args[1:])])


def ship(msg):
    apidocs()
    pushrepo(msg)
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
        " pipeline"
    )
    run(cmdLine, shell=True)


def pushrepo(msg):
    for cmdLine in (
        "git add --all .",
        f'''git commit -m "{msg}"''',
        "git push origin master",
    ):
        run(cmdLine, shell=True)


def main():
    (task, msg, remaining) = readArgs()
    if not task:
        return
    elif task == "adocs":
        apidocs()
    elif task == "docs":
        serveDocs()
    elif task == "ship":
        ship(remaining[0])


main()
