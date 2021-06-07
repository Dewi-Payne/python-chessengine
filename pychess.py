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


def index_to_square(index):
    # TODO - implement this function
    x = 0
    y = 0
    return Square(x, y)


class Board:
    # class that represents the board
    def __init__(self):
        self.squares = []
        self.initialise_squares()
        self.read_pieces()
        self.draw()


    def clear_pieces(self):
        pass
        # This caused problems elsewhere so i commented it out, it's being called where it shouldn't
        #for element in self.squares:
        #    element.piece = None

    def initialise_squares(self):
        for row in range(8):
            for col in range(8):
                self.squares.append(Square(col,row))

    def draw(self):
        # method for drawing the board based on the
        # position of pieces in the pieces dict
        self.clear_pieces()
        for row in range(8):
            for col in range(8):
                # Initialises the piece string to empty
                # before checking it it is occupied by a piece
                # This part could be improved
                piece = ""
                for square in self.squares:
                    if (square.col == col) and (square.row == row):
                        if square.piece != None:
                            piece = square.piece.colour[0] + square.piece.piece_type + ".png"

                # determines the colour of each square
                if (row + col) % 2 == 0:
                    colour = "white"
                else:
                    colour = "purple"

                # Draws the squares
                # Use Buttons instead of canvas? And can we drag an image like on lichess to move? not so important
                temp = tk.Canvas(root, width=50, height=50, bg=colour, bd=0,
                                 highlightthickness=0, relief='ridge')

                #squares[temp] = Square(col, row)
                for element in self.squares:
                    if element.row == row and element.col == col:
                        element.canvas = temp
                        # This binds the canvas to a function used to make moves
                        temp.bind("<Button-1>", lambda e, s=element: square_clicked(e, s))
                        temp.bind("<Button-3>", lambda e: clear_move())

                if piece != "":
                    temp.create_image(24, 25, image=images[piece])

                temp.grid(row=row, column=col)

    def read_pieces(self):
        # This function reads a FEN string and places them in
        # the pieces dict as values with its square as their key
        # TODO - make it take in the FEN string as an argument that can be passed to it on moving
        #pieces.clear()
        self.clear_pieces()
        col = 0
        row = 0
        for char in FEN:
            if (col >= 9) or (char == "/"):
                col = 0
                row += 1
                continue
            if char == " ":
                break
            if char.isdigit():
                col += int(char)
            else:
                #squ = Square(col, row)
                piece_type = char

                if char.isupper():
                    colour = "white"
                else:
                    colour = "black"
                #pieces[squ] = Piece(colour, piece_type)
                for element in self.squares:
                    if element.row == row and element.col == col:
                        element.piece = Piece(colour, piece_type)

                col += 1


class Piece:
    # class to store a piece with its colour and type
    def __init__(self, colour=None, piece_type=None):
        self.colour = colour
        self.piece_type = piece_type


class Move:
    # TODO - Change into a function instead of a class??
    def __init__(self, square_from, square_to):
        self.square_from = square_from
        self.square_to = square_to


        # This is a lazy way of doing it, maybe a method in
        # the square class could do this better
        for square in list(board.squares):
            if square.col == square_from.col and square.row == square_from.row:
                square_from = square
            if square.col == square_to.col and square.row == square_to.row:
                square_to = square

        # This is some basic move legality checks, should be its own function probably
        if square_from.piece is None:
            board.draw()
            return
        if square_to.piece is not None:
            if square_from.piece.colour == square_to.piece.colour:
                board.draw()
                return


        square_to.piece = square_from.piece
        square_from.piece = None


        board.draw()


def square_clicked(event, square):
    square.canvas.config(bg="red")
    global move_from
    if move_from is None:
        move_from = square
    else:
        if move_from == square:
            move_from = None
            board.draw()
            return
        move = Move(move_from, square)
        move_from = None


def clear_move():
    board.draw()
    global move_from
    move_from = None



if __name__ == "__main__":
    root = tk.Tk()

    global images
    images = {}
    local_dir = pathlib.Path(__file__).parent.absolute()
    image_dir = os.path.join(local_dir, "images")
    for filename in os.listdir(image_dir):
        images[filename] = tk.PhotoImage(file=image_dir + "/" + filename)

    board = Board()

    root.mainloop()
