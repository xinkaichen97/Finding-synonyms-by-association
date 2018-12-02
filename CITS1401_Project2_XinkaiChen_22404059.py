# CITS1401 Project 2
# Author: Xinkai Chen 22404059
# Version: May 2018
import sys
import re

# Open and process the given file: change all the characters to lower case, and get rid of the newline character
# Handle different exceptions: empty file, wrong file name and unacceptable contents
def process_file(filename):
    try:
        with open(filename, mode='r', encoding='utf-8') as fhand:
            contents = fhand.read().lower().replace('\n', ' ')
        if len(contents) == 0:
            raise Exception(filename + ' is an empty file!')
        if contents.islower() is False:
            raise Exception(filename + ' does not contain cased character(s)!')
        return contents
    except IOError:
        print(filename, 'does not exist!')
        sys.exit(1)
    except UnicodeDecodeError:
        print(filename, 'contains illegal character(s)!')
        sys.exit(1)

# Given the common words file contents, generate the set of common words
def generate_common_set(commonwords_file_contents):
    commonwords_set = set(commonwords_file_contents.split())
    return commonwords_set

# Given the corpus file contents, generate a list of strings, each of which represents one sentence in the file
def generate_sentences_list(corpus_file_contents):
    contents = corpus_file_contents
    for ch in ',;:()[]"\'':
        contents = contents.replace(ch, ' ')
    for ch in '.!?':
        contents = contents.replace(ch, '.')
    return contents.split('.')[:-1]

# Given the corpus file contents and the common words set, generate a list of sets containing words from each sentence
# The words in each set are unique and common words are excluded (if exist)
def generate_words_list(corpus_file_contents, commonwords_set):
    sentences_list = generate_sentences_list(corpus_file_contents)
    words_list = [] # we use list because we allow one sentence to appear more than once in the file
    for str in sentences_list:
        temp = set()
        words = str.split()
        for word in words:
            if word not in commonwords_set and re.search('[,;:()[\]"\'\n]+', word) is None:
                temp.add(word)
        words_list.append(temp)
    return words_list

# Given the list of word sets, generate profiles for each word
# Only two words that appear in the same sentence will be recorded in the profiles
def generate_profile(words_list):
    profiles = {}
    for words_set in words_list:
        for profile_word in words_set:
            if profile_word not in profiles:
                profiles[profile_word] = {}
            for associate_word in words_set:
                if associate_word != profile_word:
                    profiles[profile_word][associate_word] = profiles[profile_word].get(associate_word, 0) + 1
    return profiles

# Given two profiles, compute both numerator and denominator and return the score
def get_score(target_profile, query_profile):
    target_denom, query_denom = 0, 0
    if target_profile is None or query_profile is None:
        raise Exception('Profile does not exist!')
    if target_profile == {} or query_profile == {}:
        raise Exception('Profile is empty!')
    for key in target_profile:
        target_denom += target_profile[key] ** 2
    for key in query_profile:
        query_denom += query_profile[key] ** 2
    denominator = (query_denom * target_denom) ** 0.5
    numerator = 0.0
    for key in query_profile:
        if key in target_profile:
            numerator += target_profile[key] * query_profile[key]
    return numerator / denominator

# Enter one target word and several query words, print the scores for each query word (in descending order)
# The one with the highest score is the synonym; if all query words have score 0, then no synonym is found
def query_word(profiles):
    while True:
        scores = []
        target = input('Enter conceptword (or blank line to end): ')
        if len(target.split()) > 1:
            raise Exception('More than one target word entered!')
        target = target.lower().strip(' ') # we accept minor differences of input (e.g. "  RiVer " VS "river")
        if target == '':
            print('No target word entered, terminating the program')
            break
        if target.islower() is False:
            raise Exception('Target word does not contain cased characters!')
        if target in profiles:
            target_profile = profiles[target]
        else:
            raise Exception('Target word not found!')
        query_words = set()
        print('Enter query words, one per line. Blank line to end')
        while True:
            word = input()
            if len(word.split()) > 1:
                raise Exception('More than one query word in one line!')
            word = word.lower().strip(' ')
            if word == target:
                raise Exception('Target word appears in query words!')
            if word != '':
                query_words.add(word)
            else:
                break
        if len(query_words) == 0:
            raise Exception('No query word entered!')
        for query in query_words:
            if query in profiles:
                query_profile = profiles[query]
                score = get_score(target_profile, query_profile)
            else:
                score = 0.0
            scores.append((score, query))
        lst = sorted(scores, reverse=True)
        print(target)
        blank_space = ' ' * len(target)
        for score, query in lst:
            print(blank_space + "{0}{1:8.3f}".format(query, score))
        if lst[0][0] > 0:
            if len(lst) > 1 and lst[1][0] == lst[0][0]: # multiple equal scores
                equal_scores = []
                for score, query in lst:
                    if score == lst[0][0]:
                        equal_scores.append(query)
                print('Synonym for', target, 'are', ', '.join(equal_scores)[:-1], 'and', equal_scores[-1], '\n')
            else:
                print('Synonym for', target, 'is', lst[0][1], '\n')
        else:
            print('No synonym can be found for', target, '\n')

# Given the name of corpus file and common words file (optional), find the synonyms
def main(corpus_file_name, commonwords_file_name=None):
    if corpus_file_name == 'common.txt' or corpus_file_name == commonwords_file_name:
        raise Exception('Invalid input of file name(s)!')
    corpus_file_contents = process_file(corpus_file_name)
    commonwords_set = set()
    if commonwords_file_name is not None:
        common_file_contents = process_file(commonwords_file_name)
        commonwords_set = generate_common_set(common_file_contents)
    words_list = generate_words_list(corpus_file_contents, commonwords_set)
    profiles = generate_profile(words_list)
    query_word(profiles)