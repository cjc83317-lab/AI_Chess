import pygame
import chess
from engine import minimax
import os

WIDTH, HEIGHT = 480, 480
SQUARE_SIZE = WIDTH // 8
WHITE = (255, 255, 255)
GRAY = (119, 136, 153)

BOT_ELO = 1500  # Change to 1000, 1500, 2000

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Chess Bot")

board = chess.Board()
selected_square = None
promotion_choice = None
promotion_square = None
game_mode = None  # 'bot' or 'friend'

# Load and resize piece images
piece_images = {}
for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
    black_img = pygame.image.load(os.path.join("assets", f"b{piece}.png"))
    white_img = pygame.image.load(os.path.join("assets", f"w{piece}.png"))
    piece_images[piece] = pygame.transform.scale(black_img, (SQUARE_SIZE, SQUARE_SIZE))
    piece_images[piece.upper()] = pygame.transform.scale(white_img, (SQUARE_SIZE, SQUARE_SIZE))

def get_depth_from_elo(elo):
    if elo <= 1000:
        return 2
    elif elo <= 1500:
        return 3
    elif elo <= 2000:
        return 4
    else:
        return 5

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            screen.blit(piece_images[piece.symbol()], (col*SQUARE_SIZE, row*SQUARE_SIZE))

def highlight_square(square):
    row = 7 - chess.square_rank(square)
    col = chess.square_file(square)
    pygame.draw.rect(screen, (255, 255, 0), (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def draw_promotion_menu(color):
    options = ['q', 'r', 'b', 'n']
    for i, piece in enumerate(options):
        img_key = piece.upper() if color == chess.WHITE else piece
        img = piece_images[img_key]
        x = i * SQUARE_SIZE
        y = HEIGHT // 2 - SQUARE_SIZE // 2
        screen.blit(img, (x, y))
        pygame.draw.rect(screen, (0, 255, 0), (x, y, SQUARE_SIZE, SQUARE_SIZE), 2)

def draw_start_menu():
    font = pygame.font.SysFont(None, 36)
    screen.fill((0, 0, 0))
    bot_text = font.render("Play vs Bot", True, WHITE)
    friend_text = font.render("Play vs Friend", True, WHITE)
    screen.blit(bot_text, (WIDTH//2 - bot_text.get_width()//2, HEIGHT//2 - 60))
    screen.blit(friend_text, (WIDTH//2 - friend_text.get_width()//2, HEIGHT//2 + 10))
    pygame.draw.rect(screen, WHITE, (WIDTH//2 - 100, HEIGHT//2 - 70, 200, 40), 2)
    pygame.draw.rect(screen, WHITE, (WIDTH//2 - 100, HEIGHT//2 + 0, 200, 40), 2)
    pygame.display.flip()

def draw_game_over_screen(result_text):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    screen.fill((0, 0, 0))

    result_surface = font.render(result_text, True, WHITE)
    rematch_surface = small_font.render("Rematch", True, WHITE)
    home_surface = small_font.render("Home", True, WHITE)
    exit_surface = small_font.render("Exit", True, WHITE)

    screen.blit(result_surface, (WIDTH//2 - result_surface.get_width()//2, HEIGHT//2 - 120))
    pygame.draw.rect(screen, WHITE, (WIDTH//2 - 100, HEIGHT//2 - 40, 200, 40), 2)
    pygame.draw.rect(screen, WHITE, (WIDTH//2 - 100, HEIGHT//2 + 20, 200, 40), 2)
    pygame.draw.rect(screen, WHITE, (WIDTH//2 - 100, HEIGHT//2 + 80, 200, 40), 2)

    screen.blit(rematch_surface, (WIDTH//2 - rematch_surface.get_width()//2, HEIGHT//2 - 30))
    screen.blit(home_surface, (WIDTH//2 - home_surface.get_width()//2, HEIGHT//2 + 30))
    screen.blit(exit_surface, (WIDTH//2 - exit_surface.get_width()//2, HEIGHT//2 + 90))
    pygame.display.flip()

def handle_game_over(result_text):
    while True:
        draw_game_over_screen(result_text)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH//2 - 100 <= x <= WIDTH//2 + 100:
                    if HEIGHT//2 - 40 <= y <= HEIGHT//2:
                        return "rematch"
                    elif HEIGHT//2 + 20 <= y <= HEIGHT//2 + 60:
                        return "home"
                    elif HEIGHT//2 + 80 <= y <= HEIGHT//2 + 120:
                        return "exit"

def main():
    global selected_square, promotion_choice, promotion_square, game_mode
    running = True

    # Start menu
    while game_mode is None:
        draw_start_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH//2 - 100 <= x <= WIDTH//2 + 100:
                    if HEIGHT//2 - 70 <= y <= HEIGHT//2 - 30:
                        game_mode = 'bot'
                    elif HEIGHT//2 <= y <= HEIGHT//2 + 40:
                        game_mode = 'friend'

    # Main game loop
    while running:
        draw_board()
        draw_pieces()
        if selected_square is not None:
            highlight_square(selected_square)
        if promotion_choice:
            draw_promotion_menu(board.turn)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
                square = chess.square(col, 7 - row)

                if promotion_choice:
                    index = x // SQUARE_SIZE
                    if 0 <= index < 4:
                        promo_map = ['q', 'r', 'b', 'n']
                        promo_piece = promo_map[index]
                        move = chess.Move(selected_square, promotion_square, promotion=chess.PIECE_SYMBOLS.index(promo_piece))
                        if move in board.legal_moves:
                            board.push(move)
                            if board.is_game_over():
                                print("Game Over:", board.result())
                                running = False
                                break
                            if game_mode == 'bot':
                                depth = get_depth_from_elo(BOT_ELO)
                                _, ai_move = minimax(board, depth, -float('inf'), float('inf'), True)
                                board.push(ai_move)
                                if board.is_game_over():
                                    print("Game Over:", board.result())
                                    running = False
                        promotion_choice = None
                        selected_square = None
                        promotion_square = None
                    continue

                if selected_square is None:
                    selected_square = square
                else:
                    piece = board.piece_at(selected_square)
                    if piece and piece.symbol().lower() == 'p' and (
                        (board.turn == chess.WHITE and chess.square_rank(square) == 7) or
                        (board.turn == chess.BLACK and chess.square_rank(square) == 0)
                    ):
                        promotion_choice = True
                        promotion_square = square
                    else:
                        move = chess.Move(selected_square, square)
                        if move in board.legal_moves:
                            board.push(move)
                            if board.is_game_over():
                                result = board.result()
                                if result == '1-0':
                                    outcome = ' White wins'
                                elif result =='0-1':
                                    outcome = 'Black wins'
                                else:
                                    outcome = 'Draw'

                                choice = handle_game_over(outcome)
                                if choice == 'rematch':
                                    board.reset()
                                    selected_square = None
                                    promotion_choice = None
                                    promotion_square = None
                                elif choice == "home":
                                    board.reset()
                                    selected_square = None
                                    promotion_choice = None
                                    promotion_square = None
                                    game_mode = None
                                    return main()  # Restart the main loop
    
                                else:
                                    running = False
                                    break        
                                        
                            if game_mode == 'bot':
                                depth = get_depth_from_elo(BOT_ELO)
                                _, ai_move = minimax(board, depth, -float('inf'), float('inf'), True)
                                board.push(ai_move)
                                if board.is_game_over():
                                    print("Game Over:", board.result())
                                    running = False
                        selected_square = None

    pygame.quit()

if __name__ == "__main__":
    main()