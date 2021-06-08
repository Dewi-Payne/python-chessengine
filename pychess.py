import tkinter as tk
import os
import pathlib

# Global variables
FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
move_from = None


class Square:
    # class that represents a square
    def __init__(self, col, row, canvas=None, piece=None, colour=None):
        self.col = col
        self.row = row
        self.canvas = canvas
        self.piece = piece
        self.colour = colour


class Board:
    # class that represents the board
    def __init__(self):
        # Initialises the board and calls functions to create squares, read the pieces from FEN then draw the board.
        # TODO - Work on the frontend, like how the board looks
        # TODO - Also need to add an input field that works with FEN and is updated when a move is made
        self.squares = []
        self.initialise_squares()
        self.read_pieces()
        self.draw()

    def clear_pieces(self):
        pass
        # This caused problems elsewhere so i commented it out, it's being called where it shouldn't
        # for element in self.squares:
        #    element.piece = None

    def initialise_squares(self):
        # All this method does is creates all the squares for the board
        # It needs to be called before board.draw() or board.read_pieces are called
        for row in range(8):
            for col in range(8):
                self.squares.append(Square(col, row))

    def draw(self):
        # method for drawing the board based on the
        # position of pieces in the board.squares list
        for row in range(8):
            for col in range(8):
                # Fetches the correct square object to assign its canvas and to read its piece information for drawing
                square = self.get_square(Square(col, row))

                # Determines the colour of each square
                if (row + col) % 2 == 0:
                    square.colour = "linen"
                else:
                    square.colour = "PaleVioletRed3"

                # Creates canvas to represent each square of the correct colour
                # TODO - Research if drag and drop is possible with this setup
                temp = tk.Canvas(root, width=50, height=50, bg=square.colour, bd=0,
                                 highlightthickness=0, relief='ridge')

                # Sets the square from the list of squares' canvas to the one we made above,
                # and binds the commands to it
                square.canvas = temp
                temp.bind("<Button-1>", lambda e, s=square: square_clicked(e, s))
                temp.bind("<Button-3>", lambda e: clear_move())

                # Places the appropriate piece
                if square.piece is not None:
                    piece = square.piece.colour[0] + square.piece.piece_type + ".png"
                    temp.create_image(24, 25, image=images[piece])

                temp.grid(row=row, column=col)

    def get_square(self, square):
        for element in self.squares:
            if element.col == square.col and element.row == square.row:
                return element

    def read_pieces(self):
        # This function reads a FEN string and places them in
        # the pieces dict as values with its square as their key
        # TODO - make it take in the FEN string as an argument
        # TODO - Implement a function that creates a FEN string from the current board
        self.clear_pieces()
        col = 0
        row = 0
        for char in FEN:
            if (char == "/") or (col >= 9):
                # Skips to the next row if the character is a slash
                col = 0
                row += 1
                continue
            if char == " ":
                # Simply exists when there is a space - this will change
                # TODO - Add things like whose move, castling legality and move clock in the board object as fields
                break

            if char.isdigit():
                # If the FEN string has a number, skip that many columns over
                col += int(char)
            else:
                # This part creates the piece object and assigns it to the correct square
                piece_type = char
                square = self.get_square(Square(col, row))
                col += 1

                if char.isupper():
                    colour = "white"
                else:
                    colour = "black"

                square.piece = Piece(colour, piece_type)


class Piece:
    # class to store a piece with its colour and type
    def __init__(self, colour=None, piece_type=None):
        self.colour = colour
        self.piece_type = piece_type


