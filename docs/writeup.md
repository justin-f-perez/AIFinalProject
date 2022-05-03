Ascii diagram notation:
```
snake head:
◄ = left
▲ = up
▼ = down
► = right
┌───┐
│   │
│   │ = a border around a 3x3 play grid
│   │
└───┘
─│ = "straight" body segments, i.e., adjacent segments are in the same vertical/horizontal plane
┘┐┌└ = "curved" body segments, i.e., adjacent segments form an "L" shape *OR* for the tip of the tail, it may curve to indicate where the end of the tail previously was
```
note: body segments and border are composed of same characters
note: due to differences in font/character rendering, it can create an illusion of "an extra row of space" since vertical space is greater than horizontal space. Select/highlight characters with mouse if unsure.

For B1 I think we need 2 things:
* description of snake game model. this can be done mostly mechanically by translating code to English and abstracting a little (e.g. ifs/conditionals in the code collectively represent the constraints on the game model)
* description of what we're trying to do to the game model. What are we trying to optimize? Score? Score within some time constraints? Then we need definition of Score here and any other constraints on our optimization.

## Input
### Game Initialization Inputs (problem parameters)
* the game grid dimensions (the number of discrete spatial blocks in the X-dimension and Y-dimension, where snake always moves exactly 1 block at each instant tick of time)
* Framerate, or 0 for "no framerate limit"
  * **❗NOTE: framerate is probably only relevant if we timeout agent decisions during test/evaluation. We currently do not force AI agents to timeout/make a decision by each clock tick, but maybe we should when framerate is non-zero❗**.
* number of food that in play at any given time. After initialization, this is invariant for the duration of play. Whenever a food is eaten, a new one is spawned in any random location where a food does not already exist.
* Snake initial position is currently fixed like this, with length 3, head at top left, pointed down, but ❗it could be paramaterized too❗ (❗in fact if we can read initial position & direction & initial food distribution from a config file/"game save" then we could design training/testing scenarios❗):
```python
snake = Snake(
    segments=[
      Coordinate(1, 1),
      Coordinate(1, 0),
      Coordinate(0, 0),
    ],
    direction=Direction.DOWN,
)
# ┌────────┐
# │┌──────┐│
# ││┌─    ││
# ││▼     ││
# ││      ││
# │└──────┘│
# └────────┘
```

### Gameplay Inputs
* direction for snake to travel 
  * game guards against invalid changes of direction
  * this is effectively equivalent to "two actions: Turn Left, Turn Right" (three actions if you count "Do Not Turn")
* There is additionally a random element: where the food spawns is chosen randomly and not known ahead of time
  * It's random, but with the constraint that two pieces of food cannot occupy the same location simultaneously.
  * ❗The RNG seed could be made into an initialization parameter, and probably should be, to enable repeatable results❗


## Theoretical Best Output

### Snake Length
Snake length is maximized when snake occupies the entire play space + 1. By the pigeon-hole principle, the snakes head must either be out of bounds or occupying the same location as another body segment. In other words, the snake must always lose when `|snake| = grid_area + 1; grid_area = W + H` where `|snake|` is length of snake, `W` is how many discrete blocks wide the game is, and `H` is similarly grid height. Thus, best possible score, if score is length of snake, is `grid_area + 1`.

### Time to Snake Length |N|
Calculating a theoretical best for time would be trickier due to
1. the random nature of the food spawn
2. multiple food spawn
3. food may spawn "under" snake
4. snake must navigate around its own body to get to food, and body is also moving

However we could state that the "worst-case" round for collecting a piece of food is one in which 
* only one piece of food spawns at any given time
* snake just ate, next piece of food spawns just behind snake's head
* snake currently occupies the entire grid without touching itself
Then, to reach the next piece of food the snake will need to travel the entire distance of the grid, `-1`. This is because if the snake literally traveled the entire distance it would end up in the starting position, we need to go just 1 short of this. In fact, this generalizes to `- |F|` where `|F|` is the number of food that can spawn at any given time because for each piece of food that is spawned, we know 2 food cannot occupy the same location, so each subsequent food is in the next-worst location that maximizes the snake's distance traveled (and thus must be 1 step closer on the snake's optimal path.) However, in such a case, we know the snake eats `F` food if it simply travels the distance of the `grid area -1`, as it will have reached every position that a food occupied when it first set out on its journey and food do not move until eaten. Therefore, the amortized upper-bound time cost per food eaten when there are `|F|` food is `(grid_area - 1)/|F|` ticks.

Thus, an initial estimate on upper-bound of time cost to reach "end game snake length" is `(grid_area + 1) * ((grid_area -1)/|F|)`.

**Conjecture 1**: A snake whose body length is at least `game.grid_width * game.grid_height` can *always* reach the next piece of food within `2*len(snake) + 2` ticks. Thus we would have a worst case time-to-next-food of:

```python
max(
    game.grid_width + game.grid_height, 
    min(
        (2 * len(snake)) - len(food) + 2,
        game.grid_width * game.grid_height
    )
)
```

Trivially, we know from above that a snake that is already head-to-tail can reach the next piece of food when that piece of food. However, in that proof, the snake was OK with dying for the last piece. In this case, we may need to create a 'kink' as space permits.

Kink Diagram:
```
1 ┌───────┐ 2┌───────┐ 3┌───────┐
  │┌────┐ │  │┌─────▼│  │┌─────┐│
  │▲┌┐┌┐│ │  ││┌┐┌┐  │  ││┌┐┌S┌┘│
  │F┘└┘└┘ │  │F┘└┘└┘ │  │F┘└┘S◄ │
  └───────┘  └───────┘  └───────┘
```
1. snake just ate, food spawns behind head
2. if snake just follows tail, it will reach food within `|snake|` ticks of diagram 1, but it will grow into/eat its own tail (game over) when it eats the food. Therefore, it travels one extra space instead of immediately following the tail at the fist opportunity
3. snake has completed kink maneuver actions "move right, move down, move left, move down" in the top-right-most 4 cells gave it a 2 block buffer (marked with S) between head and tail.
**CONJECTURE 2**: This is the smallest buffer can be created.
