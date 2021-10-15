"""

    The Nook Programming Language.

"""
# Consts
WHITESPACE = " \t\r\f"
VERSION = "0.7"

# Lambdas
numeric = lambda c: c.isnumeric()
identifier = lambda c: c.isalpha() and c not in WHITESPACE
symbol = lambda c: c.isascii() and c not in WHITESPACE
report = lambda msg, line, pos: print(
    f"Error: {msg}" + ("" if (line == None) else f"\nAt line {line}, position {pos}")
)

# Helper functions
def set_env(env: dict, name: str, value) -> dict:
    env[name] = value
    return env


def pop(stack: list):
    if len(stack) == 0:
        report("Stack empty", None, 0)
        return 101
    else:
        return stack.pop()


def peek(stack: list):
    if len(stack) == 0:
        report("Stack empty", None, 0)
        return 101
    else:
        return stack[-1]


def consume(condition, inpt: str, pos: int):
    prev_pos = pos
    pos += 1

    while pos < len(inpt) and condition(inpt[pos]):
        pos += 1

    return (inpt[prev_pos:pos], pos)


# The main 'run' function
def run(inpt: str, stack: list, env: dict, no_curly: bool = False):
    c = 0  # Pointer
    vc = 0  # Virtual pointer
    line = 1  # Line
    start_string, end_string = ("[", "]") if no_curly else ("{", "}")

    while c < len(inpt):
        current = inpt[c]

        # String
        if current == start_string:
            prev_c = c
            c += 1

            while c < len(inpt) and inpt[c] != end_string:
                if inpt[c] == end_string:
                    break
                c += 1

            string = inpt[prev_c:c]
            stack.append(string)
            c += 1
            vc = c
        # Consume negative numbers (_500 = -500)
        elif current == "_":
            c += 1
            number, c = consume(lambda c: numeric(c), inpt, c)
            number = int(number) * -1
            vc = c
            stack.append(number)
        # Store/Load
        elif current == "s":
            c += 1
            var, c = consume(lambda c: c != " ", inpt, c)
            value = pop(stack)
            vc = c

            set_env(env, var, value)
        elif current == "l":
            c += 1
            var, c = consume(lambda c: c != " ", inpt, c)
            vc = c

            stack.append(env[var])
        elif current in WHITESPACE:
            vc += 1
            c += 1
        # Comment
        elif current == "#":
            while c < len(inpt) and inpt[c] != "\n":
                c += 1
        elif current == "\n":
            vc = 0
            line += 1
            c += 1
        elif numeric(current):
            number, c = consume(lambda c: numeric(c), inpt, c)
            number = int(number)
            vc = c
            stack.append(number)
        elif identifier(current):
            name, c = consume(lambda c: identifier(c), inpt, c)
            vc = c

            if name in env:
                env[name]()
            else:
                report(f"Name not defined: {repr(name)}", line, vc)
        elif symbol(current):
            sym, c = consume(lambda c: symbol(c), inpt, c)
            vc = c

            if sym in env:
                env[sym]()
            else:
                report(f"Symbol not defined: {repr(sym)}", line, vc)
        else:
            report(f"Invalid character: {repr(current)}", line, vc)
            vc += 1
            c += 1

    return stack, env


# Run the input without worrying about stack and environment
def run_script(script: str, env: dict = {}, no_curly: bool = True):
    if env != {}:
        stack, _ = init_env()
        stack, env = run(script, stack, env, no_curly)
    else:
        stack, env = init_env()
        stack, env = run(script, stack, env, no_curly)

    return stack


# = Control flow functions =

# Each
def nook_each(script: str, how_much: int, env: dict):
    for _ in range(how_much):
        run_script(script, env=env)


# If
def nook_if(elsee: str, then: str, iff: str, env: dict):
    if_result = not bool(pop(run_script(iff)))

    if if_result:
        _ = run_script(then, env=env)
    else:
        _ = run_script(elsee, env=env)


# Loop
def nook_loop(condition: str, script: str, env: dict):
    cond_result = True if condition == "" else not bool(pop(run_script(condition)))

    while cond_result:
        _ = run_script(script, env=env)


# Convert boolean to int
def bool_to_int(inpt: bool) -> int:
    return 0 if inpt else 1


# Logical functions
def int_not(v: int) -> int:
    return int(not v)


def int_and(v1: int, v2: int) -> int:
    return int(not (v1 and v2))


def int_or(v1: int, v2: int) -> int:
    return int(not (v1 or v2))


# Initialize environment
def init_env(stack: list = [], env: dict = {}) -> tuple:
    env = {
        "+": lambda: stack.append(stack.pop() + stack.pop()),
        "-": lambda: stack.append(stack.pop() - stack.pop()),
        "*": lambda: stack.append(stack.pop() * stack.pop()),
        "/": lambda: stack.append(stack.pop() // stack.pop()),
        "%": lambda: stack.append(stack.pop() % stack.pop()),
        ".": lambda: pop(stack),
        "v": lambda: print(stack),
        "w": lambda: print(pop(stack)),
        "p": lambda: print(peek(stack)),
        "x": lambda: run_script(str(pop(stack)).strip(), env=env),
        "e": lambda: nook_each(str(pop(stack)), pop(stack), env=env),
        "d": lambda: stack.append(stack[-1]),
        "i": lambda: stack.append(int(input(""))),
        "t": lambda: nook_loop(str(pop(stack)), str(pop(stack)), env),
        "?": lambda: nook_if(str(pop(stack)), str(pop(stack)), str(pop(stack)), env),
        "~": lambda: stack.append(int_not(pop(stack))),
        "&": lambda: stack.append(int_and(pop(stack), pop(stack))),
        "|": lambda: stack.append(int_or(pop(stack), pop(stack))),
        "=": lambda: stack.append(bool_to_int(pop(stack) == pop(stack))),
        ">": lambda: stack.append(bool_to_int(pop(stack) > pop(stack))),
        "<": lambda: stack.append(bool_to_int(pop(stack) < pop(stack))),
        ">=": lambda: stack.append(bool_to_int(pop(stack) >= pop(stack))),
        "<=": lambda: stack.append(bool_to_int(pop(stack) <= pop(stack))),
        "<>": lambda: stack.append(bool_to_int(pop(stack) != pop(stack))),
    }

    return (stack, env)
