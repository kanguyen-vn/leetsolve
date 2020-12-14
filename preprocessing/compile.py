import json
from pathlib import Path
from .constants import types, ALL_TEXTS_JSON


def compile_and_remove_duplicates(src_path):
    all_texts = []
    for problem_type in types:
        src_type_path = src_path / problem_type
        for problem_path in src_type_path.glob("*.json"):
            print(f"Getting data from {problem_path.name}")
            with open(problem_path, "r", encoding="utf-8") as f:
                problem = json.load(f)
            del problem["backend_id"]
            problem["title"] = problem["title"].lower()
            del problem["title_slug"]
            problem["content"] = " ".join([word for sentence in problem["content"]
                                           for word in sentence])
            problem["label"] = problem_type
            all_texts.append(problem)

    order = list(reversed(types))

    no_duplicates = []
    for one in all_texts:
        same = [two for two in all_texts if two !=
                one and two["id"] == one["id"]]
        if len(same) == 0:
            no_duplicates.append(one)
            continue
        chosen = ""
        for each in order:
            if any(each == problem["label"] for problem in same):
                chosen = each
                break
        for each in same:
            if each["label"] == chosen:
                no_duplicates.append(each)
                break

    all_texts_path = src_path / ALL_TEXTS_JSON
    with open(all_texts_path, "w") as f:
        json.dump(no_duplicates, f, indent=4)
