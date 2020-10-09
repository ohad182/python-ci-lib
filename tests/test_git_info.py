import os
import inspect
from execute.utils import read_json
from execute.git import get_info


def test_get_info():
    this_file_dir_path = os.path.abspath(os.path.dirname(__file__))
    tests_data_dir_path = os.path.join(this_file_dir_path, "data")
    data_file = "internal_data.json"  # exposed data is "tests_data.json"
    data_path = os.path.join(tests_data_dir_path, data_file)
    json_dict = read_json(data_path)

    this_method_name = inspect.stack()[0][3]
    project_path = json_dict[this_method_name]["project_path"]
    git_info = get_info(project_path)
    print(git_info.to_json())


test_get_info()
