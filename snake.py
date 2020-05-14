from collections import deque, namedtuple
from pygame.locals import *
import random
import pygame
import socket
import select

BOARD_LENGTH = 32
OFFSET = 16
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

DIRECTIONS = namedtuple('DIRECTIONS',
        ['Up', 'Down', 'Left', 'Right'])(0, 1, 2, 3)

def rand_color():
    return (random.randrange(254)|64, random.randrange(254)|64, random.randrange(254)|64)

#Clase Serpiente
class Snake(object):
    def __init__(self, direction=DIRECTIONS.Right, 
            point=(0, 0, rand_color()), color=None):
        self.tailmax = 4
        self.direction = direction 
        self.deque = deque()
        self.deque.append(point)
        self.color = color
        self.nextDir = deque()
    
    def get_color(self):
        if self.color is None:
            return rand_color()
        else:
            return self.color
    
    def populate_nextDir(self, events, identifier):
        if (identifier == "arrows"):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.nextDir.appendleft(DIRECTIONS.Up)
                    elif event.key == pygame.K_DOWN:
                        self.nextDir.appendleft(DIRECTIONS.Down)
                    elif event.key == pygame.K_RIGHT:
                        self.nextDir.appendleft(DIRECTIONS.Right)
                    elif event.key == pygame.K_LEFT:
                        self.nextDir.appendleft(DIRECTIONS.Left)
        if (identifier == "wasd"):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.nextDir.appendleft(DIRECTIONS.Up)
                    elif event.key == pygame.K_s:
                        self.nextDir.appendleft(DIRECTIONS.Down)
                    elif event.key == pygame.K_d:
                        self.nextDir.appendleft(DIRECTIONS.Right)
                    elif event.key == pygame.K_a:
                        self.nextDir.appendleft(DIRECTIONS.Left)
#Fin de clase serpierte

def find_food(spots):
    while True:
        food = random.randrange(BOARD_LENGTH), random.randrange(BOARD_LENGTH)
        if (not (spots[food[0]][food[1]] == 1 or
            spots[food[0]][food[1]] == 2)):
            break
    return food


def end_condition(board, coord):
    if (coord[0] < 0 or coord[0] >= BOARD_LENGTH or coord[1] < 0 or
            coord[1] >= BOARD_LENGTH):
        return True
    if (board[coord[0]][coord[1]] == 1):
        return True
    return False

def make_board():
    spots = [[] for i in range(BOARD_LENGTH)]
    for row in spots:
        for i in range(BOARD_LENGTH):
            row.append(0)
    return spots
    

def update_board(screen, snakes, food):
    rect = pygame.Rect(0, 0, OFFSET, OFFSET)

    spots = [[] for i in range(BOARD_LENGTH)]
    num1 = 0
    num2 = 0
    for row in spots:
        for i in range(BOARD_LENGTH):
            row.append(0)
            temprect = rect.move(num1 * OFFSET, num2 * OFFSET)
            pygame.draw.rect(screen, BLACK, temprect)
            num2 += 1
        num1 += 1
    spots[food[0]][food[1]] = 2
    temprect = rect.move(food[1] * OFFSET, food[0] * OFFSET)
    pygame.draw.rect(screen, rand_color(), temprect)
    for snake in snakes:
        for coord in snake.deque:
            spots[coord[0]][coord[1]] = 1
            temprect = rect.move(coord[1] * OFFSET, coord[0] * OFFSET)
            pygame.draw.rect(screen, coord[2], temprect)
    return spots

def get_color(s):
    if s == "bk":
        return BLACK
    elif s == "wh":
        return WHITE
    elif s == "rd":
        return RED
    elif s == "bl":
        return BLUE
    elif s == "fo":
        return rand_color()
    else:
        print("WHAT", s)
        return BLUE

def update_board_delta(screen, deltas):
    # accepts a queue of deltas in the form
    # [("d", 13, 30), ("a", 4, 6, "rd")]
    # valid colors: re, wh, bk, bl
    rect = pygame.Rect(0, 0, OFFSET, OFFSET)
    change_list = []
    delqueue = deque()
    addqueue = deque()
    while len(deltas) != 0:
        d = deltas.pop()
        change_list.append(pygame.Rect(d[1], d[2], OFFSET, OFFSET))
        if d[0] == "d":
            delqueue.append((d[1], d[2]))
        elif d[0] == "a":
            addqueue.append((d[1], d[2], get_color(d[3])))
    
    for d_coord in delqueue:
        temprect = rect.move(d_coord[1] * OFFSET, d_coord[0] * OFFSET)
        # TODO generalize background color
        pygame.draw.rect(screen, BLACK, temprect)

    for a_coord in addqueue:
        temprect = rect.move(a_coord[1] * OFFSET, a_coord[0] * OFFSET)
        pygame.draw.rect(screen, a_coord[2], temprect)

    return change_list

