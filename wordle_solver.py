import re
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import time
import matplotlib.pylab as plt

class WordleSolver:
    def __init__(self, possible_answers_df):
        self.misplaced_letters = dict() # will save a mapping of letter to possible positions
        self.guess_df = possible_answers_df.copy(deep=True)
        self.all_words_df = possible_answers_df.copy(deep=True)

        self.letters = defaultdict(str)
        for i in range(5):
            self.letters[i] = None
        self.update_letter_counts()
        self.guess = 0

    def update_letter_counts(self):
        self.letter_counts = Counter()
        for i in range(5):
            self.letter_counts[i + 1] = Counter(self.guess_df[f'letter_{i+1}'])

    def get_freq_score(self, letters: str) -> int:
        letters = re.sub('^A-Z', '', letters.upper())
        score = 0
        for i, letter in enumerate(letters):
            score += self.letter_counts[i+1][letter]
        
        return score
    
    def get_guess(self):
        freq_score_vector = np.vectorize(self.get_freq_score)
        self.guess_df['freq_score'] = freq_score_vector(self.guess_df['word'])
        self.guess_df = self.guess_df.sort_values(by='freq_score', ascending=False)
        return self.guess_df.iloc[0]['word']

    def update_green_letter(self, letter, pos):
        self.letters[pos] = letter
        self.guess_df = self.guess_df[self.guess_df[f'letter_{pos + 1}'] == letter]

    def update_black_letter(self, letter):
        # remove the letter from all rows in the self.guess_df
        self.guess_df.replace(letter, pd.NA, inplace=True)
        self.guess_df.dropna(inplace=True)        

    def update_yellow_letter(self, letter, pos):
        # remove the letter from pos + 1 column in the guess df.
        self.guess_df = self.guess_df[self.guess_df[f'letter_{pos + 1}'] != letter]
        rows_to_drop = self.guess_df.apply(lambda row: letter not in row.values, axis=1)
        self.guess_df = self.guess_df[~rows_to_drop]


    def make_guess(self):
        # check if self.letters is full. if yes, return that.
        # otherwise get guess.
        self.guess += 1
        if any(value is None for value in self.letters.values()):
            if self.guess_df.shape[0] > 11:
                if self.guess == 1:
                    return "SLATE"
                elif self.guess == 2:
                    return "CORNI"
                elif self.guess == 3:
                    return "DUMPY"
                else:
                    guess = self.get_guess()
            else:
                guess = self.get_guess()
        else:
            guess = ''.join(self.letters.values())
        
        return guess

    def process_response(self, guess, response):
        """len(response) = 5.
            response[i] = Y, G, B
        """
        guess = re.sub('^A-Z', '', guess.upper())
        for i in range(5):
            if response[i] == 'G':
                self.update_green_letter(guess[i], i)
            elif response[i] == 'Y':
                self.update_yellow_letter(guess[i], i)
            elif response[i] == 'B':
                self.update_black_letter(guess[i])

        self.update_letter_counts()


def parse_answers():
    with open('output/answers.txt') as file:
        possible_answers = file.readlines()

    possible_answers_list = sorted([re.sub(r'[^A-Z]', '', t.upper()) for t in possible_answers[0].split(',')])

    possible_answers_arr = np.array([list(word) for word in possible_answers_list])
    possible_answers_df = pd.DataFrame(data=possible_answers_arr, columns=[f'letter_{i+1}' for i in range(5)])
    possible_answers_df['word'] = possible_answers_list
    return possible_answers_df

def get_response(guess, word):
    guess = [c for c in guess]
    word = [c for c in word]
    response = [None for _ in range(5)]
    green = []
    yellow = []

    for i in range(5):
        if guess[i] == word[i]:
            green.append(i)
        elif guess[i] in word:
            yellow.append(i)
    
    for i in range(5):
        if i in green:
            response[i] = 'G'
        elif i in yellow:
            response[i] = 'Y'
        else:
            response[i] = 'B'
    return ''.join(response)

def plot(d):
    lists = sorted(d.items(), key=lambda kv: kv[0], reverse=False)
    x, y = zip(*lists) # unpack a list of pairs into two tuples

    plt.bar(x, y)
    plt.xlabel('Number of predictions')
    plt.ylabel('Number of words')
    for i in range(len(x)):
        plt.text(x[i], y[i], str(y[i]), ha='center', va='bottom')
    x_values = range(1, len(x) + 1)
    plt.xticks(x_values, x)
    plt.savefig('output/results.png')
    plt.show()

def solve_all(possible_answers_df):
    guess_counter = 0
    unsolved_words = []
    start = time.time()
    d = {}
    string_to_write = ""
    with open("output/output.txt", 'w') as f:
        for word in possible_answers_df.iloc[:]['word']:
            string_to_write = f'{word}: '
            response = ""
            curr_ctr = 0
            solver = WordleSolver(possible_answers_df)
            while response != 'GGGGG':
                guess = solver.make_guess()
                response = get_response(guess, word)
                # print(f'Guess: {guess}, response: {response}, words remaining: {solver.guess_df.shape[0]}')
                solver.process_response(guess, response)
                curr_ctr += 1
                guess_counter += 1
                string_to_write += f'{guess} '

            string_to_write += "\n"
            f.write(string_to_write)
            if curr_ctr not in d.keys():
                d[curr_ctr] = 1
            else:
                d[curr_ctr] += 1
            if response != 'GGGGG':
                unsolved_words.append(word)
    end = time.time()
    print(d)
    print(guess_counter / 2315)
    print(guess_counter / 2315)
    print(unsolved_words)
    print(f'time taken: {end - start}s')
    print((end - start)/2315)
    plot(d)


def main():
    possible_answers_df = parse_answers()
    solver = WordleSolver(possible_answers_df)
    print("Welcome to Wordle solver! I will solve your game for you.")
    print("Enter the feedback in the form of 'GYBBY', where ")
    print("B stands for black/grey.")
    print("Y stands for yellow.")
    print("G stands for green.")

    curr_input = ""
    while curr_input != 'GGGGG':
        guess = solver.make_guess()
        print(f"Hmmm, try {guess}")
        curr_input = input("Enter the feedback: ")
        solver.process_response(guess, curr_input)
        print(f"Words left: {solver.guess_df.shape[0]}")

    print("Great, we solved it!")

if __name__ == "__main__":
    main()
