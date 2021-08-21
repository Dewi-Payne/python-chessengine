"""A simple chess engine using Python."""

import tkinter as tk
import os
import pathlib

# Global variables
FEN = "rnbqkbnr/pPpppppp/8/8/8/8/PpPPPPPP/RNBQKBNR w KQkq - 0 1"
move_from = None
BLACK = -1
WHITE = 1
en_passant_flag = None


class Piece:
    """
    Object for pieces.

    Attributes:
        colour (int): The colour of the piece, WHITE = 1, BLACK = -1
        piece_type (str): The piece type character. Uppercase represents white, lowercase black.
    """

    def __init__(self, colour: int = None, piece_type: str = None):
        self.colour = colour
        self.piece_type = piece_type


class Square:
    """
    An object that represents a square.

    Attributes:
        col (int): Integer value for the column.
        row (int): Integer value for the row.
        canvas (tk.Canvas): Canvas object for this square, used for changing its appearance (default: None).
        piece (Piece): The piece that occupies this square (default: None).
        colour (str):
            String for the square's color, using tkinter internal colour names (default: None).
            http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
    """

    def __init__(self, col: int, row: int, canvas: tk.Canvas = None, piece: Piece = None, colour=None):
        self.col = col
        self.row = row
        self.canvas = canvas
        self.piece = piece
        self.colour = colour
        self.EP = False


class Move:
    """
    A class that represents a move between two Square objects.

    Attributes:
        square_from (Square): A Square which the Move originates from.
        square_to (Square): A Square which is the destination of the Move.
    """

    def __init__(self, square_from, square_to):
        """Initialises Move class."""
        self.square_from = board.get_square(square_from.col, square_from.row)
        self.square_to = board.get_square(square_to.col, square_to.row)

    def is_legal(self):
        """Method to check if a Move object is legal, using the check_legality function and checking
         what player's turn it is."""
        if self.square_from.piece is None:
            return check_legality(self)
        elif self.square_from.piece.colour == board.turn:
            return check_legality(self)
        else:
            return False

    def make_move(self):
        """Method for executing a move with a given Move object on the board, given a legal Move."""
        if self.is_legal():
            if self.square_to.row == 0 or self.square_to.row == 7:
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


class Board:
    """
    Board class.

    Attributes:
        squares (list): The list of all 64 squares on the board. Created in Board.initialise_squares().
        turn (int): Which colour's turn it is; WHITE = 1, BLACK = -1 (default: 1).
    """

    def __init__(self):
        """ Initialises the Board class. """
        self.squares = []
        self.turn = WHITE

        self.initialise_squares()
        self.read_fen(FEN)
        self.draw()

    def initialise_squares(self):
        """ A method for creating the squares of the board. """
        for row in range(8):
            for col in range(8):
                self.squares.append(Square(col, row))

    def draw(self):
        """
        A method that draws the board.

        It uses the Board.squares list and draws each of them, iterating through rows and columns and
        fetching each square. It then assigns the colour of the square, creates and assigns a canvas,
        binds the functions on clicking to the canvases, and then draws the piece.

        Todo:
            * Creating a new canvas and re-assigning the colours every time the board updates seems
            * inefficient, perhaps separate some functionality into Board.initialise_squares()?
        """
        for row in range(8):
            for col in range(8):
                # Fetches the correct square object to assign its canvas and to read its piece information for drawing
                square = self.get_square(col, row)

                # Determines the colour of each square
                square.colour = "linen" if (col + row) % 2 == 0 else "PaleVioletRed3"

                # Creates canvas to represent each square of the correct colour
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

    def get_square(self, col: int, row: int):
        """
        Returns a specific Square object belonging to Board.squares
        when given coordinates.

        Args:
            col (int): The column of the desired square.
            row (int): The row of the desired square.

        Returns:
            element (Square): The board's Square object, if it exists.
            None: if a square with the same coordinates as the argument square doesn't exist.
        """
        for element in self.squares:
            if element.col == col and element.row == row:
                return element
        return None

    def read_fen(self, fen_string: str):
        """
        Reads a string in FEN format, and assigns relevant variables based off of what it reads.
        https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation

        Args:
            fen_string (str): A string that should be in FEN format with information on the board's status.

        Todo:
            * Some function that reads the board's status and creates a FEN string.
            * Castling rights.
            * Remaining values at the bottom of this function.
        """
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
                square = self.get_square(col, row)
                col += 1
                if char.isupper():
                    colour = WHITE
                else:
                    colour = BLACK
                square.piece = Piece(colour, piece_type)

        if fen[1] == "w":
            self.turn = WHITE
        elif fen[1] == "b":
            self.turn = BLACK

        for char in fen[2]:
            pass


