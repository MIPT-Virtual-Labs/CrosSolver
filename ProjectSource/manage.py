# !/usr/bin/env python
# coding: utf-8
import subprocess
import os

import sys
from JmatrixGeneration.GeneratorJmatrix import generator
# setting path
# print("LAST PATH", sys.path)
sys.path.append('../')

from constants import PROGRESS_FILE, GENERATE_START_MEANINGS, GENERATE_JMATRIX, COMPILE_PROGRAM, RUN_PROGRAM
from utils import get_progress_line


def save_progress(line):
    with open(PROGRESS_FILE, 'a') as file:
        file.write(line)


def start_meanings(n, hs="", ys=""):
    y = [0.0] * n
    if ys:
        y = list(map(float, ys.strip().split(", ")))
    y_str = ""
    if len(hs) == 0:
        for i in range(n - 1):
            y_str += str(y[i]) + ','
        y_str += str(y[-1])
    else:
        try:
            y_str = "\n"
            hs = hs.split(", ")

            for i in range(len(hs) - 1):
                y_str += "\t\t" + str(y[i]) + ',' + " // " + hs[i] + "\n"
            # for i in range(len(hs), n - 1):
            #     y_str += "\t\t" + str(y[i]) + ',' + "\n"
            y_str += "\t\t" + str(y[n - 1]) + " // " + hs[n - 1] + "\n"
        except:
            y_str = ""
            for i in range(n - 1):
                y_str += str(y[i]) + ','
            y_str += str(y[-1])
    return y_str


# In[3]:


def create_str_to_add(n: int, a: str, d):
    result = ""
    n_str = f"N = {n}\n\n"
    result += n_str

    y_mass_str = "ynames = [f\"y[{i}]\" for i in range(N)]\n"
    for i in range(n - 1):
        y_mass_str += "y" + str(i) + ", "
    y_mass_str += "y" + str(n - 1) + " = sym.symbols(ynames)\n\n"
    y_mass_str += "coords = "
    for i in range(n - 1):
        y_mass_str += "y" + str(i) + ", "
    y_mass_str += "y" + str(n - 1) + "\n\n"
    result += y_mass_str

    result += a + "\n\n" + '\n'.join(d)

    func_mass = "\n\nfunctions = "
    for i in range(n - 1):
        func_mass += "f" + str(i) + ", "
    func_mass += "f" + str(n - 1) + "\n\n"

    result += func_mass

    return result


def start_generation():
    diff_equations = list()
    help_str = ""
    y_start = ""
    with open("JmatrixGeneration/diffs.txt", 'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                help_str = line.strip()
                continue
            if i == 1:
                y_start = line.strip()
                continue
            if line.strip():
                diff_equations.append(line.strip())
    n = len(diff_equations)

    # diff_equations += f"f{n-1} = 0" # уравнение для температуры

    y_str = start_meanings(n, hs=help_str, ys=y_start)
    save_progress(get_progress_line(
        5, GENERATE_START_MEANINGS, 100,
    ))
    main_code = create_str_to_add(n, "", diff_equations)
    #     print(main_code)
    #     print(y_str)
    save_progress(get_progress_line(
        10, GENERATE_JMATRIX, 0,
    ))
    generator(main_code, y_str, add_info=help_str)  # Создаётся Jmatrix
    save_progress(get_progress_line(
        30, GENERATE_JMATRIX, 100,
    ))


def start():
    # print("CURRENT DIR:", os.getcwd())
    # os.chdir('/ProjectSource')
    start_generation()
    save_progress(get_progress_line(
        30, COMPILE_PROGRAM, 0,
    ))
    subprocess.run('g++ -std=c++14 main.cpp CROS.cpp -fopenmp -o BB', shell=True)  # g++ main.cpp -fopenmp -o BB
    save_progress(get_progress_line(
        35, COMPILE_PROGRAM, 100,
    ))
    save_progress(get_progress_line(
        40, RUN_PROGRAM, 0,
    ))
    subprocess.run('./BB')
    save_progress(get_progress_line(
        100, RUN_PROGRAM, 100,
    ))


if __name__ == '__main__':
    # print("START!")
    start()
