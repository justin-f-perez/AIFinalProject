# Project Ideas (Most preferred to least preferred)
## Tic-tac-toe (Reinforcement learning | Minimax)

**Pros:**

* game state has natural grid representation where each cell is in one of 3 states (`empty` vs. `X`'s vs `O`'s)
* natural representation for SMT solver

**Cons:**

* too trivial, must be generalized, but *how* unclear:
  * obviously need to allow boards bigger than 3x3...
  * game board need to be square, or can be rectangle?
  * what are the winning conditions?
    * still 3 in a row, or
    * `N` in a row for an `NxN`` square, or
    * `N` in a row for an `MxN` rectangle where `N<=M`, or
    * number in a row is generalized (make it a parameter for game initialization)?
* we already know that two perfect players playing under standard rules always draw
  * rules of games like this tend to lead to optimal solutions where "first player wins" or "perfect adversaries always draw"- not very interesting

**misc:**

<details>
<summary>
 <ul><li><h3>tic-tac-toe (generalized) search cost/heuristic function thoughts (CLICK TO EXPAND)</h3></li></ul>
</summary>

<strong> design </strong>
unclear depending on generalizations, but for NxN squares requiring N in a row to win, this seems reasonable:

```python
# "winnable combinations": the set of sets in which each subset is a minimal set of positions such that one player owning all of them leads to a non-draw terminal state
#   minimal meaning no element may be removed without changing the win-state
#   e.g., in standard tic-tac-toe, this is the rows, columns, and diagonals; there are 8 winnable combos in total
#   each of these is minimal because e.g. if you only owned the top 2 corners (removed the top middle position) then the top-row combination would no longer be a terminal state

def combos_containing(p: Position):
    """The set of all position combinations that can cause a terminal state."""
    return {c for c in Game.all_minimal_terminal_combinations if p in c}

def gross_points(player: Player):
    """
    Scoring function that optimizes for choosing positions that can win in more than one way.
    """
    # assign the same absolute value for all wins and losses regardless of how "close" the game was
    if lost(player, Game.board):  # losing is the worst possible state; negative infinity points
        return float('-inf')
    if won(player, Game.board):  # winning is best possible state; positive infinity points
        return float('inf')

    points = 0
    for p: Position in player.positions:
        for combo in [c for c in winnable_combinations if p in c]:  # consider each terminal state where P comes into play
            if not any (owned_by_opponent(position) for position in `winnable_combination`):  # no points if opponent blocked you
                points +=1
    return points

def net_score(players: tuple[Player, Player]):
    "zero-sum score suitable for minimax agents"
    return {
        player[0]: gross_points(player[0]) - gross_points(player[1]),
        player[1]: gross_points(player[1]) - gross_points(player[0])
    }
```

<strong> analysis </strong>

* So basically, get 1 point for each winning combo that your play contributes to, but only if opponent isn't blocking
* Example boards ((2x2) board where N=2 to win)
* Gross Score (X): There are 3x winnable combos containing X's only position, so X gets 3 points. 
* Gross Score (O): O has no positions, and therefore gets 0 points.
* net_score('X'): 3
```
X | 
-----
  |
```

* Gross Score: 2 for both players (1x winnable combo starting from (0,0); top-left to top-right is blocked for both players. Both players have 3 potentials combos, where 1 is blocked)
* net_score('X'): 0
* Suppose X is going next
  * X needs to decide which position to choose
  * Either position results in 'infinity' score (win)
  * Both positions are equally good (agent could break ties arbitrarily)
```
X | O
-----
  |  
