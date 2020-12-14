from pathlib import Path
from preprocessing.scrape import fetch_leetcode_json, fetch_problems, fetch_tags, categorize_tags
# from preprocessing.inspect_data import count_problems_by_tags
from preprocessing.clean import duplicate_data, clean_problems, remove_spaces
from preprocessing.prepare_directories import prepare_directories
from preprocessing.tokenize_data import tokenize_data
from preprocessing.compile import compile_and_remove_duplicates
from preprocessing.constants import RAW_DIRECTORY, CLEAN_PROBLEMS, SPACES_REMOVED, TOKENIZED, ALL_TEXTS_JSON, types
from processing.model import train, save

"""1. Get data."""

# 1.1. Fetch json from LeetCode API
# fetch_leetcode_json()

# 1.2. Scrape all fetchable problems from LeetCode (takes a long time, comment out when done)
# fetch_problems(options)

# 1.3. Scrape problem tags (will be used as labels later)
# fetch_tags(options)

# 1.4. Scrape type of problem from LeetCode
# categorize_tags(options)

"""2. Inspect data."""

# 2.1. Count the number of problems in each type and sort
# count_problems_by_tags()

# 9 problem types chosen from sorted list (> 50 inputs):
# types = [
#     "dynamic-programming",
#     "depth-first-search",
#     "hash-table",
#     "greedy",
#     "binary-search",
#     "breadth-first-search",
#     "two-pointers",
#     "stack",
#     "backtracking"
# ]

"""3. Clean data"""

# 3.1. Filter problems by type
# raw_path = prepare_directories(RAW_DIRECTORY)
# duplicate_data(raw_path)

# 3.2. Clean problems
# clean_problems_path = prepare_directories(CLEAN_PROBLEMS)
# clean_problems(clean_problems_path, raw_path)

# 3.3. Remove spaces (including line breaks, unicode spaces, etc.)
# spaces_removed_path = prepare_directories(SPACES_REMOVED)
# remove_spaces(spaces_removed_path, clean_problems_path)

# 3.4. Tokenize data
tokenized_path = prepare_directories(TOKENIZED)
# tokenize_data(tokenized_path, spaces_removed_path)

# 3.5 Compile data (and remove duplicates) for machine learning
# compile_and_remove_duplicates(tokenized_path)

"""4. Machine learning"""

# 4.1. Train model
model = train(tokenized_path, ALL_TEXTS_JSON, types)

# 4.2. Save model
model_path = Path(__file__).parent.absolute() / "model"
model_path.mkdir(exist_ok=True)
save(model, model_path)
