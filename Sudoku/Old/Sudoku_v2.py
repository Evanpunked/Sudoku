import datetime

# Singles in box
# Hidden Singles in row/column/box
# Values locked to row/column in box
# Pairs in row/column/box
# Triples in row/column/box
# Quads in row/column/box
# Hidden Pairs in row/column/box
# Hidden Triples/Quads in row/column/box (rare)
# X-Wing
# Swordfish

class Cell:
    def __init__(self, value = None):
        # Initialize possible values from 1 to 9
        self.possibleValues = [i for i in range(1,10)]
        
        # Initialize value.
        self.setValue(value)

    def setValue(self, value):
        # Set value if a valid number from 1 to 9.
        # Otherwise, set to 0, which is used to define a blank sqare
        if value in range(1,10):
            self.value = value
            self.possibleValues = []
        else:
            self.value = 0
        return
    
    def removePossibleValue(self, value):
        if value in self.possibleValues:
            self.possibleValues.remove(value)
        return

    def addPossibleValue(self, value):
        if value in range(1,10) and value not in self.possibleValues:
            self.possibleValues.append(value)
        return

class Board:
    def __init__(self, filePath):
        self.board = loadBoard(filePath)
        self._board = []
        for i in range(0,9):
            row = []
            for j in range(0,9):
                row.append(Cell(self.board[i][j]))
            self._board.append(row)

        for i in range(0,9):
            for j in range(0,9):
                self.removePV(i, j)

    def removePV(self, row, column):
        self.removePV_Row(row, column)
        self.removePV_Column(row, column)
        self.removePV_Box(row, column)

    def removePVOptimized(self, row, column):
        x = 3 * (row/3)
        y = 3 * (column/3)
        value = self._board[row][column].value

        for i in range(0,9):
            self._board[row][i].removePossibleValue(value)
            self._board[i][column].removePossibleValue(value)
            self._board[x + (i/3)][y + (i%3)].removePossibleValue(value)
        
    def removePV_Row(self, row, column):
        value = self._board[row][column].value
        for j in range(0, 9):
            self._board[row][j].removePossibleValue(value)
        return

    def removePV_Column(self, row, column):
        value = self._board[row][column].value
        for i in range(0, 9):
            self._board[i][column].removePossibleValue(value)
        return

    def removePV_Box(self, row, column):
        x = 3 * (row/3)
        y = 3 * (column/3)

        value = self._board[row][column].value
        
        for i in range(x,x+3):
            for j in range(y,y+3):
                self._board[i][j].removePossibleValue(value)
        return