def square_offset(square: Square, col: int, row: int):
    """A function that returns a square offset by a specified row and column values."""
    return board.get_square(square.col + col, square.row + row)


def en_passant(square_from):
    print(square_from)


def check_legality(move: Move):
    """
    A function that takes in a Move object and returns if it is legal.

    Args:
        move (Move): A Move object between two squares which is checked to see if it is a valid move.

    Attributes:
        move.square_from (Square):
        move.square_to (Square):
            A Square for a Move.

    Returns:
        (Bool): True if the move is legal, False otherwise.
    """

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
                    en_passant(move.square_from)
                    return True
        # Capturing
        if move.square_to.piece is not None and move.square_to.piece.colour != move.square_from.colour:
            if move.square_to == square_offset(move.square_from, 1, - move.square_from.piece.colour):
                return True
            if move.square_to == square_offset(move.square_from, -1, - move.square_from.piece.colour):
                return True
        # Capturing en passant
        if move.square_to == en_passant_flag:
            if move.square_to == square_offset(move.square_from, -1, - move.square_from.piece.colour):
                return True
            if move.square_to == square_offset(move.square_from, 1, - move.square_from.piece.colour):
                return True

    # Movement for sliding pieces
    # the list here stores the offsets for all 8 directions which sliding pieces can move.
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


def sliding_move(square: Square, col_offset: int, row_offset: int, original_square: Square = None):
    """
    A function to calculate a list of squares a sliding piece can move to in a line with a given offset direction,
    for both straight and diagonal moving pieces.

    Args:
        square (Square): The original square to check from.
        col_offset (int): Integer value for the column offset.
        row_offset (int): Integer value for the row offset.
        original_square (Square):
            A temporary variable that is used to store the original square, to
            see see if a piece on a square we check can be captured (default: None).

    Todo:
        * This doesn't need to be recursive and may be more readable and faster if refactored.
    """

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


def square_clicked(event: tk.Event, square: Square):
    """
    A function which allows a player to make moves by clicking pieces on the board.

    It checks to see if a piece has already been clicked; if not, it will store the Square
    in the global move_from variable, highlight the square to visually differentiate it,
    and highlights possible moves from that square. If a Square has already been stored
    before this function is triggered again, it will make the move and redraw the board.

    Args:
        event (tk.Event): The Tkinter event. Not currently used.
        square (Square): The Square object that has been clicked.

    Todo:
        * Generate all legal moves elsewhere and fetch them instead of iterating through every square
            when highlighting legal moves.
    """
    square = board.get_square(square.col, square.row)
    global move_from
    if move_from is None:
        square.canvas.config(bg="red")
        move_from = square

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
    """Function to clear the global make_move variable, used in square_clicked().

    Todo:
        * move_from could be one of board's variables instead of global?
    """
    global move_from
    move_from = None

    board.draw()


class Window:
    """A static class used for drawing the UI."""
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
        """Resets the board to its original state."""
        board.squares.clear()
        board.initialise_squares()
        board.read_fen(FEN)
        board.draw()


def promotion_window(move: Move, other_piece: Piece):
    """ Function that displays pawn promotion options. """

    # Defines a list of pieces to promote to, for which ever colour is promoting.
    pieces = ["wN", "wB", "wR", "wQ"] if move.square_from.piece.colour == WHITE else ["bn", "bb", "bq", "br"]

    # Creating and setting aspects of the promotion window.
    w = tk.Toplevel(root)
    w.title("Promote pawn")
    w.geometry("264x90")

    """
    Here, it loops over the pieces in the pieces list. It creates a button with the correct image, and
    assigns the correct values within the command it triggers on being pressed.
    Credit to StackOverflow user BretBarn for the explanation on how to do this in a loop:
    https://stackoverflow.com/questions/10865116/tkinter-creating-buttons-in-for-loop-passing-command-arguments
    """
    for i, piece in enumerate(pieces):
        temp_name = "temp" + piece
        temp_name = tk.Button(w, image=images[piece+".png"], command=lambda x=piece: promote_piece(move, w, x[1]))
        temp_name.grid(row=0, column=i)
    t = tk.Button(w, text="cancel", command=lambda: cancel_promotion(move, w, other_piece))
    t.grid(row=1, column=0, columnspan=4)


def cancel_promotion(move, w, other_piece):
    """Undoes piece promotion and closes the promotion window."""
    w.destroy()
    move.square_from.piece = move.square_to.piece  # Swaps pieces
    move.square_to.piece = other_piece

    board.turn = board.turn * -1
    board.draw()


def promote_piece(move: Move, w: tk.Toplevel, piece: str):
    """Promotes a pawn to a piece given by the piece string."""
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
