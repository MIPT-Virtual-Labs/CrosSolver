import string
import random
import time


def get_random_string(size):
    random.seed(time.time())
    letters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    rand_string = ''.join(random.choice(letters) for _ in range(size))
    return rand_string


def get_size_error(size):
    return f"The size must be the same as names size ({size})"


def get_current_dir_name(pid):
    return f"process_task_{pid}"


def get_progress_line(progress, task, task_progress=0, time_left=0, time_spent=0):
    return f"{progress}${task}${task_progress}${time_left}${time_spent}\n"
