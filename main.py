import pygame

import sys

from pieces import King, Queen, Bishop, Rook, Knight, Pawn
from spritesheet import Spritesheet

HEIGHT = 768
WIDTH = 768

clock = pygame.time.Clock()
win = pygame.display.set_mode((WIDTH, HEIGHT))

take = pygame.mixer.Sound("assets/music/capture.mp3")
place = pygame.mixer.Sound("assets/music/move.mp3")
castle = pygame.mixer.Sound("assets/music/castle.mp3")
promote = pygame.mixer.Sound("assets/music/promote.mp3")
check = pygame.mixer.Sound("assets/music/check.mp3")

class Engine:
    def __init__(self, colour, opponent_colour):
        self.colour = colour
        self.opponent_colour = opponent_colour
        self.depth = 5
        self.transpoition_table = {}


    def evaluate(self, board):
        evaluation = 0

        for row in board:
            for piece in row:
                if piece == "":
                    continue

                if piece.colour == self.colour:
                    evaluation += piece.value

                else:
                    evaluation -= piece.value
                    
        return evaluation

        
    def get_moves(self, board, colour):
        moves = []

        for row in board:
            for piece in row:
                if piece:
                    if piece.colour == colour:

                        moves += piece.get_valid_moves(board, None)

        return moves


    def play_move(self, board, move):
        if len(move) == 2:
            previous, next = move
            board[next[0]][next[1]] = board[previous[0]][previous[1]]
            board[next[0]][next[1]].position = next
            board[previous[0]][previous[1]] = ""

        return board

    
    def undo(self, board, move):
        if len(move) == 2:
            previous, current = move
            board[previous[0]][previous[1]] = board[current[0]][current[1]]
            board[previous[0]][previous[1]].position = previous
            board[current[0]][current[1]] = ""

        return board
    
    
    def reset(self, board):
        for y, row in enumerate(board):
            for x, piece in enumerate(row):
                if piece:
                    piece.position = y, x
        
        return board



    def minimax(self, board, depth, maximising, alpha, beta):
        if depth == 0:
            return self.evaluate(board)

        if maximising:
            colour =  self.colour
            best_score = -float('inf')

        else:
            colour = self.opponent_colour
            best_score = float('inf')
    

        next_board = [row.copy() for row in board]


        for move in self.get_moves(next_board, colour):

            next_board = self.play_move(next_board, move)

            score = self.minimax(next_board , depth - 1, not maximising, alpha, beta)

            next_board = self.undo(next_board, move)
            next_board = self.reset(next_board)


            if maximising:
                best_score = max(score, best_score)
                alpha = max(alpha, score)

            else:
                best_score = min(score, best_score)
                beta = min(beta, score)

            if beta <= alpha:
                return best_score
              
        return best_score
    
    
    def best_move(self, board):
        best_score = -float('inf') 

        next_board = [row.copy() for row in board]


        for move in self.get_moves(board, self.colour):
            next_board = self.play_move(next_board, move)

            score = self.minimax( next_board, self.depth, False, -float('inf'), float('inf'))

            next_board = self.undo(next_board, move)
            next_board = self.reset(next_board)

            print(f"{move} : {score}")
        
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move





