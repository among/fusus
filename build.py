import sys

from subprocess import run

from pdocs import console, pdoc3serve, pdoc3, shipDocs


HELP = """
python3 build.py command

command:

-h
--help
help  : display help and exit

docs     : serve docs locally
pdocs    : build docs
sdocs    : ship docs
ship msg : push repo and publish docs on GitHub
"""


ORG = "among"
REPO = "fusus"
PKG = "pipeline"


def readArgs():
    args = sys.argv[1:]
    if not len(args) or args[0] in {"-h", "--help", "help"}:
        console(HELP)
        return (False, None, [])
    arg = args[0]
    if arg not in {
        "docs",
        "pdocs",
        "sdocs",
        "ship",
    }:
        console(HELP)
        return (False, None, [])

    if arg in {'ship'} and len(args) < 2:
        console(HELP)
        console("Provide a commit message")
        return (False, None, [])
    return (arg, None, [" ".join(args[1:])])


def ship(msg):
    shipDocs(ORG, REPO, PKG)
    pushrepo(msg)


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
    elif task == "docs":
        pdoc3serve(PKG)
    elif task == "pdocs":
        pdoc3(PKG)
    elif task == "sdocs":
        shipDocs(ORG, REPO, PKG)
    elif task == "ship":
        ship(remaining[0])


main()
