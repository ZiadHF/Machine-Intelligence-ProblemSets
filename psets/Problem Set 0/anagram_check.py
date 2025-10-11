import utils

def anagram_check(s1: str, s2: str) -> bool:
    '''
    This function takes two strings and returns whether they are anagrams of each other or not.
    An anagram is formed when two strings contain exactly the same letters in any order.
    For example, "listen" and "silent" are anagrams, while "hello" and "world" are not.
    Assume the comparison is case-sensitive.
    '''
    return sorted(s1) == sorted(s2)