from api import create_task, get_progress
from local_constants import TOKEN, STATUS, DONE
from time import sleep
import os


def test_1():
    t = 0.06
    steps_amount = 1200
    names = ["O2", "3t3x", "xhbrrv", "xgbxrz", "xfhdx"]
    masses = [0, 34, 53, 12, 65]
    equations = [
        "f0 = 100500*y2/y3-y4",
        "f1 = 12*(y3-y1)/(y2+y4)**3",
        "f2 = (y2+y4)*(y1+y2)/y1**3",
        "f3 = 12*(y3-y1)/(y2+y3)**3",
        "f4 = (y0-y1+y2)/(y3+y4)"
    ]

    return create_task(t, steps_amount, names, masses, equations)
    # print("|> RESULT CREATE TASK [TEST 1]:", result)


if __name__ == '__main__':
    result = test_1()
    process_token = result[TOKEN]
    print("GET TOKEN:", process_token)
    for i in range(40):
        os.chdir(f'../')
        status = get_progress(process_token=process_token)[STATUS]
        print("GET STATUS:", status)
        if status == DONE:
            break
        sleep(0.2)
