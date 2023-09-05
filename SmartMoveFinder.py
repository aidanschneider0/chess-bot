pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1, "-": 0}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

import random 

def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0: 
        return scoreBoard(gs)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move

            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves: 
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True) 
            if score < minScore:
                minScore = score 
                if depth == DEPTH:
                    nextMove = move
            
            gs.undoMove()
        return minScore
    

# does the same thing as minmax but more concise --> look into both
def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0: 
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -CHECKMATE, CHECKMATE, -turnMultiplier)
        if score > maxScore:
            maxScore = score 
            if depth == DEPTH:
                nextMove = move

        gs.undoMove()

    return maxScore

# move ordering (looking at better branches first) is a quick and easy way to improve efficiency - implement later
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0: 
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score 
            if depth == DEPTH:
                nextMove = move

        gs.undoMove()
        if maxScore > alpha: #pruning happens here
            alpha = maxScore 

        if alpha >= beta:
            break

    return maxScore


def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else: 
            return CHECKMATE

    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for col in row:
            pieceType = col[0]
            
            if pieceType[0] == 'w':
                score += pieceScore[col[1]]
            else:
                score -= pieceScore[col[1]]

    return score