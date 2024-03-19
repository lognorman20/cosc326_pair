import sys
from matplotlib import pyplot as plt

class Ant:
    '''
    An object representing the movement of an ant
    '''
    def __init__(self, dna, num_moves, init_char):
        self.position = (0,0)
        self.positions = [self.position]
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
        return ['N', 'E', 'S', 'W'].index(dir)

    def graph(self):
        '''
        Constructs a graph of the path that the ant has taken
        '''
        # extract x and y values from the coordinates
        x_values, y_values = zip(*self.positions)

        # plot the points and connect them with lines
        plt.plot(x_values, y_values, marker='o')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Continuous Path of Points')
        plt.grid(True)
        
        # give padding in the graph
        plt.xlim(min(x_values) - 1, max(x_values) + 1)
        plt.ylim(min(y_values) - 1, max(y_values) + 1)

        # annotate the start and end points
        start_point = self.positions[0]
        end_point = self.positions[-1]
        plt.annotate('Start', start_point, textcoords="offset points", xytext=(0,10), ha='center')
        plt.annotate('End', end_point, textcoords="offset points", xytext=(0,10), ha='center')
        plt.show()

    def move(self):
        '''
        Simulates the movement of a given ant from its input DNA and first char 
        @return - a tuple of the final position after moving
        '''
        DIR_CHANGES = {
            'N': (0, 1),
            'E': (1, 0),
            'S': (0, -1),
            'W': (-1, 0)
        }

        while self.num_moves > 0:
            # get the char of the position the ant is currently at
            curr_state = self.board.get(self.position, self.init_state)
            dir_idx = self.get_idx(self.curr_dir)
            next_dir = self.dna[curr_state][0][dir_idx]
            set_state = self.dna[curr_state][1][dir_idx]

            # set the state of the current space
            self.board[self.position] = set_state

            # go to the new position
            change = DIR_CHANGES[next_dir]
            self.position = (self.position[0] + change[0], self.position[1] + change[1])

            # maintain a log of positions for graphing
            self.positions.append(self.position)

            # update ant state
            self.curr_dir = next_dir
            self.num_moves -= 1

        return self.position

class AntSimulator:
    '''
    An environment to run the simulation of the movement of an ant.
    '''
    def __init__(self, file):
        self.file = file
        self.ants = []

    def simulate(self):
        '''
        Parses the input file and prints an output of the simulated ant movement
        '''
        # read all the lines from the input file into an array
        lines = [line.strip() for line in self.file.readlines()]
        # structure is { character : [[direction instructions], [states to set]] }
        dna = {}
        num_moves = None
        first_char = None
        for line in lines:
            # base case: newline
            if not line:
                continue
            # case one: the line contains the number of steps
            elif all(c.isdigit() or c.isspace() for c in line):
                num_moves = int(line)
                ant = Ant(dna, num_moves, first_char)
                output_pos = ant.move()
                self.ants.append(ant)
                
                # print the final position of the ant after moving
                print(num_moves)
                print('#', output_pos[0], output_pos[1], '\n')

                # reset ant data
                first_char = None
                num_moves = None
                dna.clear()
                continue
            # case two: the line is a comment
            elif line[0] == '#':
                # print the comment
                print(line)
                continue

            # case three: the line is DNA for the ant
            print(line)
            init_char, dirs, states = line.split()
            first_char = init_char if not first_char else first_char
            dna[init_char] = [dirs, states]

    def visualize(self):
        '''
        Creates a graph for every ant in the simulator showing its path
        '''
        for ant in self.ants:
            ant.graph()

# run the simulation
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Please pass in an input file')
    else:
        try:
            filename = sys.argv[1]
            with open(filename, 'r') as file:
                simulator = AntSimulator(file)
                simulator.simulate()
                simulator.visualize()
            file.close()
        except IndexError:
            print("Usage: python main.py <filename>")
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except IOError:
            print(f"Error reading file '{filename}'.")
