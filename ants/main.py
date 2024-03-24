import sys, argparse, os
from collections import deque
from itertools import islice
from PIL import Image

class AntState:
    def __init__(self, direction, colorSet, maxRadius, position):
        self.direction = direction
        self.colorSet = colorSet
        self.maxRadius = maxRadius
        self.position = position

class Ant:
    '''
    An object representing the movement of an ant
    '''
    def __init__(self, dna, num_moves, init_char, simpleMode=False):
        self.position = (0, 0)
        self.curr_dir = 'N'
        self.init_state = init_char
        self.dna = {k: (v[0], v[1]) for k, v in dna.items()} # deep copy
        self.num_moves = num_moves
        self.board = {(0, 0): init_char}

        # For loop detection:
        self.prevStates = deque(maxlen=100000) 
        self.maxRadius = 0 

        self.simpleMode = simpleMode
        self.doLoopDetectionAtNumMoves = num_moves - 1 
        self.loopDetectionInterval = 2

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
        fullLoopChange = (self.prevStates[-1].position[0] - self.prevStates[-1-loopLen].position[0], self.prevStates[-1].position[1] - self.prevStates[-1-loopLen].position[1])
        extraMovesChange = (self.prevStates[-1-loopLen+numExtraMoves].position[0] - self.prevStates[-1-loopLen].position[0], self.prevStates[-1-loopLen+numExtraMoves].position[1] - self.prevStates[-1-loopLen].position[1])
        self.position = (self.position[0] + fullLoopChange[0] * numFullLoops + extraMovesChange[0],
                         self.position[1] + fullLoopChange[1] * numFullLoops + extraMovesChange[1])
        self.num_moves = 0



    def detectStationaryLoop(self, loopLen):
        '''
        Given a repeating set of moves of length [loopLen], this function checks if
        the ant is in a stationary loop.
        If the ant repeats the same set of moves and ends up where it started, it
        must go on forever!
        '''
        return self.prevStates[-loopLen].position == self.prevStates[-2*loopLen].position

    def detectHighwayLoop(self, loopLen):
        '''
        Given a repeating set of moves of length [loopLen], this function checks if
        the ant is in a highway loop.
        If the ant repeats the same moves, setting the same colors, and it does this
        until the entire loop is further away from the origin than anything before
        it, its path is unobstructed and it will go on forever! 
        '''
        psLength = len(self.prevStates)
        latestLoopMinRadius = min([prevState.position[0]**2+prevState.position[1]**2 for prevState in islice(self.prevStates, psLength - loopLen, psLength)])
        currentLoopIndex = psLength - loopLen - 1
        while (currentLoopIndex > loopLen*2 and self.detectLoop(psLength-currentLoopIndex,loopLen)):
            prevMaxRadius = self.prevStates[currentLoopIndex].maxRadius
            if (prevMaxRadius < latestLoopMinRadius):
                return True
            currentLoopIndex -= loopLen
        return False
    
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
        Searches for loops in the ant's previous states.
        Returns the length of the loop if one is found, else None.
        '''
        for i in range(1, int(len(self.prevStates)/2)):
            if self.detectLoop(0, i) and (self.detectStationaryLoop(i) or self.detectHighwayLoop(i)):
                return i
        return None
    
    def generateImage(self):
        '''
        Generates an image of the board state
        '''
        # Get the bounds of the board
        minX = min(position[0] for position in self.board.keys())
        minY = min(position[1] for position in self.board.keys())
        maxX = max(position[0] for position in self.board.keys())
        maxY = max(position[1] for position in self.board.keys())
        width = maxX - minX + 1
        height = maxY - minY + 1
        if width > 50000 or height > 50000:
            raise ValueError("Board is too large to generate an image")

        # Mapping characters to colors
        colorOptions = [(255, 45, 85),(76, 217, 100),(88, 86, 214),(255, 149, 0),(255, 204, 0),(255, 59, 48),(90, 200, 250),(0, 122, 255)]
        colorMap = {'w': (255, 255, 255), 'b': (0, 0, 0)}

        img = Image.new('RGB', (width, height), 'white')
        pixels = img.load()
        i = 0
        for x in range(width):
            for y in range(height):
                if (x + minX, y + minY) in self.board:
                    colorKey = self.board[(x + minX, y + minY)]
                    if colorKey not in colorMap:
                        colorMap[colorKey] = colorOptions[i % len(colorOptions)]
                        i += 1
                    pixels[x, height-y-1] = colorMap[colorKey]
        return img 


    def move(self):
        '''
        Simulates the movement of a given ant from its input DNA and first char 
        @return - a tuple of the final position after moving
        '''
        while self.num_moves > 0:
            if not self.simpleMode and self.num_moves == self.doLoopDetectionAtNumMoves:
                loopLen = self.findLoops()
                if loopLen != None:
                    # print("Fast fowarding...")
                    self.fastFoward(loopLen)
                    break
                self.loopDetectionInterval *= 1.2
                self.doLoopDetectionAtNumMoves = self.num_moves - int(self.loopDetectionInterval)
            # get the char of the position the ant is currently at
            curr_state = self.board.get(self.position, self.init_state)
            dir_idx = Ant.get_idx(self.curr_dir)
            next_dir = self.dna[curr_state][0][dir_idx]
            set_state = self.dna[curr_state][1][dir_idx]

            # set the state of the current space
            self.board[self.position] = set_state

            # go to the new position
            change = Ant.DIR_CHANGES[next_dir]
            self.position = (self.position[0] + change[0], self.position[1] + change[1])

            # update ant state
            self.curr_dir = next_dir

            if not self.simpleMode:
                self.maxRadius = max(self.maxRadius, self.position[0]**2 + self.position[1]**2)
                self.prevStates.append(AntState(self.curr_dir, set_state, self.maxRadius, self.position))

            self.num_moves -= 1

        return self.position


class AntSimulator:
    '''
    An environment to run the simulation of the movement of an ant.
    '''

    def __init__(self, file, simpleMode=False):
        self.file = file
        self.ants = []
        self.simpleMode = simpleMode

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
                ant = Ant(dna, num_moves, first_char, self.simpleMode)
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

    def generateImages(self, imageDirectory):
        '''
        Creates an image for every ant's board state
        '''
        for i, ant in enumerate(self.ants):
            try:
                img = ant.generateImage()
                img.save(f"{imageDirectory}/ant_{i}.png")
            except ValueError as e:
                print(f"Ant {i}: {e}", file=sys.stderr)



# run the simulation
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulates the movement of Langton's Ant")
    parser.add_argument('filename', type=str, help="The file containing ant instructions")
    parser.add_argument('-i', '--image_dir', type=str, help="The directory to save the output images to. Specifying this option will disable loop detection and fast forwarding.")
    parser.add_argument('-s', '--simple', action="store_true", help="Disable loop detection and fast forwarding")
    args = parser.parse_args()
    simpleMode = args.simple if args.image_dir == None else True

    simulator = None
    f = None

    try:
        f = open(args.filename, 'r')
    except FileNotFoundError:
        print(f"File '{args.filename}' not found.")
        sys.exit(1)

    if args.image_dir and not os.path.isdir(args.image_dir):
        print(f"No such directory: '{args.image_dir}'")
        sys.exit(1)

    try:
        simulator = AntSimulator(f, simpleMode)
        simulator.simulate()
    except IOError:
        print(f"Error reading file '{args.filename}'.")
        sys.exit(1)

    if args.image_dir:
        simulator.generateImages(args.image_dir)
