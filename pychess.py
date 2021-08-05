import tkinter as tk
import os
import pathlib

# Global variables
FEN = "rnbqkbnr/pPpppppp/8/8/8/8/P1PPPPPP/RNBQKBNR w KQkq - 0 1"
move_from = None
BLACK = -1
WHITE = 1
en_passant_flag = None


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
        self.squares = []
        self.initialise_squares()
        self.turn = WHITE  # default
        self.read_fen(FEN)
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
                square.colour = "linen" if (col + row) % 2 == 0 else "PaleVioletRed3"

                # Creates canvas to represent each square of the correct colour
                # TODO - Research if drag and drop is possible with this setup
                square.canvas = tk.Canvas(window.board_frame, width=50, height=50, bg=square.colour, bd=0,
                                          highlightthickness=0, relief='ridge')

                # Binds commands to the canvas
                square.canvas.bind("<Button-1>", lambda e, s=square: square_clicked(e, s))
                square.canvas.bind("<Button-3>", lambda e: clear_move())

                # If a piece exists it places it
                if square.piece is not None:
                    colour = "w" if square.piece.colour == WHITE else "b"
                    piece = colour + square.piece.piece_type + ".png"
                    square.canvas.create_image(24, 25, image=images[piece])
                square.canvas.grid(row=row, column=col)

    def get_square(self, square):
        for element in self.squares:
            if element.col == square.col and element.row == square.row:
                return element
        return None


    def read_fen(self, fen_string):
        # This function reads a FEN string, creating piece objects and
        # TODO - Implement a function that creates a FEN string from the current board
        self.clear_pieces()
        col = 0
        row = 0

        fen = fen_string.split()
        for char in fen[0]:
            if (char == "/") or (col >= 9):
                # Skips to the next row if the character is a slash
                col = 0
                row += 1
                continue
            if char.isdigit():
                # If the FEN string has a number, skip that many columns over
                col += int(char)
            else:
                # This part creates the piece object and assigns it to the correct square
                piece_type = char
                square = self.get_square(Square(col, row))
                col += 1
                if char.isupper():
                    colour = WHITE
                else:
                    colour = BLACK
                square.piece = Piece(colour, piece_type)

        if fen[1] == "w":
            self.turn = WHITE
        elif fen[1] == "b":
            self.turn == BLACK

        for char in fen[2]:
            pass
            # TODO - Set castling rights here
        # TODO - read the rest of the FEN string


class Piece:
    # class to store a piece with its colour and type
    def __init__(self, colour=None, piece_type=None):
        self.colour = colour
        self.piece_type = piece_type


def square_offset(square, col, row):
    return board.get_square(Square(square.col + col, square.row + row))


def check_legality(move):
    # Function for checking move legality; only makes sure the square from isn't blank
    # or if the pieces are of the same colour (so far).
    # returns True if move is legal, False otherwise

    if move.square_from.piece is None:
        # If you're trying to move an empty square, it fails
        return False
    if move.square_to.piece is not None:
        if move.square_from.piece.colour == move.square_to.piece.colour:
            # If you're trying to capture a piece of the same colour, it fails
            return False

    # If it gets here we know a piece is moving and isn't trying to capture its own piece - do more checks here
    if move.square_from.piece.piece_type.lower() == "p":
        # Pawns
        # Moving forward if the square is empty
        if move.square_to == square_offset(move.square_from, 0, - move.square_from.piece.colour):
            if move.square_to.piece is None:
                return True
        # Moving two squares if on the 2nd or 7th rank
        if move.square_to == square_offset(move.square_from, 0, - move.square_from.piece.colour * 2):
            if move.square_to.piece is None:
                if move.square_from.row == 6 or move.square_from.row == 1:
                    return True
        # Capturing
        if move.square_to.piece is not None and move.square_to.piece.colour != move.square_from.colour:
            if move.square_to == square_offset(move.square_from, 1, - move.square_from.piece.colour):
                return True
            if move.square_to == square_offset(move.square_from, -1, - move.square_from.piece.colour):
                return True
        # Capturing en passant
        if move.square_to == en_passant_flag:
            if move.square_to == square_offset(move.square_from,-1,- move.square_from.piece.colour):
                return True
            if move.square_to == square_offset(move.square_from, 1, - move.square_from.piece.colour):
                return True

    # Movement for sliding pieces
    # the list here stores the offsets for all 8 directions which sliding pieces can move in
    sliding_directions = [(1, 1), (-1, 1), (1, -1), (-1, -1), (0, 1), (0, -1), (1, 0), (-1, 0)]
    if move.square_from.piece.piece_type.lower() == "r":
        # Rooks
        for i in range(4, 8):
            if move.square_to in sliding_move(move.square_from, sliding_directions[i][0], sliding_directions[i][1]):
                return True

    if move.square_from.piece.piece_type.lower() == "b":
        # Bishops
        for i in range(4):
            if move.square_to in sliding_move(move.square_from, sliding_directions[i][0], sliding_directions[i][1]):
                return True

    if move.square_from.piece.piece_type.lower() == "q":
        # Queens
        for i in range(8):
            if move.square_to in sliding_move(move.square_from, sliding_directions[i][0], sliding_directions[i][1]):
                return True

    if move.square_from.piece.piece_type.lower() == "k":
        # Kings
        for i in range(8):
            if move.square_to == square_offset(move.square_from, sliding_directions[i][0], sliding_directions[i][1]):
                return True

    if move.square_from.piece.piece_type.lower() == "n":
        # Knights
        knight_moves = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        for m in knight_moves:
            if move.square_to == square_offset(move.square_from, m[0], m[1]):
                return True

    return False


