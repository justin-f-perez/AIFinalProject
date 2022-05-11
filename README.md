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

# Features
* Multiple AI agents defined in [agents.py](./agents.py).
* Immutable representation of [`Game`](./game.py) state.
* Auto-saved [game stats and history](./stats.py) (saves to ./game-stats/ -- .csv files are summary, .txt files [auto-cleaned every run] show ASCII art of each time step)
* Verbose logging, auto-cleaned (deleted) every run
* [Lots](./test_agents.py) of [test](./test_game.py) [code](./test_serializers.py) to [demonstrate](./test_snake.py) [usage](./test_utils.py) for customization (each is prefixed with `test_`, see below for more details.)
* [Serialization](./serializers.py) to multiple formats: ASCII-art, JSON, YAML
* fully type annotated
* Customization [hooks](./hooks.py) have full access to full game state, agent, and game controller
```python
import controllers
import subprocess

def json_saver(ctl: controllers.Controller, _):
    print(ctl.game.to_json(), stream=open('mygame.json', 'w'))
    subprocess.run("arbitrary_shell_cmd")

controllers.on_tick.append(json_saver)
```
#### Live Terminal Display - Unicode Text Representation of Game State
```
🍎🔵🔵🔵🔵🔵🔵🔵🔵
🐍🔵🔵🔵🔵🔵🔵🔵🔵
🐍🍎🔵🔵🔵🔵🔵🐍🔵
🐍🔵🔵🔵🔵🔵🔵🐍🔵
🐍🔵🔵🔵🔵🔵🔵🐍🔵
🐍🔵🔵🔵🔵🔵🔵🐍🔵
🐍🐍🐍🐍🐍🐍🐍🐍🔵
🔵🔵🔵🔵🔵🔵🔵🔵🔵
```

#### Live Terminal Display -- Game History/Stats
```
┏━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ game # ┃ tick # ┃ score ┃
┡━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ 8      │ 219    │ 27    │
│ 7      │ 162    │ 20    │
│ 6      │ 152    │ 19    │
│ 5      │ 1      │ 0     │
│ 4      │ 1      │ 0     │
│ 3      │ 1      │ 0     │
│ 2      │ 1      │ 0     │
│ 1      │ 443    │ 46    │
└────────┴────────┴───────┘
```

#### Live Terminal Display -- Q Agent Params
```
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ discount ┃ learning_rate ┃ learning_rat… ┃ exploration_… ┃ exploration_… ┃ discount ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 0.99     │ 0.6292468477… │ 0.999         │ 0.3146234238… │ 0.999         │ 0.99     │
└──────────┴───────────────┴───────────────┴───────────────┴───────────────┴──────────┘
```



#### Live Terminal Display - Q Value Summary Table
```
┏━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ # total ┃ #[Q>0] ┃ #[Q=0] ┃ #[Q<0] ┃ #[Q=nan] ┃ #[Q=-inf] ┃ sum(Q)            ┃
┡━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ 30      │ 7      │ 0      │ 23     │ 0        │ 0         │ -5.87771361100647 │
└─────────┴────────┴────────┴────────┴──────────┴───────────┴───────────────────┘
```



#### Live Terminal Display - Q Value Table
```
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ <-🍎  ┃  🍎->  ┃ 🍎^   ┃ 🍎v   ┃  <-🐍  ┃ 🐍->  ┃ 🐍^   ┃ 🐍v    ┃ act      ┃ $        ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ False │ True  │ False │ True  │ False │ False │ False │ False │ Directi… │ -1.0422… │
│ True  │ False │ True  │ False │ True  │ False │ True  │ False │ Directi… │ -0.9303… │
│ True  │ True  │ True  │ True  │ False │ False │ False │ False │ Directi… │ -0.8432… │
│ False │ True  │ False │ True  │ False │ True  │ False │ True  │ Directi… │ -0.8384… │
│ True  │ True  │ True  │ True  │ False │ True  │ False │ True  │ Directi… │ -0.7941… │
│ False │ True  │ False │ True  │ True  │ False │ True  │ False │ Directi… │ -0.7192… │
│ False │ True  │ False │ True  │ False │ True  │ False │ True  │ Directi… │ -0.4185… │
│ True  │ False │ True  │ False │ True  │ False │ True  │ False │ Directi… │ -0.2504… │
│ True  │ True  │ True  │ True  │ True  │ False │ True  │ False │ Directi… │ -0.1660… │
│ False │ True  │ False │ True  │ False │ False │ False │ False │ Directi… │ -0.1456… │
│ False │ True  │ False │ True  │ True  │ False │ True  │ False │ Directi… │ -0.1436… │
│ False │ True  │ False │ True  │ True  │ False │ True  │ False │ Directi… │ -0.1265… │
│ True  │ True  │ True  │ True  │ False │ True  │ False │ True  │ Directi… │ -0.1030… │
│ True  │ True  │ True  │ True  │ False │ False │ False │ False │ Directi… │ -0.0956… │
│ False │ True  │ False │ True  │ False │ False │ False │ False │ Directi… │ -0.0896… │
│ True  │ True  │ True  │ True  │ True  │ False │ True  │ False │ Directi… │ -0.0731… │
│ False │ True  │ False │ True  │ False │ True  │ False │ True  │ Directi… │ -0.0611… │
│ True  │ True  │ True  │ True  │ False │ True  │ False │ True  │ Directi… │ -0.0390… │
│ True  │ True  │ True  │ True  │ False │ True  │ False │ True  │ Directi… │ -0.0346… │
│ True  │ False │ True  │ False │ False │ True  │ False │ True  │ Directi… │ -0.0300… │
```


# DEVELOPMENT
## Install pre-commit hooks
This step only needs to be completed once per clone. The [pre-commit](https://pre-commit.com/) hooks automatically run the linter (flake8), type-checking (mypy), and code formatters (isort, black) whenever you commit. Together, these tools can catch common development errors.
```console
pre-commit install --install-hooks  # assumes conda env is activated
```

# TESTING

Files prefixed with `test_` contain tests intended to be run via pytest. The part after `test_` corresponds to the file under test (e.g., `test_game.py` and `game.py`). Additionally, 

Assuming you set up the suggested conda environment, you can just run:
```bash
./run_tests
./run_tests --help  # show pytest's --help
./run_tests --timeout=1  # set timeout per-test to 1sec
# etc.
```
Above is just a simple wrapper so you don't have to bother activating your conda env. All arguments you supply to `run_tests` are passed through to pytest.

Otherwise, activate your environment with all of the installed dependencies and run:
```bash
pytest
```
