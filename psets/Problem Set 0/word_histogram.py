from typing import Any, Dict, List
import utils


def word_histogram(text: str) -> dict:
    '''
    This function takes a string and returns a dictionary containing
    each word and its frequency in the string.
    
    A word histogram counts how many times each word appears.
    Assume words are separated by spaces and the comparison is case-sensitive.
    
    Example:
    word_histogram("cat dog cat") -> {"cat": 2, "dog": 1}
    '''
    # return { word: text.split(" ").count(word) for word in text.split(" ") if len(word) > 0 }
    word_dict = dict()
    words = text.split(" ")
    for word in words:
        if len(word) == 0:
            continue
        word_dict[word] = word_dict.get(word, 0) + 1
    return word_dict