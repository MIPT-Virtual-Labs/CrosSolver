import math
import re
import time
import sympy as sym


def generator(code_to_power: str, y, t=0.05, steps_amount="1000", add_info="", file_name="Jmatrix.h"):
    N = 0
    functions = ''
    coords = ''

    ldict = {}

    exec(code_to_power, globals(), ldict)
    N = ldict['N']
    functions = ldict['functions']
    coords = ldict['coords']

    string_to_file = []
    equations = []

    print("|> Get reactions.")

    def Print(*args, file=''):
        for arg in args:
            string_to_file.append(arg)
            print(arg, file=file)

    def Print2(*args, file=''):
        for arg in args:
            equations.append(arg)
            # print(arg, file=file)

    def power_parser(string: str) -> str:
        # s = string[::-1]
        def change_to_pow(line, pos):

            def get_argument(ss, right_order=True):
                amount_space = 0
                while ss[amount_space] == ' ':
                    amount_space += 1
                ss = ss[amount_space:]
                rb = ')'
                lb = '('
                if not right_order:
                    rb = '('
                    lb = ')'
                stop = False
                prev_e = False
                argument = ""
                brackets_balance = 0
                local_pos = 0
                while not stop:
                    if local_pos == 0:
                        if ss[0] == '-':
                            local_pos += 1
                            continue
                        if ss[0] == lb:
                            brackets_balance += 1
                            local_pos += 1
                            continue
                    if local_pos == len(ss):
                        stop = True
                        break
                    if brackets_balance > 0:
                        if ss[local_pos] == rb:
                            brackets_balance -= 1
                            if brackets_balance == 0:
                                local_pos += 1
                                stop = True
                                break
                        if ss[local_pos] == lb:
                            brackets_balance += 1
                        local_pos += 1
                        continue
                    if ss[local_pos] == lb:
                        brackets_balance += 1
                        local_pos += 1
                        continue
                    if ss[local_pos] == 'e':
                        prev_e = True
                        local_pos += 1
                        continue
                    if ss[local_pos] in "+-" and not prev_e:
                        if local_pos + 1 < len(ss) and ss[local_pos + 1] == 'e':
                            local_pos += 1
                            continue
                        stop = True
                        break
                    if ss[local_pos] in "+-" and prev_e:
                        prev_e = False
                        local_pos += 1
                        continue
                    if ss[local_pos] in "*/= ":
                        stop = True
                        break
                    local_pos += 1
                    prev_e = False

                # print("STOPNUM:", stop_num)
                argument = ss[:local_pos]
                # print("ARG:", argument)
                if argument[0] == lb and argument[-1] == rb:
                    ans_pos = local_pos
                    # if not right_order:
                    #     ans_pos = local_pos - 1
                    return argument[1:-1], ans_pos + amount_space
                return argument, local_pos + amount_space

            arg2, pos2 = get_argument(line[pos + 2:])
            arg1, pos1 = get_argument(line[:pos][::-1], right_order=False)

            # print("PART ANS:", line[:pos-pos1])
            return f"{line[:pos - pos1]}pow({arg1[::-1]}, {arg2}){line[pos + 2 + pos2:]}"

        last_pos = string.rfind('**')
        # string = change_to_pow(string, last_pos)
        while last_pos != -1:
            string = change_to_pow(string, last_pos)
            last_pos = string.rfind('**')

        return string

    def find_common_elements(equations, new_arg_str="args"):
        new_equations = []
        # new_arg_str = "args"
        new_equations_amount = 0

        #     for i in range(len(equations)):
        #         equations[i] = equations[i].split('=')

        # print("T1")
        def get_balanced_string(string):
            balance = 0
            new_str = ""
            for s in string:
                new_str += s
                if s == '(':
                    balance += 1
                elif s == ')':
                    balance -= 1
                    if balance == 0:
                        break
            return new_str

        def create_parallel(arguments_in_section, equation_list, comment=''):
            sections_amount = len(equation_list) // arguments_in_section - 1
            equation_list[0] = comment + "\n\t#pragma omp sections\n\t{\n\t\t#pragma omp section\n\t\t{\n" \
                              + equation_list[0]
            for num, equation in enumerate(equation_list):
                if num == 0 or num >= len(equation_list) - 2:
                    continue
                if (num + 1) % arguments_in_section == 0 and sections_amount > 0:
                    sections_amount -= 1
                    equation_list[num] = equation_list[num] + "\n\t\t}\n\t\t#pragma omp section\n\t\t{"
            equation_list[-1] += "\n\t\t}\n\t}\n"
            return equation_list


        print('|>>> Start finding special functions : ["exp", "log", "pow", "sqrt", "sin", "cos", "tan"]')
        # List of special functions to search in code
        special_functions = ["exp", "log", "pow", "sqrt", "sin", "cos", "tan"]

        total_amount_of_special_functions = 0
        for equation in equations:
            new_args = []
            for spec_function in special_functions:
                last_pos = 0
                arg = equation.find(spec_function, last_pos)
                while arg != -1:
                    complex_function = get_balanced_string(equation[arg:])
                    new_args.append(complex_function)
                    last_pos = arg + 1
                    arg = equation.find(spec_function, last_pos)
            for complex_function in new_args:
                # print(complex_function)
                arg_name = new_arg_str + "[" + str(new_equations_amount) + "]"
                new_equations_amount += 1

                local_counter = 0
                for i, eq in enumerate(equations):
                    local_counter += eq.count(complex_function)
                    eq = eq.replace(complex_function, arg_name)
                    equations[i] = eq

                total_amount_of_special_functions += local_counter
                if local_counter != 0:
                    new_equations.append("\t\t\t" + arg_name + "=" + complex_function + ';\t//\t' + str(local_counter) + " times")

        print(f'|>>> Found {total_amount_of_special_functions} special functions')

        # Попробуем найти зависимости первых аргументов друг от друга
        # То есть, если какой-то из аргументов ссылается на другой при вычислении, то
        # опасно пихать их в разные секции параллельных вычислений.
        # Поэтому пока просто это выделим.
        # И если такое есть, то пусть всё будет вычисляться в одной секции без параллельности
        # Потому что перестроение делать нам сейчас не нужно - у нас таких сложных случаев ещё не было
        args_pairs = []
        for num, equation in enumerate(new_equations):
            equation = equation.split('=')
            pos = equation[1].find(new_arg_str)
            if pos != -1:
                arg_num = ''
                curr_pos = pos # + len(new_arg_str)
                while equation[1][curr_pos] in "0123456789":
                    arg_num += equation[1][curr_pos]
                    curr_pos += 1
                #print("ARG_NUM: ", arg_num)
                #print("C EQ:", equation)
                args_pairs.append([num])

        # Amount of arguments in one pragma section
        arguments_in_section = 15

        if len(args_pairs) == 0:
            first_comment = '\t// "Complex" functions\n'
            new_equations = create_parallel(120, new_equations, first_comment)

        # print("T2")

        print('|>>> Start finding expressions in brackets')

        expr_name = "expr"
        expr_counter = 0
        has_expr = True
        special_equations = []
        for num, equation in enumerate(equations):
            pos = equation.find("(")
            while pos != -1:
                complex_expression = get_balanced_string(equation[pos:])
                local_expr_name = expr_name + '[' + str(expr_counter) + ']'
                expr_counter += 1
                special_equations.append("\t\t\t" + local_expr_name + "=" + complex_expression[1:-1])
                # equation.replace(complex_expression, local_expr_name)
                for i, eq in enumerate(equations):
                    eq = eq.replace(complex_expression, local_expr_name)
                    equations[i] = eq
                equation = equations[num]
                pos = equation.find("(")

        # special_equations.reverse()

        complex_expressions_amount = expr_counter

        # print("T3")

        while has_expr:
            has_expr = False
            for num, equation in enumerate(special_equations):
                # print(num, end=' ')
                pos = equation.find("(")
                while pos != -1:
                    has_expr = True
                    complex_expression = get_balanced_string(equation[pos:])
                    local_expr_name = expr_name + '[' + str(expr_counter) + ']'
                    expr_counter += 1
                    special_equations.append("\t\t\t" + local_expr_name + "=" + complex_expression[1:-1])
                    # equation.replace(complex_expression, local_expr_name)
                    for i, eq in enumerate(special_equations):
                        eq = eq.replace(complex_expression, local_expr_name)
                        special_equations[i] = eq
                    equation = special_equations[num]
                    pos = equation.find("(")

        special_equations.reverse()  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        simple_expressions_amount = expr_counter - complex_expressions_amount

        for eq in equations:
            special_equations.append("\t\t" + eq)

        # Устроим теперь поиск мелких выражений для сокращения
        # Попарные умножения, которые встречаются наиболее часто, будем выносить

        # print("T4")
        # print(special_equations)

        # Это ломает запись типа "421е-12" :(((((((((
        # for p, eq_ in enumerate(special_equations):
        #     # print(p, end=' ')
        #     eq_ = eq_.replace(" ", "")
        #     eq_ = eq_.replace("+", " + ")
        #     eq_ = eq_.replace("-", " - ")
        #     special_equations[p] = eq_

        # print("\nT5")
        # print(special_equations)

        print('|>>> Start finding expressions of repeated multiplications')


        equation_set = []
        pair_statistics = {}
        for num, equation in enumerate(special_equations):
            if equation.find('=') == -1:
                continue
            equation = equation.split("=")
            equation[1] = equation[1].split(' ')
            for j in range(len(equation[1])):
                equation[1][j] = equation[1][j].split('*')
                if len(equation[1][j]) > 1:
                    for el1 in equation[1][j]:
                        for el2 in equation[1][j]:
                            if el1 == el2:
                                continue
                            key = ""
                            if el1.find(expr_name) != -1 or el2.find(expr_name) != -1 or el1.find(';') != -1 or el2.find(';') != -1:
                                continue
                            if el1 < el2:
                                key = el1 + "$" + el2
                            else:
                                key = el2 + "$" + el1
                            if key not in pair_statistics.keys():
                                pair_statistics[key] = 1
                            else:
                                pair_statistics[key] += 1
            special_equations[num] = equation

        # for sp in special_equations:
        #     print(sp)

        sort_statistics = []
        for k in pair_statistics.keys():
            if pair_statistics[k] < 2:
                continue
            sort_statistics.append([k, pair_statistics[k]])

        def k_sort(e):
            return -e[1]

        sort_statistics.sort(key=k_sort)

        total_amount_of_expressions = 0

        for elem in sort_statistics:
            amount = elem[1]
            elem[0] = elem[0].split('$')
            el1 = elem[0][0]
            el2 = elem[0][1]

            # Пока мальца тяжело отлавливать такие "квадраты", поэтому пропустим их
            if el1 == el2:
                continue

            # Проверка, что замена нужна (встречается более 2 раз
            local_amount = 0
            border_amount = 2
            for num, equation in enumerate(special_equations):
                for j in range(len(equation[1])):
                    if len(equation[1][j]) < 2:
                        continue
                    for e1 in equation[1][j]:
                        for e2 in equation[1][j]:
                            if e1 == el1 and e2 == el2:
                                local_amount += 1
                    if local_amount >= border_amount:
                        break
                if local_amount >= border_amount:
                    break
            if local_amount < border_amount:
                continue

            new_expr = expr_name + '[' + str(expr_counter) + ']'
            expr_counter += 1
            equation_set.append("\t\t\t" + new_expr + '=' + el1 + "*" + el2 + ";\t//\t" + str(amount) + " times")

            total_amount_of_expressions += amount

            for num, equation in enumerate(special_equations):
                for j in range(len(equation[1])):
                    if len(equation[1][j]) < 2:
                        continue
                    get_pair = False
                    for i1, e1 in enumerate(equation[1][j]):
                        for i2, e2 in enumerate(equation[1][j]):
                            if e1 == el1 and e2 == el2 and i1 != i2:
                                get_pair = True
                                break
                    if get_pair:
                        new_list = [new_expr]
                        for e in equation[1][j]:
                            if e != el1 and e != el2:
                                new_list.append(e)

                        # new_list.append(new_expr)
                        equation[1][j] = new_list

        #print(pair_statistics)

        print(f'|>>> Found {total_amount_of_expressions} repeated multiplications')

        set_comment = f'\n\t// First groups of multiplication\n'
        for j in range(len(equation_set)):
            equation_set[j] += ';'
        if len(equation_set):
            equation_set = create_parallel(600, equation_set, comment=set_comment)
        # new_equations.append(set_comment)
        for seq in equation_set:
            new_equations.append(seq)

        '''
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        SECOND ITERATION OF FINDING COMMON MULTIPLICATIONS
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        '''

        equation_set = []
        pair_statistics = {}
        for num, equation in enumerate(special_equations):
            if len(equation) <= 1:
                continue
            for j in range(len(equation[1])):
                if len(equation[1][j]) > 1:
                    for el1 in equation[1][j]:
                        for el2 in equation[1][j]:
                            if el1 == el2:
                                continue
                            key = ""
                            if el1.find(';') != -1 or el2.find(';') != -1:
                                continue
                            if el1.find(expr_name) != -1 or el2.find(expr_name) != -1:
                                continue

                            if el1 < el2:
                                key = el1 + "$" + el2
                            else:
                                key = el2 + "$" + el1
                            if key not in pair_statistics.keys():
                                pair_statistics[key] = 1
                            else:
                                pair_statistics[key] += 1
            #special_equations[num] = equation

        sort_statistics = []
        for k in pair_statistics.keys():
            if pair_statistics[k] < 2:
                continue
            sort_statistics.append([k, pair_statistics[k]])

        def k_sort(e):
            return -e[1]

        sort_statistics.sort(key=k_sort)
        # print(sort_statistics)

        for elem in sort_statistics:
            amount = elem[1]
            elem[0] = elem[0].split('$')
            el1 = elem[0][0]
            el2 = elem[0][1]

            # Пока мальца тяжело отлавливать такие "квадраты", поэтому пропустим их
            if el1 == el2:
                continue

            # Проверка, что замена нужна (встречается более 2 раз)
            local_amount = 0
            border_amount = 2
            for num, equation in enumerate(special_equations):
                for j in range(len(equation[1])):
                    if len(equation[1][j]) < 2:
                        continue
                    for e1 in equation[1][j]:
                        for e2 in equation[1][j]:
                            if e1 == el1 and e2 == el2:
                                local_amount += 1
                    if local_amount >= border_amount:
                        break
                if local_amount >= border_amount:
                    break
            if local_amount < border_amount:
                continue

            new_expr = expr_name + '[' + str(expr_counter) + ']'
            expr_counter += 1
            equation_set.append("\t\t\t" + new_expr + '=' + el1 + "*" + el2 + "; // " + str(amount) + " times")

            for num, equation in enumerate(special_equations):
                for j in range(len(equation[1])):
                    if len(equation[1][j]) < 2:
                        continue
                    get_pair = False
                    for e1 in equation[1][j]:
                        for e2 in equation[1][j]:
                            if e1 == el1 and e2 == el2:
                                get_pair = True
                                break
                    if get_pair:
                        new_list = [new_expr]
                        for e in equation[1][j]:
                            if e != el1 and e != el2:
                                new_list.append(e)

                        # new_list.append(new_expr)
                        equation[1][j] = new_list

        set_comment_2 = f'\n\t// Second groups of multiplication\n'
        # equation_set = create_parallel(40, equation_set, comment=set_comment)
        new_equations.append(set_comment_2)
        for seq in equation_set:
            new_equations.append(seq + ';')

        string_set = []
        for seq in special_equations:
            s = seq[0] + '='
            for el in seq[1]:
                if len(el) == 1:
                    s += ' ' + el[0]
                else:
                    for arg_num in range(len(el) - 1):
                        s += el[arg_num] + '*'
                    s += el[-1]
            string_set.append(s + ';')

        first_set = string_set[0:simple_expressions_amount]
        second_set = string_set[simple_expressions_amount:(simple_expressions_amount + complex_expressions_amount)]
        third_set = string_set[(simple_expressions_amount + complex_expressions_amount):]
        # new_equations.append("FIRST")
        fst_comment = "\n\t// Simple functions\n"
        # first_set = create_parallel(25, first_set, comment=fst_comment)
        new_equations.append(fst_comment)
        for seq in first_set:
            new_equations.append(seq)

        snd_comment = "\n\t// Complex big functions\n"
        #second_set = create_parallel(6, second_set, comment=snd_comment)
        new_equations.append(snd_comment)
        for seq in second_set:
            new_equations.append(seq)

        trd_comment = "\n\t// Jacobian and right part\n"
        #third_set = create_parallel(65, third_set, comment=trd_comment)
        new_equations.append(trd_comment)
        for seq in third_set:
            new_equations.append(seq)

        # for eq in equations:
        #     new_equations.append(eq)
        return new_equations, new_equations_amount, expr_counter

    i, j = 0, 0

    print("|> START differentiations")
    start_time = time.time()

    # Генерация header-файла, который мы будем использовать
    with open(file_name, "w") as text_file:
        Print("#include <iostream>\n#include <vector>\n#include <omp.h>\n", file=text_file)
        Print("using namespace std;\n", file=text_file)
        Print(
            f"static const unsigned int N = {N};\nstatic const double T = {t};\nstatic const unsigned int stepsAmount "
            f"= static_cast<unsigned int>({steps_amount});\n",
            file=text_file)
        elements = ""
        for name in add_info.split(', '):
            elements += '"' + name + '", '
        Print(f"\nvoid CROS::SetElements() {{\n\telements = {{\n\t\t{elements[:-2]}\n\t}};\n}};\n\n", file=text_file)
        Print("// " + add_info, file=text_file)
        Print(f"static vector<double> yy={{{y}}};  \n", file=text_file)
        Print("void CROS::SetJacobianAndF(vector<double> &y) {\n", file=text_file)
        total_times = len(functions) * len(coords)
        print(f"\r|>>> PROGRESS: {0}%", end='')
        with open("Jacob.txt", "w") as jacob_file:
            for f_num, f in enumerate(functions):
                for y_num, y in enumerate(coords):
                    buff = str(sym.diff(f, y))
                    # if j == 4 and i == 3:
                    #     print("B1:", buff)
                    if buff != '0':
                        print(f"\tJacob_[{j}][{i}] = {buff}", file=jacob_file)
                    buff = power_parser(buff)
                    # if j == 4 and i == 3:
                    #     print("B2:", buff)
                    # buff = re.sub(r'\(([^\(\)]*)\)\*\*(\d+\.?\d*)', r'pow(\1, \2)', buff)
                    # buff = re.sub(r'([^\*/+-]*?)\*\*(\(-\d+\.?\d*\))', r'pow(\1, \2)', buff)
                    # buff = re.sub(r'([^\*/+-\\)\\(][^\*/+-]*?)\*\*(\d+\.?\d*)', r'pow(\1, \2)', buff)
                    # buff = re.sub(r'\(([^\(\)]*)\)\*\*(\d+\.?\d*)', r'pow(\1, \2)', buff)
                    if buff != '0':
                        Print2(f"\tJacob_[{j}][{i}] = {buff}", file=text_file)
                        print(f"\tJacob_[{j}][{i}] = {buff}", file=jacob_file)
                    i += 1
                    print(f"\r|>>> PROGRESS: {(f_num * len(coords) + y_num + 1) * 100 // total_times}."
                          f"{((f_num * len(coords) + y_num + 1) * 1000 // total_times) % 10}%", end='')
                i = 0
                j += 1
            print('')
            # Print(f"\n    return Jacobi;\n }}", file=text_file)
            # Print(f"vector<double> funk(vector<double> &y) {{ \n vector<double> func({N});  \n", file=text_file)
            for f in functions:
                buff = str(f)
                if buff != '0':
                    print(f"\tf_[{i}] = {buff}", file=jacob_file)
                buff = power_parser(buff)
                # buff = re.sub(r'\(([^\(\)]*)\)\*\*(\d+\.?\d*)', r'pow(\1, \2)', buff)
                # buff = re.sub(r'([^\*/+-]*?)\*\*(\(-\d+\.?\d*\))', r'pow(\1, \2)', buff)
                # buff = re.sub(r'([^\*/+-\\)\\(][^\*/+-]*?)\*\*(\d+\.?\d*)', r'pow(\1, \2)', buff)
                # buff = re.sub(r'\(([^\(\)]*)\)\*\*(\d+\.?\d*)', r'pow(\1, \2)', buff)
                if buff != '0':
                    Print2(f"\tf_[{i}] = {buff}", file=text_file)
                    print(f"\tf_[{i}] = {buff}", file=jacob_file)
                i += 1

        print("|> END of differentiations")
        print(f"|> TIME (differentiations): {int(time.time() - start_time)}s")
        print("|> START optimizations")
        start_time = time.time()

        list_name = "args"
        amount_of_arguments = 0
        amount_of_expr = 0
        #new_eq = equations
        new_eq, amount_of_arguments, amount_of_expr = find_common_elements(equations, new_arg_str=list_name)

        print("|> END of optimization")
        print(f"|> TIME (optimization): {int(time.time() - start_time)}s")

        Print(f"\tdouble {list_name}[{amount_of_arguments}] = {{0.0}};\n", file=text_file)
        Print(f"\tdouble expr[{amount_of_expr}] = {{0.0}};\n", file=text_file)

        for eq in new_eq:
            Print(eq, file=text_file)
        Print("\n\n}", file=text_file)
        # Print("\n    return Jacobi, func;\n } } ", file=text_file)

        # return find_common_elements(equations)
#         for eq in equations:
#             print(eq)
