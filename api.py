import subprocess
import shutil
import os

from time import sleep
from utils import get_current_dir_name, get_random_string, get_progress_line
from checker import check_arguments
from local_constants import (
    CORRECT, STATUS, ERROR, ERRORS, DONE,
    PROJECT_SOURCE_DIR_NAME, PROGRESS_FILE,
    PROCESS, TOKEN, INFORMATION, PERCENT, TASK,
    TASK_CREATE_MATRIX, PATH_TO_ARGUMENTS_FILE,
    FIELD, INCORRECT_PROCESS_TOKEN_DICT, DATA)


def create_task(t, steps_amount, names, masses, equations, **kwargs):
    """
    Create task to compute equations

    :param t: float: time of work algorithm
    :param steps_amount: int: amount of steps
    :param names: List<string>: list of names of items
    :param masses: List<float>: list of float masses
    :param equations: List<string>: list of string equations
    :param kwargs: additional parameters
    :return:
    - status: task status (default: 'process', variants from ['process', 'error', 'done', 'failed'])
    - token: token of process to get information about progress
    - process: information about progress in notion:


    """
    # check that arguments are correct
    arguments_information = check_arguments(t, steps_amount, names, masses, equations)
    # if something is wrong return errors
    if not arguments_information[CORRECT]:
        return {
            STATUS: ERROR,
            ERRORS: arguments_information[ERRORS],
        }

    # index = process.pid()
    TOKEN_SIZE = 12
    process_token = get_random_string(TOKEN_SIZE)
    dir_name = get_current_dir_name(process_token)
    while True:
        try:
            if not os.path.isdir(dir_name):
                shutil.copytree(PROJECT_SOURCE_DIR_NAME, dir_name)
                break
            process_token = get_random_string(TOKEN_SIZE)
            dir_name = get_current_dir_name(process_token)
        except Exception as e:
            print("ERROR [copytree]:", e)
            process_token = get_random_string(TOKEN_SIZE)
            dir_name = get_current_dir_name(process_token)
            continue

    # WRITE TO DIFFS.TXT
    with open(dir_name + PATH_TO_ARGUMENTS_FILE, 'w') as file:
        # names_line = ', '.join(names)
        # print(names_line)
        file.writelines(', '.join(map(str, [t, steps_amount])) + '\n')
        file.writelines(', '.join(names) + '\n')
        file.writelines(', '.join(map(str, masses)) + '\n')
        for equation in equations:
            file.writelines(equation + '\n')

    # write state progress
    with open(dir_name + '/' + PROGRESS_FILE, 'w') as file:
        file.write(get_progress_line(0, TASK_CREATE_MATRIX, 0, 0, 30))

    # os.open()
    # old_dir = os.getcwd()
    os.chdir(f'{dir_name}')
    process = subprocess.Popen(["python3.9", f"manage.py"])
    # print("NEW PROCESS", process.pid)
    # process.stdin.write(dir_name)

    return {
        STATUS: PROCESS,
        TOKEN: process_token,
        INFORMATION: {
            PERCENT: 0,
            TASK: {
                INFORMATION: TASK_CREATE_MATRIX,
                PERCENT: 0
            }
        }
    }


def get_progress(process_token=None):
    if process_token is None:
        return INCORRECT_PROCESS_TOKEN_DICT

    dir_name = get_current_dir_name(process_token)
    # print("Get dir name", dir_name)
    if not os.path.isdir(dir_name):
        # print("NOT DIR!!!!!! Current:", os.getcwd())
        return INCORRECT_PROCESS_TOKEN_DICT
    # print("|> Current dir:", os.getcwd())
    os.chdir(f'{dir_name}')
    try:
        with open(PROGRESS_FILE, 'r') as file:
            for line in file:
                pass
            last_line = line
            percent, task, task_percent, time_left, time_spent = last_line.split('$')
            if int(percent) == 100:
                result = []
                with open('OUT.txt', 'r') as out:
                    for line in out:
                        result.append(line.strip().split('\t'))
                # print("Current (1):", os.getcwd())
                # os.chdir(f'../')
                # print("Current (2):", os.getcwd())
                # print(result)
                # sleep(3)
                # shutil.rmtree(f'/{dir_name}')
                try:
                    shutil.rmtree(os.getcwd())
                except Exception as delete_error:
                    print("Delete dir error:", delete_error)
                return {
                    STATUS: DONE,
                    'type': 'graph',
                    DATA: result
                }
            else:
                return {
                    STATUS: PROCESS,
                    TOKEN: process_token,
                    INFORMATION: {
                        PERCENT: percent,
                        TASK: {
                            PERCENT: task_percent,
                            INFORMATION: task
                        }
                    }
                }
    except Exception as e:
        print("Error [get_progress]", e)
        return INCORRECT_PROCESS_TOKEN_DICT
