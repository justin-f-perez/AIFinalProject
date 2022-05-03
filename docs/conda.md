# Mini-Conda Tutorial

## Whats the difference between conda and pip?

They fill some similar roles, but conda does things pip cannot, and the two can (and should) be used together. In my experience, the best approach is to use conda for environmnent creation/management, using pip to install python packages into that environment.

Shortcomings of pip-alone approach:
Pip is for python packages only. This means it cannot install binaries such as new versions of python. However, an alternative approach is to use `pyenv` for compiling new versions of python.

Pip does not support creating or managing environments. The python3 [`venv`](https://docs.python.org/3/library/venv.html) module and the third-party module [`virtualenv`](https://virtualenv.pypa.io/en/latest/) can create environments that pip can install packages into. python3 `venv` only supports creating environments with the same interpreter version. `virtualenv` can integrate with [`pyenv`](https://github.com/pyenv/pyenv) to provide new versions of python.

Neither `virtualenv` nor `venv` support creating globally named `venv` in the way that conda does. All three of these (including) conda can creating virtual envs at a given location:
```console
conda create --prefix ./path/to/venv [python=<python_version>]
virtualenv [-p <python_version>] ./path/to/venv
python3 -m venv ./path/to/venv
```
However, a third-party package [`virtualenvwrapper`]( https://virtualenvwrapper.readthedocs.io/en/latest/) can be used to provide global namespace for virtualenvs.

Additionally, pip does not provide support for managing environments, while conda does; although you can use the python3 `venv` module in place of conda for environment management. Thus, a better comparison might be between `pip + pyenv + virtualenvwrapper + binary installers` vs. `conda`. There's considerably less cognitive and setup overhead using one tool vs three or more.

## How do I create a conda environment?
There are two main ways that I create environments, and the differences between them aren't well-documented. The first is to use the standard `conda` command supplying either a name or a prefix (you must supply one, but not both):
```console
# use name notation
conda create --name "my-env"
# -or- use path
conda create --prefix "/path/to/my/env"
```

The second way is to create an environment from a configuration file using the `conda env` subcommand.
```console
# create an environment, using whatever name is specified in the file
# (error if name is not given in the file)
conda env create --file environment.yml
# override the name given in the file, if there is one, with the value specified on the command line
conda env create --file environment.yml --name my-env
# override the name given in the file, if there is one, using the given prefix instead
conda env create --file environment.yml --prefix /path/to/my/env
```

## How do I use a conda environment?
It's very similar to a python3 `venv`, except that with python3-style venvs you activate them by sourcing an activate script (e.g., `. venv/bin/activate`) whereas with conda environments you activate them with a conda command:
```console
conda activate environment-name
```

You should activate the conda environment anytime you want to use packages you've installed into it. This "activation" is only good for the duration of your shell session. Thus, if you close your terminal and re-open it, you will need to re-activate. I often define aliases to quickly navigate me to a project's directory and activate the related environment, e.g.:
```console
# ~/.zshrc
alias ai-final="cd /home/jfperez/school/AI-Final\ Project && conda activate ai-final"
```

With your environment activated, you should be able to use any package you have installed into that environment. For example, if you've installed `pip` into your environment, any packages you install using that environment's `pip` will be local to that environment.

```console
❯ conda deactivate  # deactivate current environment
❯ python3 -c 'import pygame'  # This should fail because I haven't installed pygame outside an environment
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'pygame'
❯ conda activate ai-final  # now activate environment where pygame was installed via pip
❯ python3 -c 'import pygame'  # this should succeed because I `pip install`ed pygame into this environment
pygame 2.1.2 (SDL 2.0.18, Python 3.10.4)
Hello from the pygame community. https://www.pygame.org/contribute.html
```

Alternatively, (this is particularly useful for scripting purposes) you can run one-off commands "inside" of a conda environment via `conda run`, e.g.,
```console
❯ conda run --name ai-final which python3
/opt/homebrew/Caskroom/miniconda/base/envs/ai-final/bin/python3
❯ ##### equivalent to... #####
❯ conda activate ai-final && which python3 && conda deactivate
/opt/homebrew/Caskroom/miniconda/base/envs/ai-final/bin/python3
```

## Installing new packages
There are a few ways to get new packages into a conda environment. First, note that many packages are available both via pip and via conda, and that you can use either of these tools as package managers to install your desired package into the environment. For example, we can install `jupyterlab` into the environment in either of these ways:
```
# installation via conda package
conda install --name my-env --channel=conda-forge jupyterlab

# installation via pip package by activating conda environment first
conda activate my-env && pip install jupyterlab

# installation via pip package by telling conda to run pip inside of the environment
conda run --name my-env pip install jupyterlab
```

### Note on Channels
With `pip`, there is only one "channel", and that is [pypi](https://pypi.org/). Conda supports multiple channels for distributing packages. The maintainers of jupyterlab recommend the `conda-forge` channel when installing their software via conda.


## Updating an environment
For software projects, it's usually a good idea to have dependencies explicitly listed in a requirements file of some form (this could be a conda environment.yml file or a pip requirements.txt file). Updating a conda environment for a given `environment.yml` file is simply:
```
conda env update --file environment.yml --prune --name my-env
```
As before, if the environment.yml file specifies an environment name, you may omit it from the command-line. The `--prune` flag tells conda to get rid of any packages we might have installed in this environment that are not specified in the `environment.yml` (e.g., if a bad dependency was removed since last update).

## Removing an environment
```
conda env remove --name my-env
conda env remove --prefix /path/to/my/env
```