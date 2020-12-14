from pathlib import Path
import json
import io
import re
from shutil import copyfile
from bs4 import BeautifulSoup

from .constants import types, PROBLEMS_PATH, PROBLEMS_BY_TAG_JSON, RAW_DIRECTORY, CLEAN_PROBLEMS, SPACES_REMOVED
from .prepare_directories import prepare_directories


def clean_problem(content, example_re=re.compile("Example *[0-9]* *:", re.I), constraints_re=re.compile("Constraints *:", re.I), id=0):
    soup = BeautifulSoup(content, "html.parser")

    # Unwrapping big outer div
    possible_div = soup.find()
    if possible_div and possible_div.name == "div":
        possible_div.unwrap()

    # good divs: 497? 856, 863, 864, 884, 911, 977, 1078
    div_skips = [497, 856, 863, 864, 884, 911, 977, 1078]
    if id not in div_skips:
        for div in soup.find_all("div"):
            div.decompose()
    else:
        for div in soup.find_all("div"):
            div.unwrap()

    # Decomposing irrelevant tags
    for tag in soup.find_all(["pre", "code", "table", "font", "small", "video", "var", "blockquote", "sup"]):
        if tag.text.isnumeric():
            tag.unwrap()
            continue
        tag.decompose()

    # leave spans with style, remove otherwise
    for span in soup.find_all("span"):
        if span.has_attr("style"):
            span.unwrap()
        else:
            span.decompose()

    # links
    # 316=1081, 1296 same questions; 377, 392 credits
    for a in soup.find_all("a"):
        a.unwrap()

    # Unwrapping blocks that might contain useful information
    for to_unwrap in soup.find_all(["em", "u", "i", "sub", "li", "ol", "ul"]):
        to_unwrap.unwrap()

    for p in soup.find_all("p"):
        text = p.get_text().strip()
        if example_re.match(text) or constraints_re.match(text):
            p.decompose()
        else:
            p.unwrap()

    for strong in soup.find_all("strong"):
        text = strong.get_text().strip()
        if example_re.match(text) or constraints_re.match(text):
            strong.decompose()

    # Delete everything appearing after the following keywords
    for keyword in ["Follow up", "Follow-up", "Credits", "Note:", "Notes:"]:
        for text in soup.find_all(string=re.compile(keyword)):
            tag = text.parent
            if tag == "[document]" or not tag.parent:
                text_pos = str(tag).find(text)
                soup = BeautifulSoup(
                    str(tag)[:text_pos], "html.parser")
            else:
                parent = tag.parent
                parent_contents = parent.contents
                tag_index = parent_contents.index(tag)
                new_parent_contents = u""
                for elem in parent_contents[:tag_index]:
                    new_parent_contents += str(elem)
                if parent == soup:
                    soup = BeautifulSoup(
                        new_parent_contents, "html.parser")
                else:
                    parent.string = new_parent_contents

    for b in soup.find_all("b"):
        b.unwrap()

    # Removing examples and constraints blocks, otherwise unwrapping strongs
    for strong in soup.find_all("strong"):
        strong.unwrap()

    # print("Removing empty tags...")
    empties = soup.find_all(lambda tag: (
        not tag.contents or len(tag.get_text().strip()) <= 0))
    for empty in empties:
        empty.decompose()

    return str(soup)


def clean_problems(dest_path, src_path):
    example_re = re.compile("Example *[0-9]* *:", re.I)
    constraints_re = re.compile("Constraints *:", re.I)

    for problem_type in types:
        src_type_path = src_path / problem_type
        dest_type_path = dest_path / problem_type
        for problem_path in src_type_path.glob("*.json"):
            print(f"Cleaning {problem_path.name}")
            with open(problem_path, "r", encoding="utf-8") as f:
                problem = json.load(f)

            problem["content"] = clean_problem(
                problem["content"], example_re, constraints_re, problem["id"])

            output_file_path = dest_type_path / problem_path.name
            with open(output_file_path, "w") as f:
                json.dump(problem, f, indent=4)


def remove_spaces_one(content):
    content = "".join([i if i.isascii() else " " for i in content])
    return " ".join(content.replace("\n", " ").split())


def remove_spaces(dest_path, src_path):
    for problem_type in types:
        src_type_path = src_path / problem_type
        dest_type_path = dest_path / problem_type
        for problem_path in src_type_path.glob("*.json"):
            print(f"Removing spaces in {problem_path.name}")
            with open(problem_path, "r", encoding="utf-8") as f:
                problem = json.load(f)
            problem["content"] = remove_spaces_one(problem["content"])
            output_file_path = dest_type_path / problem_path.name
            with open(output_file_path, "w") as f:
                json.dump(problem, f, indent=4)


def duplicate_data(dest_path, src_path=PROBLEMS_PATH):
    if src_path == PROBLEMS_PATH:
        with open(PROBLEMS_BY_TAG_JSON, "r") as f:
            all_data = json.load(f)
        for problem_type in types:
            type_path = dest_path / problem_type
            for id in all_data[problem_type]:
                print(f"Copying {id}.json...")
                unprocessed_problem_path = src_path / f"{id}.json"
                if not unprocessed_problem_path.exists():
                    continue
                processed_problem_path = type_path / f"{id}.json"
                copyfile(unprocessed_problem_path, processed_problem_path)
    else:
        for problem_type in types:
            type_path = dest_path / problem_type
            src_type_path = src_path / problem_type
            for entry in src_type_path.glob("*.*"):
                print(f"Copying {entry.name}...")
                processed_problem_path = type_path / entry.name
                copyfile(entry.path, processed_problem_path)


if __name__ == "__main__":
    raw_path = prepare_directories(RAW_DIRECTORY)
    duplicate_data(raw_path)

    clean_problems_path = prepare_directories(CLEAN_PROBLEMS)
    clean_problems(clean_problems_path, raw_path)

    spaces_removed_path = prepare_directories(SPACES_REMOVED)
    remove_spaces(spaces_removed_path, clean_problems_path)
