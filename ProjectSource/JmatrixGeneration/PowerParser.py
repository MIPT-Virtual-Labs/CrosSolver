import ast
import inspect
import math

import re


def square_balance(string):
    count = 0
    squares = list()
    for i in string:
        if i == '(':
            count += 1
            is_squares = True
        if i == ')':
            count -= 1
        squares.append(count)
    return squares



def changin_squarse_pow(string, squares):
    sq = re.finditer('\*\*', string)
    new_string = ""
    right_squares = False
    left_squares = False
    for i in sq:
        #print(i.span())
        p_start = 0
        p_end = 0
        if string[i.span()[1]] == '(':
            right_squares = True
            #print("right_squares")
            #print(squares)
            level = squares[i.span()[1]]
            p_start = i.span()[1]
            ending = 0
            for j in range(i.span()[1], len(squares)):
                if squares[j] == level - 1:
                    ending = j
                    p_end = j + 1
                    break
        else:
            p_start = i.span()[1]
            symbols = {'+', '-', '/', '*', '='}
            for j in range(i.span()[1], len(squares)):
                if string[j] in symbols:
                    p_end = j
                    break
                if j == len(squares) - 1:
                    ending = j
                    p_end = j + 1
                    break
        arg_start = 0
        arg_end = 0
        if string[i.span()[0] - 1] == ')':
            left_squares = True
            arg_end = i.span()[0]
            level = squares[i.span()[0] - 1]
            #print("level " + str(level) + " " + str(i.span()[0] - 1))
            for j in range(1, len(squares[:i.span()[0]])):
                if i.span()[0] - 1 - j == 0:
                    arg_start = 0
                    break
                if squares[i.span()[0] - 1 - j] == level:
                    arg_start = i.span()[0] - j
                    #print(arg_start)
                    break
        else:
            arg_end = i.span()[0]
            symbols = {'+', '-', '/', '*', '='}
            for j in range(len(squares[:i.span()[0]])):
                if string[i.span()[0] - 1 - j] in symbols:
                    arg_start = i.span()[0] - j
                    break
                if i.span()[0] - 1 - j == 0:
                    arg_start = 0
                    break
        #print(arg_start, arg_end, p_start, p_end)
        #print(string[:arg_start])
        #print(string[arg_start:arg_end])
        #print(string[p_start:p_end ])
        #print(string[p_end:])
        new_string = string[:arg_start]
        if left_squares:
            new_string += "pow(" + string[arg_start + 1:arg_end - 1] + ','
        else:
            new_string += "pow(" + string[arg_start:arg_end] + ','
        if right_squares:
            new_string += string[p_start + 1:p_end - 1] + ')' + string[p_end + 1:]
        else:
            new_string += string[p_start:p_end] + ')' + string[p_end:]
        #print(new_string)
        break
    return new_string