class Board:
    def __init__(self, fen):
        self.WIDTH, self.HEIGHT = 512, 512

        self.decode_fen(fen)

        self.selected_peice = None
        self.picked_square = None
        self.picked_up = False

        self.prev_move = []

        promotion_spritesheet = Spritesheet("assets/promotion.png")

        self.promotion_images = {
            "white" : promotion_spritesheet.parse_sprite("promotion1.png"),
            "black" : promotion_spritesheet.parse_sprite("promotion0.png")
        }

        self.must_promote = False
        self.valid_moves = []   
       
        
    def decode_fen(self, fen):
        piece_symbol = {
            "k": King,
            "q": Queen,
            "b": Bishop,
            "n": Knight,
            "r": Rook,
            "p": Pawn
      
        }

        king_pos = {}
        board = [["" for _ in range(8)] for _ in range(8)]
        row = column = 0   

        for character in fen:
            if character.isnumeric():
                column += int(character)

            elif character == "/":
                column = 0
                row += 1

            elif character.lower() in piece_symbol:
                piece = piece_symbol[character.lower()]
                colour = "white" if character.isupper() else "black"

                board[row][column] = piece(colour ,(row, column))
            
                if character.lower() == "k":
                    king_pos[colour] = (row, column)

                column += 1

            else:
                break


        self.board = board
        self.current_player = "white"
        self.king_positions = king_pos

    
    def get_opposite_colour(self):
        return "black" if self.current_player == "white" else "white"

    
    def draw_board(self):
        board_colours = [(240, 217, 181), (181, 136, 99)]

        for y, row in enumerate(self.board):
            for x, square in enumerate(row):

                pygame.draw.rect(win, board_colours[(x + y)  % 2], (x * 96, y * 96, 96, 96))

                if square != "":
                    win.blit(square.image, (x * 96, y * 96))


    def update_peices(self):
        square = mx // 96, my // 96
        
        if self.selected_peice and self.picked_square:  
            self.selected_peice = None
            self.picked_square = None 
            
        else:
            self.selected_peice = self.board[square[1]][square[0]]
            self.picked_square = square


    def get_attacked_squares(self, board, colour):
        attacked = []
        for row in board:
            for piece in row:
                if piece and piece.colour != colour:
                    moves = piece.get_valid_moves(board, None)

                    if isinstance(piece, Pawn):
                        moves = piece.get_attacked(board)

                    for move in moves:
                        if len(move) == 2:
                            attacked.append(move[1])

        return list(set(attacked))
    
    def not_in_check(self, square):
        temp_king_pos = self.king_positions[self.current_player]

        check_board = [row.copy() for row in self.board]
        check_board[self.picked_square[1]][self.picked_square[0]] = ""

        check_board[square[1]][square[0]] = self.selected_peice

        if isinstance(self.selected_peice, King):
            temp_king_pos = square[::-1]

        return temp_king_pos not in self.get_attacked_squares(check_board, self.current_player)


    def promote(self, colour, position):
        box_rect = pygame.Rect(position[1] * 96, 0, 98, 392)

        if colour == "black":
            box_rect.y -= box_rect.height
            
        win.blit(self.promotion_images[colour], (box_rect.x, box_rect.y))

        if keys[pygame.K_SPACE]:
            self.must_promote = False

        peice = [Queen, Knight, Rook, Bishop]

        if box_rect.collidepoint(mx, my) and pygame.mouse.get_pressed(5)[0]:
            self.board[position[0]][position[1]] = peice[(my - box_rect.y - 1) // 98](colour, position)
            self.must_promote = False
            self.current_player = self.get_opposite_colour()
            promote.play()
            self.play_check_sound()


    def castle(self, current_row, new_king_column, new_rook_column, square):

        self.board[current_row][new_king_column] = self.selected_peice
        self.board[current_row][new_rook_column] = self.board[square[1]][square[0]]

        self.selected_peice.position[1] = new_king_column
        self.board[current_row][new_rook_column].position[1] = new_rook_column

        self.selected_peice.moves += 1
        self.board[current_row][new_rook_column].moves += 1

        self.board[self.picked_square[1]][self.picked_square[0]] = ""
        self.board[square[1]][square[0]] = ""

        self.current_player = self.get_opposite_colour()


    def passant(self, square):
        self.board[square[1]][square[0]] = self.selected_peice
        self.board[square[1]][square[0]].position = square[::-1]

        self.board[self.picked_square[1]][self.picked_square[0]] = ""
        self.board[self.prev_move[2][0]][self.prev_move[2][1]] = ""

        self.current_player = self.get_opposite_colour()


    def pick_up(self):
        win.blit(self.selected_peice.image, (mx - 48, my - 48))
        self.board[self.picked_square[1]][self.picked_square[0]] = ""

        self.prev_board = self.board
        self.picked_up = True


    def place(self, square, move):
        if isinstance(self.selected_peice, King):
            self.king_positions[self.current_player] = square[1], square[0]

        if self.board[square[1]][square[0]]:
            take.play()

        else:
            place.play()
            
        self.board[square[1]][square[0]] = self.selected_peice
        self.selected_peice.position = list(move[1])
        self.selected_peice.moves += 1

        self.current_player = self.get_opposite_colour()
        self.prev_move =  [self.selected_peice, *move]

        self.selected_peice = None
        self.picked_up = False

    def play_check_sound(self):
        if self.king_positions[self.current_player] in self.get_attacked_squares(self.board, self.current_player):
            take.stop()
            place.stop()
            promote.stop()
            castle.stop()
            check.play()
        

    def play_move(self, square, move):
        if isinstance(self.selected_peice, Pawn) and (str((square[1], square[0])) + "*") in self.valid_moves:
            self.passant(square)
            take.play()

        elif isinstance(self.selected_peice, Pawn) and (str((square[1], square[0])) + "=") in self.valid_moves:

            self.board[self.picked_square[1]][self.picked_square[0]] = ""
            self.board[square[1]][square[0]] = ""
            self.prev_move =  [self.selected_peice, *move]
            self.must_promote = True
            


        elif isinstance(self.selected_peice, King) and isinstance(self.board[square[1]][square[0]], Rook) and ("o-o-o" in self.valid_moves or "o-o" in self.valid_moves):
            current_row = square[1]

            if square[0] == 0:
                new_king_column, new_rook_column = 2, 3

            elif square[0] == 7:
                new_king_column, new_rook_column = 6, 5

            self.castle(current_row, new_king_column, new_rook_column, square)
            castle.play()


        elif move in self.valid_moves:
            self.place(square, move)

        else:
           
            self.board[self.picked_square[1]][self.picked_square[0]] = self.selected_peice


    def drag_peice(self):
        square = mx // 96, my // 96
      
        if self.selected_peice:
            self.valid_moves = self.selected_peice.get_valid_moves(self.board, self.prev_move)

        if self.must_promote:
            self.promote(self.current_player, self.prev_move[2])
        
        elif pygame.mouse.get_pressed(5)[0] and self.selected_peice and self.picked_square:
            self.pick_up()
            
            
        elif self.picked_up:
            self.picked_up = False

            move = [self.picked_square[::-1], square[::-1]]

            if [self.picked_square[::-1], self.picked_square[::-1]] in self.valid_moves:       
                self.valid_moves.remove([self.picked_square[::-1], self.picked_square[::-1]])

        
            if self.selected_peice and self.selected_peice.colour == self.current_player and self.not_in_check(square):       
                self.play_move(square, move)
                self.play_check_sound()

            else:
                self.board[self.picked_square[1]][self.picked_square[0]] = self.selected_peice
        
            
                
     

    def update(self):
        self.draw_board()
        self.drag_peice()
        
        
board = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")


while True:
    win.fill((255, 255, 255))
    mx, my = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            case pygame.MOUSEBUTTONDOWN:
                board.update_peices()
            
    board.update()

    pygame.display.flip()
    pygame.display.set_caption(str(int(clock.get_fps())))
    clock.tick(120)
