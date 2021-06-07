import tkinter as tk
import os
import pathlib

# Global variables
FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
move_from = None


class Square:
    # class that represents a square
    def __init__(self, col, row, canvas=None, piece=None):
        self.col = col
        self.row = row
        self.canvas = canvas
        self.piece = piece


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
        self.clear_pieces()
        for row in range(8):
            for col in range(8):
                # Initialises the piece string to empty
                # before checking it it is occupied by a piece

                piece = ""
                # TODO [A] - Equality between square objects - Make a function there to check if co-ords are the same
                for square in self.squares:
                    if (square.col == col) and (square.row == row):
                        if square.piece is not None:
                            # TODO - figure out a better way than just adding strings to get the file name
                            piece = square.piece.colour[0] + square.piece.piece_type + ".png"

                # determines the colour of each square
                if (row + col) % 2 == 0:
                    colour = "white"
                else:
                    colour = "purple"

                # Draws the squares
                # TODO - Research if drag and drop is possible with this setup
                temp = tk.Canvas(root, width=50, height=50, bg=colour, bd=0,
                                 highlightthickness=0, relief='ridge')

                # Finds the matching square and sets its canvas field to the temporary canvas object we made above
                # TODO [A] - Same as the other TODOs tagged [A]
                for element in self.squares:
                    if element.row == row and element.col == col:

                        element.canvas = temp
                        temp.bind("<Button-1>", lambda e, s=element: square_clicked(e, s))
                        temp.bind("<Button-3>", lambda e: clear_move())

                # If the square has a piece then it draws it here
                if piece != "":
                    temp.create_image(24, 25, image=images[piece])

                temp.grid(row=row, column=col)

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

                if char.isupper():
                    colour = "white"
                else:
                    colour = "black"

                # TODO [A] - again this should become a function
                for element in self.squares:
                    if element.row == row and element.col == col:
                        element.piece = Piece(colour, piece_type)

                col += 1


class Piece:
    # class to store a piece with its colour and type
    def __init__(self, colour=None, piece_type=None):
        self.colour = colour
        self.piece_type = piece_type


def check_legality(move):
    # Function for checking move legality; only makes sure the square from isn't blank
    # and if the pieces are of the same colour
    # returns True if move is legal, False otherwise
    # TODO - Lots to do for checking move legality
    if move.square_from.piece is None:
        board.draw()
        return False
    if move.square_to.piece is not None:
        if move.square_from.piece.colour == move.square_to.piece.colour:
            board.draw()
            return False
    return True


class Move:
    # TODO - Move most of this to a function to leave the class move as a basic data structure that just stores squares
    def __init__(self, square_from, square_to):
        self.square_from = square_from
        self.square_to = square_to

        # This is a lazy way of doing it, maybe a method in
        # the square class could do this better
        for square in list(board.squares):
            if square.col == square_from.col and square.row == square_from.row:
                self.square_from = square
            if square.col == square_to.col and square.row == square_to.row:
                self.square_to = square

        self.islegal = check_legality(self)
        if not self.islegal:
            board.draw()
            return

        self.square_to.piece = self.square_from.piece
        self.square_from.piece = None

        board.draw()


def square_clicked(event, square):
    # This function is triggered every time you click on a canvas and
    # depending on if you have already started a move or not decides to
    # colour the square and set the move_from to that square or tries to execute a move
    # from the stored square to the current one passed as an argument here named "square"

    global move_from
    if move_from is None:
        # TODO - Find some way to colour in all the squares you can legally move to with that piece would be nice
        square.canvas.config(bg="red")
        move_from = square

    else:
        if move_from == square:
            move_from = None
            board.draw()
            return
        Move(move_from, square)
        move_from = None


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
