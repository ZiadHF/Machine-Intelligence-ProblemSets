from typing import Tuple, List
import utils

'''
    The DecipherResult is the type defintion for a tuple containing:
    - The deciphered text (string).
    - The shift of the cipher (non-negative integer).
        Assume that the shift is always to the right (in the direction from 'a' to 'b' to 'c' and so on).
        So if you return 1, that means that the text was ciphered by shifting it 1 to the right, and that you deciphered the text by shifting it 1 to the left.
    - The number of words in the deciphered text that are not in the dictionary (non-negative integer).
'''
DechiperResult = Tuple[str, int, int]

def caesar_dechiper(ciphered: str, dictionary: List[str]) -> DechiperResult:
    '''
        This function takes the ciphered text (string)  and the dictionary (a list of strings where each string is a word).
        It should return a DechiperResult (see above for more info) with the deciphered text, the cipher shift, and the number of deciphered words that are not in the dictionary. 
    '''
    dictionary = set(dictionary)
    current_max_correct = 0
    current_deciphered = ""
    current_shift = 0
    for i in range(26):
        deciphered = ""
        correct_words = 0
        for char in ciphered:
            if char == ' ':
                deciphered += ' '
                continue
            modified_char = ord(char) - i
            if modified_char < ord('a'):
                modified_char = modified_char + 26
            deciphered += chr(modified_char)
        decipher_split = deciphered.split(" ")
        for word in decipher_split:
            if word in dictionary:
                correct_words += 1
        if correct_words == len(decipher_split):
            return (deciphered, i, 0)
        if correct_words > current_max_correct:
            current_max_correct = correct_words
            current_deciphered = deciphered
            current_shift = i
    return (current_deciphered, current_shift, current_max_correct)
