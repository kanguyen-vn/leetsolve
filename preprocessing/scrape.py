import json
import io
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from .constants import LEETCODE_API_URL, LEETCODE_PATH, CHROMEDRIVER_PATH, PROBLEMS_PATH, TAGS_JSON, PROBLEMS_BY_TAG_JSON


def fetch_leetcode_json():
    """
    Fetch the json file containing problem slugs and IDs from LeetCode's API.
    """
    LEETCODE_PATH.mkdir(exist_ok=True)
    leetcode_json = LEETCODE_PATH / "leetcode.json"
    data = requests.get(LEETCODE_API_URL).json()
    pairs = data["stat_status_pairs"]
    for pair in pairs:
        del pair["frequency"]
        del pair["is_favor"]
        del pair["progress"]
        del pair["status"]
        stat = pair["stat"]
        del stat["is_new_question"]
        del stat["question__hide"]
        del stat["total_acs"]
        del stat["total_submitted"]
    with open(leetcode_json, "w") as f:
        json.dump(pairs, f, indent=4, sort_keys=True)


def fetch_problem(problem, driver_options):
    """
    Scrape a problem from the LeetCode website.
    """
    problem_url = f'https://leetcode.com/problems/{problem["title_slug"]}'
    print(f"Getting {problem_url}...")
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=driver_options)
    driver.get(problem_url)
    try:
        content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "question-content__JfgR"))
        )
        title = driver.find_element_by_class_name("css-v3d350").text.strip()
        problem_file = PROBLEMS_PATH / f"{title.split('.', 1)[0]}.json"
        with open(problem_file, "w", encoding="utf-8") as f:
            json_obj = {
                "id": problem["id"],
                "title": problem["title"],
                "title_slug": problem["title_slug"],
                "backend_id": problem["backend_id"],
                "content": content.get_attribute('innerHTML')
            }
            json.dump(json_obj, f, indent=4)
        print(f"Wrote to {title}.json")
    finally:
        driver.close()


def fetch_problems(driver_options):
    """
    Scrape all (unpaid) problems from the LeetCode website.
    """
    leetcode_json = LEETCODE_PATH / "leetcode.json"
    with open(leetcode_json, "r") as f:
        data = json.load(f)
        for each in data:
            filename = f'{each["stat"]["frontend_question_id"]}.json'
            to_check = PROBLEMS_PATH / filename
            if to_check.exists():
                print(
                    f'{each["stat"]["frontend_question_id"]}.json already exists')
                continue
            # something wrong with 155
            if not each["paid_only"] and each["stat"]["frontend_question_id"] != 155:
                problem = {
                    "title": each["stat"]["question__title"].strip(),
                    "title_slug": each["stat"]["question__title_slug"].strip(),
                    "id": each["stat"]["frontend_question_id"],
                    "backend_id": each["stat"]["question_id"]
                }
                fetch_problem(problem, driver_options)


def categorize_by_tag(tag, tags_dict, driver_options):
    """
    Fetch all problems pertaining to a particular tag.
    """
    print("Processing", tag)
    tags_dict[tag] = []
    problems_by_tag = f'https://leetcode.com/problemset/all/?topicSlugs={tag}'
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=driver_options)
    driver.get(problems_by_tag)
    driver.find_element_by_xpath(
        '//*[@id="question-app"]/div/div[2]/div[2]/div[2]/table/tbody[2]/tr/td/span/select/option[4]').click()  # display all problems with tag
    num_rows = len(driver.find_elements_by_xpath(
        '//*[@id="question-app"]/div/div[2]/div[2]/div[2]/table/tbody[1]/tr'))
    for i in range(1, num_rows + 1):
        text = driver.find_element_by_xpath(
            f'//*[@id="question-app"]/div/div[2]/div[2]/div[2]/table/tbody[1]/tr[{i}]/td[2]').get_attribute("innerText")
        tags_dict[tag].append(int(text))
    driver.close()
    with open(PROBLEMS_BY_TAG_JSON, "w") as f:
        json.dump(tags_dict, f, indent=4)


def fetch_tags(driver_options):
    """
    Fetch available tags from the LeetCode website.
    """
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=driver_options)
    driver.get("https://leetcode.com/problemset/all")
    filter_lists = driver.find_elements_by_class_name("filter-title")
    tags_button = list(filter(lambda list: list.get_attribute(
        "innerText") == "Tags", filter_lists))[0]
    tags_button.click()
    tags = []
    try:
        content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".false.tag-category"))
        )
        tags = ["-".join(tag.lower().split())
                for tag in content.get_attribute("innerText").split("\n")]
    finally:
        print("Fetched tags:", tags)
        driver.close()
    with open(TAGS_JSON, "w") as f:
        json.dump(tags, f, indent=4)


def categorize_tags(driver_options):
    with open(TAGS_JSON, "r") as f:
        tags = json.load(f)
    if PROBLEMS_BY_TAG_JSON.exists():
        with open(PROBLEMS_BY_TAG_JSON, "r") as f:
            tags_dict = json.load(f)
    else:
        tags_dict = {}
    for tag in tags:
        if tag in tags_dict:
            print("Already processed", tag)
            continue
        categorize_by_tag(tag, tags_dict, driver_options)

    with open(PROBLEMS_BY_TAG_JSON, "w") as f:
        json.dump(tags_dict, f, indent=4)


options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--log-level=OFF")
PROBLEMS_PATH.mkdir(exist_ok=True)
