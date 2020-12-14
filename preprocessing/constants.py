from pathlib import Path

types = [
    "dynamic-programming",  # 232
    "depth-first-search",  # 138
    "hash-table",  # 135
    "greedy",  # 108
    "binary-search",  # 95
    "breadth-first-search",  # 77
    "two-pointers",  # 66
    "stack",  # 62
    "backtracking"  # 61
]

# types = [
#     # "dynamic-programming",  # 232
#     "depth-first-search",  # 138
#     "hash-table",  # 135
#     "greedy",  # 108
#     "binary-search"  # 95
# ]

LEETCODE_API_URL = "https://leetcode.com/api/problems/algorithms/"
CHROMEDRIVER_PATH = r"C:\Program Files (x86)\chromedriver.exe"

LEETCODE_PATH = Path(__file__).parent.parent.absolute() / "data"
PROBLEMS_PATH = LEETCODE_PATH / "problems"
TAGS_JSON = LEETCODE_PATH / "tags.json"
COUNT_TAGS_JSON = LEETCODE_PATH / "count_tags.json"
PROBLEMS_BY_TAG_JSON = LEETCODE_PATH / "problems_by_tag.json"
CLEANED_DATA_PATH = LEETCODE_PATH / "cleaned_data"
ALL_TEXTS_JSON = "all_texts.json"

RAW_DIRECTORY = "0_raw_filtered"
CLEAN_PROBLEMS = "1_clean_problems"
SPACES_REMOVED = "2_spaces_removed"
TOKENIZED = "3_tokenized"
