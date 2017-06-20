from sys import *

tokens = []
lines = []
num_stack = []

symbols = {}

NUM_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
OP_LIST = ["+", "-", "*", "/", "%", "(", ")", "**", "//"]
SPECIAL_OP_LIST = ["(",")"]
COMP_LIST = ["EQ", "NE", "GT", "GE", "LT", "LE"]
NOTVAR_LIST = [":", ">", "<", "=", "?", "!", ".", ",", ";", \
             "/", "^", "~", "[", "]", "{", "}", "(", ")"]

keys = {}

keys["IF"] = "IF"
keys["THEN"] = "THEN"
keys["ELSE"] = "ELSE"
keys["ENDIF"] = "ENDIF"
keys["LOOP"] = "LOOP"
keys["DO"] = "DO"
keys["ENDLOOP"] = "ENDLOOP"
keys["PRINT"] = "PRINT"
keys["VAR"] = "VAR"
keys["STRING"] = "STRING"
keys["INPUT"] = "INPUT"
keys["LET"] = "LET"

keys["EQ"] = ":EQ"
keys["NE"] = ":NE"
keys["GT"] = ":GT"
keys["LT"] = ":LT"
keys["GE"] = ":GE"
keys["LE"] = ":LE"

keys["TO"] = ":TO"

keys["ASSIGN"] = "="
keys["STARTVAR"] = "$"
keys["COMMENT"] = "#"
keys["TERMINATOR"] = ";"
keys["NEWLINE"] = "\n"
keys["TAB"] = "\t"
keys["EOF"] = "<EOF>"
keys["EOE"] = "<EOE>"

INC = ["THEN", "DO", "ELSE"]
DEC = ["ENDIF", "ENDLOOP", "ELSE"]

def open_file(filename):
    data = open(filename, "r").read()
    data += keys["EOF"]
    return data

def lex(filecontents):

    global tokens, lines

    tok = ""
    expr = ""
    isexpr = 0
    varstarted = 0
    iscomment = 0
    var = ""
    instring = 0    # flag se o caracrete lido esta em uma string
    string = ""
    #n = ""
    level = 0       # nivel de aninhamento
    escape = 0      # flag para indicacao de escape
    #line = []
    filecontents = list(filecontents)
    for char in filecontents:
        tok += char
        #print(tok)

        if iscomment == 1:
            if tok != keys["NEWLINE"]:
                tok = ""
                continue
        if tok == keys["COMMENT"]:
            if instring == 0:
                tok = ""
                iscomment = 1

        if tok == " ":
            if instring == 0:
                if expr != "" and isexpr == 1:
                    tokens.append("EXPR:" + expr)
                    expr = ""
                    isexpr = 0
                elif expr != "" and isexpr == 0:
                    tokens.append("NUM:" + expr)
                    expr = ""
                elif var != "":
                    tokens.append("VAR:" + var)
                    var = ""
                    varstarted = 0
                tok = ""

        elif tok == keys["NEWLINE"]   or \
            tok == keys["TERMINATOR"] or \
            tok == keys["EOF"]:
            if expr != "" and isexpr == 1:
                tokens.append("EXPR:" + expr)
                expr = ""
            elif expr != "" and isexpr == 0:
                tokens.append("NUM:" + expr)
                expr = ""
            elif var != "":
                tokens.append("VAR:" + var)
                var = ""
                varstarted = 0
            tok = ""
            iscomment = 0
            isexpr = 0

            stack_tokens()

        elif tok == keys["ASSIGN"] and instring == 0:
            if var != "":
                tokens.append("VAR:" + var)
                var = ""
                varstarted = 0
            if len(tokens) > 0:
                if tokens[-1][0:3] == "VAR":
                    tokens.append("ASSIGN")
                else:
                    treat_parse_error(tokens)
            tok = ""

        elif tok.upper() == keys["EQ"] and instring == 0:
            if expr != "" and isexpr == 0:
                tokens.append("NUM:" + expr)
                expr = ""
            tokens.append("EQ")
            tok = ""

        elif tok.upper() == keys["NE"] and instring == 0:
            if expr != "" and isexpr == 0:
                tokens.append("NUM:" + expr)
                expr = ""
            tokens.append("NE")
            tok = ""

        elif tok.upper() == keys["TO"] and instring == 0:
            if expr != "" and isexpr == 0:
                tokens.append("NUM:" + expr)
                expr = ""
            tokens.append("TO")
            tok = ""

        elif tok == keys["STARTVAR"] and instring == 0:
            varstarted = 1
            var += tok
            tok = ""

        elif varstarted == 1:
            if tok in NOTVAR_LIST:
                if var != "":
                    tokens.append("VAR:" + var)
                    var = ""
                    varstarted = 0
            else:
                var += tok
            tok = ""

        elif tok.upper() == keys["PRINT"]:
            tokens.append("PRINT")
            tok = ""

        elif tok.upper() == keys["ENDIF"]:
            level -= 1
            tokens.append("ENDIF")
            tok = ""

        elif tok.upper() == keys["ELSE"]:
            level -= 1
            tokens.append("ELSE")
            level += 1
            tok = ""

        elif tok.upper() == keys["IF"]:
            tokens.append("IF")
            tok = ""

        elif tok.upper() == keys["THEN"]:
            if expr != "" and isexpr == 0:
                tokens.append("NUM:" + expr)
                expr = ""
            tokens.append("THEN")
            line = [level]
            level += 1
            tok = ""

        elif tok.upper() == keys["ENDLOOP"]:
            level -= 1
            tokens.append("ENDLOOP")
            tok = ""

        elif tok.upper() == keys["LOOP"]:
            tokens.append("LOOP")
            tok = ""

        elif tok.upper() == keys["DO"]:
            if expr != "" and isexpr == 0:
                tokens.append("NUM:" + expr)
                expr = ""
            tokens.append("DO")
            level += 1
            tok = ""

        elif tok.upper() == keys["INPUT"]:
            tokens.append("INPUT")
            tok = ""

        elif tok.upper() == keys["LET"] and instring == 0:
            tokens.append("LET")
            tok = ""

        elif tok in NUM_LIST:
            expr += tok
            tok = ""

        elif tok in OP_LIST:
            isexpr = 1
            expr += tok
            tok = ""

        elif tok == keys["TAB"]:
            tok = ""

        elif tok == "\"" or tok == " \"":
            if instring == 0:
                instring = 1
            elif instring == 1:
                tokens.append("STRING:" + string + "\"")
                string = ""
                instring = 0
                tok = ""

        elif instring == 1:
            string += tok
            tok = ""

    stack_tokens()

    #return tokens
    return lines