class ElegantSolver:
    def __init__(self, filePath):
        # Load in board, and time how long it takes to solve.
        self.board = Board(filePath)

    def setValue(self, value, i, j):
        self.board._board[i][j].setValue(value)
        self.board.board[i][j] = value
        self.board.removePV(i,j)
        
    def solve(self):
        running = True
        while running:
            result3 = self.double()
            result4 = self.hiddenDouble()
            result1 = self.single()
            result2 = self.hiddenSingle()
            running = (result1 or result2) and result3 and result4
            #running = self.single() or self.hiddenSingle() or self.double()
            
        solvedBoard, result = SmartBruteForce(self.board)

        return solvedBoard, result

    def single(self):
        board = self.board._board
        found = False
        for i in range(0,9):
            for j in range(0,9):
                if len(board[i][j].possibleValues) is 1:
                    found = True
                    self.setValue(board[i][j].possibleValues[0], i, j)

        return found
    
    def hiddenSingle(self):
        numberCount = [(0, []) for value in range(0,9)]
        board = self.board._board
        found = False
        
        # Find single in row
        for i in range(0,9):
            for j in range(0,9):
                for value in board[i][j].possibleValues:
                    count, location = numberCount[value - 1]
                    count += 1
                    location.append((i, j))
                    numberCount[value - 1] = (count, location)
            for value in range(1,10):
                if numberCount[value - 1][0] is 1:
                    (x, y) = numberCount[value - 1][1][0]
                    self.setValue(value, x, y)
                    found = True
            numberCount = [(0, []) for value in range(0,9)]

        numberCount = [(0, []) for value in range(0,9)]
        
        # Find single in column
        for j in range(0,9):
            for i in range(0,9):
                for value in board[i][j].possibleValues:
                    count, location = numberCount[value - 1]
                    count += 1
                    location.append((i, j))
                    numberCount[value - 1] = (count, location)
            for value in range(1,10):
                if numberCount[value - 1][0] is 1:
                    (x, y) = numberCount[value - 1][1][0]
                    self.setValue(value, x, y)
                    found = True
            numberCount = [(0, []) for value in range(0,9)]

        numberCount = [(0, []) for value in range(0,9)]
        
        # Find single in box
        for i in range(0,3):
            for j in range(0,3):
                for k in range(0,3):
                    for l in range(0,3):
                        for value in board[i*3 + k][j*3 +l].possibleValues:
                            count, location = numberCount[value - 1]
                            count += 1
                            location.append((i*3 + k, j*3 +l))
                            numberCount[value - 1] = (count, location)
                for value in range(1,10):
                    if numberCount[value - 1][0] is 1:
                        (x, y) = numberCount[value - 1][1][0]
                        self.setValue(value, x, y)
                        found = True
                numberCount = [(0, []) for value in range(0,9)]   
        return found

    def double(self):
        board = self.board._board
        found = False
        
        doubles = []
        # Find double in row
        for i in range(0,9):
            for j in range(0,9):
                # Append any cell with only 2 possible values
                if len(board[i][j].possibleValues) is 2:
                    doubles.append(board[i][j])
            if len(doubles) > 1:
                for k in range(0, len(doubles)):
                    for l in range(k + 1, len(doubles)):
                        if (doubles[k].possibleValues[0] == doubles[l].possibleValues[0] and
                            doubles[k].possibleValues[1] == doubles[l].possibleValues[1]):
                            value1 = doubles[k].possibleValues[0]
                            value2 = doubles[k].possibleValues[1]
                            for column in range(0, 9):
                                board[i][column].removePossibleValue(value1)
                                board[i][column].removePossibleValue(value2)
                            doubles[k].addPossibleValue(value1)
                            doubles[k].addPossibleValue(value2)
                            doubles[l].addPossibleValue(value1)
                            doubles[l].addPossibleValue(value2)
                            found = True
            doubles = []

        # Find double in column
        for j in range(0,9):
            for i in range(0,9):
                # Append any cell with only 2 possible values
                if len(board[i][j].possibleValues) is 2:
                    doubles.append(board[i][j])
            if len(doubles) > 1:
                for k in range(0, len(doubles)):
                    for l in range(k + 1, len(doubles)):
                        if (doubles[k].possibleValues[0] == doubles[l].possibleValues[0] and
                            doubles[k].possibleValues[1] == doubles[l].possibleValues[1]):
                            value1 = doubles[k].possibleValues[0]
                            value2 = doubles[k].possibleValues[1]
                            for row in range(0, 9):
                                board[row][j].removePossibleValue(value1)
                                board[row][j].removePossibleValue(value2)
                            doubles[k].addPossibleValue(value1)
                            doubles[k].addPossibleValue(value2)
                            doubles[l].addPossibleValue(value1)
                            doubles[l].addPossibleValue(value2)
                            found = True
            doubles = []

        # Find double in 3x3 box
        for i in range(0,3):
            for j in range(0,3):
                for k in range(0,3):
                    for l in range(0,3):
                        if len(board[i*3 + k][j*3 + l].possibleValues) is 2:
                            doubles.append(board[i*3 + k][j*3 + l])
                if len(doubles) > 1:
                    for k in range(0, len(doubles)):
                        for l in range(k + 1, len(doubles)):
                            if (doubles[k].possibleValues[0] == doubles[l].possibleValues[0] and
                                doubles[k].possibleValues[1] == doubles[l].possibleValues[1]):
                                value1 = doubles[k].possibleValues[0]
                                value2 = doubles[k].possibleValues[1]
                                for row in range(0, 3):
                                    for column in range(0,3):
                                        board[i*3 + row][j*3 + column].removePossibleValue(value1)
                                        board[i*3 + row][j*3 + column].removePossibleValue(value2)
                                doubles[k].addPossibleValue(value1)
                                doubles[k].addPossibleValue(value2)
                                doubles[l].addPossibleValue(value1)
                                doubles[l].addPossibleValue(value2)
                                found = True
                doubles = []
        return found

    def hiddenDouble(self):
        numberCount = [(0, []) for value in range(0,9)]
        doubles = []
        board = self.board._board
        found = False
        
        # Find double in row
        for i in range(0,9):
            for j in range(0,9):
                for value in board[i][j].possibleValues:
                    count, location = numberCount[value - 1]
                    count += 1
                    location.append((i, j))
                    numberCount[value - 1] = (count, location)
            for value in range(1,10):
                if numberCount[value - 1][0] is 2:
                    doubles.append((value,numberCount[value-1][1]))
            if len(doubles) > 1:
                for k in range(0, len(doubles)):
                    for l in range(k + 1, len(doubles)):
                        if (doubles[k][1][0] == doubles[l][1][0] and
                            doubles[k][1][1] == doubles[l][1][1]):
                            x1 = doubles[k][1][0][0]
                            x2 = doubles[k][1][1][0]
                            y1 = doubles[k][1][0][1]
                            y2 = doubles[k][1][1][1]
                            value1 = doubles[k][0]
                            value2 = doubles[l][0]
                            for value in range(0, 9):
                                board[x1][y1].removePossibleValue(value)
                                board[x2][y2].removePossibleValue(value)
                            board[x1][y1].addPossibleValue(value1)
                            board[x1][y1].addPossibleValue(value2)
                            board[x2][y2].addPossibleValue(value1)
                            board[x2][y2].addPossibleValue(value2)
                            found = True
            numberCount = [(0, []) for value in range(0,9)]
            doubles = []

        numberCount = [(0, []) for value in range(0,9)]
        doubles = []
        
        # Find double in column
        for j in range(0,9):
            for i in range(0,9):
                for value in board[i][j].possibleValues:
                    count, location = numberCount[value - 1]
                    count += 1
                    location.append((i, j))
                    numberCount[value - 1] = (count, location)
            for value in range(1,10):
                if numberCount[value - 1][0] is 2:
                    doubles.append((value,numberCount[value-1][1]))
            if len(doubles) > 1:
                for k in range(0, len(doubles)):
                    for l in range(k + 1, len(doubles)):
                        if (doubles[k][1][0] == doubles[l][1][0] and
                            doubles[k][1][1] == doubles[l][1][1]):
                            x1 = doubles[k][1][0][0]
                            x2 = doubles[k][1][1][0]
                            y1 = doubles[k][1][0][1]
                            y2 = doubles[k][1][1][1]
                            value1 = doubles[k][0]
                            value2 = doubles[l][0]
                            for value in range(0, 9):
                                board[x1][y1].removePossibleValue(value)
                                board[x2][y2].removePossibleValue(value)
                            board[x1][y1].addPossibleValue(value1)
                            board[x1][y1].addPossibleValue(value2)
                            board[x2][y2].addPossibleValue(value1)
                            board[x2][y2].addPossibleValue(value2)
                            found = True
            numberCount = [(0, []) for value in range(0,9)]
            doubles = []

        numberCount = [(0, []) for value in range(0,9)]
        doubles = []
        
        # Find double in box
        for i in range(0,3):
            for j in range(0,3):
                for k in range(0,3):
                    for l in range(0,3):
                        for value in board[i*3 + k][j*3 +l].possibleValues:
                            count, location = numberCount[value - 1]
                            count += 1
                            location.append((i*3 + k, j*3 +l))
                            numberCount[value - 1] = (count, location)
                for value in range(1,10):
                    if numberCount[value - 1][0] is 2:
                        doubles.append((value,numberCount[value-1][1]))
                if len(doubles) > 1:
                    for k in range(0, len(doubles)):
                        for l in range(k + 1, len(doubles)):
                            if (doubles[k][1][0] == doubles[l][1][0] and
                                doubles[k][1][1] == doubles[l][1][1]):
                                x1 = doubles[k][1][0][0]
                                x2 = doubles[k][1][1][0]
                                y1 = doubles[k][1][0][1]
                                y2 = doubles[k][1][1][1]
                                value1 = doubles[k][0]
                                value2 = doubles[l][0]
                                for value in range(0, 9):
                                    board[x1][y1].removePossibleValue(value)
                                    board[x2][y2].removePossibleValue(value)
                                board[x1][y1].addPossibleValue(value1)
                                board[x1][y1].addPossibleValue(value2)
                                board[x2][y2].addPossibleValue(value1)
                                board[x2][y2].addPossibleValue(value2)
                                found = True
                numberCount = [(0, []) for value in range(0,9)]
                doubles = []

        return found
    
