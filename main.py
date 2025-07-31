import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1536, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape Room")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

# Load images
main_page = pygame.image.load("main.png")
shelf_page = pygame.image.load("shelf.png")
key_page = pygame.image.load("key_page.jpg")
key_empty=pygame.image.load("key_empty.png")
key=pygame.image.load("key.png")
box=pygame.image.load("box.png")
box_open=pygame.image.load("box_open.png")
unlocked=pygame.image.load("unlocked.png")
card=pygame.image.load("card.png")
unlocked_empty=pygame.image.load("unlocked_empty.png")
handler=pygame.image.load("handler.png")
finished=pygame.image.load("finished.png")

# Setup puzzle
difference_rects = [
    pygame.Rect(700, 200, 30, 30),
    pygame.Rect(830, 270, 30, 30),
    pygame.Rect(1000, 350, 30, 30)
]
found_differences = []

# Inventory and items
inventory_items = {}
selected_item = None

# Game state
current_page = "main"
start_time = time.time()
game_over = False
game_result = None
end_display_time = None

# Game loop
running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_page == "main":
                # Clicking on the TV to go to puzzle
                if pygame.Rect(1047, 227, 300, 230).collidepoint(event.pos):
                    current_page = "puzzle"

            elif current_page == "puzzle":
                for rect in difference_rects:
                    if rect.collidepoint(event.pos) and rect not in found_differences:
                        found_differences.append(rect)
                if len(found_differences) == len(difference_rects):
                    inventory_items['card'] = True
                    current_page = "main"

            elif current_page == "main":
                # If card is collected, enable door handler
                if pygame.Rect(400, 150, 200, 200).collidepoint(event.pos):
                    if inventory_items.get('card'):
                        current_page = "handler"
                    else:
                        print("You need the card!")

            elif current_page == "handler":
                # Check if card is selected
                if inventory_items.get('card'):
                    current_page = "door_open"
                    if not game_over:
                        if time.time() - start_time <= 60:
                            game_result = "win"
                        else:
                            game_result = "lose"
                        game_over = True
                        current_page = "end"
                        end_display_time = time.time()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and inventory_items.get('card'):
                selected_item = 'card'

    # Page rendering
    if current_page == "main":
        screen.blit(main_page, (0, 0))
        screen.blit(inventory_slot, (0, 700))
        if inventory_items.get('card'):
            screen.blit(card, (50, 710))

    elif current_page == "puzzle":
        screen.blit(puzzle_page, (0, 0))
        for rect in difference_rects:
            if rect in found_differences:
                pygame.draw.rect(screen, (0, 255, 0), rect, 3)

    elif current_page == "handler":
        screen.blit(door_page, (0, 0))
        screen.blit(inventory_bar, (0, 700))
        if inventory_items.get('card'):
            screen.blit(card, (50, 710))

    elif current_page == "door_open":
        screen.blit(door_open_page, (0, 0))

    elif current_page == "end":
        screen.fill((0, 0, 0))
        if game_result == "win":
            text = font.render("🎉 YOU WIN! 🎉", True, (0, 255, 0))
        else:
            text = font.render("💀 YOU LOSE! 💀", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))

        # After 5 seconds, quit
        if end_display_time and time.time() - end_display_time > 5:
            running = False

    # Timeout check
    if not game_over and time.time() - start_time >= 60:
        game_result = "lose"
        game_over = True
        current_page = "end"
        end_display_time = time.time()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