def stack_tokens():
    global tokens, lines
    if len(tokens) > 0:
        lines.append(tokens)
    tokens = []

def eval_expression(expr):
    do_print(split_expression(expr))
    return eval(expr)

def split_expression(expr):
    expr = ";" + expr
    i = len(expr) - 1
    num = ""
    last = ""
    while i >= 0:
        if num != "":
            last = num
        elif len(num_stack) > 0:
            last = num_stack[-1]
        else:
            last = ""
        if expr[i] in OP_LIST:
            num = num[::-1]
            if len(num_stack) > 0 and \
                last in OP_LIST and expr[i] + last in OP_LIST:
                num_stack[-1] = expr[i] + last
            elif last in OP_LIST and \
                 last not in SPECIAL_OP_LIST and \
                 expr[i] not in SPECIAL_OP_LIST:
                treat_expr_error(num_stack, expr[i])
            else:
                if num != "":
                    num_stack.append(num)
                num_stack.append(expr[i])
            num = ""
        elif expr[i] == ";":
            num = num[::-1]
            if num != "":
                num_stack.append(num)
            num = ""
        else:
            num += expr[i]
            #print "NUMBER " + expr[i]
        i -= 1

    for tok in num_stack:
        if not tok in OP_LIST and \
            not tok.isdigit() and \
            not tok == " ":
            print("Wrong expression in '" + tok + "': <<" \
                     + " ".join(num_stack) + ">>")
            exit()

    return(num_stack[::-1])
    #return "Got it! " + expr

def do_print(toPrint):
    if(toPrint[0:6] == "STRING"):
        toPrint = toPrint[8:]
        toPrint = toPrint[:-1]
    elif(toPrint[0:3] == "NUM"):
        toPrint = toPrint[4:]
    elif(toPrint[0:4] == "EXPR"):
        #toPrint = split_expression(toPrint[5:])
        toPrint = eval_expression(toPrint[5:])
    print(toPrint)

def do_assign(varname, varvalue):
    symbols[varname[5:]] = varvalue

def get_variable(varname):
    varname = varname[5:]
    if varname in symbols:
        return symbols[varname]
    else:
        return "VARIABLE ERROR: Undefined variable"
        exit()

def get_input(text, varname):
    string = str(input(text[8:-1] + " "))
    symbols[varname[5:]] = "STRING:\"" + string + "\""

def get_value(tok):
    if tok[0:3] == "VAR":
        return symbols[tok[5:]]
    if tok[0:3] == "NUM":
        return tok[5:]
    if tok[0:4] == "EXPR":
        return eval_expression(tok[6:])
    if tok[0:6] == "STRING":
        return tok[8:]

