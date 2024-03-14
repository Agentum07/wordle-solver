import re
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import string
import time

class WordleSolver:
    def __init__(self, possible_answers_df):
        self.misplaced_letters = dict() # will save a mapping of letter to possible positions
        self.guess_df = possible_answers_df.copy(deep=True)
        self.all_words_df = possible_answers_df.copy(deep=True)

        self.letters = defaultdict(str)
        for i in range(5):
            self.letters[i] = None
        self.update_letter_counts()
        # print(self.make_guess())
        # print(self.letter_counts)
        # self.update_green_letter('S', 0)
        # self.get_letter_counts()
        # print("123123123123123123123123123123123")
        # print(self.letter_counts)

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

    def make_guess(self):
        # check if self.letters is full. if yes, return that.
        # otherwise get guess.
        if any(value is None for value in self.letters.values()):
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
                self.update_letter_counts()
            elif response[i] == 'B':
                self.update_black_letter(guess[i])
                self.update_letter_counts()



def parse_answers():
    with open('data/answers.txt') as file:
        possible_answers = file.readlines()

    possible_answers_list = sorted([re.sub(r'[^A-Z]', '', t.upper()) for t in possible_answers[0].split(',')])
    # print(len(possible_answers_list), possible_answers_list[:5])

    possible_answers_arr = np.array([list(word) for word in possible_answers_list])
    possible_answers_df = pd.DataFrame(data=possible_answers_arr, columns=[f'letter_{i+1}' for i in range(5)])
    possible_answers_df['word'] = possible_answers_list
    return possible_answers_df

possible_answers_df = parse_answers()

def get_response(guess, word):
    print(f'Guess: {guess}, word: {word}')
    guess = [c for c in guess]
    word = [c for c in word]
    response = [None for _ in range(5)]
    green = []
    yellow = []
    black = []
    # get all the green ones first.
    for i in range(5):
        if guess[i] == word[i]:
            green.append(i)
    print(green)
    print(guess)
    print(word)
    for i in green:
        guess.pop(i)
        word.pop(i)

    for i in range(len(word)):
        if guess[i] in word and guess[i] != word[i]:
            yellow.append(i)
        else:
            black.append(i)
    
    for i in range(5):
        if i in green:
            response[i] = 'G'
        elif i in yellow:
            response[i] = 'Y'
        else:
            response[i] = 'B'
    return ''.join(response)

guess_counter = 0
unsolved_words = []
start = time.time()
# words = ['BATCH', 'HOUND', 'JAUNT', 'SAPPY']
words = ['BATCH']
# for word in possible_answers_df.iloc[:]['word']:
for word in words:
    response = ""
    curr_ctr = 0
    solver = WordleSolver(possible_answers_df)
    while response != 'GGGGG':
        guess = solver.make_guess()
        response = get_response(guess, word)
        print(f'Guess: {guess}, response: {response}, words remaining: {solver.guess_df.shape[0]}')
        solver.process_response(guess, response)
        curr_ctr += 1
        guess_counter += 1

    if response != 'GGGGG':
        unsolved_words.append(word)
    else:
        print(f'guessed {word} in {curr_ctr} tries!')
    print()
end = time.time()

print(guess_counter / 4)
print(unsolved_words)
print(f'time taken: {end - start}s')
# print(possible_answers_df.shape[0])
# print(solver.make_guess())
# solver.process_response("SLATE", "GBBBG")
# print(solver.make_guess())
# solver.process_response("SHONE", "GBBYG")
# print(solver.make_guess())
# solver.process_response("SPICE", "GBYGG")
# print(solver.make_guess())
# solver.process_response("SINCE", "GGGGG")
# print(solver.make_guess())