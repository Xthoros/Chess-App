
# Schaakspel met hoofdmenu, uitleg, AI en geluid
import pygame
import chess
import chess.engine
import os
import sys
import time

WIDTH, HEIGHT = 480, 560
SQUARE_SIZE = WIDTH // 8
FPS = 60
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
YELLOW = (246, 246, 105)
BLUE = (106, 168, 255)
GRAY = (200, 200, 200)

DIFFICULTY = {
    "Makkelijk": 0.1,
    "Normaal": 0.5,
    "Moeilijk": 2.0
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schaak tegen AI")
clock = pygame.time.Clock()

script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(script_dir, "assets")

# Geluiden
move_sound = pygame.mixer.Sound(os.path.join(assets_path, "move.wav"))
capture_sound = pygame.mixer.Sound(os.path.join(assets_path, "capture.wav"))
check_sound = pygame.mixer.Sound(os.path.join(assets_path, "check.wav"))
game_over_sound = pygame.mixer.Sound(os.path.join(assets_path, "game_over.wav"))

# Stukken
piece_images = {}
piece_names = {'p': 'pawn', 'n': 'knight', 'b': 'bishop', 'r': 'rook', 'q': 'queen', 'k': 'king'}
for color in ['white', 'black']:
    for symbol, name in piece_names.items():
        filename = f"{color}_{name}.png"
        image_path = os.path.join(assets_path, filename)
        if os.path.exists(image_path):
            image = pygame.image.load(image_path)
            piece_images[f"{color}_{name}"] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))

def main_menu():
    font = pygame.font.SysFont(None, 36)
    options = ["Nieuw spel", "Uitleg", "Afsluiten"]
    selected = 0

    while True:
        screen.fill((30, 30, 30))
        title = font.render("Schaak tegen AI", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            text = font.render(option, True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Nieuw spel":
                        return
                    elif options[selected] == "Uitleg":
                        show_explanation()
                    else:
                        pygame.quit()
                        sys.exit()

def show_explanation():
    font = pygame.font.SysFont(None, 28)
    explanation = [
        "Schaakregels (beknopt):",
        "- Elk stuk beweegt anders.",
        "- Probeer de koning van de AI schaakmat te zetten.",
        "- Je verliest als je schaakmat staat.",
        "- Gebruik Enter om terug te keren."
    ]

    while True:
        screen.fill((10, 10, 10))
        for i, line in enumerate(explanation):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (20, 100 + i * 40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

def get_difficulty():
    font = pygame.font.SysFont(None, 36)
    options = list(DIFFICULTY.keys())
    selected = 0

    while True:
        screen.fill((30, 30, 30))
        title = font.render("Kies moeilijkheidsgraad:", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            text = font.render(option, True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return DIFFICULTY[options[selected]]

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            rect = pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)
            square = chess.square(col, 7 - row)
            if square in move_highlight:
                pygame.draw.rect(screen, BLUE, rect, 3)
            if last_move and square in [last_move.from_square, last_move.to_square]:
                pygame.draw.rect(screen, YELLOW, rect, 3)

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            color = 'white' if piece.color == chess.WHITE else 'black'
            name = piece_names[piece.symbol().lower()]
            image = piece_images.get(f"{color}_{name}")
            if image:
                screen.blit(image, (col*SQUARE_SIZE, row*SQUARE_SIZE))

def choose_promotion():
    options = ['q', 'r', 'b', 'n']
    index = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    index = (index - 1) % len(options)
                elif event.key == pygame.K_RIGHT:
                    index = (index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[index]
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 36)
        text = font.render("Kies promotie: " + options[index], True, (255, 255, 255))
        screen.blit(text, (20, HEIGHT // 2))
        pygame.display.flip()

def ai_move():
    global last_move
    if not board.is_game_over():
        pygame.time.wait(2000)
        result = engine.play(board, chess.engine.Limit(time=difficulty_time))
        last_move = result.move
        if board.is_capture(last_move):
            capture_sound.play()
        else:
            move_sound.play()
        board.push(last_move)
        if board.is_check():
            check_sound.play()

def show_game_over():
    font = pygame.font.SysFont(None, 48)
    if board.is_checkmate():
        msg = "Schaakmat!"
    elif board.is_stalemate():
        msg = "Pat!"
    elif board.is_insufficient_material():
        msg = "Ongenoeg materiaal!"
    else:
        msg = "Remise"

    game_over_sound.play()
    text = font.render(msg, True, (255, 0, 0))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 20))
    pygame.display.flip()
    pygame.time.wait(4000)
    main()

def main():
    global board, last_move, selected_square, move_highlight, player_turn, difficulty_time, engine

    board = chess.Board()
    last_move = None
    selected_square = None
    move_highlight = []
    player_turn = True

    difficulty_time = get_difficulty()
    engine_path = "C:/Program Files/stockfish/stockfish.exe"
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.quit()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn and not board.is_game_over():
                x, y = pygame.mouse.get_pos()
                if y < 480:
                    file = x // SQUARE_SIZE
                    rank = 7 - (y // SQUARE_SIZE)
                    square = chess.square(file, rank)
                    if selected_square is None:
                        piece = board.piece_at(square)
                        if piece and piece.color == chess.WHITE:
                            selected_square = square
                            move_highlight = [m.to_square for m in board.legal_moves if m.from_square == square]
                    else:
                        move = chess.Move(from_square=selected_square, to_square=square)
                        if move in board.legal_moves:
                            if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(square) in [0, 7]:
                                promo = choose_promotion()
                                move = chess.Move(from_square=selected_square, to_square=square, promotion=chess.PIECE_SYMBOLS.index(promo))
                            if board.is_capture(move):
                                capture_sound.play()
                            else:
                                move_sound.play()
                            board.push(move)
                            if board.is_check():
                                check_sound.play()
                            last_move = move
                            player_turn = False
                        selected_square = None
                        move_highlight = []

        if not player_turn and not board.is_game_over():
            ai_move()
            player_turn = True

        draw_board()
        draw_pieces()

        if board.is_game_over():
            show_game_over()
            running = False

        pygame.display.flip()

    engine.quit()

main_menu()
main()
