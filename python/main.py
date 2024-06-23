import pygame
from game import Game
from player_mode import PlayerMode
from ai_mode import AIMode
from level_editor import LevelEditor

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
GAME_WIDTH = 800
GAME_HEIGHT = 600

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AI Training Environment")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    game = Game()

    running = True
    mode = main_menu(screen, font)

    while running:
        if mode is None:
            running = False
            continue

        if mode == 'player':
            player_mode = PlayerMode(screen, font, game, clock)
            mode = player_mode.run()
        elif mode == 'ai':
            ai_mode = AIMode(screen, font, game, clock)
            mode = ai_mode.run()
        elif mode == 'editor':
            level_editor = LevelEditor(GAME_WIDTH, GAME_HEIGHT)
            level_editor.run(screen, clock)
            game.levels = game.load_all_levels()  # Reload levels after editing

        mode = main_menu(screen, font)

    pygame.quit()

def main_menu(screen, font):
    buttons = [
        pygame.Rect(450, 150, 300, 50),
        pygame.Rect(450, 250, 300, 50),
        pygame.Rect(450, 350, 300, 50)
    ]

    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, font, 'Main Menu', (255, 255, 255), (SCREEN_WIDTH // 2, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].collidepoint(event.pos):
                    return 'player'
                elif buttons[1].collidepoint(event.pos):
                    return 'ai'
                elif buttons[2].collidepoint(event.pos):
                    return 'editor'

        pygame.draw.rect(screen, (100, 100, 100), buttons[0])
        pygame.draw.rect(screen, (100, 100, 100), buttons[1])
        pygame.draw.rect(screen, (100, 100, 100), buttons[2])
        draw_text(screen, font, 'Player Mode', (255, 255, 255), buttons[0].center)
        draw_text(screen, font, 'AI Mode', (255, 255, 255), buttons[1].center)
        draw_text(screen, font, 'Level Editor', (255, 255, 255), buttons[2].center)

        pygame.display.flip()

def draw_text(screen, font, text, color, position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    main()  