import pygame, random, time, getpass, hashlib, platform, configparser, json, subprocess
from enum import Enum
from collections import namedtuple
from player import DefinePlayer
from kafka import KafkaProducer

# Read configuration from 'config.cfg' file
config = configparser.ConfigParser()
config.read('config.cfg')

# Retrieve Kafka bootstrap server from the configuration and create a Kafka producer
bootstrap_server = config['KAFKA']['bootstrap_server']
kafka_producer = KafkaProducer(bootstrap_servers=bootstrap_server)


# Open a window to get the user's desired player name
# DefinePlayer is a class defined in 'player.py' that handles this input
player_window = DefinePlayer()
player_window.run() # Run the player input window
player_name = player_window.player_name # Retrieve the entered player name

# Initialize pygame library
pygame.init()

# Define the font to be used in the game (arial, size 25)
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    """
    An enumeration representing the four possible directions in which an object can move.

    Members:
        RIGHT (int): Represents the right direction, with a value of 1.
        LEFT (int): Represents the left direction, with a value of 2.
        UP (int): Represents the upward direction, with a value of 3.
        DOWN (int): Represents the downward direction, with a value of 4.
    """
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Define a named tuple 'Point' to represent coordinates (x, y)
Point = namedtuple('Point', 'x, y')

# RGB colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

# Define block size
BLOCK_SIZE = 20

# Define framerate
SPEED = 20

