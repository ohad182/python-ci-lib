import argparse
import os
import errno
import datetime
import json
import shutil

workspace = ""


def write_log(relative_path, content, console=True, mode="a"):
    if console is True:
        print(content)
    if relative_path is not None:
        log_path = os.path.join(workspace, relative_path)
        create_dir_for_file(log_path)
        with open(log_path, mode) as log:
            log.write("{}\n".format(content))


def create_dir_for_file(path):
    if not os.path.exists(path):
        try:
            item = path
            if os.path.isfile(item) or "." in item.split(os.path.sep)[-1]:
                item = os.path.dirname(item)
            os.makedirs(item)
        except OSError as ose:
            if ose.errno != errno.EEXIST:
                raise


def clear_directory(directory_path):
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def get_same_seq_count(str1, str2):
    counter = 0
    last_char = None
    for a, b in zip(str1, str2):
        if a.lower() == b.lower():
            counter = counter + 1
            last_char = a
        else:
            if last_char == '_':
                counter = counter - 1
            break
    return counter


def get_most_exact(items, wanted):
    most_wanted = wanted
    wanted_len = len(wanted)
    most_similar_portion = 0

    for item in items:
        similar_portion_size = get_same_seq_count(item, wanted)
        if similar_portion_size == wanted_len:
            most_wanted = item
            break
        elif similar_portion_size > most_similar_portion and len(item) < wanted_len:
            most_similar_portion = similar_portion_size
            most_wanted = item

    return most_wanted


def timeit(func):
    def timeit_wrapper(*args, **kwargs):
        start = datetime.datetime.now()

        result = func(*args, **kwargs)

        end = datetime.datetime.now()
        print("method {} took {}".format(func.__name__, end - start))
        return result

    return timeit_wrapper


def seconds_to_timestamp(duration):
    """
    Gets duration in seconds and returns readable str
    :param duration: the time represented in seconds
    :return: a human readable str that describes the given time
    """
    days = duration // (24 * 3600)
    duration = duration % (24 * 3600)
    hours = duration // 3600
    duration = duration % 3600
    minutes = duration // 60
    duration = duration % 60
    seconds = duration

    if days > 0:
        return '{} day(s) {:02d}:{:02d}:{:02d}'.format(int(days), int(hours), int(minutes), int(seconds))
    else:
        return '{:02d}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))


def index_of(array, item):
    """
    Checks if item is in array and returns its index, if not found returns -1
    :param array: the array to search in
    :param item: the item to find
    :return: item index in array or -1 if not present
    """
    try:
        return array.index(item)
    except ValueError:
        return -1


def try_parse_int(num_str):
    try:
        return int(num_str), True
    except ValueError:
        return num_str, False


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def fix_path(path):
    """
    Fix given path according to os path sep
    :param path: the original path (should be combined from cwd + module path)
    :return: the full fixed path
    """
    not_sep = "/" if os.path.sep == "\\" else "\\"
    return path.replace(not_sep, os.path.sep)


def encode_utf(s):
    if s is not None and not isinstance(s, str):
        s = s.encode('utf-8')
    return s


def read_json(full_path):
    json_dict = None
    if os.path.exists(full_path):
        with open(full_path, 'r') as conf_file:
            json_dict = json.load(conf_file)
    return json_dict
