class Ant:
    def __init__(self, char_instructions, num_moves, init_char):
        self.position = (0,0)
        self.prev_dir = 'N'
        self.init_state = init_char
        self.char_instructions = char_instructions
        self.num_moves = num_moves
        self.board = { (0,0) : init_char }
        self.idx = {}

    def move(self):
        return 'moved'

class Ants:
    def __init__(self, filename):
        self.filename = filename

    def read_input(self):
        lines = [line.strip() for line in open(self.filename, "r").readlines()]
        char_instr = {}
        num_moves = None
        first_char = None
        for line in lines:
            if not line:
                ant = Ant(char_instr, num_moves, first_char)
                print(ant.move())

                # reset ant data
                first_char = None
                num_moves = None
                char_instr.clear()
                continue
            elif all(c.isdigit() or c.isspace() for c in line):
                num_moves = int(line)
                continue
            elif line[0] == '#':
                print(line)
                continue

            init_char, dirs, states = line.split()
            first_char = init_char if not init_char else first_char
            # todo: what should we do if the initial direction ('N') isn't in
            # the input?
            char_instr[init_char] = [dirs, states]


ants = Ants('i1.txt')
ants.read_input()