def check_legality(move):
    # Function for checking move legality; only makes sure the square from isn't blank
    # or if the pieces are of the same colour (so far).
    # returns True if move is legal, False otherwise
    # TODO - Lots to do for checking move legality

    if move.square_from.piece is None:
        # If you're trying to move an empty square, it fails
        return False
    if move.square_to.piece is not None:
        if move.square_from.piece.colour == move.square_to.piece.colour:
            # If you're trying to capture a piece of the same colour, it fails
            return False

    # If it gets here we know a piece is moving and isn't trying to capture its own piece - do more checks here
    if move_from.piece.piece_type == "P":
        # White pawns
        # Moving forward if the square is empty
        if move.square_to == board.get_square(Square(move_from.col, move_from.row - 1)):
            if move.square_to.piece is None:
                return True
        # Moving twice if on the 7th rank
        if move.square_to == board.get_square(Square(move_from.col, move_from.row - 2)):
            if move.square_to.piece is None:
                if move_from.row == 6:
                    return True
        # Capturing
        if move.square_to == board.get_square(Square(move_from.col-1,move_from.row -1)) or \
                move.square_to == board.get_square(Square(move_from.col+1,move_from.row -1)):
            if move.square_to.piece is not None and move.square_to.piece.colour != move.square_from.colour:
                return True
    if move_from.piece.piece_type == "p":
        # black pawns
        # Moving forward if the square is empty
        if move.square_to == board.get_square(Square(move_from.col, move_from.row + 1)):
            if move.square_to.piece is None:
                return True
        # Moving twice if on the 2th rank
        if move.square_to == board.get_square(Square(move_from.col, move_from.row + 2)):
            if move.square_to.piece is None:
                if move_from.row == 1:
                    return True
        # Capturing
        if move.square_to == board.get_square(Square(move_from.col-1,move_from.row +1)) or \
                move.square_to == board.get_square(Square(move_from.col+1,move_from.row +1)):
            if move.square_to.piece is not None and move.square_to.piece.colour != move.square_from.colour:
                return True

    return False


class Move:
    # Class that represents a move between two given squares, legality is calculated on creation
    # TODO - Move most of this to a function to leave the class move as a basic data structure that just stores squares
    def __init__(self, square_from, square_to):
        self.square_from = board.get_square(square_from)
        self.square_to = board.get_square(square_to)

    def is_legal(self):
        return check_legality(self)

    def make_move(self):
        # Takes in an object of class Move then makes the move if it is legal
        if self.is_legal():
            self.square_to.piece = self.square_from.piece
            self.square_from.piece = None
            board.draw()


def square_clicked(event, square):
    # This function is triggered every time you click on a canvas and
    # depending on if you have already started a move or not decides to
    # colour the square and set the move_from to that square or tries to execute a move
    # from the stored square to the current one passed as an argument here named "square"
    square = board.get_square(square)
    global move_from
    if move_from is None:
        square.canvas.config(bg="red")
        move_from = square

        # There's probably a neater way to do this - this is pretty makeshift but it seems to work
        for squ in board.squares:
            if move_from is not squ:
                if Move(move_from, squ).is_legal():
                    squ.canvas.create_oval(20,20,30,30,fill="orange")

    else:
        if move_from == square:
            move_from = None
            board.draw()
            return
        Move(move_from, square).make_move()
        move_from = None
        board.draw()


def clear_move():
    # This is triggered by right clicking on the board and just
    # resets the stored global move variable and re-draws the squares to reset the colour
    # TODO - maybe it could be one of board's variables instead of global?
    global move_from
    move_from = None

    board.draw()


if __name__ == "__main__":
    root = tk.Tk()

    # This just fetches images from the folder images, creates tkinter PhotoImage classes
    # and stores them in a dictionary with the file name as the key for easy access
    # TODO - there's got to be a cleaner way of both retrieving the files, and maybe don't rely on file names?
    global images
    images = {}
    local_dir = pathlib.Path(__file__).parent.absolute()
    image_dir = os.path.join(local_dir, "images")
    for filename in os.listdir(image_dir):
        images[filename] = tk.PhotoImage(file=image_dir + "/" + filename)

    # Creates the main board whose __init__ method has calls to other functions to initialise the game
    board = Board()

    root.mainloop()
