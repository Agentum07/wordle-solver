## Wordle Solver
Created in honour of 1000 days of Wordle!

_For when you really need to maintain your streak._

I created a solver from scratch that uses a simple algorithm built upon the basic rules of the game and a couple of predetermined useful predictions to solve Wordle. The algorithm has managed to reach avg. levels of predictions that are less than 0.21 away from the [best known automated solver (avg. 3.42)](https://jonathanolson.net/wordle-solver/).

## Statistics
* Total words: 2315
* Average number of predictions per word: 3.6358
* Number of words failed (i.e took more than 6 guesses): 10
* Accuracy: **99.56%**

![results graph](output/results.png)

## Usage
1. Run wordle_solver.py: `python wordle_solver.py`.
2. Use the prediction provided by the algorithm.
3. Enter the feedback in the form of "GYBBY", where
    * B stands for black/grey.
    * Y stands for yellow.
    * G stands for green.
Repeat until you win.

## Demo
[demo video](https://github.com/Agentum07/wordle-solver/assets/62797335/e32c8ea5-289a-4773-88a2-fec7e8ea7c6f)

## Future Plans
* Create frontend to remove running python script.
* Create a telegram bot to automatically solve the most recent wordle.
