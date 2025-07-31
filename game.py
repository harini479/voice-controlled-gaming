import pygame
import sys
import random
import time
import threading
import speech_recognition as sr
import queue

pygame.init()
WIDTH, HEIGHT = 1536, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape Room")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
c=""

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

current_page = "main"
tv_rect = pygame.Rect(20, 300, 300, 300)
start_time = time.time()
game_over = False
game_result = None  
end_display_time = None  


ROWS, COLS = 3, 3
PIECE_WIDTH = tv_rect.width// COLS
PIECE_HEIGHT = tv_rect.height// ROWS
shelf_rect = pygame.Rect(20, 500, 300, 150)
open_shelf=pygame.Rect(450,400,350,150)
get_key=pygame.Rect(600,500,350,150)
key_rect = pygame.Rect(420, 500, 50, 50)
box_rect=pygame.Rect(750, 500, 300, 150)
box_key_rect=pygame.Rect(600,470,350,150)
password=pygame.Rect(600,470,350,150)
get_card=pygame.Rect(600,470,350,150)
door_handler=pygame.Rect(635,360,45,90)
door_open=pygame.Rect(920,202,200,400)
shelf_open=False
key_collected = False
card_collected=False
box_open_bool=False
password_unlocked=False
selected_item = None
digits = [0, 0, 0]
selected_index = 0
correct_password = [4, 2, 9]
submit_button = pygame.Rect(230, 250, 140, 50)
message = ""
message_timer = 0
digit_positions = [(200, 150), (270, 150), (340, 150)]
small_font = pygame.font.SysFont(None, 24)


font = pygame.font.SysFont(None, 80)

def recognize_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    global running  

    while running:
        try:
            with mic as source:
                print("🎙️ Listening for a command...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                print("🔊 Audio captured, recognizing...")

                command = recognizer.recognize_google(audio).lower()
                print(f"🗣️ You said: {command}")

                handle_command(command)

        except sr.WaitTimeoutError:
            print("⌛ Listening timed out...")
            continue
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
        except sr.RequestError as e:
            print(f"❌ Could not request results: {e}")

def handle_command(command):
    global current_page, selected_item, inventory_items,c
    if "shelf" in command:
        c="s"
        current_page="shelf"
    elif "open" in command:
        c="s_o"
        current_page="key_page"
    elif "main" in command:
        c="m"
        current_page="main"
    elif "key" in command and current_page == "key_page":
        c="gk"
        key_collected=True
        current_page="main"
        inventory_items[0]='key'
    elif "box" in command:
        c="b"
        current_page="box"
    elif "door" in command:
        c="d"
    elif "select" in command:
        if "card" in  command:
            c="sc"
        elif "key" in command:
            c="sk"



# Inventory system
inventory_slots = [pygame.Rect(100 + i * 70, HEIGHT - 80, 60, 60) for i in range(5)]
inventory_items = [None] * 5  # holds 'key' or other item names
def draw_inventory():
    pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT - 100, WIDTH, 100))  # bar background

    for i, slot in enumerate(inventory_slots):
        pygame.draw.rect(screen, (200, 200, 200), slot)
        pygame.draw.rect(screen, (0, 0, 0), slot, 2)

        if inventory_items[i] == 'key':
            screen.blit(key, (slot.x + 10, slot.y + 10))
        elif inventory_items[i] == 'card':
            screen.blit(card,(slot.x+10,slot.y+10))

        # Highlight if selected
        if selected_item == i:
            pygame.draw.rect(screen, (255, 255, 0), slot, 3)

