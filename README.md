
# Setup
## Create a conda environment
```console
conda env create --file environment.yml --name ai-final
```

## Activate the conda environment
```console
conda activate ai-final
```

## Install pre-commit hooks
This step only needs to be completed once per clone. The [pre-commit](https://pre-commit.com/) hooks automatically run the linter (flake8), type-checking (mypy), and code formatters (isort, black) whenever you commit. Together, these tools can catch common development errors.
```console
pre-commit install --install-hooks
```

# Start a Manual Game
```console
conda activate ai-final
./cli.py --graphics --keyboard
```

# Start an Agent-Based Game
NOTE: The current agent implementation is an extremely simple proof of concept that just spins in a circle.
```console
conda activate ai-final
./cli.py --agent
```


# Final Project
## Members
Justin Perez<br>
Levin Leesemann<br>
Melissa Krumm<br>
Miaomiao Zou
## Documents
[Project Report](https://docs.google.com/document/d/14OXp7eeJq8z1no57VwKUTgWbHgY5yk8jf76AjHZQZYQ/edit?usp=sharing)<br>