def elegantSolverTest():
    # Load in board, and time how long it takes to solve.
    solver1 = ElegantSolver('Sudoku Board 1.txt')
    solver2 = ElegantSolver('Sudoku Board 2.txt')
    solver3 = ElegantSolver('Sudoku Board 3.txt')
    solver4 = ElegantSolver('Sudoku Board 4.txt')
    solver5 = ElegantSolver('Sudoku Board 5.txt')
    solver6 = ElegantSolver('Sudoku Board 6.txt')

    print "\nOriginal Board 1\n"
    printBoard(solver1.board.board)
    print "\nOriginal Board 2\n"
    printBoard(solver2.board.board)
    print "\nOriginal Board 3\n"
    printBoard(solver3.board.board)
    print "\nOriginal Board 4\n"
    printBoard(solver4.board.board)
    print "\nOriginal Board 5\n"
    printBoard(solver5.board.board)
    print "\nOriginal Board 6\n"
    printBoard(solver6.board.board)
    
    startTime = datetime.datetime.now()
    
    startTime1 = datetime.datetime.now()
    solvedBoard1, result = solver1.solve()
    endTime1 = datetime.datetime.now()

    startTime2 = datetime.datetime.now()
    solvedBoard2, result = solver2.solve()
    endTime2 = datetime.datetime.now()

    startTime3 = datetime.datetime.now()
    solvedBoard3, result = solver3.solve()
    endTime3 = datetime.datetime.now()

    startTime4 = datetime.datetime.now()
    solvedBoard4, result = solver4.solve()
    endTime4 = datetime.datetime.now()

    startTime5 = datetime.datetime.now()
    solvedBoard5, result = solver5.solve()
    endTime5 = datetime.datetime.now()
    
    startTime6 = datetime.datetime.now()
    solvedBoard6, result = solver6.solve()
    endTime6 = datetime.datetime.now()
    
    endTime = datetime.datetime.now()

    # Calculate the difference between the start and end time
    diffTime = endTime - startTime
    diffTime1 = endTime1 - startTime1
    diffTime2 = endTime2 - startTime2
    diffTime3 = endTime3 - startTime3
    diffTime4 = endTime4 - startTime4
    diffTime5 = endTime5 - startTime5
    diffTime6 = endTime6 - startTime6
    
    # Get the time in seconds
    time = float(diffTime.seconds) + float(diffTime.microseconds)/float(1000000)
    time1 = float(diffTime1.seconds) + float(diffTime1.microseconds)/float(1000000)
    time2 = float(diffTime2.seconds) + float(diffTime2.microseconds)/float(1000000)
    time3 = float(diffTime3.seconds) + float(diffTime3.microseconds)/float(1000000)
    time4 = float(diffTime4.seconds) + float(diffTime4.microseconds)/float(1000000)
    time5 = float(diffTime5.seconds) + float(diffTime5.microseconds)/float(1000000)
    time6 = float(diffTime6.seconds) + float(diffTime6.microseconds)/float(1000000)
    
    # Display information to the user.
    print time
    print ''
    
    print time1
    print "\nOriginal Board 1\n"
    printBoard(solver1.board.board)
    print "\nSolved Board 1\n"
    printBoard(solvedBoard1)

    print time2
    print "\nOriginal Board 2\n"
    printBoard(solver2.board.board)
    print "\nSolved Board 2\n"
    printBoard(solvedBoard2)

    print time3
    print "\nOriginal Board 3\n"
    printBoard(solver3.board.board)
    print "\nSolved Board 3\n"
    printBoard(solvedBoard3)

    print time4
    print "\nOriginal Board 4\n"
    printBoard(solver4.board.board)
    print "\nSolved Board 4\n"
    printBoard(solvedBoard4)

    print time5
    print "\nOriginal Board 5\n"
    printBoard(solver5.board.board)
    print "\nSolved Board 5\n"
    printBoard(solvedBoard5)

    print time6
    print "\nOriginal Board 6\n"
    printBoard(solver6.board.board)
    print "\nSolved Board 6\n"
    printBoard(solvedBoard6)

    print 'Board 1'
    smartSolveBoard('Sudoku Board 1.txt')
    print 'Board 2'
    smartSolveBoard('Sudoku Board 2.txt')
    print 'Board 3'
    smartSolveBoard('Sudoku Board 3.txt')
    print 'Board 4'
    smartSolveBoard('Sudoku Board 4.txt')
    print 'Board 5'
    smartSolveBoard('Sudoku Board 5.txt')
    print 'Board 6'
    smartSolveBoard('Sudoku Board 6.txt')

    # Test with single, hidden single
    # Board 1: 0.082, 0.413
    # Board 2: 0.001, 0.000
    # Board 3: 4.632, 4.669
    # Board 4: 0.002, 9.183
    # Board 5: 0.001, 0.424
    # Board 6: 0.003, 0.019

    # Test with single, hidden single, double
    # Board 1: 0.002, 0.409
    # Board 2: 0.000, 0.000
    # Board 3: 4.626, 4.637
    # Board 4: 0.002, 9.137
    # Board 5: 0.002, 0.419
    # Board 6: 0.003, 0.019

    # Test with single, hiddlen single, double, hidden double
    # Board 1: 0.003, 0.408
    # Board 2: 0.001, 0.000
    # Board 3: 3.789, 4.626
    # Board 4: 0.003, 9.107
    # Board 5: 0.002, 0.418
    # Board 6: 0.005, 0.019
    