def treat_parse_error(toks, tip=""):
    print("PARSE ERROR: " + " ".join(map(str, toks)) + " <<" + tip + ">>")
    exit()

def treat_lex_error(toks):
    print("LEX ERROR: " + " ".join(map(str, toks)))
    exit()

def treat_expr_error(expr, tip=""):
    print("EXPR ERROR: " + " ".join(expr) + " <<" + tip + ">>")
    exit()

def parse(toks):
    i = 0
    while i < len(toks):
        parse_chunk(toks[i])
        i += 1
    print(symbols)


def parse_chunk(toks):
    i = 0
    while i < len(toks):

        if toks[i] == "ENDIF":
            i += 1

        elif toks[i] == "ELSE":
            i += 1

        elif toks[i] == "ENDLOOP":
            i += 1

        elif toks[i] == "PRINT":
            if len(toks) < 2:
                treat_parse_error(toks)
            if toks[i+1][0:6] == "STRING":
                do_print(toks[i+1])
            elif toks[i+1][0:3] == "NUM":
                do_print(toks[i+1])
            elif toks[i+1][0:4] == "EXPR":
                do_print(toks[i+1])
            elif toks[i+1][0:3] == "VAR":
                do_print(get_variable(toks[i+1]))
            i += 2

        elif toks[i][0:3] + " " + toks[i+1] == "VAR ASSIGN":
            if len(toks) < 3:
                treat_parse_error(toks)
            if toks[i+2][0:6] == "STRING":
                do_assign(toks[i], toks[i+2])
            elif toks[i+2][0:3] == "NUM":
                do_assign(toks[i], toks[i+2])
            elif toks[i+2][0:4] == "EXPR":
                do_assign(toks[i], "NUM:" + str(eval_expression(toks[i+2][5:])))
            elif toks[i+2][0:3] == "VAR":
                do_assign(toks[i], get_variable(toks[i+2]))
            i += 3

        elif toks[i] + " " + toks[i+1][0:6] == "INPUT STRING":
            if len(toks) < 3:
                treat_parse_error(toks)
            if  toks[i+2][0:3] == "VAR":
                get_input(toks[i+1], toks[i+2])
            i += 3

        elif toks[i] + " " + toks[i+1][0:3] == "LET VAR":
            if len(toks) < 3:
                treat_parse_error(toks)
            if toks[i+2][0:6] == "STRING":
                do_assign(toks[i+1], toks[i+2])
            elif toks[i+2][0:3] == "NUM":
                do_assign(toks[i+1], toks[i+2])
            elif toks[i+2][0:4] == "EXPR":
                do_assign(toks[i], "NUM:" + str(eval_expression(toks[i+2][5:])))
            else:
                treat_parse_error(toks)
            i += 3

        elif toks[i] == "IF":
            if len(toks) < 5:
                treat_parse_error(toks, "len")
            if toks[-1] != "THEN": # then obrigatorio
                treat_parse_error(toks, "then")
            if toks[i+2] not in COMP_LIST:
                treat_parse_error(toks, "comp")
            if toks[i+2] == "EQ":
                if get_value(toks[i+1]) == get_value(toks[i+3]):
                    do_print("TRUE")
                else:
                    do_print("FALSE")
            elif toks[i+2] == "NE":
                if get_value(toks[i+1]) != get_value(toks[i+3]):
                    do_print("TRUE")
                else:
                    do_print("FALSE")
            i += 5

        elif toks[i] == "LOOP":
            if len(toks) < 5:
                treat_parse_error(toks, "len")
            if toks[-1] != "DO": # do obrigatorio
                treat_parse_error(toks, "do")
            if toks[i+2] != "TO": # to obrigatorio
                treat_parse_error(toks, "to")
            if toks[i+1][0:3] != "NUM":
                treat_parse_error(toks, "num1")
            if toks[i+3][0:3] != "NUM":
                treat_parse_error(toks, "num2")
            do_print("LOOPING!")
            i += 5

        else:
            i += 1

def make_tree(toks, level=0):
    print("-"*50)
    for line in toks:
        if line[-1] in DEC:
            level -= 1
        print('\t'*level + " ".join(line))
        if line[-1] in INC:
            level += 1
    print("-"*50)

def run():

    debug = 0
    if len(argv) < 2:
        print("File must be passed")
        exit()
    if len(argv) > 2:
        if argv[2] == "token":
            debug = 1
        elif argv[2] == "parse":
            debug = 2
        elif argv[2] == "tree":
            debug = 3

    data = open_file(argv[1])
    toks = lex(data)
    if debug != 0:
        print(toks)
    if debug == 3:
        make_tree(toks)
    if debug != 1:
        parse(toks)

run()
