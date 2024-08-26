"""
This is our main driver file. It will be responsible for handling user input and the current GameState object.
"""
import pygame as p
import ChessEngine

WIDTH = HEIGHT = 720
DIMENSION = 8  # Dimensions are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

'''
Initialize a global dictionary of image. This will be called once in the main
'''
def loadImages():
    # Alter: IMAGES["wP"] = p.image.load("images/wP.png")---------But this is not an effective way as we will
    # have to assign pieces separately
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # NOTE: We can access an image by saying "IMAGES['wP']"


'''
The main driver for our code. This will handle the user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(38,36,33))
    gs = ChessEngine.GameState()
    '''
    "gs" is a game state object for calling the constructor and so this calls the initialise 
    constructor (The one in ChessEngine.py and it creates the three variables "board", "whiteToMove", "moveLog")
    '''
    validMoves = gs.getValidMoves()
    moveMade = False    #flag variable when a move is made
    animate = False     #flag variable when we should animate a move
    loadImages()    # only do this once, before the while loop
    running = True
    sqSelected = ()         # no square is selected, Keep track of last click of the user (tuple:(row,col))
    playerClicks = []       #keep tracks of player clicks (two Tuples: [(6,4), (4,4]
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()    # (x,y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):    #If the user clicked the square twice,undo it
                        sqSelected = ()     #deselect
                        playerClicks = []   #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)     #append for both first and second click
                    if len(playerClicks) == 2:  #after the 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()     #reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # Key Handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  #Undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:     #Reset the board OR Rematch
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Draw")

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight square selected and moves for a piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # sqselected is a piece that can be moved
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value for square highlight
            s.fill(p.Color(20, 85, 30))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # Draw circles on valid move squares with transparency
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    # Create a new surface for the circle with per-pixel alpha
                    circle_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                    circle_surface = circle_surface.convert_alpha()  # Ensure surface supports alpha
                    
                    center = (SQ_SIZE // 2, SQ_SIZE // 2)
                    radius = SQ_SIZE // 6
                    
                    circle_color = (20, 85, 30, 60)  
                    p.draw.circle(circle_surface, circle_color, center, radius)
                    blit_pos = (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE)
                    screen.blit(circle_surface, blit_pos)




'''
Responsible for all the graphics within a current game state.
'''
def drawGameState(screen, gs, validMoves, sqSelected):  # This function draws the board
    drawBoard(screen)   # to draw pieces on top of those squares
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)    # draw pieces on top of those squares


'''
Draw the squares on the board.
'''
def drawBoard(screen):
    global colors
    colors = [p.Color(240,217,181), p.Color(181, 136, 99)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":   #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    coords = []     #list of coords that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5    #Frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 40, True, False)
    textObject = font.render(text, 0, p.Color('Red'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2- textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)



if __name__ == "__main__":
    main()


