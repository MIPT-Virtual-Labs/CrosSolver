import subprocess
import shutil
import os

from time import sleep
from utils import get_current_dir_name, get_random_string, get_progress_line
from checker import check_arguments
from local_constants import (
    CORRECT, STATUS, ERROR, ERRORS, DONE, FAILED,
    PROJECT_SOURCE_DIR_NAME, PROGRESS_FILE, DESCRIPTION,
    PROCESS, TOKEN, INFORMATION, PERCENT, TASK,
    TASK_CREATE_MATRIX, PATH_TO_ARGUMENTS_FILE,
    FIELD, INCORRECT_PROCESS_TOKEN_DICT, DATA)


def create_task(
    t = 0, 
    steps_amount = 0, 
    names = None, 
    init_values = None, 
    equations = None):
    """
    Create task to compute equations

    :param t: float
        time of work algorithm
    :param steps_amount: int
        amount of steps for algorithm
    :param names: List<string>
        names of items
    :param init_values: List<float>
        list of float initial values
    :param equations: List<string>
        list of string equations with python syntax:
            - left parts are f_{i} for i=0..(n-1), example: f0
            - right parts are f_i(y_{0}, ..., y_{n-1}), example: 12*(y3-y1)/(y2+y3)**3
            - example of total equations: 
                [
                    "f0 = 100500*y2/y3-y4",
                    "f1 = 12*(y3-y1)/(y2+y4)**3",
                    "f2 = (y2+y4)*(y1+y2)/y1**3",
                    "f3 = 12*(y3-y1)/(y2+y3)**3",
                    "f4 = (y0-y1+y2)/(y3+y4)",
                ]
    :param kwargs: dict [optional]
        additional parameters
    
    :return: dict with keys:
        - status: string
            task status from values in ['process', 'error', 'done', 'failed']
        - token: string
            ONLY if status == 'process'
            token of process to get information about progress in next requests
        - information: dict
            ONLY if status == 'process'
            information about current task progress with fields:
                - percent: int
                    number from 0 to 100: percent of total progress 
                - task: dict
                    information about current subtask with fields:
                        - information: string
                            current subtask name
                        - percent: int
                            number from 0 to 100: percent of progress of this subtask
        - errors: List<dict>
            ONLY if status == 'error'
            every item of list is dict with fields:
                - error: string
                    error description
                - field: string
                    name of field with error format of data
        - description: string
            ONLY if status == 'failed'
            description of reasons why task was failed
        - type: string
            ONLY if status == 'done'
            [default: 'graph'] type of return data
        - data: List<List<dict>>
            ONLY if status == 'done'
            list of lists with point's dicts

    """
    # check that arguments are correct
    arguments_information = check_arguments(t, steps_amount, names, init_values, equations)
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
        file.writelines(', '.join(map(str, init_values)) + '\n')
        for equation in equations:
            file.writelines(equation + '\n')

    # write state progress
    with open(dir_name + '/' + PROGRESS_FILE, 'w') as file:
        file.write(get_progress_line(0, TASK_CREATE_MATRIX, 0, 0, 30))

    # os.open()
    # old_dir = os.getcwd()
    os.chdir(f'{dir_name}')
    try:
        process = subprocess.Popen(["python3.9", f"manage.py"])
    except:
        process = subprocess.Popen(["python3", f"manage.py"])
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
    """
    Get progress of task

    :param process_token: string
        token of process with user's task
    
    :return: dict with keys:
        - status: string
            task status from values in ['process', 'error', 'done', 'failed']
        - token: string
            ONLY if status == 'process'
            token of process to get information about progress in next requests
        - information: dict
            ONLY if status == 'process'
            information about current task progress with fields:
                - percent: int
                    number from 0 to 100: percent of total progress 
                - task: dict
                    information about current subtask with fields:
                        - information: string
                            current subtask name
                        - percent: int
                            number from 0 to 100: percent of progress of this subtask
        - errors: List<dict>
            ONLY if status == 'error'
            this status can be caused by old or nonexistent process
            every item of list is dict with fields:
                - error: string
                    error description
                - field: string
                    [default: 'process_token'] name of field with error format of data
        - description: string
            ONLY if status == 'failed'
            description of reasons why task was failed
        - type: string
            ONLY if status == 'done'
            [default: 'graph'] type of return data
        - data: List<List<dict>>
            ONLY if status == 'done'
            list of lists with point's dicts

    """
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
            status, percent, task, task_percent, time_left, time_spent = last_line.split('$')
            if status == FAILED:
                answer = {
                    STATUS: FAILED,
                    DESCRIPTION: task,
                }
                try:
                    shutil.rmtree(os.getcwd())
                except Exception as delete_error:
                    print("Delete dir error:", delete_error)
                return answer
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
                    # pass
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
