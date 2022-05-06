# Quick Reference

```bash
# see all CLI options, including available agents
./run --help

# --graphics is implied for --keyboard
./run --keyboard

# --headless, i.e., no graphics, is implied for --agent if --graphics is not given
./run --agent agents.GentleBrute

# set 0 frame-rate to disable frame throttling (update as fast as CPU allows)
./run --agent agents.GentleBrute --graphics --frame-rate 0

# can control screen (window) size (in pixels)
./run --agent agents.Random --graphics --screen-height 600 --screen-width 800

# can also control game grid dimensions
./run --agent agents.Hungry --graphics --grid-height 10 --grid-width 10

# various flags for different log levels are available
./run --agent agents.TailChaser --graphics --frame-rate 0 --debug
```

_Note: the shebang in the CLI executable assumes you've set up the conda environment with the name given in environment.yml. If you specify a custom environment name, you must specify the interpreter yourself. `./run` is just a symlink to cli.py. all of the above examples can be run replacing `./run` with `python3 cli.py`, e.g., `conda activate my-env && python3 cli.py --help`._


# Setup
Unless otherwise noted, all subsequent commands will assume you have activated the conda environment.
## Create (or update) conda environment
NOTE: same command works whether environment already exists or not. If you're not sure if you have the environment, or unsure if up-to-date, this is safe to run repeatedly, so just go ahead and run it
```console
conda env update --file environment.yml --prune
```

## Activate the conda environment
```console
conda activate ai-final
```

## Install pre-commit hooks
This step only needs to be completed once per clone. The [pre-commit](https://pre-commit.com/) hooks automatically run the linter (flake8), type-checking (mypy), and code formatters (isort, black) whenever you commit. Together, these tools can catch common development errors.
```console
pre-commit install --install-hooks  # assumes conda env is activated
```

# Using the CLI
NOTE: the CLI now assumes you have a conda environment named 'ai-final'. If you created the conda environment using the command provided in this README, or let the environment name default to the one supplied in the environment.yml file, you should be good to go.
## Start a Manual Game
In this mode, you can control the snake with your keyboard to test out the game environment.
```console
./cli.py --graphics --keyboard
```

## Start an Agent-Based Game
NOTE: This example is a very simple agent that just spins in a circle. The notation for providing the path to the agent you wish to use is the same syntax you'd use to import it. In the example below, the `SpinnerAgent` class resides in the `agents` module (i.e., [agents.py](./agents.py))
```console
./cli.py --graphics --agent agents.SpinnerAgent
```

## Training mode
For reinforcement learning, you may want to run the game as fast as your computer will allow without rendering any graphics. Use `--headless` to disable graphics, use `--frame-rate 0` to disable update throttling.
```console
./cli.py --agent --headless --frame-rate 0
```

# Contributing New Agents
Feel free to use the existing agents.py file or to create a more specific file (e.g., search.py for search-based agents, deep.py for deep-learning based agents, etc.) In [agents.py](./agents.py) there is a minimal `SpinnerAgent` class that shows what the bare minimum to get a functional agent is. Basically, you just need a class that implements a `get_action` method that accepts a `game` argument. In this method, you can do any computation required to perform an action, and you have the `game` object representing the current [`Game`](./game.py)/[`Snake`](./snake.py) state.

# Start the notebook server
A convenience script is provided for starting the notebook server (dependencies are installed from environment.yml; ensure your environment is up-to-date.) This script also handles activation of the conda environment for the server, so you do _not_ need to activate the conda environment before running the script (but any python code you run in a notebook will run inside the conda environment).
```console
./start_notebook.sh
```

# Running test code

Files prefixed with `test_` contain some test code for unit testing pieces of functionality. The part after `test_` corresponds to the implementation code being tested (e.g., `test_game.py` and `game.py`).

```console
./run_tests
```


# Final Project
## Members
Justin Perez<br>
Levin Leesemann<br>
Melissa Krumm<br>
Miaomiao Zou
## Documents
[Project Report](https://docs.google.com/document/d/14OXp7eeJq8z1no57VwKUTgWbHgY5yk8jf76AjHZQZYQ/edit?usp=sharing)<br>
