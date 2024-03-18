
class Ant:
    def __init__(self, num_moves, init_state, char_instr):
        self.coord = (0,0)
        self.prevDir = "S"
        self.direction = "N"
        self.num_moves = num_moves
        self.board = { (0,0) : init_state }
        self.char_instr = char_instr

    def move(self):
        return 'helloooooo'

class Runner:
    def __init__(self, filename):
        self.filename = filename
        self.num_moves = -1
        self.char_instr = {}
        self.init_char = None
        self.ants = []

    def read_file(self):
        lines = [line.strip() for line in open(self.filename, "r").readlines()]
        for line in lines:
            if not line:
                ant = Ant(self.num_moves, self.char_instr, self.init_char)
                self.ants.append(ant)
                self.init_char = None
                self.num_moves = -1
                self.char_instr.clear()

                output = ant.move()
                print(output)
                continue
            elif all(c.isdigit() or c.isspace() for c in line):
                self.num_moves = int(line)
                continue
            elif line[0] == '#':
                print(line)
                continue

            init_char, instrs, states = line.split()
            dir_instrs = {}
            state_instrs = {}
            for i in range(len(instrs)):
                self.init_char = init_char if not self.init_char else self.init_char

                curr = (instrs[i], i)
                N = len(instrs)
                next_idx = (i + 1) % N

                # todo: fix storing duplicates in the case of 'EEEE xx!x'
                dir_instrs[curr] = (instrs[next_idx], next_idx)
                state_instrs[curr] = (states[i], i)

            self.char_instr[init_char] = (dir_instrs, state_instrs)


runner = Runner('i0.txt')
runner.read_file()