# Return 0 to exit the program, 1 for a one-player game
def menu(screen):
    font = pygame.font.Font(None, 30)
    menu_message1 = font.render("Presiona enter, T para dos jugadores", True, WHITE)
    menu_message2 = font.render("Primero juagdor color rojo, Azul es el segundo", True, WHITE)

    screen.fill(BLACK)
    screen.blit(menu_message1, (32, 32)) 
    screen.blit(menu_message2, (32, 64))
    pygame.display.update()
    while True: 
        done = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 1
                if event.key == pygame.K_t:
                    return 2
                if event.key == pygame.K_l:
                    return 3
                if event.key == pygame.K_n:
                    return 4
        if done:
            break
    if done:
        pygame.quit()
        return 0

def quit(screen):
    return False

def move(snake):
    if len(snake.nextDir) != 0:
        next_dir = snake.nextDir.pop()
    else:
        next_dir = snake.direction
    head = snake.deque.pop()
    snake.deque.append(head)
    next_move = head
    if (next_dir == DIRECTIONS.Up):
        if snake.direction != DIRECTIONS.Down:
            next_move =  (head[0] - 1, head[1], snake.get_color())
            snake.direction = next_dir
        else:
            next_move =  (head[0] + 1, head[1], snake.get_color())
    elif (next_dir == DIRECTIONS.Down):
        if snake.direction != DIRECTIONS.Up:
            next_move =  (head[0] + 1, head[1], snake.get_color())
            snake.direction = next_dir
        else:
            next_move =  (head[0] - 1, head[1], snake.get_color())
    elif (next_dir == DIRECTIONS.Left):
        if snake.direction != DIRECTIONS.Right:
            next_move =  (head[0], head[1] - 1, snake.get_color())
            snake.direction = next_dir
        else:
            next_move =  (head[0], head[1] + 1, snake.get_color())
    elif (next_dir == DIRECTIONS.Right):
        if snake.direction != DIRECTIONS.Left:
            next_move =  (head[0], head[1] + 1, snake.get_color())
            snake.direction = next_dir
        else:
            next_move =  (head[0], head[1] - 1, snake.get_color())
    return next_move

def is_food(board, point):
    return board[point[0]][point[1]] == 2


# Return false to quit program, true to go to
# gameover screen
def one_player(screen): 
    clock = pygame.time.Clock()
    spots = make_board()

    snake = Snake()
    # Board set up
    spots[0][0] = 1
    food = find_food(spots)

    while True:
        clock.tick(15)
        # Event processing
        done = False
        events = pygame.event.get()
        for event in events: 
            if event.type == pygame.QUIT:
                print("Quit given")
                done = True
                break
        if done:
            return False

        snake.populate_nextDir(events, "arrows")

        # Game logic
        next_head = move(snake)
        if (end_condition(spots, next_head)):
            return snake.tailmax

        if is_food(spots, next_head):
            snake.tailmax += 4
            food = find_food(spots)

        snake.deque.append(next_head)

        if len(snake.deque) > snake.tailmax:
            snake.deque.popleft()

        # Draw code
        screen.fill(BLACK)  # makes screen black

        spots = update_board(screen, [snake], food)

        pygame.display.update()

def two_player(screen):
    clock = pygame.time.Clock()
    spots = make_board()

    snakes = [Snake(DIRECTIONS.Right, (0, 0, RED), RED), Snake(DIRECTIONS.Right, (5, 5, BLUE), BLUE)]
    for snake in snakes:
        point = snake.deque.pop()
        spots[point[0]][point[1]] = 1
        snake.deque.append(point)
    food = find_food(spots)

    while True:
        clock.tick(15)
        done = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                done = True
                break
        if done:
            return False
        snakes[0].populate_nextDir(events, "arrows")
        snakes[1].populate_nextDir(events, "wasd")

        for snake in snakes:
            next_head = move(snake)
            if (end_condition(spots, next_head)):
                return snake.tailmax

            if is_food(spots, next_head):
                snake.tailmax += 4
                food = find_food(spots)

            snake.deque.append(next_head)

            if len(snake.deque) > snake.tailmax:
                snake.deque.popleft()

        screen.fill(BLACK)

        spots = update_board(screen, snakes, food)

        pygame.display.update()

def network_nextDir(events, net_id):
    # assume "arrows"
    enc_dir = ""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                enc_dir += net_id + "u"
            elif event.key == pygame.K_DOWN:
                enc_dir += net_id + "d"
            elif event.key == pygame.K_RIGHT:
                enc_dir += net_id + "r"
            elif event.key == pygame.K_LEFT:
                enc_dir += net_id + "l"
    return enc_dir

