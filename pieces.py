from spritesheet import Spritesheet

class Peice:
    def __init__(self, colour, position, image_num, directions, value):
        self.colour_num = 0 if colour == "white" else 1
        peices_spritesheet = Spritesheet("assets/pieces.png")

        self.colour = colour
        self.position = list(position)

        self.image = peices_spritesheet.parse_sprite("pieces" + str(image_num + self.colour_num * 6) + ".png")

        self.directions = directions
        self.moves = 0
        self.value = value


    def is_in_bounds(self, next_x, next_y, board):
        return 0 <= next_x and next_x < len(board) and 0 <= next_y and next_y < len(board)


    def get_valid_moves(self, board, _):
        valid_moves = []

        for dx, dy in self.directions:

            next_x, next_y = self.position[0] + dx, self.position[1] + dy

            while self.is_in_bounds(next_x, next_y, board):

                square = board[next_x][next_y]

                if not square:
                    valid_moves.append([(self.position[0], self.position[1]), (next_x, next_y)])

                else:
                    if self.colour != square.colour:
                        valid_moves.append([(self.position[0], self.position[1]), (next_x, next_y)])

                    break

                next_x += dx
                next_y += dy

        return valid_moves
    
    
    def get_attacked_squares(self, board):
        attacked = []
        for row in board:
            for piece in row:
                if piece and piece.colour != self.colour:
                    moves = piece.get_valid_moves(board, None)

                    if isinstance(piece, Pawn):
                        moves = piece.get_attacked(board)

                    for move in moves:
                        if len(move) == 2:
                            attacked.append(move[1])

        return list(set(attacked))

 

class Pawn(Peice):
    def __init__(self, colour, position):
        super().__init__(colour, position, 5, [], 1)
        self.direction = -1 if self.colour == "white" else 1


    def get_valid_moves(self, board, previous_move):
        valid_moves = []

        step = 1

        if self.position[0] == 1 or self.position[0] == 6:
            step = 2

        for dx in range(step + 1):
            next_x = self.position[0] + dx * self.direction
           
            if self.can_promote(next_x):
                valid_moves.append(str((next_x, self.position[1])) + "=")

            if self.is_in_bounds(next_x, self.position[0], board) and not board[next_x][self.position[1]]:
                valid_moves.append([(self.position[0], self.position[1]),
                                    (next_x, self.position[1])])
                

        return valid_moves + self.passant(board, previous_move) + self.get_attacked(board)
    

    def can_promote(self, next_x):
        return (self.colour == "white" and next_x == 0) or (self.colour == "black" and next_x == 7)
    

    def get_attacked(self, board):
        valid_moves = []

        for dy in [-1, 1]:
            next_x = self.position[0] + self.direction
            next_y = self.position[1] + dy

            if self.is_in_bounds(next_x, next_y, board):
                square = board[next_x][next_y]

                if square and square.colour != self.colour:
                    valid_moves.append([(self.position[0], self.position[1]),(next_x, next_y)])

                    if self.can_promote(next_x):
                        valid_moves.append(str((next_x, next_y)) + "=")


        return valid_moves


    def passant(self, board, previous_move):
        valid_moves = []

        if previous_move and isinstance(previous_move[0], Pawn) and previous_move[0].colour != self.colour and abs(previous_move[1][0] - previous_move[2][0]) == 2: # check if move can be passanted

            for direction in [-1, 1]:
                next_y = self.position[1] + direction

                if self.is_in_bounds(self.position[0], next_y, board) and (self.position[0], next_y) == previous_move[2]:
                    x = -1 if self.colour == "white" else  1
                    valid_moves.append(str((self.position[0] + x, next_y)) + "*")

        return valid_moves



class King(Peice):
    def __init__(self, colour, position):
        super().__init__(colour, position, 0, None, 1_000_000)


    def get_valid_moves(self, board, _):
        valid_moves = []

        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                next_x = self.position[0] + dx
                next_y = self.position[1] + dy

                if self.is_in_bounds(next_x, next_y, board):

                    square = board[next_x][next_y]

                    if not square or square.colour != self.colour:
                        valid_moves.append([
                            (self.position[0], self.position[1]),
                            (next_x, next_y)
                        ])

        return valid_moves + self.castle(board)
    

    def castle(self, board):
        valid_moves = []

        if self.moves == 0 and (self.position[0] == 7 and self.colour == "white" or self.position[0] == 0 and self.colour == "black"):
                
            attacked = []
            for row in board:
                for piece in row:
                    
                    if piece and piece.colour != self.colour and not isinstance(piece, King):
                        moves = piece.get_valid_moves(board, None)

                        if isinstance(piece, Pawn):
                            moves = piece.get_attacked(board)

                        for move in moves:
                            if len(move) == 2:
                                attacked.append(move[1])

            next_square = self.position[1]

            while True:
                next_square -= 1

                if self.is_in_bounds(self.position[0], next_square, board):
                    if board[self.position[0]][next_square] != "" or (self.position[0], next_square) in attacked:
                        break

                if next_square == 1 and board[7][0]and board[7][0].moves == 0:
                    valid_moves.append("o-o-o")

            next_square = self.position[1]

            while True:
                next_square += 1

                if self.is_in_bounds(next_square, self.position[1], board):
                    if board[self.position[0]][next_square] != "" or (self.position[0], next_square) in attacked:
                        break

                if next_square == 6 and board[7][7] and board[7][7].moves == 0:
                    valid_moves.append("o-o")

        return valid_moves
  
        
    
class Knight(Peice):
    def __init__(self, colour, position):
        super().__init__(colour, position, 3, [[2, 1], [1, 2], [-1, 2], [-2, 1], [-2, -1], [-1, -2], [1, -2], [2, -1]], 3)
        

    def get_valid_moves(self, board, _):
        valid_moves = []

        for dx, dy in self.directions:

            next_x = self.position[0] + dx
            next_y = self.position[1] + dy

            if self.is_in_bounds(next_x, next_y, board):

                square = board[next_x][next_y]

                if not square or square.colour != self.colour:
                    valid_moves.append([(self.position[0], self.position[1]),
                                        (next_x, next_y)])

        return valid_moves



class Queen(Peice):
    def __init__(self, colour, position):
        super().__init__(colour, position, 1, [[1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]], 9)



class Bishop(Peice):
    def __init__(self, colour, position):
        super().__init__(colour, position, 2, [[1, 1], [1, -1], [-1, 1], [-1, -1]], 3)



class Rook(Peice):
    def __init__(self, colour, position):
        super().__init__(colour, position, 4, [[1, 0], [-1, 0], [0, 1], [0, -1]], 5)