# Puzzle piece class
class PuzzlePiece:
    def __init__(self, image, correct_pos, random_pos):
        self.image = image
        self.correct_pos = correct_pos
        self.rect = self.image.get_rect(topleft=random_pos)
        self.dragging = False
        self.offset = (0, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                offset_x = self.rect.x - mouse_x
                offset_y = self.rect.y - mouse_y
                self.offset = (offset_x, offset_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset[0]
                self.rect.y = mouse_y + self.offset[1]

    def is_correct(self):
        return abs(self.rect.x - self.correct_pos[0]) < 10 and abs(self.rect.y - self.correct_pos[1]) < 10

# Load and slice puzzle
def load_puzzle(image_path):
    try:
        image = pygame.image.load(image_path)
    except:
        print("❌ Error: Could not load image.")
        sys.exit()

    image = pygame.transform.scale(image, (tv_rect.width, tv_rect.height))
    pieces = []

    for row in range(ROWS):
        for col in range(COLS):
            x = col * PIECE_WIDTH
            y = row * PIECE_HEIGHT
            piece_img = image.subsurface(pygame.Rect(x, y, PIECE_WIDTH, PIECE_HEIGHT))
            correct_x = x + tv_rect.x
            correct_y = y + tv_rect.y
            rand_x = random.randint(500, 700)
            rand_y = random.randint(100, 400)
            piece = PuzzlePiece(piece_img, (correct_x, correct_y), (rand_x, rand_y))
            pieces.append(piece)

    return pieces

# Load puzzle
pieces = load_puzzle("jigsaw_image.png")
puzzle_solved = False
flag=0

# Start the voice recognition in a separate thread
voice_thread = threading.Thread(target=recognize_voice, daemon=True)



running=True
while running:
    if flag==0:
        voice_thread.start()
        flag=1
    screen.fill((30, 30, 30))
    if current_page == "main":
        screen.blit(main_page, (0, 0))
    elif current_page == "shelf":
        screen.blit(shelf_page, (250, 0))
    elif current_page == "key_page":
        screen.blit(key_page, (250, 0))
    elif current_page=="key_empty":
        screen.blit(key_empty,(250,0))
    elif current_page=="box":
        screen.blit(box,(250,0))
    elif current_page=="box_open":
        screen.blit(box_open,(0,0))
    elif current_page == "paas":
        screen.fill((0, 0, 0))
        digit_colors   = [(255, 255,   0),  # Yellow
                      (255,   0,   0),  # Red
                      (  0, 255,   0)]  # Green
        digit_positions = [
        (WIDTH // 2 - 120, HEIGHT // 2),
        (WIDTH // 2      , HEIGHT // 2),
        (WIDTH // 2 + 120, HEIGHT // 2)]
        for i, digit in enumerate(digits):
            base_color = digit_colors[i]
            draw_color = (255, 255, 255) if i == selected_index else base_color
            surf = font.render(str(digit), True, draw_color)
            rect = surf.get_rect(center=digit_positions[i])
            screen.blit(surf, rect)
            if i == selected_index:
                pygame.draw.circle(screen, base_color, digit_positions[i], 60, 4)
        submit_w, submit_h = 200, 60
        submit_x = WIDTH // 2 - submit_w // 2
        submit_y = HEIGHT // 2 + 120
        submit_button = pygame.Rect(submit_x, submit_y, submit_w, submit_h)
        pygame.draw.rect(screen, (100, 200, 100), submit_button)
        txt = small_font.render("SUBMIT", True, (0, 0, 0))
        txt_rect = txt.get_rect(center=submit_button.center)
        screen.blit(txt, txt_rect)
        if message and time.time() - message_timer < 2:
            msg_surf = small_font.render(message, True, (255,  0,  0))
            msg_rect = msg_surf.get_rect(center=(WIDTH//2, submit_y + submit_h + 30))
            screen.blit(msg_surf, msg_rect)
    elif current_page=="unlocked":
        passowrd_unlocked=True
        screen.blit(unlocked,(100,0))
    elif current_page=="unlocked_empty":
        screen.blit(unlocked_empty,(0,0))
    elif current_page=="handler":
        screen.blit(handler,(0,0))
    elif current_page=="finished":
        screen.fill((0, 0, 0))
        if game_result == "win":
            end_text = font.render("🎉 YOU WIN! 🎉", True, (0, 255, 0))
        else:
            end_text = font.render("💀 YOU LOSE! 💀", True, (255, 0, 0))
        screen.blit(end_text, (WIDTH // 2 - 150, HEIGHT // 2))
    elif current_page=="puzzle":
        if not puzzle_solved:
            for piece in pieces:
                piece.handle_event(event)
        pygame.draw.rect(screen, (100, 100, 100), tv_rect)
        pygame.draw.rect(screen, (200, 220, 200), tv_rect, 3)
        for piece in pieces:
            piece.draw(screen)
        # Check completion
        if not puzzle_solved and all(piece.is_correct() for piece in pieces):
            puzzle_solved = True
        # Show password if puzzle solved
        if puzzle_solved:
            text = font.render("Password: 429", True, (255, 255, 0))
            screen.blit(text, (tv_rect.centerx - 80, tv_rect.centery - 20))
        #pygame.display.flip()
        #clock.tick(60)

    draw_inventory()

    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and current_page == "paas":
            if event.key == pygame.K_LEFT:
                selected_index = (selected_index - 1) % 3
            elif event.key == pygame.K_RIGHT:
                selected_index = (selected_index + 1) % 3
            elif event.key == pygame.K_UP:
                digits[selected_index] = (digits[selected_index] + 1) % 10
            elif event.key == pygame.K_DOWN:
                digits[selected_index] = (digits[selected_index] - 1) % 10
        elif event.type == pygame.MOUSEBUTTONDOWN:


            # for shelf when it is in the main page
            if current_page == "main" and (shelf_rect.collidepoint(event.pos) or c=="s"):
                if key_collected==False and shelf_open==False:
                    current_page = "shelf"
                elif key_collected==False and shelf_open==True:
                    current_page="key_page"
                else:
                    current_page="key_empty"
            elif current_page == "main" and tv_rect.collidepoint(event.pos):
                if not puzzle_solved:
                    current_page="puzzle"
            elif current_page=="puzzle":
                if puzzle_solved:
                    current_page="main"
                    
                


            # for box when its is in the main page
            elif current_page=="main" and (box_rect.collidepoint(event.pos) or c=="b"):
                if box_open_bool==False:
                    current_page="box"
                else:
                    current_page="box_open"

            #for door handler
            elif current_page=="main" and (door_handler.collidepoint(event.pos) or c=="d"):
                current_page="handler"
                    

            #shelf open when the it is in the shelf
            elif current_page == "shelf":
                # Click anywhere to return
                if open_shelf.collidepoint(event.pos) or c=="s_o":
                    current_page="key_page"
                    shelf_open=True
                else:
                    current_page = "main"


            #collecting the key
            elif current_page=="key_page":
                if get_key.collidepoint(event.pos) or c=="gk":
                    key_collected=True
                    current_page="main"
                    inventory_items[0]='key'
                else:
                    current_page="main"
            elif current_page=="key_empty":
                    current_page="main"


            #opening the box
            elif current_page=="box":
                if selected_item is not None and inventory_items[selected_item] == 'key':
                    if box_key_rect.collidepoint(event.pos) or c=="sk":
                        current_page = "box_open"
                        box_open_bool=True
                else:
                    current_page="main"


            #navigating to the password page
            elif current_page=="box_open":
                if password.collidepoint(event.pos):
                    if password_unlocked==False:
                        current_page="paas"
                    elif card_collected==False:
                        current_page="unlocked"
                    else:
                        current_page="unlocked_empty"
                    
                else:
                    current_page="main"
            elif current_page=="paas":
                if submit_button.collidepoint(event.pos):
                    if digits == correct_password:
                        password_unlocked=True
                        current_page = "unlocked"
                    else:
                        message = "Wrong code!"
                        message_timer = time.time()
            elif current_page=="unlocked":
                if get_key.collidepoint(event.pos):
                    current_page="main"
                    inventory_items[1]='card'
                    card_collected=True
                else:
                    current_page="main"
            elif current_page=="unlocked_empty":
                current_page="main"
            elif current_page=="main" and door_handler.collidepoint(event.pos):
                current_page="handler"
            elif current_page=="handler":
                if selected_item is not None and inventory_items[selected_item] == 'card':
                    if door_open.collidepoint(event.pos):
                        current_page = "finished"
                else:
                    current_page="main"
            elif current_page!="finished":
                if not game_over:
                    if time.time() - start_time <= 300:
                        game_result = "win"
                    else:
                        game_result = "lose"
                        current_page="finished"
            elif current_page == "finished":
                screen.fill((0, 0, 0))
                if game_result == "win":
                    end_text = font.render("🎉 YOU WIN! 🎉", True, (0, 255, 0))
                else:
                    end_text = font.render("💀 YOU LOSE! 💀", True, (255, 0, 0))
                screen.blit(end_text, (WIDTH // 2 - 150, HEIGHT // 2))
                if end_display_time and time.time() - end_display_time > 5:
                    running = False
            for i, slot in enumerate(inventory_slots):
                if slot.collidepoint(event.pos) and inventory_items[i]:
                    selected_item = i
                    print("Selected item:", inventory_items[i])
    # Check for timeout
    if not game_over and time.time() - start_time >= 60:
        game_result = "lose"
        game_over = True
        current_page = "finished"
        end_display_time = time.time()
        
 





pygame.quit()
sys.exit()
