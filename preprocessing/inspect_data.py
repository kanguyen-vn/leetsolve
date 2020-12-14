import json
import io
import re
from pathlib import Path
from bs4 import BeautifulSoup
from nltk.corpus import words

from .constants import types, PROBLEMS_BY_TAG_JSON, COUNT_TAGS_JSON, CLEANED_DATA_PATH


def count_problems_by_tags():
    """Count the number of problems pertaining to each tag."""
    with open(PROBLEMS_BY_TAG_JSON, "r") as f:
        tags = json.load(f)
    data = {key: len(tags[key]) for key in tags}
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    with open(COUNT_TAGS_JSON, "w") as f:
        json.dump(sorted_data, f, indent=4)


def inspect_remaining_divs(src_path):
    """Inspect all remaining divs in problems."""
    div_dict = {}
    for type in types:
        type_path = src_path / type
        for problem_path in type_path.glob("*.json"):
            with open(problem_path, "r", encoding="utf-8") as f:
                problem = json.load(f)
            soup = BeautifulSoup(problem["content"], "html.parser")
            id = problem["id"]
            for div in soup.find_all("div"):
                if div.parent == None or div.parent.name != "div":
                    text = str(div)
                    if id not in div_dict:
                        div_dict[id] = [text]
                    elif text not in div_dict[id]:
                        div_dict[id].append(text)

    examine_path = src_path / "examine_divs.txt"
    with open(examine_path, "w") as f:
        json.dump(div_dict, f, indent=4, sort_keys=True)


def find_remaining_tags(src_path):
    """Find remaining HTML tags in problems."""
    tags = []
    for type in types:
        type_path = src_path / type
        for problem_path in type_path.glob("*.json"):
            with open(problem_path, "r", encoding="utf-8") as f:
                problem = json.load(f)
            soup = BeautifulSoup(problem["content"], "html.parser")
            for tag in soup.find_all():
                if tag.name not in tags:
                    tags.append(tag.name)
    remaining_tags_path = src_path / "remaining_tags.txt"
    with open(remaining_tags_path, "w") as f:
        json.dump(tags, f, indent=4, sort_keys=True)
    return tags


def inspect_remaining_tag(tag_name, src_path):
    """Find which tag blocks remain for a remaining HTML tag in a problem."""
    tag_dict = {}
    for problem_type in types:
        type_path = src_path / problem_type
        for problem_path in type_path.glob("*.json"):
            with open(problem_path.path, "r", encoding="utf-8") as f:
                problem = json.load(f)
            soup = BeautifulSoup(problem["content"], "html.parser")
            id = problem["id"]
            for tag in soup.find_all(tag_name):
                text = str(tag)
                if id not in tag_dict:
                    tag_dict[id] = [text]
                elif text not in tag_dict[id]:
                    tag_dict[id].append(text)

    examine_path = src_path / f"examine_{tag_name}s.txt"
    with open(examine_path, "w") as f:
        json.dump(tag_dict, f, indent=4, sort_keys=True)


def process_remaining_tags(path_name):
    """With remaining HTML tags found, look for remaining tag blocks."""
    src_path = CLEANED_DATA_PATH / path_name

    remaining_tags = find_remaining_tags(src_path)
    inspect_remaining_divs(src_path)
    for file_path in src_path.glob("*.*"):
        if file_path.name.startswith("examine_"):
            file_tag = file_path.name[8:-5]
            if file_tag not in remaining_tags:
                file_path.unlink()

    for tag in remaining_tags:
        if tag != "div":
            inspect_remaining_tag(tag, src_path)


def inspect_nonascii_characters(path_name):
    """Inspect non-ASCII characters in a problem."""
    output_path = CLEANED_DATA_PATH / path_name
    nonascii_dict = {}
    for problem_type in types:
        type_path = output_path / problem_type
        for problem_path in type_path.glob("*.json"):
            with open(problem_path.path, "r", encoding="utf-8") as f:
                problem = json.load(f)
            content = problem["content"]
            if not content.isascii():
                nonascii_dict[problem["id"]] = content
    nonascii_path = output_path / f"{path_name}.json"
    with open(nonascii_path, "w") as f:
        json.dump(nonascii_dict, f, indent=4)


