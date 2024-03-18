
class Ant:

    def __init__(self, dna, num_moves, init_char):
        self.position = (0,0)
        self.curr_dir = 'N'
        self.init_state = init_char
        self.dna = dna
        self.num_moves = num_moves
        self.board = { (0,0) : init_char }

    def get_idx(self, dir):
        match dir:
            case 'N':
                return 0
            case 'E':
                return 1
            case 'S':
                return 2
            case 'W':
                return 3
            case _:
                return -1

    def move(self):
        while self.num_moves > 0:
            curr_state = self.board[self.position] if self.board[self.position] else self.init_state
            dir_idx = self.get_idx(self.curr_dir)
            next_dir = self.dna[curr_state][0][dir_idx]
            set_state = self.dna[curr_state][1][dir_idx]

            match next_dir:
                case 'N':
                    self.position = (self.position[0], self.position[1] + 1)
                case 'E':
                    self.position = (self.position[0] + 1, self.position[1])
                case 'S':
                    self.position = (self.position[0], self.position[1] - 1)
                case 'W':
                    self.position = (self.position[0] - 1, self.position[1])
                case _:
                    print('INVALID NEXT DIR')
                    return

            self.curr_dir = next_dir
            self.board[self.position] = set_state
            self.num_moves -= 1

        return self.position

class Ants:
    def __init__(self, filename):
        self.filename = filename

    def read_input(self):
        lines = [line.strip() for line in open(self.filename, "r").readlines()]
        dna = {}
        num_moves = None
        first_char = None
        for line in lines:
            if not line:
                ant = Ant(dna, num_moves, first_char)
                output_position = ant.move()
                print(output_position)

                # reset ant data
                first_char = None
                num_moves = None
                dna.clear()
                continue
            elif all(c.isdigit() or c.isspace() for c in line):
                num_moves = int(line)
                print(num_moves)
                continue
            elif line[0] == '#':
                continue

            print(line)
            init_char, dirs, states = line.split()
            first_char = init_char if not first_char else first_char
            dna[init_char] = [dirs, states]


ants = Ants('i0.txt')
ants.read_input()
