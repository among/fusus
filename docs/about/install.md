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

You are going to install the Python package `pipeline` that is contained in the repo.

During install, all the packages that `pipeline` is dependent on, will be installed
into your current Python3 installation.

The package `pipeline` itself will be added to your Python3 installation in such a way
that it can be used from anywhere, while the package inside the repo is being accessed.
This is achieved by the fact that the installer will create a link to the repo.

``` sh
cd ~/github/among/fusus
pip3 install pipeline -e .
```

??? caution "Mind the dot"
    Do not forget the `.` at the end of the line in the above instruction.

??? hint "No nead to repeat this step"
    When you update the repo later, it will not be necessary to redo the
    `pip3 install` step, because the soft link to the pipeline package in the repo
    will still be valid.
