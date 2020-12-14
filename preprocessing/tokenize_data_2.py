import string
import re
import json
from pathlib import Path
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag
from html import unescape
from .constants import types, SPACES_REMOVED, TOKENIZED
from .prepare_directories import prepare_directories


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def tokenize_one(content, stops=stopwords.words("english"), lemmatizer=WordNetLemmatizer()):
    """Tokenize the content of one problem."""
    sentences = []
    for sentence in sent_tokenize(content):
        tokens = word_tokenize(unescape(sentence).lower())
        # delete all non-word strings
        tokens = list(filter(lambda token: any(c.isalpha()
                                               for c in token), tokens))

        # split strings with the following characters in them
        modified = []
        delimiters = ["/", ".", "-"]
        pattern = "|".join(map(re.escape, delimiters))
        for token in tokens:
            modified.extend(re.split(pattern, token))

        # remove single-character strings
        tokens = list(filter(lambda token: len(token) > 1, modified))

        # remove punctuations and stopwords
        tokens = list(
            filter(lambda token: token not in string.punctuation and token not in stops, tokens))

        # lemmatize tokens with POS tagging
        tagged = pos_tag(tokens)
        for index, pair in enumerate(tagged):
            token, tag = pair
            pos = get_wordnet_pos(tag)
            lemmatized = lemmatizer.lemmatize(
                token, pos=pos) if pos else lemmatizer.lemmatize(token)
            # try
            if tag == "NNS" and lemmatized == token:
                lemmatized = lemmatizer.lemmatize(
                    token, pos=wordnet.VERB)
            tokens[index] = lemmatized

        # tokens = [st.stem(token) for token in tokens]
        # remove numbers
        tokens = list(filter(lambda token: not (
            token.isnumeric() or (token[0] == "-" and token[1:].isnumeric())), tokens))
        if len(tokens) > 0:
            sentences.append(tokens)
    return sentences


def tokenize_data(dest_path, src_path):
    """Tokenize all text data."""
    stops = stopwords.words("english")
    lemmatizer = WordNetLemmatizer()
    for problem_type in types:
        src_type_path = src_path / problem_type
        dest_type_path = dest_path / problem_type
        for problem_path in src_type_path.glob("*.json"):
            print(f"Tokenizing {problem_path.name}")
            with open(problem_path, "r", encoding="utf-8") as f:
                problem = json.load(f)
                if not problem:
                    continue

            problem["content"] = tokenize_one(
                problem["content"], stops, lemmatizer)

            output_file_path = dest_type_path / problem_path.name
            with open(output_file_path, "w") as f:
                json.dump(problem, f, indent=4)


if __name__ == "__main__":
    spaces_removed_path = prepare_directories(SPACES_REMOVED)
    tokenized_path = prepare_directories(TOKENIZED)
    tokenize_data(tokenized_path, spaces_removed_path)
