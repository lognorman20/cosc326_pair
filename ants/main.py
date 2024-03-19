
class Ant:

    def __init__(self, dna, num_moves, init_char):
        self.position = (0,0)
        self.curr_dir = 'N'
        self.init_state = init_char
        self.dna = dna
        self.num_moves = num_moves
        self.board = { (0,0) : init_char }

    def get_idx(self, dir):
        '''
        Gets the index of a cardinal direction in the array ['N','E','S','W']
        @return - an integer for the index if successful, else -1
        '''
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
                print('FAILED TO GET IDX')
                return -1

    def move(self):
        '''
        Simulates the movement of a given ant from its input DNA and first char 
        @return - a tuple of the final position after moving
        '''
        while self.num_moves > 0:
            curr_state = self.board[self.position] if self.position in self.board else self.init_state
            dir_idx = self.get_idx(self.curr_dir)
            next_dir = self.dna[curr_state][0][dir_idx]
            set_state = self.dna[curr_state][1][dir_idx]

            self.board[self.position] = set_state

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
                    return (-1, -1)

            self.curr_dir = next_dir
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
                continue
            elif all(c.isdigit() or c.isspace() for c in line):
                print(line)

                num_moves = int(line)
                ant = Ant(dna, num_moves, first_char)
                output_pos = ant.move()
                
                # print the final position of the ant after moving
                print('#', output_pos[0], output_pos[1], '\n')

                # reset ant data
                first_char = None
                num_moves = None
                dna.clear()
                continue
            elif line[0] == '#':
                continue

            print(line)
            init_char, dirs, states = line.split()
            first_char = init_char if not first_char else first_char
            dna[init_char] = [dirs, states]


ants = Ants('i0.txt')
ants.read_input()