def sliding_move(square, col_offset, row_offset, original_square=None):
    # Returns a list of squares a piece can move to in a given direction
    # TODO - capturing pieces and probably other rules need to be implemented

    # This is meant to be for capturing
    if original_square is None:
        original_square = square

    temp_square = square_offset(square, col_offset, row_offset)
    if temp_square is None:
        return [square]
    if temp_square.piece is not None:
        if temp_square.piece.colour == original_square.colour:
            return [square]
        else:
            return [square] + [temp_square]

    else:
        return [temp_square] + sliding_move(temp_square, col_offset, row_offset, original_square)


class Move:
    # Class that represents a move between two given squares, legality is calculated on creation
    # TODO - Move most of this to a function to leave the class move as a basic data structure that just stores squares
    def __init__(self, square_from, square_to):
        self.square_from = board.get_square(square_from)
        self.square_to = board.get_square(square_to)

    def is_legal(self):
        if self.square_from.piece is None:
            return check_legality(self)
        elif self.square_from.piece.colour == board.turn:
            return check_legality(self)
        else:
            return check_legality(self)  # This is temporary to allow a colour to move when it is not their turn
            return False

    def make_move(self):
        # Takes in an object of class Move then makes the move if it is legal

        if self.is_legal():
            if self.square_to.row == 0 or self.square_from.row == 7:
                if self.square_from.piece.piece_type.lower() == "p":
                    promotion_window(self, self.square_to.piece)

            self.square_to.piece = self.square_from.piece
            self.square_from.piece = None
            board.draw()
            board.turn = board.turn * -1

            # This flags the en passant square
            global en_passant_flag
            if self.square_from.row == 1 or self.square_from.row == 6:
                if self.square_from == square_offset(self.square_to, 0, + self.square_to.piece.colour * 2):
                    if self.square_to.piece.piece_type.lower() == "p":
                        en_passant_flag = square_offset(self.square_to, 0, + self.square_to.piece.colour)
            else:
                en_passant_flag = None


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
                    squ.canvas.create_oval(20, 20, 30, 30, fill="orange")

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


class Window:
    def __init__(self):
        main_frame = tk.Frame(root, width=1200, height=600, bg="white")
        main_frame.grid(row=0, column=0)

        self.board_frame = tk.Frame(main_frame, height=400, width=400, bd=10, bg="pink")
        self.board_frame.grid(row=0, column=0)

        right_frame = tk.Frame(root, width=600)
        right_frame.grid(row=0, column=1, rowspan=2)

        bottom_left_frame = tk.Frame(root, width=420, height=200)
        bottom_left_frame.grid(row=1, column=0)

        fen_string_entry = tk.Entry(bottom_left_frame, width=40, relief="flat", bd=4)
        fen_string_entry.grid(row=0, column=0)

        reset_button = tk.Button(bottom_left_frame, width=10, relief="groove", pady=10, text="Reset",
                                 command=lambda: self.reset())
        reset_button.grid(row=1, column=0)

    def reset(self):
        board.squares.clear()
        board.initialise_squares()
        board.read_fen(FEN)
        board.draw()


def promotion_window(move, other_piece):
    w = tk.Toplevel(root)
    w.title("Promote pawn")
    w.geometry("264x90")
    b1 = tk.Button(w, image=images["wN.png"], command=lambda: promote_piece(move, w, "N"))
    b2 = tk.Button(w, image=images["wB.png"], command=lambda: promote_piece(move, w, "B"))
    b3 = tk.Button(w, image=images["wQ.png"], command=lambda: promote_piece(move, w, "Q"))
    b4 = tk.Button(w, image=images["wR.png"], command=lambda: promote_piece(move, w, "R"))
    bC = tk.Button(w, text="cancel", command=lambda: cancel_promotion(move, w, other_piece))

    b1.grid(row=0, column=0)
    b2.grid(row=0, column=1)
    b3.grid(row=0, column=2)
    b4.grid(row=0, column=3)
    bC.grid(row=1, column=0, columnspan=4)


def cancel_promotion(move, w, other_piece):
    w.destroy()
    move.square_to.piece, move.square_from.piece = move.square_from.piece, move.square_to.piece # Swaps pieces
    move.square_to.piece = other_piece

    board.turn = board.turn * -1
    board.draw()
    a = 1
    b = 2
    a, b = b, a


def promote_piece(move, w, piece):
    move.square_to.piece.piece_type = piece
    board.draw()
    w.destroy()


if __name__ == "__main__":
    root = tk.Tk()

    # This just fetches images from the folder images, creates tkinter PhotoImage classes
    # and stores them in a dictionary with the file name as the key for easy access
    # TODO - there's got to be a cleaner way of both retrieving the files, and maybe don't rely on file names?
    images = {}
    local_dir = pathlib.Path(__file__).parent.absolute()
    image_dir = os.path.join(local_dir, "images")
    for filename in os.listdir(image_dir):
        images[filename] = tk.PhotoImage(file=image_dir + "/" + filename)

    # Makes the window that the board is drawn in
    window = Window()

    # Creates the main board whose __init__ method has calls to other functions to initialise the game
    board = Board()

    root.mainloop()