class SnakeGame:
    
    def __init__(self, w=640, h=480):
        """
        Initializes a new game instance with the given width and height, and sets up the initial game state.

        This constructor method performs the following initializations:
        - Sets the game window's width and height.
        - Encodes the current user and timestamp to generate a unique game_id using SHA-256 hashing.
        - Initializes the collision type, display, clock, direction, move state, snake's position, and score.
        - Serializes and sends initialization data to the Kafka topic 'initialization'.
        - Sets the initial state flag to True.

        Parameters:
            w (int, optional): The width of the game window in pixels. Defaults to 640.
            h (int, optional): The height of the game window in pixels. Defaults to 480.

        Note:
            - This method assumes that the pygame library is being used for rendering.
            - The constants BLOCK_SIZE and player_name, along with the 'Direction' and 'Point' classes, are defined elsewhere in the code.
            - The 'kafka_producer' is a Kafka producer object.
            - The method uses system information like the current user and platform for fetching data about who the user is and which platform they use to play.

        Example:
            game = Game(w=800, h=600)
            This line creates a new game instance with a window size of 800 by 600 pixels.

        """
        self.w = w
        self.h = h

        # Initialize user and game id
        user = getpass.getuser()
        user_encoded = user.encode("utf-8")
        hasher = hashlib.sha256()
        hasher.update(user_encoded + str(time.time()).encode("utf-8"))
        self.game_id = hasher.hexdigest()

        # Initialize collision type
        self.collision_type = None

        # Initialize display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.direction = Direction.RIGHT
        self.move = True

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0

        # Create initialization data and send it JSON serialized to the Kafka topic 'initialization'
        self.init_data = {"game_id": self.game_id, "player": player_name, 
                     "screen_width": self.w, "screen_height": self.h, 
                     "platform": platform.system(), "init_time": time.time()}
        #kafka_producer.send('initializations', json.dumps(self.init_data).encode('utf-8'))

        self.init_state = True

    def _place_food(self):
        """
        Places a food item at a random location within the game window, avoiding the snake's body.

        This method randomly generates the x and y coordinates for the food, ensuring that they fall within the
        game window's boundaries and do not overlap with the snake's body. If the randomly generated food location
        does overlap with the snake, the method recursively calls itself until a valid location is found.

        After placing the food, the method serializes and sends the food's position data to the Kafka topic 'food_positions'.

        Note:
            - The constant BLOCK_SIZE and attributes like 'w', 'h', 'snake', 'food', and 'game_id' are defined elsewhere in the class.
            - The 'kafka_producer' is a valid Kafka producer object.
            - This method uses the 'Point' class to represent the coordinates, which is defined elsewhere in the code.
            - The method assumes that the food will fit within the game window given the BLOCK_SIZE.

        Example:
            Calling this method places a food item at a random location within the game window and sends the position data to Kafka.

        """
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        # Create food position data and send it JSON serialized to the Kafka topic 'food_positions'
        food_position = {"game_id": self.game_id, "food_x": x, "food_y": y, "time": time.time()}
        kafka_producer.send('food_positions', json.dumps(food_position).encode('utf-8'))
        
    def play_step(self):
        """
        Executes a single step of the game, including handling user input, moving the snake, checking for collisions,
        placing new food, updating the UI, and sending various game-related data to Kafka topics.

        The method performs the following actions in sequence:
        1. Serializes and sends the current position data to the Kafka topic 'positions'.
        2. Handles user input for controlling the snake's direction and sends event data to the Kafka topic 'events'.
        3. Moves the snake in the specified direction.
        4. Checks for collisions with the boundary or self, ending the game if a collision occurs.
        5. Places new food if the snake's head is at the food's location, and updates the score.
        Sends the score data to the Kafka topic 'scores'.
        6. Updates the UI and controls the game's speed using a clock.
        7. Returns whether the game is over and the current score.

        Returns:
            game_over (bool): True if the game is over (due to a collision); False otherwise.
            score (int): The current score of the game.

        Note:
            - The constants SPEED and BLOCK_SIZE, along with attributes like 'head', 'game_id', 'food', 'direction',
            'move', 'snake', 'clock', and 'score', are defined elsewhere in the class.
            - The 'kafka_producer' is a Kafka producer object.
            - This method assumes that the pygame library is being used for rendering and handling events.

        Example:
            game_over, score = play_step()
            This line executes a single step of the game and returns whether the game is over and the current score.

        """

        # Create position data and send it JSON serialized to the Kafka topic 'positions'
        snake_head_position_data = {"game_id": self.game_id, "head_x": self.head.x, "head_y": self.head.y, "time": time.time()}
        kafka_producer.send('snake_head_positions', json.dumps(snake_head_position_data).encode('utf-8'))

        if self.init_state:
            self.food = None
            kafka_producer.send('initializations', json.dumps(self.init_data).encode('utf-8'))
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

                # Create event data and send it JSON serialized to the Kafka topic 'events'
                event_data = {"game_id": self.game_id, "event_key": event.key, "time": time.time()}
                kafka_producer.send('events', json.dumps(event_data).encode('utf-8'))

        # 2. Move
        self._move(self.direction) # Update the head
        self.move = True
        
        self.snake.insert(0, self.head)
        
        # 3. Check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. Place new food or just move
        if self.head == self.food:
            self.score += 1 # Increment score by 1
            # create score data and send it JSON serialized to the Kafka topic 'scores'
            score_data = {"game_id": self.game_id, "score": self.score, "time": time.time()}
            kafka_producer.send('scores', json.dumps(score_data).encode('utf-8'))
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. Update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. Return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        """
        Checks if a collision has occurred in the game, either with the boundary or with the snake itself.

        This method evaluates two types of collisions:
        - Boundary collision: Occurs when the snake's head goes beyond the boundary of the game window.
        - Self collision: Occurs when the snake's head collides with any other part of its body.

        If a collision occurs, this method sets the 'collision_type' attribute to either "boundary" or "self" 
        based on the type of collision. The final data (game id, collision type, final score, and the time) of 
        the game is sent to the Kafka topic 'final_scores'.

        Returns:
            bool: True if a collision has occurred; False otherwise.

        Note:
            - The attributes 'head', 'w', 'h', 'game_id', and 'score' should be defined elsewhere in the class.
            - The constant BLOCK_SIZE should be defined elsewhere in the code, representing the size of a block in the game.

        Example:
            If the snake's head goes beyond the game window, this method will return True and set the collision_type to "boundary".

        """

        # Hits boundary
        if (self.head.x > self.w - BLOCK_SIZE 
            or self.head.x < 0 
            or self.head.y > self.h - BLOCK_SIZE 
            or self.head.y < 0):
           self.collision_type = "boundary"

           final_score_data = {"game_id": self.game_id, "collision_type": self.collision_type, "score": self.score,
                               "time": time.time()}
           kafka_producer.send('game_overs', json.dumps(final_score_data).encode('utf-8'))
           return True
        
        # Hits itself
        if self.head in self.snake[1:]:

            self.collision_type = "self"
            final_score_data = {"game_id": self.game_id, "collision_type": self.collision_type, "score": self.score,
                               "time": time.time()}
            kafka_producer.send('game_overs', json.dumps(final_score_data).encode('utf-8'))
            return True
        
        return False
        
    def _update_ui(self):
        """
        Updates the user interface by redrawing the snake, food, and score.

        This method is responsible for redrawing the game's display, including:
        - Filling the background with black color.
        - Drawing the snake's body using two shades of blue rectangles.
        - Drawing the food using a red rectangle.
        - Rendering and displaying the current score in white text at the top left corner of the display.

        The snake's body is represented by a series of rectangles, and each part of the snake is drawn using two
        rectangles. The first, larger rectangle represents the main body, and the second, smaller rectangle adds
        a shading effect.

        Note:
            - This method assumes that the pygame library is being used for rendering.
            - The constants BLACK, BLUE1, BLUE2, RED, WHITE, and BLOCK_SIZE should be defined elsewhere in the code.
            - The 'font' object should also be defined elsewhere and represents the font used for rendering the score text.

        Example:
            Calling this method updates the game's display to reflect the current state of the snake, food, and score.
        """
        self.display.fill(BLACK)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, direction):
        """
        Moves the object's head in the specified direction by a distance of BLOCK_SIZE.

        The method modifies the x and y coordinates of the object's head based on the direction passed. 
        The direction must be one of the constants from the Direction enumeration.

        Parameters:
            direction (Direction): The direction in which to move the head. It must be one of the following:
                                Direction.RIGHT, Direction.LEFT, Direction.DOWN, or Direction.UP.

        Example:
            If direction is Direction.RIGHT, the head's x coordinate is increased by BLOCK_SIZE.

        Note:
            This method is intended to be used internally, and the BLOCK_SIZE is defined elsewhere in the code.
        """
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
        """
        Displays the start screen of the game, welcoming the player and instructing them to press a key to begin.

        This method fills the display with a black background and renders two lines of text:
        - A welcome message, including the player's name.
        - Instructions to press any key to start the game.

        The method then enters a waiting loop, monitoring for key-up events or a quit event. If a key is pressed or
        the game window is closed, the method exits, allowing the game to proceed or terminate accordingly.

        Note:
            - This method assumes that the pygame library is being used for rendering.
            - The constants BLACK and WHITE, along with the 'font' object, are defined elsewhere in the code.
            - The attribute 'display' and the player_name variable are also defined elsewhere.

        Example:
            This method can be called at the beginning of the game to present the start screen to the player.
        """
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
        """
        Displays the game over screen, showing the player's final score and instructing them to press a key to restart.

        This method fills the display with a black background and renders three lines of text:
        - A "GAME OVER" message.
        - The player's final score.
        - Instructions to press any key to play again.

        The method then enters a waiting loop, monitoring for key-up events or a quit event. If a key is pressed or
        the game window is closed, the method exits, allowing the game to restart or terminate accordingly.

        Note:
            - This method assumes that the pygame library is being used for rendering.
            - The constants BLACK and WHITE, along with the 'font' object, are defined elsewhere in the code.
            - The attribute 'display' and 'score' are also defined elsewhere.

        Example:
            This method can be called at the end of the game to present the game over screen to the player.
        """
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
    show_start_screen = True  # Flag to control whether to show the start screen
    try:
        # Game loop
        while True:
            # If the start screen should be displayed, initialize a new game and show the start screen
            if show_start_screen:
                game = SnakeGame()  # Create a new game instance
                game.show_start_screen()  # Display the start screen
                show_start_screen = False  # Reset the flag

            # Main game loop
            while True:
                game_over, score = game.play_step()  # Play a single step of the game, returning game over status and score

                # If the game is over, display the game over screen and prepare to show the start screen again
                if game_over == True:
                    game.show_game_over_screen()  # Show the game over screen
                    show_start_screen = True  # Set the flag to show the start screen in the next iteration
                    break  # Exit the inner loop to restart the game
    finally:
        pygame.quit()  # Close down the Pygame window
        
        # When closing down the game, start transferring Kafka data to Postgres DB.
        script_path = "kafka_to_postgres_consumer.py"
        subprocess.Popen(['python3', script_path])  # Run the script in the background

        # Exit the main script immediately
        exit(0)
        
