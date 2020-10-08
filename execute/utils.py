import os
import errno
import datetime

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