def SmartBruteForce(cBoard, board=None):
    if board is None:
        board = cBoard.board

    # Return true if solved.  This will bring the correct board up through the chain of calls.
    if isSolvedBoard(board):
        return board, True
    # If board is not valid, move up the call chain once.
    if not isValidBoard(board):
        return board, False

    # Find the first blank space from the top left
    x, y = findBlank(board)

    # Create a copy of board to be possed down the chain
    newBoard = [[board[i][j] for j in range(0,9)] for i in range(0,9)]

    for value in cBoard._board[x][y].possibleValues:
        
        # Place a value in the empty spot and go to the next spot.
        newBoard[x][y] = value
        resultBoard, result = SmartBruteForce(cBoard, newBoard)

        # If the call below this found a solved board, bring the solved board up to the next call
        if result is True:
            return resultBoard, result
        # If the call below found an invalid board, replace the current spot with the next value

    # If all values were found to be invalid, go up a call and continue with checking the next value for the previous blank spot
    return board, False

def smartSolveBoard(filePath):
    
    # Load in board, and time how long it takes to solve.
    board = Board(filePath)
    startTime = datetime.datetime.now()
    solvedBoard, result = SmartBruteForce(board)
    endTime = datetime.datetime.now()

    # Calculate the difference between the start and end time
    diffTime = endTime - startTime

    # Get the time in seconds
    time = float(diffTime.seconds) + float(diffTime.microseconds)/float(1000000)

    # Display information to the user.
    print time
    print "\nOriginal Board\n"
    printBoard(board.board)
    print "\nSolved Board\n"
    printBoard(solvedBoard)

    return solvedBoard, result

