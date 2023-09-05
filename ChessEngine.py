'''

This class is responsible for storing all the information about the current state of the chess game. 
It will also be responsible for determining the valid moves. It will also keep a move log. 

'''
# class is a template for objects, def __init__ is necessary, 'self' items belong to each object

class GameState ():
    def __init__ (self):
        #board is 8x8 2d list, and each element has two characters
        #The first character denotes the colour (black or white), the second character represents the piece type
        #The string empty quotes "--" represents an empty space with no piece

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR" ],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP" ],
            ["--", "--", "--", "--", "--", "--", "--", "--" ],
            ["--", "--", "--", "--", "--", "--", "--", "--" ],
            ["--", "--", "--", "--", "--", "--", "--", "--" ],
            ["--", "--", "--", "--", "--", "--", "--", "--" ],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP" ],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR" ]]
        
        
        self.whiteToMove = True
        self.moveLog = []

        self.whiteToCastleRight = True
        self.whiteToCastleLeft = True
        self.blackToCastleRight = True
        self.blackToCastleLeft = True

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.checkMate = False
        self.staleMate = False

        
    '''
    Takes a Move (object) as a parameter and executes it 
    '''    

    def makeMove (self, Move, PromotionChoice=''):

        self.board[Move.startRow][Move.startCol] = "--" #replaces original spot with blank notation      

        if PromotionChoice != '':
            self.board[Move.endRow][Move.endCol] = Move.pieceMoved[0] + PromotionChoice
            print("Promoted")
        else:
            self.board[Move.endRow][Move.endCol] = Move.pieceMoved #replaces end row and col with the place holder of the piece to be moved

        if(Move.enPassant and self.whiteToMove):
            self.board[(Move.endRow)+1][Move.endCol] = '--'
        if(Move.enPassant and not self.whiteToMove):
            self.board[(Move.endRow)-1][Move.endCol] = '--'
                                
        if(Move.leftCastle):
            if(Move.startRow == 0):
                self.board[0][3] = 'bR'
                self.board[0][0] = '--'
            else:
                self.board[7][3] = 'wR'
                self.board[7][0] = '--'

        if(Move.rightCastle):
            if(Move.startRow == 0):
                self.board[0][5] = 'bR'
                self.board[0][7] = '--'
            else:
                self.board[7][5] = 'wR'
                self.board[7][7] = '--'

        self.moveLog.append(Move) #log the move so we can undo it later
        
        self.whiteToMove = not self.whiteToMove #swap players        
        #updated the king's location if moved
        if Move.pieceMoved == 'wK':
            self.whiteKingLocation = (Move.endRow, Move.endCol)
        if Move.pieceMoved == 'bK':
            self.blackKingLocation = (Move.endRow, Move.endCol)


    '''
    Undo the last move made
    '''
    def undoMove (self):
        if len(self.moveLog) == 0:
            pass
        else:
            lastMove = self.moveLog.pop()
            pieceMoved = lastMove.pieceMoved
            pieceCaptured = lastMove.pieceCaptured

            castles = (lastMove.leftCastle, lastMove.rightCastle)
            turns = (self.whiteToMove, not self.whiteToMove)

            #colours flipped for this segment

            if lastMove.enPassant and not self.whiteToMove:
                self.board[(lastMove.endRow)+1][(lastMove.endCol)] = 'bP'
                self.board[lastMove.endRow][lastMove.endCol] = '--'
                self.board[lastMove.startRow][lastMove.startCol] = pieceMoved

            elif lastMove.enPassant and self.whiteToMove:
                self.board[(lastMove.endRow)-1][(lastMove.endCol)] = 'wP'
                self.board[lastMove.endRow][lastMove.endCol] = '--'
                self.board[lastMove.startRow][lastMove.startCol] = pieceMoved

            for castle in castles:
                for turn in turns:

                    if castle: #dealing with a castling move 
                            if lastMove.endCol < 4: #left
                                self.board[lastMove.startRow][lastMove.startCol] = pieceMoved
                                self.board[lastMove.startRow][0] = lastMove.pieceMoved[0] + 'R'

                                if lastMove.pieceMoved[0] == 'w':
                                    self.whiteToCastleLeft = True
                                    self.whiteToCastleRight = True
                                else:
                                    self.blackToCastleLeft = True
                                    self.blackToCastleRight = True
                                for i in range(3):
                                    self.board[lastMove.startRow][i+1] = '--'

                            else: #right
                                self.board[lastMove.startRow][lastMove.startCol] = pieceMoved
                                self.board[lastMove.startRow][7] = lastMove.pieceMoved[0] + 'R'

                                if lastMove.pieceMoved[0] == 'w':
                                    self.whiteToCastleLeft = True
                                    self.whiteToCastleRight = True
                                else:
                                    self.blackToCastleLeft = True
                                    self.blackToCastleRight = True

                                for i in range(2):
                                    self.board[lastMove.startRow][7-(i+1)] = '--'
            else:
                self.board[lastMove.startRow][lastMove.startCol] = pieceMoved
                self.board[lastMove.endRow][lastMove.endCol] = pieceCaptured
    

            self.whiteToMove = not self.whiteToMove #change turns back if a move is undone
            if lastMove.pieceMoved == 'wK':
                self.whiteKingLocation = (lastMove.startRow, lastMove.startCol)
            if lastMove.pieceMoved == 'bK':
                self.blackKingLocation = (lastMove.startRow, lastMove.startCol)

        self.checkMate = False
        self.staleMate = False


    '''
    All moves considering checks
    '''

    def getValidMoves(self):
        #1.) generate all possible moves

        moves = self.getAllPossibleMoves() 
        
        #2.) for each move, make the move

        for i in range(len(moves)-1, -1, -1): #consider all moves starting from the very last move, and work our way backwards
            self.makeMove(moves[i]) #we will make the move
            
            #3.) after we make the move, let's generate all opponent's moves            
            #4.) for each of the opponent's moves see if they attack your king 

            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove

            #5.) if someone attacks your king it is not a valid move

            self.undoMove()

        
        
        return moves
    
    '''
    Determine if the current player is under attack
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    '''
    Determine if the current square is under attack
    '''
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove #switch to opponent's moves
        opponentMoves = self.getAllPossibleMoves() #get all of opponent's move
        self.whiteToMove = not self.whiteToMove #switch back to white

        for move in opponentMoves: #if one of the opponents moves has an ending row and column equal to the row and col passed then that means under attach
            if move.endRow == row and move.endCol == col:
                return True
    
        return False #else if it is not equal then we are safe
            
    def getAllPossibleMoves(self, ):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0] #returns either b or w
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1] #returns the piece type
                    if piece == 'P':
                        self.getPawnMoves(row, col, moves)
                    if piece == 'R':
                        self.getRookMoves(row, col, 0, moves)
                    if piece == 'N':
                        self.getNiteMoves(row, col, moves)
                    if piece == 'B':
                        self.getBishopMoves(row, col, 0, moves)   
                    if piece == 'Q':
                        self.getQueenMoves(row, col, moves)
                    if piece == 'K':  
                        self.getKingMoves(row, col, moves) 
        return moves
    
    '''
    Get all the pawn moves for the pawn located at (row, col) and add these moves to the list
    '''

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove: #white's turn to move
            if row > 0 and self.board[row-1][col] == "--":
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row-2][col] == "--":
                    moves.append(Move((row, col), (row-2, col), self.board))
                else: 
                    pass
            
            if row > 0 and col < 7 and self.board[row-1][col+1] != '--' and self.board[row-1][col+1][0] == 'b':
                moves.append(Move((row, col), (row-1, col+1), self.board))
            if row > 0 and col > 0 and self.board[row-1][col-1] != '--' and self.board[row-1][col-1][0] == 'b':
                moves.append(Move((row, col), (row-1, col-1), self.board))

        elif not self.whiteToMove: #black's turn to move
            if row < 7 and self.board[row+1][col] == "--":
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and self.board[row+2][col] == "--":
                    moves.append(Move((row, col), (row+2, col), self.board))
                else:
                    pass
            
            if row < 7 and col < 7 and self.board[row+1][col+1] != '--' and self.board[row+1][col+1][0] == 'w':
                moves.append(Move((row, col), (row+1, col+1), self.board))
            if row < 7 and col > 0 and self.board[row+1][col-1] != '--' and self.board[row+1][col-1][0] == 'w':
                moves.append(Move((row, col), (row+1, col-1), self.board))
                    
 
    '''
    Checks each direction within the boundaries and iteratives add moves if the position is empty
    '''

    def getRookMoves(self, row, col, iter, moves):
       
        rightCol = col
        leftCol = col
        topRow = row
        botRow = row

        while iter < 8:    
            if rightCol < 7:

                if self.board[row][rightCol+1] == "--":
                    moves.append(Move((row, col), (row, rightCol+1), self.board))
                    rightCol += 1
                elif self.board[row][col][0] != self.board[row][rightCol+1][0]:
                    moves.append(Move((row, col), (row, rightCol+1), self.board))

            if botRow < 7:
                
                if self.board[botRow+1][col] == "--":
                    moves.append(Move((row, col), (botRow+1, col), self.board))
                    botRow += 1
                elif self.board[row][col][0] != self.board[botRow+1][col][0]:
                    moves.append(Move((row, col), (botRow+1, col), self.board))
            
            
            if leftCol > 0:
                
                if self.board[row][leftCol-1] == "--":
                    moves.append(Move((row, col), (row, leftCol-1), self.board))
                    leftCol -= 1
                elif self.board[row][col][0] != self.board[row][leftCol-1][0]:
                    moves.append(Move((row, col), (row, leftCol-1), self.board))
            

            if topRow > 0:
                
                if self.board[topRow-1][col] == "--":
                    moves.append(Move((row, col), (topRow-1, col), self.board))
                    topRow -= 1
                elif self.board[row][col][0] != self.board[topRow-1][col][0]:
                    moves.append(Move((row, col), (topRow-1, col), self.board))
            
            iter += 1
    '''
    Checks all eight possible spots for a Knight to move within the 
    '''

    def getNiteMoves(self, row, col, moves):

        if 7 >=  row-2 >= 0 and 0 <= col+1 <= 7:
            if self.board[row][col][0] != self.board[row-2][col+1][0]:
                moves.append(Move((row, col), (row-2, col+1), self.board))

        if 7 >=  row+1 >= 0 and 0 <= col+2 <= 7:
            if self.board[row][col][0] != self.board[row+1][col+2][0]:
                moves.append(Move((row, col), (row+1, col+2), self.board))

        if 7 >=  row-1 >= 0 and 0 <= col-2 <= 7: 
            if self.board[row][col][0] != self.board[row-1][col-2][0]:
                moves.append(Move((row, col), (row-1, col-2), self.board))
            
        if 7 >=  row+2 >= 0 and 0 <= col+1 <= 7:
            if self.board[row][col][0] != self.board[row+2][col+1][0]:
                moves.append(Move((row, col), (row+2, col+1), self.board))
            
        if 7 >=  row+2 >= 0 and 0 <= col-1 <= 7:
            if self.board[row][col][0] != self.board[row+2][col-1][0]:
                moves.append(Move((row, col), (row+2, col-1), self.board))
            
        if 7 >=  row+1 >= 0 and 0 <= col-2 <= 7: 
            if self.board[row][col][0] != self.board[row+1][col-2][0]:
                moves.append(Move((row, col), (row+1, col-2), self.board))
            
        if 7 >=  row-1 >= 0 and 0 <= col+2 <= 7:
            if self.board[row][col][0] != self.board[row-1][col+2][0]:
                moves.append(Move((row, col), (row-1, col+2), self.board))
            
        if 7 >=  row-2 >= 0 and 0 <= col-1 <= 7:
            if self.board[row][col][0] != self.board[row-2][col-1][0]:
                moves.append(Move((row, col), (row-2, col-1), self.board))

    '''
    Traverse in each diagonol until you can't any further    
    '''

    def getBishopMoves(self, row, col, iter, moves):

        topRightRow, topRightCol = row, col
        topLeftRow, topLeftCol = row, col
        botRightRow, botRightCol = row, col
        botLeftRow, botLeftCol = row, col
        
        while iter < 8:
            if 0 < topRightRow and topRightCol < 7:
                if self.board[topRightRow-1][topRightCol+1] == "--":
                    moves.append(Move((row, col), (topRightRow-1, topRightCol+1), self.board))
                    topRightRow -= 1
                    topRightCol += 1
                elif self.board[row][col][0] != self.board[topRightRow-1][topRightCol+1][0]:
                    moves.append(Move((row, col), (topRightRow-1, topRightCol+1), self.board))
                

            if 0 < topLeftRow and 0 < topLeftCol:
                if self.board[topLeftRow-1][topLeftCol-1] == "--":
                    moves.append(Move((row, col), (topLeftRow-1, topLeftCol-1), self.board))
                    topLeftRow -= 1
                    topLeftCol -= 1
                elif self.board[row][col][0] != self.board[topLeftRow-1][topLeftCol-1][0]:
                    moves.append(Move((row, col), (topLeftRow-1, topLeftCol-1), self.board))

            if botRightRow < 7 and botRightCol < 7:
                if self.board[botRightRow+1][botRightCol+1] == "--":
                    moves.append(Move((row, col), (botRightRow+1, botRightCol+1), self.board))
                    botRightRow += 1
                    botRightCol += 1
                elif self.board[row][col][0] != self.board[botRightRow+1][botRightCol+1][0]:
                    moves.append(Move((row, col), (botRightRow+1, botRightCol+1), self.board))


            if botLeftRow < 7 and botLeftCol > 0:
                if self.board[botLeftRow+1][botLeftCol-1] == "--":
                    moves.append(Move((row, col), (botLeftRow+1, botLeftCol-1), self.board))
                    botLeftRow += 1
                    botLeftCol -= 1
                elif self.board[row][col][0] != self.board[botLeftRow+1][botLeftCol-1][0]:
                    moves.append(Move((row, col), (botLeftRow+1, botLeftCol-1), self.board))          

            iter += 1
        
    '''
    Queen is just the combination of the bishop and rook
    '''

    def getQueenMoves(self, row, col, board):
        self.getBishopMoves(row, col, 0, board)
        self.getRookMoves(row, col, 0, board)

    '''
    King is the combination of the bishop and rook but only to one square
    '''

    def getKingMoves(self, row, col, board):
        self.getBishopMoves(row, col, 7, board)
        self.getRookMoves(row, col, 7, board)

    def enPassant(self, lastMove, board):

        newMoves = []

        if lastMove.pieceMoved[1] == 'P' and abs(lastMove.startRow - lastMove.endRow) == 2: #last move was a pawn of two rows
             if self.whiteToMove and lastMove.endRow == 3 and 0 < lastMove.endCol < 7:
                if(self.board[3][(lastMove.endCol)-1]) == 'wP':
                    newMoves.append(Move((3, lastMove.endCol-1), (2, lastMove.endCol), board, enPassant=True))

            
                if(self.board[3][(lastMove.endCol)+1]) == 'wP':
                    newMoves.append(Move((3, lastMove.endCol+1), (2, lastMove.endCol), board, enPassant=True))  

                if self.whiteToMove and lastMove.endRow == 3 and lastMove.endCol == 7:
                    if(self.board[3][(lastMove.endCol)-1]) == 'wP':
                        newMoves.append(Move((3, lastMove.endCol-1), (2, lastMove.endCol), board, enPassant=True))

                if self.whiteToMove and lastMove.endRow == 3 and lastMove.endCol == 0:
                    if(self.board[3][(lastMove.endCol)+1]) == 'wP':
                        newMoves.append(Move((3, lastMove.endCol+1), (2, lastMove.endCol), board, enPassant=True)) 

        if lastMove.pieceMoved[1] == 'P' and abs(lastMove.startRow - lastMove.endRow) == 2: #last move was a pawn of two rows
             if not self.whiteToMove and lastMove.endRow == 4 and 0 < lastMove.endCol < 7:
                if(self.board[4][(lastMove.endCol)-1]) == 'bP':
                    newMoves.append(Move((4, lastMove.endCol-1), (5, lastMove.endCol), board, enPassant=True))

            
                if(self.board[4][(lastMove.endCol)+1]) == 'bP':
                    newMoves.append(Move((4, lastMove.endCol+1), (5, lastMove.endCol), board, enPassant=True))  

                if not self.whiteToMove and lastMove.endRow == 4 and lastMove.endCol == 7:
                    if(self.board[4][(lastMove.endCol)-1]) == 'bP':
                        newMoves.append(Move((4, lastMove.endCol-1), (5, lastMove.endCol), board, enPassant=True))

                if not self.whiteToMove and lastMove.endRow == 4 and lastMove.endCol == 0:
                    if(self.board[4][(lastMove.endCol)+1]) == 'bP':
                        newMoves.append(Move((4, lastMove.endCol+1), (5, lastMove.endCol), board, enPassant=True)) 

        return newMoves
        
    def castling(self, board):

        newMoves = []

        if self.board[0][0] != 'bR' or self.board[0][4] != 'bK':
            self.blackToCastleLeft = False
        if self.board[0][7] != 'bR'  or self.board[0][4] != 'bK':
            self.blackToCastleRight = False
        if self.board[7][0] != 'wR'  or self.board[7][4] != 'wK':
            self.whiteToCastleLeft = False
        if self.board[7][7] != 'wR'  or self.board[7][4] != 'wK':
            self.whiteToCastleRight = False

        if self.blackToCastleLeft and not self.whiteToMove and self.board[0][1] == '--' and self.board[0][2] == '--' and self.board[0][3] == '--': 
            newMoves.append(Move((0, 4), (0, 2), board, leftCastle=True))
        if self.whiteToCastleLeft and self.whiteToMove and self.board[7][1] == '--' and self.board[7][2] == '--' and self.board[7][3] == '--':
            newMoves.append(Move((7, 4), (7, 2), board, leftCastle=True))
        
        if self.blackToCastleRight and not self.whiteToMove and self.board[0][5] == '--' and self.board[0][6] == '--':
            newMoves.append(Move((0, 4), (0, 6), board, rightCastle=True))
        if self.whiteToCastleRight and self.whiteToMove and self.board[7][5] == '--' and self.board[7][6] == '--':
            newMoves.append(Move((7, 4), (7, 6), board, rightCastle=True))

        return newMoves

class Move():
    # mapys keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, 
                   "5": 3, "6": 2, "7": 1, "8": 0}
    #really cool way of reversing a dictionary
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, 
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant=False, leftCastle=False, rightCastle=False):
        self.leftCastle = leftCastle
        self.rightCastle = rightCastle
        self.enPassant = enPassant
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        if self.pieceMoved == 'wP' and self.endRow == 0:
            self.isPawnPromotion = True
        if self.pieceMoved == 'bP' and self.endRow == 7:
            self.isPawnPromotion = True
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #unique move ID between 0001-7777

    '''
    Overriding the equals method - i.e., two different move objects do not know how to compare eachother
    '''

    def __eq__(self, other):
        if isinstance(other, Move): #check we are comparing Move objects
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        #has potential to look more like chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    