import sys
from matplotlib import pyplot as plt

class Ant:
    '''
    An object representing the movement of an ant
    '''
    def __init__(self, dna, num_moves, init_char):
        self.position = (0, 0)
        self.positions = [self.position]
        self.directionHistory = ['N']
        self.bounds = [0, 0, 0, 0] # maxX, maxY, minX, minY
        self.numMovesWhenPushedBound = [[],[],[],[]] 
        self.curr_dir = 'N'
        self.init_state = init_char
        self.dna = dna
        self.num_moves = num_moves
        self.board = {(0, 0): init_char}

    DIR_CHANGES = {
        'N': (0, 1),
        'E': (1, 0),
        'S': (0, -1),
        'W': (-1, 0)
    }

    @staticmethod
    def get_idx(dir):
        '''
        Gets the index of a cardinal direction in the array ['N','E','S','W']
        @return - an integer for the index if successful, else -1
        '''
        return ['N', 'E', 'S', 'W'].index(dir)
    
    @staticmethod
    def getPositionChange(moves):
        '''
        Given a list of moves (N, E, S, W characters), this function returns the change
        in position that would result from following the moves in order.
        '''
        x, y = 0, 0
        for positionChange in (Ant.DIR_CHANGES[move] for move in moves):
            x += positionChange[0]
            y += positionChange[1]
        return (x, y)

    def fastFoward(self, loopLen):
        '''
        Given the number of steps back from the current position that the loop starts,
        this function calculates and sets the final position of the ant if it were to
        repeat the loop until running out of moves.
        '''
        numExtraMoves = self.num_moves % loopLen
        numFullLoops = int((self.num_moves - numExtraMoves) / loopLen)
        fullLoopChange = Ant.getPositionChange(self.directionHistory[-loopLen:])
        extraMovesChange = Ant.getPositionChange(self.directionHistory[-loopLen:-(loopLen-numExtraMoves)])
        self.position = (self.position[0] + fullLoopChange[0] * numFullLoops + extraMovesChange[0],
                         self.position[1] + fullLoopChange[1] * numFullLoops + extraMovesChange[1])
        self.num_moves = 0

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
        plt.annotate('Start', start_point,
                     textcoords="offset points", xytext=(0, 10), ha='center')
        plt.annotate('End', end_point, textcoords="offset points",
                     xytext=(0, 10), ha='center')
        plt.show()

    def findHighwayLoops(self):
        '''
        Detects highways (loops that result in the ant moving in a straight line away from the origin)
        This method records the maximum and minimum x and y values that the ant has reached, which it uses
        to detect when the ant is moving away from the origin.
        Returns the length of the loop if one is found, else None.
        '''
        x, y = self.position
        for i, coord in enumerate([x,y,-x,-y]):
            if coord > self.bounds[i]:
                self.bounds[i] = coord 
                self.numMovesWhenPushedBound[i].append(self.num_moves)
                while (self.numMovesWhenPushedBound[i][0]-self.num_moves) > (len(self.directionHistory) / 2):
                    self.numMovesWhenPushedBound[i].pop(0)
                for numMovesAtPush in reversed(self.numMovesWhenPushedBound[i][:-1]):
                    stepsBack = numMovesAtPush - self.num_moves
                    if all((self.directionHistory[-1-stepsBack-j] == self.directionHistory[-1-j]) for j in range(0, stepsBack)):
                        return stepsBack
        return None

    def findLoops(self):
        '''
        Searches for different types of loop.
        Returns the length of the loop if one is found, else None.
        '''
        return self.findHighwayLoops()

    def move(self):
        '''
        Simulates the movement of a given ant from its input DNA and first char 
        @return - a tuple of the final position after moving
        '''

        while self.num_moves > 0:
            # get the char of the position the ant is currently at

            loopLen = self.findLoops()
            if loopLen != None and True:
                print("Fast fowarding...")
                self.fastFoward(loopLen)
            else:
                curr_state = self.board.get(self.position, self.init_state)
                dir_idx = Ant.get_idx(self.curr_dir)
                next_dir = self.dna[curr_state][0][dir_idx]
                set_state = self.dna[curr_state][1][dir_idx]

                # set the state of the current space
                self.board[self.position] = set_state

                # go to the new position
                change = Ant.DIR_CHANGES[next_dir]
                self.position = (
                    self.position[0] + change[0], self.position[1] + change[1])

                # maintain a log of positions for graphing
                self.positions.append(self.position)
                # self.positions.append(self.position)

                # update ant state
                self.curr_dir = next_dir
                self.directionHistory.append(self.curr_dir)
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
        # except IndexError:
        #     print("Usage: python main.py <filename>")
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except IOError:
            print(f"Error reading file '{filename}'.")
