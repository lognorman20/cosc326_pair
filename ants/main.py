import sys
from matplotlib import pyplot as plt
from collections import deque
from itertools import islice

class AntState:
    def __init__(self, direction, colorSet, bounds, position):
        self.direction = direction
        self.colorSet = colorSet
        self.bounds = bounds
        self.position = position

class Ant:
    '''
    An object representing the movement of an ant
    '''
    def __init__(self, dna, num_moves, init_char):
        self.position = (0, 0)
        self.positions = [self.position]
        self.curr_dir = 'N'
        self.init_state = init_char
        self.dna = dna
        self.num_moves = num_moves
        self.board = {(0, 0): init_char}
        self.doLoopDetectionAtNumMoves = num_moves - 1 
        self.loopDetectionInterval = 2

        # For loop detection:
        self.prevStates = deque(maxlen=10000) 
        # self.directionHistory = ['N']
        # self.colorHistory = [init_char]
        self.bounds = [0, 0, 0, 0] # maxX, maxY, minX, minY
        # self.boundsHistory = [[],[],[],[]] # maxX, maxY, minX, minY. The elements in each array is the num_moves of the move which pushed the bound

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
        # fullLoopChange = Ant.getPositionChange(direction for direction in self.directionHistory[-loopLen:-1])
        fullLoopChange = (self.prevStates[-1].position[0] - self.prevStates[-1-loopLen].position[0], self.prevStates[-1].position[1] - self.prevStates[-1-loopLen].position[1])
        # extraMovesChange = Ant.getPositionChange(self.directionHistory[-loopLen:-(loopLen-numExtraMoves)])
        extraMovesChange = (self.prevStates[-1-loopLen+numExtraMoves].position[0] - self.prevStates[-1-loopLen].position[0], self.prevStates[-1-loopLen+numExtraMoves].position[1] - self.prevStates[-1-loopLen].position[1])
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

    # def findHighwayLoops(self):
    #     '''
    #     Detects highways (loops that result in the ant moving in a straight line away from the origin)
    #     This method records the maximum and minimum x and y values that the ant has reached, which it uses
    #     to detect when the ant is moving away from the origin.
    #     Returns the length of the loop if one is found, else None.
    #     '''
    #     x, y = self.position
    #     for i, coord in enumerate([x,y,-x,-y]):
    #         if coord > self.bounds[i]:
    #             self.bounds[i] = coord 
    #             self.numMovesWhenPushedBound[i].append(self.num_moves)
    #             while (self.numMovesWhenPushedBound[i][0]-self.num_moves) > (len(self.directionHistory) / 2):
    #                 self.numMovesWhenPushedBound[i].pop(0)
    #             for numMovesAtPush in reversed(self.numMovesWhenPushedBound[i][:-1]):
    #                 stepsBack = numMovesAtPush - self.num_moves
    #                 if all((self.directionHistory[-1-stepsBack-j] == self.directionHistory[-1-j]) for j in range(0, stepsBack)):
    #                     return stepsBack
    #     return None

    @staticmethod
    def doBoundsIntersect(bounds1, bounds2):
        '''
        Given two sets of bounds, this function returns whether the two sets intersect at all (rectangle intersection)
        '''
        return not (bounds1[0] < bounds2[2] or bounds1[2] > bounds2[0] or bounds1[1] < bounds2[3] or bounds1[3] > bounds2[1])
    
    @staticmethod
    def calculateBounds(positions):
        '''
        Given a list of positions, this function calculates the bounds of the positions.
        '''
        numPos = len(positions)
        maxX = max(position[0] for position in positions)
        maxY = max(position[1] for position in positions)
        minX = min(position[0] for position in positions)
        minY = min(position[1] for position in positions)
        return [maxX, maxY, minX, minY]
    
    def detectHighwayLoop(self, loopLen):
        psLength = len(self.prevStates)
        latestLoopBounds = Ant.calculateBounds([prevState.position for prevState in islice(self.prevStates, psLength - loopLen, psLength)])
        currentLoopIndex = psLength - loopLen - 1
        while (currentLoopIndex > loopLen*2 and self.detectLoop(psLength-currentLoopIndex,loopLen)):
            prevBounds = self.prevStates[currentLoopIndex].bounds
            if (not Ant.doBoundsIntersect(latestLoopBounds, prevBounds)):
                print("It's a highway!")
                print("Loop length: ", loopLen)
                return True
            currentLoopIndex -= loopLen
        return False

    def detectStationaryLoop(self, loopLen):
        return self.prevStates[-loopLen].position == self.prevStates[-2*loopLen].position
    
    def detectLoop(self, stepsBack, loopLen):
        '''
        Do the [loopLen] moves ending [stepsBack] moves ago match the [loopLen] moves that came before them?
        '''
        for i in range(0, loopLen):
            if (self.prevStates[-1-stepsBack-i].direction != self.prevStates[-1-stepsBack-i-loopLen].direction or
               self.prevStates[-1-stepsBack-i].colorSet != self.prevStates[-1-stepsBack-i-loopLen].colorSet):
                return False
        return True

    def findLoops(self):
        '''
        Searches for different types of loop.
        Returns the length of the loop if one is found, else None.
        '''
        for i in range(1, int(len(self.prevStates)/2)):
            if (self.detectLoop(0, i) and (self.detectStationaryLoop(i) or self.detectHighwayLoop(i))):
                return i
        return None


    def move(self):
        '''
        Simulates the movement of a given ant from its input DNA and first char 
        @return - a tuple of the final position after moving
        '''

        while self.num_moves > 0:
            # get the char of the position the ant is currently at

            if (self.num_moves == self.doLoopDetectionAtNumMoves):
                loopLen = self.findLoops()
                if loopLen != None:
                    print("Fast fowarding...")
                    self.fastFoward(loopLen)
                    break
                self.loopDetectionInterval *= 1.2
                self.doLoopDetectionAtNumMoves = self.num_moves - int(self.loopDetectionInterval)
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

            newBounds = [0] * 4
            newBounds[0] = max(self.position[0], self.bounds[0])
            newBounds[1] = max(self.position[1], self.bounds[1])
            newBounds[2] = min(self.position[0], self.bounds[2])
            newBounds[3] = min(self.position[1], self.bounds[3])
            self.bounds = newBounds

            
            self.num_moves -= 1
            self.prevStates.append(AntState(self.curr_dir, set_state, newBounds, self.position))

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
