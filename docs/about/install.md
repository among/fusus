# Convention

A lot of configuration can be avoided by this simple convention:

Put your cloned version of this repository in your `~/github` directory.
If you do not have it, make it, and organize it exactly as GitHub is organized:
by organization and then by repo.

# Get the software

Clone the `among/fusus` repo from GitHub.

Here are the instructions to get this repo and place it in the conventional place
on your file system.

``` sh
cd
mkdir github
cd github
mkdir among
git clone https://github.com/among/fusus
cd fusus
```

If you want to update later, make sure that you do not have work of your own
in this repo.
If you have, copy it to a location outside of this repo.

``` sh
cd ~/github/among/fusus
git fetch origin
git checkout master
git reset --hard origin/master
```

# Install the software

You are going to install the Python package `fusus` that is contained in the repo.

During install, all the packages that `fusus` is dependent on, will be installed
into your current Python3 installation.

The package `fusus` itself will be added to your Python3 installation in such a way
that it can be used from anywhere, while the package inside the repo is being accessed.
This is achieved by the fact that the installer will create a link to the repo.

``` sh
cd ~/github/among/fusus
pip3 install -e .
```

??? caution "Mind the dot"
    Do not forget the `.` at the end of the line in the above instruction.

??? hint "No nead to repeat this step"
    When you update the repo later, it will not be necessary to redo the
    `pip3 install` step, because the soft link to the fusus package in the repo
    will still be valid.

# Build steps

The following steps are relevant if you modify the software and documentation.

There is a script `build.py` in the top-level directory that performs these tasks.

Go to the repo's top level directory and say

``` sh
python3 build.py --help
```

to see what it can do.

Tip: in your `.zshrc` define this function:

``` sh
function fsb {
    cd ~/github/among/fusus
    python3 build.py "$@"
}

```

Then you can invoke the build script from anywhere:

``` sh
fsb --help
```

## Documentation

Documentation is collected from

* the docstrings in the Python files in the *fusus* directory;
* the markdown files in the *docs* directory.

## View documentation locally

To open a browser and view the dynamically generated documentation, say

``` sh
fsb docs
```

## Generate documentation locally

To generate documentation, say

``` sh
fsb pdocs
```

The documentation is now in the *site* directory.

## Publish documentation online

To generate and publish documentation online, say

``` sh
fsb shipDocs
```

This will publish the documentation to the *gh-pages* branch
in the online GitHub repository *among/fusus*, from where it can be
accessed by [https://among.github.io/fusus/](https://among.github.io/fusus/).

## Push everything

To generate and publisj documentation and to push all changes to
the *main* branch in the online GitHub directory, say

``` sh
fsb ship "commit message"
```

You have to provide a commit message.

