# Setup
Unless otherwise noted, all subsequent commands will assume you have activated the conda environment.
## Create (or update) conda environment
```console
# NOTE: same command works whether environment already exists or not
conda env update --file environment.yml --name ai-final --prune
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

# Start a Manual Game
In this mode, you can control the snake with your keyboard to test out the game environment.
```console
./cli.py --graphics --keyboard  # assumes conda env is activated
```

# Start an Agent-Based Game
NOTE: The current agent implementation is an extremely simple proof of concept that just spins in a circle.
```console
./cli.py --agent --graphics  # assumes conda env is activated
```

## Training mode
For reinforcement learning, you may want to run the game as fast as your computer will allow without rendering any graphics. Use `--headless` to disable graphics, use `--frame-rate 0` to disable update throttling.
```console
./cli.py --agent --headless --frame-rate 0  # assumes conda env is activated
```

# Start the notebook server
A convenience script is provided for starting the notebook server (dependencies are installed from environment.yml; ensure your environment is up-to-date.) This script also handles activation of the conda environment for the server, so you do _not_ need to activate the conda environment before running the script (but any python code you run in a notebook will run inside the conda environment).
```console
./start_notebook.sh
```


# Final Project
## Members
Justin Perez<br>
Levin Leesemann<br>
Melissa Krumm<br>
Miaomiao Zou
## Documents
[Project Report](https://docs.google.com/document/d/14OXp7eeJq8z1no57VwKUTgWbHgY5yk8jf76AjHZQZYQ/edit?usp=sharing)<br>
