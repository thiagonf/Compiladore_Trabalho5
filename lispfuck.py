from sys import argv
import pprint
import ox

file_name, file_in, file_out = argv

in_file = open(file_in)
code = in_file.read()

lexer = ox.make_lexer([
    ('LOOP', r'loop'),
    ('DEC', r'dec'),
    ('INC', r'inc'),
    ('LPAR', r'\('),
    ('RPAR', r'\)'),
    ('RIGHT', r'right'),
    ('LEFT', r'left'),
    ('PRINT', r'print'),
    ('READ', r'read'),
    ('DO', r'do'),
    ('DO_AFTER', r'do-after'),
    ('DO_BEFORE', r'do-before'),
    ('ADD', r'add'),
    ('SUB', r'sub'),
    ('NUMBER', r'[0-9]+'),
    ('ignore_COMMENT', r';[^\n]*'),
    ('ignore_BREAK_LINE', r'\n'),
    ('ignore_SPACE', r'\s+')
])

tokens_list = ['LOOP',
               'DEC',
               'INC',
               'LPAR',
               'RPAR',
               'RIGHT',
               'LEFT',
               'PRINT',
               'READ',
               'DO',
               'DO_AFTER',
               'DO_BEFORE',
               'ADD',
               'SUB',
               'NUMBER']

parser = ox.make_parser([
    ('expr : LPAR RPAR', lambda x, y: '[]'),
    ('expr : LPAR term RPAR', lambda x, y, z: y),
    ('term : atom term', lambda x, y: [x,] + y),
    ('term : atom', lambda x:[x,]),
    ('atom : expr', lambda x:x),
    ('atom : DEC', lambda x:x),
    ('atom : INC', lambda x:x),
    ('atom : LOOP', lambda x:x),
    ('atom : RIGHT', lambda x:x),
    ('atom : LEFT', lambda x:x),
    ('atom : PRINT', lambda x:x),
    ('atom : READ', lambda x:x),
    ('atom : DO', lambda x:x),
    ('atom : DO_AFTER', lambda x:x),
    ('atom : DO_BEFORE', lambda x:x),
    ('atom : ADD', lambda x:x),
    ('atom : SUB', lambda x:x),
    ('atom : NUMBER', int),
], tokens_list)


tokens = lexer(code)
tokens = [token for token in tokens if token.type != 'COMMENT' and token.type != 'SPACE']
ast = parser(tokens)

class Compiler:
    def right(self):
        self.file_out.write('>')

    def left(self):
        self.file_out.write('<')

    def inc(self):
        self.file_out.write('+')

    def dec(self):
        self.file_out.write('-')

    def dot(self):
        self.file_out.write('.')

    def comma(self):
        self.file_out.write(',')

    def do(self, args):
        for operation in args:
            if isinstance(operation, str):
                if operation in self.node_to_func:
                    self.node_to_func[operation]()
                if operation in self.node_to_func_def:
                    self.compile(self.node_to_func_def[operation])
            elif isinstance(operation, list):
                self.compile(operation)

    def loop(self, args):
        self.file_out.write('[')
        self.do(args)
        self.file_out.write(']')

    def define(self, args):
        head, parenthesis, list_of_commands, *tail = args
        commands = []
        for command in list_of_commands:
            commands.append(command)

        self.node_to_func_def[head] = commands

    def add(self, args):
        times = args[0]
        for i in range(int(times)):
            self.file_out.write('+')

    def sub(self, args):
        times = args[0]
        for i in range(int(times)):
            self.file_out.write('-')

    def do_after(self, args):
        head, *tail = args
        another_tail = []
        for x in tail:
            if isinstance(x, list):
                for k in x:
                    another_tail.append(['do', k, head])
            else:
                another_tail.append(x)
        another_tail.insert(0, 'do')
        self.compile(another_tail)


    def do_before(self, args):
        head, *tail = args
        another_tail = []
        for x in tail:
            if isinstance(x, list):
                for k in x:
                    another_tail.append(['do', head, k])
            else:
                another_tail.append(x)
        another_tail.insert(0, 'do')
        self.compile(another_tail)

    def compile(self, commands=None):
        if commands is None:
            commands = self.ast

        head, *tail = commands

        if head in self.node_to_func:
            self.node_to_func[head]()
        elif head in self.node_to_func_with_args:
            self.node_to_func_with_args[head](tail)

    def __init__(self, ast, file_out):
        self.file_out = open(file_out, "w")
        self.ast = ast

        self.node_to_func = {
            'right': self.right,
            'left': self.left,
            'inc': self.inc,
            'dec': self.dec,
            'print': self.dot,
            'read': self.comma,
        }

        self.node_to_func_with_args = {
            'loop': self.loop,
            'do': self.do,
            'def': self.define,
            'add': self.add,
            'sub': self.sub,
            'do-before': self.do_before,
            'do-after': self.do_after,
        }

        self.node_to_func_def = {}

compiler = Compiler(ast, file_out)
compiler.compile()