def loadBoard(filePath):

    # Load 9x9 Sudoku Board
    SudokuFile = open(filePath, 'r')

    board = []
    rawData = SudokuFile.read()
    data = rawData.splitlines()

    # Add each row from the file to the board
    for row in data:
        board.append(row.split(' '))

    # Convert each item from a string to an integer
    for i in range(0,9):
        for j in range(0,9):
            board[i][j] = int(board[i][j])

    # return 9x9 board
    return board

def bruteForce(board):

    # Return true if solved.  This will bring the correct board up through the chain of calls.
    if isSolvedBoard(board):
        return board, True
    # If board is not valid, move up the call chain once.
    if not isValidBoard(board):
        return board, False

    # Find the first blank space from the top left
    x, y = findBlank(board)

    # Create a copy of board to be possed down the chain
    newBoard = [[board[i][j] for j in range(0,9)] for i in range(0,9)]

    for value in range(1,10):
        
        # Place a value in the empty spot and go to the next spot.
        newBoard[x][y] = value
        resultBoard, result = bruteForce(newBoard)

        # If the call below this found a solved board, bring the solved board up to the next call
        if result is True:
            return resultBoard, result
        # If the call below found an invalid board, replace the current spot with the next value

    # If all values were found to be invalid, go up a call and continue with checking the next value for the previous blank spot
    return board, False

def findBlank(board):
    
    # Checks across the row then down for the first blank spot.  
    for i in range(0,9):
        for j in range(0,9):
            if board[i][j] is 0:
                
                # Return the coordinates for the first blank spot
                return i,j
            
    # If no blank spot found, return (-1, -1)
    return -1,-1

def isValidBoard(board):
    
    # Returns true if every row, column, and 3x3 box contains no duplicates
    isValid = checkRows(board) and checkColumns(board) and checkBoxes(board)
    return isValid

