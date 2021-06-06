import tkinter as tk
import os
import pathlib

# Global variables
# "pieces" maps squares to what piece occupies it
FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
pieces = {}
squares = {}
move_from = None


class Square:
    # class that represents a square
    def __init__(self, col, row):
        self.col = col
        self.row = row


def index_to_square(index):
    # TODO - implement this function
    x = 0
    y = 0
    return Square(x, y)


class Board:
    # class that represents the board
    def __init__(self):
        self.draw()

    def draw(self):
        # method for drawing the board based on the
        # position of pieces in the pieces dict
        squares.clear()
        for row in range(8):
            for col in range(8):
                # Initialises the piece string to empty
                # before checking it it is occupied by a piece
                # This part could be improved
                piece = ""
                for i in pieces.keys():
                    if (i.col == col) and (i.row == row):
                        piece = pieces[i].colour[0] + pieces[i].piece_type + ".png"

                # determines the colour of each square
                if (row + col) % 2 == 0:
                    colour = "white"
                else:
                    colour = "purple"

                # Draws the squares
                # Use Buttons instead of canvas? And can we drag an image like on lichess to move? not so important
                temp = tk.Canvas(root, width=50, height=50, bg=colour, bd=0,
                                 highlightthickness=0, relief='ridge')
                squares[temp] = Square(col, row)
                if piece != "":
                    temp.create_image(25, 25, image=images[piece])

                # This binds the canvas to a function used to make moves
                temp.bind("<Button-1>", lambda e, t=temp: square_clicked(e, t))
                temp.bind("<Button-2>", lambda: clear_move())

                temp.grid(row=row, column=col)


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
        print(square_to.col, square_to.row)
        for square in list(pieces.keys()):
            if square.col == square_from.col and square.row == square_from.row:
                square_from = square
            if square.col == square_to.col and square.row == square_to.row:
                square_to = square


        pieces.pop(square_to)
        pieces[square_to] = pieces[square_from]
        pieces.pop(square_from)

        board.draw()


def move_piece():
    board.draw()


def square_clicked(event, obj):
    global move_from
    if move_from is None:
        move_from = obj
    else:
        if move_from == obj:
            move_from = None
            return
        move = Move(squares[move_from], squares[obj])
        move_from = None


def clear_move():
    global move_from
    move_from = None
    print("cleared")


def read_pieces():
    # This function reads a FEN string and places them in
    # the pieces dict as values with its square as their key
    # TODO - make it take in the FEN string as an argument that can be passed to it on moving
    pieces.clear()
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
            squ = Square(col, row)
            piece_type = char

            if char.isupper():
                colour = "white"
            else:
                colour = "black"
            pieces[squ] = Piece(colour, piece_type)
            col += 1


if __name__ == "__main__":
    root = tk.Tk()

    global images
    images = {}
    local_dir = pathlib.Path(__file__).parent.absolute()
    image_dir = os.path.join(local_dir, "images")
    for filename in os.listdir(image_dir):
        images[filename] = tk.PhotoImage(file=image_dir + "/" + filename)
    print(images)

    read_pieces()

    for p in pieces:
        print(p.col, p.row, pieces[p].colour, pieces[p].piece_type)

    board = Board()

    root.mainloop()
