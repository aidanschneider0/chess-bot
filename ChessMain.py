'''
This is our main driver file - handles user input and displaying the GameState information object
'''

import pygame as pg
import ChessEngine
import SmartMoveFinder

boardWIDTH = boardHEIGHT = screenHEIGHT = 512
screenWIDTH = boardWIDTH + 192

DIMENSION = 8 #dimensions of a chess board are 8x8
SQ_SIZE = boardHEIGHT // DIMENSION
MAX_FPS = 15 #for animations later on 
IMAGES = {} #directory of images 

'''
Only want to load in images once 
Initiilze a global dictionary of images, this will be called exactly once in the main 
'''

def loadImages():
    pieces = {'wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ'}
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

    #can access images by using key in dictionary

'''
The main driver for our code, this will handle user input and updating the graphics
'''

def main():


    pg.init()
    screen = pg.display.set_mode((screenWIDTH, screenHEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves() #returns a list of valid moves and see if the move made by the user is in this list
    moveMade = False #flag variable for when a move is made

    loadImages() #only doing this once, before the while loop
    running = True
    sqSelected = () #no square is selected initially, keeps track of the last user click (tuple: row, col)
    playerClicks = [] #keep track of the player clicks (two tuples: [(6, 4)], [(4, 4)])
    drawGameState(screen, gs)
    pg.display.flip()
    pg.display.set_caption("Chess!")
    font = pg.font.Font('freesansbold.ttf', 32)

    update = True
    gameOver = False
    playerOne = True #If a Human is playing white, this this will be True. IF an AI is playing, then this will be False
    playerTwo = True #Same as above but for black

    moves_made = {}
    moves_made_counter = 0

    while running:

        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if humanTurn:
                    location = pg.mouse.get_pos() #returns x, y location list -> divide by square size and truncate to find the spot
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE

                if sqSelected == (row, col): #the user clicked the same square twice
                    sqSelected = () #deselects
                    playerClicks = [] #clear what has been selected
                    drawGameState(screen, gs)

                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                    if len(playerClicks) == 1:
                        update = highlight(screen, validMoves, row, col, gs)                        

                    #append both first and second clicks                   

                if len(playerClicks) == 2:

                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    
                    for i in range(len(validMoves)):
                    
                        if move == validMoves[i]:

                            if (moves_made_counter // 2) in moves_made.keys():
                                moves_made[(moves_made_counter // 2)].append(move)
                            else:
                                moves_made[(moves_made_counter // 2)] = [move] 
                            
                            drawMoveLog(screen, pg.font.Font('freesansbold.ttf', 16), moves_made, gs.whiteToMove)
                            moves_made_counter += 1

                            print(move.getChessNotation())
                            if validMoves[i].isPawnPromotion:
                                userInput = input("Please select which piece you would like to promoto to: 'Q', 'R', 'B', 'N': ")
                                promotionPiece = userInput.strip()
                                gs.makeMove(validMoves[i], PromotionChoice=promotionPiece)
                                moveMade = True
                                sqSelected = () #reset user clicks 
                                playerClicks = []
                                
                            else:
                                gs.makeMove(validMoves[i])
                                update = True
                                moveMade = True
                                sqSelected = () #reset user clicks 
                                playerClicks = []
                                break #to allow playerChange after 

                    if not moveMade:
                        drawGameState(screen, gs)
                        playerClicks = [sqSelected]
                        highlight(screen, validMoves, sqSelected[0], sqSelected[1], gs)

            elif event.type == pg.KEYDOWN and len(sqSelected) == 0:
                    if event.key == pg.K_z: #undo when 'z' is pressed
                        print((moves_made_counter // 2)) 
                        print(moves_made.keys())
                        gs.undoMove()
                        moveMade = True

        #AI move finder
        if not gameOver and not humanTurn:
            
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)  
            moves_made[moves_made_counter].append(AIMove) if (moves_made_counter // 2) in moves_made.keys() else [AIMove] 
            drawMoveLog(screen, pg.font.Font('freesansbold.ttf', 16), AIMove.getChessNotation(), moves_made_counter)
            moves_made_counter += 1

            if AIMove.isPawnPromotion:
                gs.makeMove(AIMove, PromotionChoice='Q')
                moveMade = True
                update = True
                sqSelected = () #reset user clicks 
                playerClicks = []
 
            else:
                gs.makeMove(AIMove)
                moveMade = True
                update = True

        if moveMade:

            #SmartMoveFinder.scoreMaterial(gs.board)
            validMoves = gs.getValidMoves()
            if len(gs.moveLog) ==  0:
                pass
            else:
                enPassantMoves = gs.enPassant(gs.moveLog[-1], gs.board)
                if not (gs.whiteToMove and gs.squareUnderAttack(gs.whiteKingLocation[0], gs.whiteKingLocation[1])) and not (not gs.whiteToMove and gs.squareUnderAttack(gs.blackKingLocation[0], gs.blackKingLocation[1])):
                    castlingMoves = gs.castling(gs.board)

            for moves in enPassantMoves:
                validMoves.append(moves)

            for moves in castlingMoves:
                validMoves.append(moves) 
    
                
            if len(validMoves) == 0:
                if gs.whiteToMove and gs.squareUnderAttack(gs.whiteKingLocation[0], gs.whiteKingLocation[1]): #white wins
                    gameOver = gameover(screen, "Black", "White", font, gs)
                elif not gs.whiteToMove and gs.squareUnderAttack(gs.blackKingLocation[0], gs.blackKingLocation[1]): #black wins                 
                    gameOver = gameover(screen, "White", "Black", font, gs)
                else:
                    gameOver = gameover(screen, "Stalemate!", "Black", font, gs)
                    
            moveMade = False 


        clock.tick(MAX_FPS)
        drawGameState(screen, gs)
        if update and not gameOver:
            pg.display.flip()

        if gameOver == True:
            pass
'''
Responsible for all the graphics within the current game state
'''

def drawGameState(screen, gs):
    drawBoard(screen) #draw squares on the board
    drawPieces(screen, gs.board) #draw pieces on top of those squares

def drawBoard(screen):
    colourList = [pg.Color("white"), pg.Color("gray")]
    for height in range(DIMENSION):
        for width in range(DIMENSION):
            if height % 2 == 0:
                if width % 2 == 0:
                    screen.fill(colourList[0], rect = [height*SQ_SIZE, width*SQ_SIZE, SQ_SIZE, SQ_SIZE])
                else:
                    screen.fill(colourList[1], rect = [height*SQ_SIZE, width*SQ_SIZE, SQ_SIZE, SQ_SIZE])
            else:
                if width % 2 == 1:
                    screen.fill(colourList[0], rect = [height*SQ_SIZE, width*SQ_SIZE, SQ_SIZE, SQ_SIZE])
                else:
                    screen.fill(colourList[1], rect = [height*SQ_SIZE, width*SQ_SIZE, SQ_SIZE, SQ_SIZE])

#draw the pieces on the board using the current GameState.board
def drawPieces(screen, board):
    for height in range(DIMENSION):
        for width in range(DIMENSION):
            piece = board[width][height]
            if piece != "--":
                screen.blit(IMAGES[piece], [height*SQ_SIZE, width*SQ_SIZE])


def drawMoveLog(screen, moveLogFont, moveLog, column):

    var = list(moveLog)[-1]
    lenVar = len(moveLog[var])
                 
    if(len(moveLog[var]) == 1 and var == 0):
        pg.draw.rect(screen, "white", pg.Rect(boardWIDTH, 0, (screenWIDTH-boardWIDTH), screenHEIGHT))
        title = moveLogFont.render("Move Log: ", True, "Black")
        titleRectangle = title.get_rect()
        titleRectangle.center = (boardWIDTH + ((screenWIDTH - boardWIDTH) // 2), 8)
        screen.blit(title, titleRectangle)

    if column:
        moveLogTemp = moveLogFont.render(str(var+1) + "." + str(moveLog[list(moveLog)[-1]][0].getChessNotation()), True, "Black")
        moveRectangle = moveLogTemp.get_rect()
        moveRectangle.center = (boardWIDTH + 64), 30*(1+(var%16))
        screen.blit(moveLogTemp, moveRectangle)
    else: 
        moveLogTemp = moveLogFont.render(str(moveLog[list(moveLog)[-1]][1].getChessNotation()), True, "Black")
        moveRectangle = moveLogTemp.get_rect()
        moveRectangle.center = (boardWIDTH + 128), 30*(1+(var%16))
        screen.blit(moveLogTemp, moveRectangle)

    if(lenVar == 1 and var % 16 == 0 and var != 0):
        pg.draw.rect(screen, "white", pg.Rect(boardWIDTH, 0, (screenWIDTH-boardWIDTH), screenHEIGHT))
        title = moveLogFont.render("Move Log: ", True, "Black")
        titleRectangle = title.get_rect()
        titleRectangle.center = (boardWIDTH + ((screenWIDTH - boardWIDTH) // 2), 8)
        screen.blit(title, titleRectangle)

        moveLog = moveLogFont.render(str(var+1) + "." + str(moveLog[list(moveLog)[-1]][0].getChessNotation()), True, "Black")
        moveRectangle = moveLog.get_rect()
        moveRectangle.center = (boardWIDTH + 64), 30*(1+(var%16))
        screen.blit(moveLog, moveRectangle)
    

    print(column)

    pg.display.flip()

    pass

def highlight(screen, validMoves, row, col, gs):
    moveList = validMoves
    for move in moveList:
        if (row == move.startRow and col == move.startCol):
            yellowHighlights = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA)
            blueHighlight = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA)

            pg.draw.rect(yellowHighlights, (255, 255, 0), yellowHighlights.get_rect())
            pg.draw.rect(blueHighlight, (137, 196, 244), blueHighlight.get_rect())

            screen.blit(yellowHighlights, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE), special_flags=pg.BLEND_RGBA_MULT)
            screen.blit(blueHighlight, (move.startCol*SQ_SIZE, move.startRow*SQ_SIZE))

            pieceType = gs.board[row][col][0] + gs.board[row][col][1]
            screen.blit(IMAGES[pieceType], (move.startCol*SQ_SIZE, move.startRow*SQ_SIZE))

    
    pg.display.flip()

    return False

def gameover(screen, backgroundColor, printColor, font, gs):

    if backgroundColor == "Stalemate!":
        screen.fill(pg.Color("Red"))
        text = font.render('It''s a stalemate!', True, "Blue", "Red")
        textRectangle = text.get_rect()
        textRectangle.center = (boardWIDTH // 2, boardHEIGHT // 2)
        screen.blit(text, textRectangle)
        gs.staleMate = True
    
    else:
        screen.fill(pg.Color(backgroundColor))
        text = font.render(backgroundColor + ' Wins!', True, printColor, backgroundColor)
        textRectangle = text.get_rect()
        textRectangle.center = (boardWIDTH // 2, boardHEIGHT // 2)
        screen.blit(text, textRectangle)
        gs.checkMate = True

    pg.display.flip()

    return True

main()