def power_parser_r(string: str) -> str:
    #print(re.findall(r'([\w\[\]]*)\*\*(-*[\w\[\].]*)', string))
    #print(re.sub(r'([\/*+-])([\w\[\]]*?)\*\*([\-]*[\w\.]*?)([\/*+ $-])', r"\1pow(\2, \3)\4", string))
    #print(re.findall(r'([\w\[\]]*)\*\*(\(.*\)?)', string))
    squares = list()
    count = 0
    pows = dict()
    while(string.find('pow') != -1):
        is_squares = False
        squares = list()
        for i in string:
            if i == '(':
                count += 1
                is_squares = True
            if i == ')':
                count -= 1
            squares.append(count)
        #print(squares)
        count = 0
        pows = dict()
        locate = string.find('pow') + 3
        ending = 0
        for j in range(locate, len(string)):
            if squares[j] == squares[locate] - 1:
                ending = j + 1
                break
        name = "a" + str(count)
        pre_string = string[locate + 1:ending - 1]
        pre_balance = square_balance(pre_string)
        operand = ""
        pre_pow = ""

        for i in range(len(pre_string)):
            if pre_string[i] == ',' and pre_balance[i] == 0:
                operand = pre_string[:i]
                pre_pow = pre_string[i + 1:]
                break
        if operand.find("**") != -1:
            edit_operand = power_parser(operand)
            operand = edit_operand
        if pre_pow.find("**") != -1:
            edit_pre_pow = power_parser(pre_pow)
            pre_pow = edit_pre_pow

        pows[name] = "pow(" + operand + "," + pre_pow + ")"
        string = string[:locate-3] + name + string[ending:]
    is_squares = False
    squares = list()
    for i in string:
        if i == '(':
            count += 1
            is_squares = True
        if i == ')':
            count -= 1
        squares.append(count)
    #print(squares)
    count = 0
    #print(string)
    if is_squares:
        #print("start")
        string=changin_squarse_pow(string, squares)
    else:
        #string = re.sub(r'([\w\[\]]*)\*\*\((.*)?\)', r"pow(\1,\2)", string)
        #print("finish")
        string = re.sub(r'([\w.\[\]]*e-[\w.\[\]]*|[\w.\[\]]*)\*\*(-*[\w.\[\]]*e-[\w.\[\]]*|-*[\w.\[\]]*)', r"pow(\1,\2)", string, count=1)
    #print(re.findall(r'[\/*+-]([\w\[\]]*?)\*\*([\-]*[\w\.]*?)[\/*+ $-]', string))
    #tree = compile(string, '<string>', mode='single', flags=ast.PyCF_ONLY_AST)
    #tree = ast.parse(string, mode='exec', type_comments=True)
    #print(astunparse.unparse(tree))
    #print(ast.dump(tree))
    #code = PowForDoubleStar().visit(tree)
    #print(ast.dump(code))
    #return code.body[0].targets[0] + "=" + code.body[0].value
    #print(pows)
    for key in pows:
        #print(key)
        #if pows[key].find("**") != -1:
        #    edit_key = power_parser(pows[key])
        #    pows[key] = edit_key
        pow_locate = string.find(key)
        edit_string = string[:pow_locate] + pows[key] + string[pow_locate + len(key):]
        string = edit_string
    return string


counter = 0