def isSolvedBoard(board):
    
    # Check if the board is valid first. If not, then the board cannot be solved.
    if not isValidBoard(board):
        return False

    # Create list of numbers from 1 to 9.
    nums = [i+1 for i in range(0,9)]
    for i in range(0,9):
        for j in range(0,9):
            
            # If any part of the board is blank, then the board is not solved
            if board[i][j] not in nums:
                return False
    return True

def checkRows(board):
    for i in range(0,9):
        
        # Create a list of values from 1 to 9 to be checked later and removed
        nums = [x+1 for x in range(0,9)]
        for j in range(0,9):
            value = board[i][j]
            
            # A value of 0 is used to show a blank square.  If it is 0, do nothing
            if value is not 0:
                
                # If the current value is in the list, then it has not been found.  Remove from the list of nums
                # Otherwise, it has been previously found in the row, and so the board is 
                if value in nums:
                    nums.remove(value)
                else:
                    return False
    return True

def checkColumns(board):
    for i in range(0,9):
        
        # Create a list of values from 1 to 9 to be checked later and removed
        nums = [x+1 for x in range(0,9)]
        for j in range(0,9):
            value = board[j][i]
            
            # A value of 0 is used to show a blank square.  If it is 0, do nothing
            if value is not 0:
                
                # If the current value is in the list, then it has not been found.  Remove from the list of nums
                # Otherwise, it has been previously found in the row, and so the board is 
                if value in nums:
                    nums.remove(value)
                else:
                    return False
    return True

def checkBoxes(board):
    
    # Check each of the 9 3x3 boxes
    for i in range(0,3):
        for j in range(0,3):
            
            # Create a list of values from 1 to 9 to be checked later and removed
            nums = [x+1 for x in range(0,9)]

            # Check each of the 9 values in the box
            for k in range(0,3):
                for l in range(0,3):
                    
                    # i and j represent the box indexes, so 3*i and 3*j represent the value index
                    value = board[3*i + k][3*j + l]

                    # A value of 0 is used to show a blank square.  If it is 0, do nothing
                    if value is not 0:

                        # If the current value is in the list, then it has not been found.  Remove from the list of nums
                        # Otherwise, it has been previously found in the row, and so the board is 
                        if value in nums:
                            nums.remove(value)
                        else:
                            return False
    return True
                    
def printBoard(board):
    output = ""
    for i in range(0,9):
        for j in range(0,9):

            # If value is 0, then add a blank.
            if board[i][j] is 0:
                output += " "

            # Otherwise, display value
            else:
                output += str(board[i][j])

            # Add a new line if at end of row
            if (j + 1) is 9:
                output += "\n"

            # Add a barrier for the 3x3 box at every 3rd column
            elif (j + 1) % 3 is 0:
                output += "|"

            # Add a blank between numbers on screen
            else:
                output += " "
                
        # Add a barrier for every 3rd row
        if (i + 1) % 3 is 0 and i is not 8:
            output += "-----+-----+-----\n"

    # Print output onto screen
    print output
    return output
    
def solveBoard(filePath):

    # Load in board, and time how long it takes to solve.
    board = loadBoard(filePath)
    startTime = datetime.datetime.now()
    solvedBoard, result = bruteForce(board)
    endTime = datetime.datetime.now()

    # Calculate the difference between the start and end time
    diffTime = endTime - startTime

    # Get the time in seconds
    time = float(diffTime.seconds) + float(diffTime.microseconds)/float(1000000)

    # Display information to the user.
    print time
    print "\nOriginal Board\n"
    printBoard(board)
    print "\nSolved Board\n"
    printBoard(solvedBoard)

    return solvedBoard, result

'''
Original Board

5 2 8|4 7 3|1 9 6
9 5 1|6    |4 7 8
7 5 6|9 1 8|2 3 5
-----+-----+-----
3 7 9|2 8 4|5 6 1
8 6 2|7 3  |9 4  
4 1  |5 6 9|7 2 3
-----+-----+-----
1 9 5|3 4 6|8   7
2 4 3|8 5 7|6 1 9
6 8 7|1 9 2|3   5


Solved Board

5 3 9|2 7 6|4 1 8
7 2 8|3 1 4|9 6 5
6 4 1|8 9 5|7 3 2
-----+-----+-----
4 6 2|5 3 9|8 7 1
3 8 5|7 2 1|6 4 9
1 9 7|4 6 8|2 5 3
-----+-----+-----
2 5 6|1 8 7|3 9 4
9 1 3|6 4 2|5 8 7
8 7 4|9 5 3|1 2 6
'''