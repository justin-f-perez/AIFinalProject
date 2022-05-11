# Final Project

Request access on GitHub: https://github.com/meliakru/AIFinalProject

## Members
Justin Perez<br>
Levin Leesemann<br>
Melissa Krumm<br>
Miaomiao Zou

## Documents
[Project Report](https://docs.google.com/document/d/14OXp7eeJq8z1no57VwKUTgWbHgY5yk8jf76AjHZQZYQ/edit?usp=sharing)<br>

# Quick Start

## Create (or update) conda environment
NOTE: same command works whether environment already exists or not. If you're not sure if you have the environment, or unsure if up-to-date, this is safe to run repeatedly, so just go ahead and run it
```bash
conda env update --file environment.yml --prune
```

## Activate the conda environment
```bash
conda activate ai-final
```


## Usage
_Note: the shebang in the CLI executable assumes you've set up the conda environment with the name given in environment.yml. If you specify a custom environment name, you must specify the interpreter yourself. `./run` is just a symlink to cli.py. all of the above examples can be run replacing `./run` with `python3 cli.py`, e.g., `conda activate my-env && python3 cli.py --help`._

```bash
# see all CLI options, including available agents
./run --help

# --graphics is implied for --keyboard
./run keyboard

# set 0 frame-rate to disable frame throttling (update as fast as CPU allows)
# NOTE: flags that aren't specific to agents must precede the "agent" subcommand
./run --graphics --frame-rate 0 agent GentleBrute 
# various flags for different log levels are available
./run  --graphics --frame-rate 0 --debug agent TailChaser
```

# Architecture
All AI agents are defined in [agents.py](./agents.py). The primary state object is `Game`, defined in [game.py](./game.py) and it's child object, [`Snake`](./snake.py). Additionally, statistics are automatically saved to a `game-stats` subdirectory of this project directory every 100 game ticks by [stats.py](./stats.py). There are some additional abstractions in controllers.py and views.py to help all of the pieces work together. Finally, example usage of code can be found in the test files (each is prefixed with `test_`, see below for more details.)


# DEVELOPMENT
## Install pre-commit hooks
This step only needs to be completed once per clone. The [pre-commit](https://pre-commit.com/) hooks automatically run the linter (flake8), type-checking (mypy), and code formatters (isort, black) whenever you commit. Together, these tools can catch common development errors.
```console
pre-commit install --install-hooks  # assumes conda env is activated
```

# Running test code

Files prefixed with `test_` contain some test code for unit testing pieces of functionality. The part after `test_` corresponds to the implementation code being tested (e.g., `test_game.py` and `game.py`).

```console
./run_tests
```