```

Using above functions, a time-bounded minimax agent could perform IDS search on the state space to choose the best strategy it can within the time constraint given.

</details>

## Minesweeper (Reinforcement learning)

**pros:**

* already sufficiently hard problem (NP-complete, can't be bruteforced for non-trivial board sizes)
* game state can be naturally represented by sparse matrices (which may just be a list of coordinates):
  * matrix 1: guesses (game ends when you hit a mine, so we don't need to remember `guessed & mine` vs `guessed & missed`)
  * matrix 2: revealed squares (can be re-calculated from guesses, but should be memorized for better performance)
  * matrix 3: location of mines
  * matrix 4: hints (the #'s indicating how many mines are adjacent; could be calculated from matrix 3 but should be memorized for performance)
* one player game- AI can play alone many times; no need to answer questions about who we're training to defeat (e.g. human vs ai agent)
* lends itself to "stretch goals"; we can try & compare to approaches:
  1. start w/ just solving safely (make agent choose a position each turn, agent is rewarded for each move it makes without 'dying')
  2. more complex cost functions to make trade-offs between # of moves and safety, e.g., higher reward for clicks revealing more new information

**cons:**
* scoring function maybe a little unclear:
  * should AI attempt to minimize # of moves
  * or do we only care about solving?
  * Maybe this is actually a pro... (see 'stretch goals' in 'pros')

## Connect four (Reinforcement learning)

**Pros:**

* game state has natural grid representation where each cell takes one of 3 state (`empty` vs `red` vs `black`)
  * checking if game state is valid (no floating pieces) is computationally in-expensive
* alternatively can be represented as array of lists where each list represents pieces w/ head of list=bottom (appending new pieces as they're "dropped" into the column)

**Cons:**

* like tic-tac-toe, too easy to brute-force & would require generalization (but *how* is unclear):
  * lifting restriction that pieces are placed on bottom?
  * bigger "board"?
  * winning condition requires different # in a row?
  * unclear which of the above would make the game non-trivial

## Snake(Reinforcement Learning)

**Pros:**

* non-trivial game (exponential state space)
* fun to visualize
* interesting properties not really seen in pacman:
  * interaction with environment causes agent itself to change (i.e., eating food -> grow)
  * agent is its own worst enemy (easy to lose by blocking self in/eating self)

**cons:**

* not representable by a grid alone (snake spans multiple cells)
  * however, trivially solved: snake = linked list. on each game update, prepend `Cell.at(snake.position, snake.current_direction)` to snake list. If snake did not eat during this update, pop tail element. (i.e., grow by one if we ate, otherwise we're just moving by removing the segment at the tail position and adding one to the head)
* probably not suitable for search strategies (number of branches that can be pruned e.g. via minimax won't make up for the long number of timesteps required to complete the game; the search tree is very very large and once the snake is long enough it's not clear we can compute a strategy where the snake doesn't block itself in within a reasonable amount of time)
* scoring function and agent properties not obvious (should it optimize to grow fast, or do we only care that it grows eventually and doesn't lose?)

## Battleship (Reinforcement learning | Minimax)

**Pros:**

**Cons:**

* game state can't be represented by a grid alone (ships span multiple cells)
* problem definition is unclear
  * just battle phase, or solve placement phase too?
  * if not solving placement phase too, how to generate & evaluate AI on placements (how do we get board setups to play on, and what are we comparing performance to)?
  * if solving placement phase too, should we be training to beat human players or AI agents?
      * human players: where to get training data?
      * AI agents: adverserial learning agents, or fixed agents?
        * fixed agents:
          * e.g. in pacman projects we had pacman learning against agents that weren't doing any learning themselves
          * is this even interesting? I don't think so...
        * learning agents: could be hard to do right. do we always train against the current version of our AI? it might get stuck in weird local minima, e.g., evolving to choose the worst possible placement strategy so that every game is a quick win or quick loss
* cost function could be hard to design (all hits worth the same? sinking ship give extra points? small ships worth more than big ships?:)

# Final Project
## Members
Justin Perez<br>
Levin Leesemann<br>
Melissa Krumm<br>
Miaomiao Zou
## Documents
[Project Report](https://docs.google.com/document/d/14OXp7eeJq8z1no57VwKUTgWbHgY5yk8jf76AjHZQZYQ/edit?usp=sharing)<br>

