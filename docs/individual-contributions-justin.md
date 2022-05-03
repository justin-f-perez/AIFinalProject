Feel free to use this as a scratch-pad/journal to keep notes on what you accomplished. To avoid merge conflicts you might consider either:
1. put notes on others' contributions at the TOP. Git is pretty good at merging text changes when there aren't overlaps. I think we'll mostly be editing our own notes, and I don't think there's a chance of merge conflict when a text insert happens at the top of a document if only 1 person adds to it at a time (leaving rest of the document for the primary author to edit)
2. Or, open a pull request and assign to the person whose file you edited (that way they are sure to be aware what changes you made and can be sure to pull these changes in before making subsequent edits of their own.)

Justin:
* provided input for/helped decide what problem to solve
* technical design & implementation of snake game
  * need the game to run correctly
  * need to be flexible/easy to modify so new experiments can be implemented quickly & painlessly
  * need input control decoupled from game model (to "hook up" an agent; most available game code is coupled to HID [human input device])
      * implemented via Controller classes in [controllers.py](../controllers.py), an abstraction which solicits inputs from an input source and feeds them to the game model for each update
  * need game model decoupled from GUI (to "uncap framerate" for faster training and evaluation; when an agent is playing, the game can elapse time as fast as processing power allows agent to make decisions)
      * implemented by abstracting view/display (or lack of display) into separate View classes [views.py](../views.py)
 * wrote problem-definition section
