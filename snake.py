import pygame, random, time, getpass, hashlib, platform, configparser, json
from enum import Enum
from collections import namedtuple
from player import DefinePlayer
from kafka import KafkaProducer

config = configparser.ConfigParser()
config.read('config.cfg')

bootstrap_server = config['KAFKA']['bootstrap_server']
kafka_producer = KafkaProducer(bootstrap_servers=bootstrap_server)


# Get user input for their desired player name
player_window = DefinePlayer()
player_window.run()
player_name = player_window.player_name

pygame.init()
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 20

class SnakeGame:
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h

        # init user and game id
        user = getpass.getuser()
        user_encoded = user.encode("utf-8")
        hasher = hashlib.sha256()
        hasher.update(user_encoded + str(time.time()).encode("utf-8"))
        self.game_id = hasher.hexdigest()

        # init collision type
        self.collision_type = None

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        # init game state
        self.direction = Direction.RIGHT
        self.move = True

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        init_data = {"game_id": self.game_id, "user": user, "player": player_name, 
                     "screen_width": self.w, "screen_height": self.h, 
                     "platform": platform.system(), "init_time": time.time()}
        print(init_data)

        self.init_state = True

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        food_position = {"game_id": self.game_id, "food_x": x, "food_y": y, "time": time.time()}
        print(food_position)
        
    def play_step(self):
        position_data = {"game_id": self.game_id, "head_x": self.head.x, "head_y": self.head.y, "time": time.time()}
        print(position_data)

        if self.init_state:
            self.food = None
            self._place_food()
            self.init_state = False

        # 1. Collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT 
                    and self.direction != Direction.RIGHT 
                    and self.move):
                    self.direction = Direction.LEFT
                    self.move = False
                elif (event.key == pygame.K_RIGHT 
                      and self.direction != Direction.LEFT 
                      and self.move):
                    self.direction = Direction.RIGHT
                    self.move = False
                elif (event.key == pygame.K_UP 
                      and self.direction != Direction.DOWN 
                      and self.move):
                    self.direction = Direction.UP
                    self.move = False
                elif (event.key == pygame.K_DOWN
                      and self.direction != Direction.UP 
                      and self.move):
                    self.direction = Direction.DOWN
                    self.move = False
                event_data = {"game_id": self.game_id, "event_key": event.key, "time": time.time()}
                print(event_data)

        # 2. Move
        self._move(self.direction) # update the head
        self.move = True
        
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            score_data = {"game_id": self.game_id, "score": self.score, "time": time.time()}
            print(score_data)
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        # hits boundary
        if (self.head.x > self.w - BLOCK_SIZE 
            or self.head.x < 0 
            or self.head.y > self.h - BLOCK_SIZE 
            or self.head.y < 0):
           self.collision_type = "boundary"

           final_score_data = {"game_id": self.game_id, "collision_type": self.collision_type, "final_score": self.score,
                               "time": time.time()}
           print(final_score_data)
           return True
        
        # hits itself
        if self.head in self.snake[1:]:

            self.collision_type = "self"
            final_score_data = {"game_id": self.game_id, "collision_type": self.collision_type, "final_score": self.score,
                               "time": time.time()}
            print(final_score_data)
            return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
            
        self.head = Point(x, y)
   
    def show_start_screen(self):
        self.display.fill(BLACK)
        text1 = font.render(f"Welcome {player_name}!", True, WHITE)
        self.display.blit(text1, [150, self.h//2-50])
        text2 = font.render("Press any key to start the game", True, WHITE)
        self.display.blit(text2, [150, self.h//2])
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYUP:
                    waiting = False

    def show_game_over_screen(self):
        self.display.fill(BLACK)
        text1 = font.render("GAME OVER", True, WHITE)
        text2 = font.render("Your score: " + str(self.score), True, WHITE)
        text3 = font.render("Press any key to play again", True, WHITE)
        self.display.blit(text1, [150, 150])
        self.display.blit(text2, [150, 200])
        self.display.blit(text3, [150, 250])
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYUP:
                    waiting = False


if __name__ == '__main__':
    show_start_screen = True
    # game loop
    while True:
        if show_start_screen:
            game = SnakeGame()
            game.show_start_screen()
        while True:
            game_over, score = game.play_step()

            if game_over == True:
                game.show_game_over_screen()
                show_start_screen = True
                break
