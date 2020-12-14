from .constants import CLEANED_DATA_PATH, types


def prepare_directories(directory_name):
    CLEANED_DATA_PATH.mkdir(exist_ok=True)
    data_path = CLEANED_DATA_PATH / directory_name
    data_path.mkdir(exist_ok=True)
    for problem_type in types:
        type_path = data_path / problem_type
        type_path.mkdir(exist_ok=True)
    return data_path