def encode_deltas(delta_str):
    # delta_str is in the form
    # "(15 23 bk)(22 12 fo)(10 11 rm)"
    deltas = deque()
    state = "open"
    while len(delta_str) != 0:
        if state == "open":
            encoded_delta = ["fx", 0, 0, "fx"]
            delta_str = delta_str[1:]
            on_num = 1
            store_val = ""
            state = "num"
        if state == "num":
            if delta_str[0] == " ":
                delta_str = delta_str[1:]
                encoded_delta[on_num] = int(store_val)
                store_val = ""
                on_num += 1
                if on_num > 2:
                    state = "color"
            else:
                store_val += delta_str[0]
                delta_str = delta_str[1:]
        if state == "color":
            if delta_str[0] == ")":
                if store_val == "rm":
                    encoded_delta[0] = "d"
                elif store_val == "fo":
                    encoded_delta[0] = "a"
                    encoded_delta[3] = "fo"
                else:
                    encoded_delta[0] = "a"
                    encoded_delta[3] = store_val
                delta_str = delta_str[1:]
                state = "open"
                deltas.appendleft(encoded_delta)
            else:
                store_val += delta_str[0]
                delta_str = delta_str[1:]
    return deltas
                
def client(screen):
    HOST, PORT = "samertm.com", 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((HOST, PORT))
    net_id = s.recv(1024)
    net_id = net_id.decode("utf-8")
    fake_snake= Snake()
    screen.fill(BLACK)
    pygame.display.update()
    
    while True:
        done = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                done = True
        if done:
            return False
        send_data = network_nextDir(events, net_id)
        if send_data != "":
            s.sendall(send_data.encode("utf-8"))

        read, _write, _except = select.select([s], [], [])
        recv_data = ""

        if len(read) != 0:
            recv_data = read[0].recv(1024)
            recv_data = recv_data.decode("utf-8")
            if recv_data == "":
                break
            deltas = encode_deltas(recv_data)
            change_list = update_board_delta(screen, deltas)
            pygame.display.update()

        
def game_over(screen, eaten):
    message1 = "You ate %d foods" % eaten
    message2 = "Press enter to play again, esc to quit."
    game_over_message1 = pygame.font.Font(None, 30).render(message1, True, BLACK)
    game_over_message2 = pygame.font.Font(None, 30).render(message2, True, BLACK)

    overlay = pygame.Surface((BOARD_LENGTH * OFFSET, BOARD_LENGTH * OFFSET))
    overlay.fill((84, 84, 84))
    overlay.set_alpha(150)
    screen.blit(overlay, (0,0))

    screen.blit(game_over_message1, (35, 35))
    screen.blit(game_over_message2, (65, 65))
    game_over_message1 = pygame.font.Font(None, 30).render(message1, True, WHITE)
    game_over_message2 = pygame.font.Font(None, 30).render(message2, True, WHITE)
    screen.blit(game_over_message1, (32, 32))
    screen.blit(game_over_message2, (62, 62))
   
    pygame.display.update()

    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    return True

def leaderboard(screen):
    font = pygame.font.Font(None, 30)
    screen.fill(BLACK)
    try:
        with open("leaderboard.txt") as f:
            lines = f.readlines()
            titlemessage = font.render("Leaderboard", True, WHITE)
            screen.blit(titlemessage, (32, 32))
            dist = 64
            for line in lines:
                delimited = line.split(",")
                delimited[1] = delimited[1].strip()
                message = "{0[0]:.<10}{0[1]:.>10}".format(delimited)
                rendered_message = font.render(message, True, WHITE)
                screen.blit(rendered_message, (32, dist))
                dist += 32
    except IOError:
        message = "Nothing on the leaderboard yet."
        rendered_message = font.render(message, True, WHITE)
        screen.blit(rendered_message, (32, 32))

    pygame.display.update()

    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    return True
#Fin de funciones


#Función principal
def main():
    pygame.init()
    screen = pygame.display.set_mode([BOARD_LENGTH * OFFSET,
        BOARD_LENGTH * OFFSET])
    pygame.display.set_caption("Mike's Sanke")
    thing = pygame.Rect(10, 10, 50, 50)
    pygame.draw.rect(screen,pygame.Color(255,255,255,255),pygame.Rect(50,50,10,10))
    first = True
    playing = True
    while playing:
        if first or pick == 3:
            pick = menu(screen)

        options = {0 : quit,
                1 : one_player,
                2 : two_player,
                3 : leaderboard,
                4 : client }
        now = options[pick](screen)
        if now == False:
            break
        elif pick == 1 or pick == 2:
            eaten = now / 4 - 1
            playing = game_over(screen, eaten)
            first = False

    pygame.quit()

if __name__ == "__main__":
    main()