def inspect_sus_keywords(path_name, cleaned_data_path=CLEANED_DATA_PATH):
    """Inspect problems that might contain superfluous sections as marked by keywords like Follow-up, Credit, or Notes."""
    keywords = ["Follow up",
                "Follow-up", "Credit", "Note:", "Notes:"]
    output_path = CLEANED_DATA_PATH / path_name
    keywords_dict = {}
    tags_containing_keyword = {}
    for keyword in keywords:
        tags_containing_keyword[keyword] = []
    for problem_type in types:
        type_path = output_path / problem_type
        for problem_path in type_path.glob("*.json"):
            print(f"Inspecting {problem_path.name}")
            with open(problem_path, "r", encoding="utf-8") as f:
                problem = json.load(f)
            # content = problem["content"]
            # for keyword in keywords:
            #     if keyword in content:
            #         keywords_dict[problem["id"]] = content
            #         break
            id = problem["id"]
            soup = BeautifulSoup(problem["content"], "html.parser")
            for keyword in keywords:
                for text in soup.find_all(string=re.compile(keyword)):
                    tag = text.parent

                    if id not in keywords_dict:
                        keywords_dict[id] = {}
                    if tag.name != "[document]":
                        if (tag.name not in tags_containing_keyword[keyword]):
                            tags_containing_keyword[keyword].append(tag.name)

                        if keyword not in keywords_dict[id]:
                            keywords_dict[id
                                          ][keyword] = [str(tag)]
                        elif str(tag) not in keywords_dict[id
                                                           ][keyword]:
                            keywords_dict[id
                                          ][keyword].append(str(tag))
                    elif tag.name:
                        keywords_dict[id][keyword] = []

                        # for next in tag.find_all_next():
                        #     if str(next) not in keywords_dict[id][keyword]:
                        #         keywords_dict[id][keyword].append(str(next))

                        # for next_text in tag.parent.find_all(string=True, recursive=False):
                        #     p = str(tag.parent)
                        #     if p.find(next_text) > p.find(text):
                        #         keywords_dict[id][keyword].append(next_text)
                    parent = tag.parent
                    remaining = ""
                    if not parent:
                        soup_str = str(soup)
                        tag_pos = soup_str.find(text)
                        remaining = soup_str[tag_pos + len(text):]
                    else:
                        parent_contents = parent.contents
                        tag_index = parent_contents.index(tag)
                        for elem in parent_contents[tag_index + 1:]:
                            remaining += str(elem)
                    keywords_dict[id][keyword].append(remaining)

    sus_keywords_path = output_path / "sus_keywords.json"
    with open(sus_keywords_path, "w") as f:
        json.dump(keywords_dict, f, indent=4)

    tags_containing_keywords_path = output_path / "tags_containing_keywords.json"
    with open(tags_containing_keywords_path, "w") as f:
        json.dump(tags_containing_keyword, f, indent=4)


def inspect_english_words(path_name):
    """Find words that are not in NLTK's words corpus."""
    output_path = CLEANED_DATA_PATH / path_name
    vocab = set(words.words())
    meaningless_words_dict = {}
    for problem_type in types:
        type_path = output_path / problem_type
        for problem_path in type_path.glob("*.json"):
            print(f"Inspecting {problem_path.name}")
            with open(problem_path.path, "r", encoding="utf-8") as f:
                problem = json.load(f)
            id = problem["id"]
            sentences = problem["content"]
            for sentence in sentences:
                for word in sentence:
                    if word not in vocab:
                        if id not in meaningless_words_dict:
                            meaningless_words_dict[id] = [word]
                        elif word not in meaningless_words_dict[id]:
                            meaningless_words_dict[id].append(word)

    meaningless_words_path = output_path / "meaningless_words.json"
    with open(meaningless_words_path, "w") as f:
        json.dump(meaningless_words_dict, f, indent=4)