def power_parser(string):
    if string.find("**") != -1:
        location = len(string) - string[::-1].find("**") - 2
        operand_start = 0
        operand_end = location
        pow_start = location + 2
        pow_end = 0
        square_operand = False
        square_pow = False
        pow_whitespace = False
        operand_whitespace = False
        while string[operand_end - 1] == ' ':
            operand_end -= 1
            operand_whitespace = True
        if string[operand_end - 1] == ')':
            square_operand = True
            current_balance = square_balance(string)
            level = current_balance[operand_end - 1]
            for i in range(1, len(string[:operand_end])):
                if current_balance[operand_end - 1 - i] == level:
                    operand_start = operand_end - i
                    break
        else:
            symbols = {'=', '-', '+', '*', '/', ' ', '('}
            for i in range(1, len(string[:operand_end])):
                if string[operand_end - i] in symbols:
                    if string[operand_end - i] == '-':
                        if string[operand_end - i - 1] == 'e':
                            continue
                    break
                operand_start = operand_end - i
        #print(len(current_balance))
        #print(current_balance)
        #print(operand_start, operand_end)
        while string[pow_start] == ' ':
            pow_whitespace = True
            pow_start += 1
        #print(pow_start, pow_end)
        if string[pow_start] == '(':
            square_pow = True
            current_balance = square_balance(string)
            level = current_balance[pow_start] - 1
            for i in range(1, len(string[pow_start:])):
                if current_balance[pow_start + i] == level:
                    pow_end = pow_start + i + 1
                    break
        else:

            symbols = {'=', '-', '+', '*', '/', ' ', ')'}
            for i in range(len(string[pow_start:])):
                if string[pow_start + i] in symbols:
                    if string[pow_start + i] == '-':
                        if string[pow_start + i - 1] == 'e' or string[pow_start + i - 1] == '*' or (string[pow_start + i - 1] == ' ' and pow_whitespace):
                            continue
                    pow_end = pow_start + i
                    break
                if pow_start + i == len(string) - 1:
                    pow_end = pow_start + i + 1
        #print(pow_start, pow_end)
        edit_string = string[:operand_start]
        edit_operand = string[operand_start:operand_end]
        edit_pow = string[pow_start:pow_end]
        edit_other = string[pow_end:]
        if square_pow:
            edit_pow = string[pow_start + 1: pow_end - 1]
            edit_other = string[pow_end + 1:]
        if square_operand:
            edit_string = string[:operand_start]
            edit_operand = string[operand_start + 1: operand_end - 1]
        #print("edit_string = " + edit_string)
        #print("edit_operand = " + edit_operand)
        #print("edit_pow = " + edit_pow)
        #print("edit_other = " + edit_other)
        if edit_operand.find("**") != -1:
            edit_operand = power_parser(edit_operand)
        else:
            pass
        if edit_pow.find("**") != -1:
            edit_pow = power_parser(edit_pow)
        else:
            pass
        pows = dict()
        if edit_string.find("**") != -1:
            pows["a" + str(counter)] = 'pow(' + edit_operand + ', ' + edit_pow + ')'
            #print("pows:" + str(pows))
            #print("nes_string " + edit_string + "a" + str(counter) + edit_other)
            edit_other = power_parser(edit_string + "a" + str(counter) + edit_other)
        else:
            edit_other = edit_string + 'pow(' + edit_operand + ', ' + edit_pow + ')' + edit_other
        for key in pows:
            loc_key = edit_other.find(key)
            if loc_key != -1:
                new_other = edit_other[:loc_key] + pows[key] + edit_other[loc_key + len(key):]
                edit_other = new_other
        string = edit_other
    return string


def power_parser_1(string):
    #print("My string: " + string)
    while(string.find("**") != -1):
        edit_string = power_parser_r(string)
        string = edit_string
    return string
#print("d = 2e-6+3 * y[5] ** 68.0025345e5 ** (y[4] + y[3] ** 44.234e-6)")
#print(power_parser("d = 2e-6+3 * y[5] ** 68.0025345e5 ** (y[4] + y[3] ** 44.234e-6)"))
#print("d = 2+3 * y[5] ** -68.0025345e5")
#print(power_parser("d = 2+3 * y[5] ** -68.0025345e5"))
#print("d = 2e-6+3 * y[5] ** 68.0025345e5 ** (y[4] + y[3] ** 44.234e-6)")
#print(power_parser("d = 2e-6+3 * y[5] ** 68.0025345e5 ** (y[4] + y[3] ** 44.234e-6)"))
#print("1/(y[0]+ y[2]*(3.24372837e-12*y[4]**4 - 9.68129509e-9*y[4]**3 + 9.84730201e-6*y[4]**23 - 0.00299673416*y[4] + 3.78245636) + y[3]*(1.3641147e-12*y[4]**4 - 3.88113333e-9*y[4]**3 + 4.61793841e-6*y[4]**2 - 0.00240131752*y[4] + 3.99201543))**2")
#print(power_parser("1/(y[0]+ y[2]*(3.24372837e-12*y[4]**4 - 9.68129509e-9*y[4]**3 + 9.84730201e-6*y[4]**23 - 0.00299673416*y[4] + 3.78245636) + y[3]*(1.3641147e-12*y[4]**4 - 3.88113333e-9*y[4]**3 + 4.61793841e-6*y[4]**2 - 0.00240131752*y[4] + 3.99201543))**2"))
#print("d = 2e-6+3 * a0 ** y[4]".find("**"))
#print(len("d = 2e-6+3 * a0 ** y[4]") - "d = 2e-6+3 * a0 ** y[4]"[::-1].find("**") - 2)
