import pygame, sys
import os
import time
import random
pygame.font.init() #so that we can later choose a font for our texts

#create the pygame window
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Load all the images using the os.path.join method. This basically indicates that the image that has to be loaded can be found in the "assets" folder, and we specify its name.
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Import the image for the player 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# import the different lasers of the specific ships
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))


class Button(): #define how the buttons work for the main menu
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image #start by identifying the properties of the rectangles in the main menu put over the texts, and use as a surface to be clicked.
        self.x_pos = pos[0] #define its x position
        self.y_pos = pos[1] #define its y position
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color 
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos)) #set the position of the image
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos)) #set the position of the text

    def update(self, screen): #to put the elements on the screen
        if self.image is not None:
            screen.blit(self.image, self.rect) #the blit function puts the image on the screen where we positioned our rect
        screen.blit(self.text, self.text_rect) #the text is put on the screen where we set its rect

    def checkForInput(self, position):#checks wether a positions coordinates are within our defined buttons. Later, the connection of this position and the mouse will be made
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom): #if the position is within the button's left to right boarder of its x position, and top to button boarders of the y position, it outputs TRUE, otherwise FALSE
            return True
        return False

    def changeColor(self, position):#function that makes the color of the text change when we go over it with the mouse, or so called "hover"
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom): #if we are within the (x,y) coordinates of the button, the text of the button changes color to its defined hovering color
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color) #if we are not on the button, the text stays in its initial color

pygame.init()

SCREEN = pygame.display.set_mode((750, 750))
pygame.display.set_caption("Main Menu")#set the name of the pygame window to main menu

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Background.png")), (WIDTH, HEIGHT))


class Laser: #define the characteristics of lasers
    def __init__(self, x, y, img):
        self.x = x #define x coordinates
        self.y = y #define y coordinates
        self.img = img
        self.mask = pygame.mask.from_surface(self.img) #define the laser hitbox

    def draw(self, window):
        window.blit(self.img, (self.x, self.y)) #draw the laser on the screen

    def move(self, vel):
        self.y += vel #the laser only moves vertically, so only define velocity in y coordinate 

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0) #define what qualifies as off-screen, so later we can delete the laser when it goes beyond the boarders of our screen

    def collision(self, obj):
        return collide(self, obj) #using the collide function below, we use the hitboxes created to define if a laser hit a ship 


class Ship: #this general class will be used for properties that both enemy and player ship share so they all are in one place.
    COOLDOWN = 30 #define the cooldown of our laser to 0.5s (30 at 60fps = 0.5s)

    def __init__(self, x, y, health=100): #function that determines the position of the ship at all times, and its health.
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window): #draw the ship onto the screen
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT): #if the laser goes outside of the screen, remove it
                self.lasers.remove(laser)
            elif laser.collision(obj): #if laser touches an object, substract 10 from the object's health and remove the laser 
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self): #manage the laser cooldown time. If the cooldown value is = 0, then don't do anything, you are ready to shoot. If the cooldown value is greater than 0, then increment it by 1 until it reaches our cooldown threshold.
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self): #shoot your laser only if the cooldown time is at 0
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width() #define the width of our ship image

    def get_height(self):
        return self.ship_img.get_height() #define the height of our ship image


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP #assign the yellow spaceship image to the player
        self.laser_img = YELLOW_LASER #assign the yellow laser to the player
        self.mask = pygame.mask.from_surface(self.ship_img) # creates the hitbox for the ship by putting it into a rectangle.
        self.max_health = health #to set the health bar

    def move_lasers(self, vel, objs): #using a similar laser function as in the class Ship above, we adapt it to our player specifically
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel) #define the laser speed
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj) #instead of removing health from the enemies when a laser touches them, we just make them disapear, by taking them off of the list. 
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window): #draw the healthbar, by making a red rectangle, and a green rectangle superpose, and when we loose health, the green rectangle is reduced so that we see the red rectangle appear underneath. 
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship): #create the enemy ships 
    #create a dictionary that defines the different colored spaceships according to their images, and their respective lasers
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health) 
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img) #create the hitbox for the enemy ships

    def move(self, vel): #function defining the movements of the enemy ships. They only need to go down, so only y coordinates
        self.y += vel

    def shoot(self): #define how enemies shoot their lasers
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img) #substract 20 from x position of enemies, so that the lasers seem to come out from the center of the enemies and not the side. 
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2): # here we use the preestablished hitboxes and make them even more precise. Using the overlap function, we want to only signal a collision if the laser touches one of the pixels of the ship, and not the shape that was drawn around it by the mask. 
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None 

def main(): #define the main game loop, where all the previoussly put up functions are put together to make the actual game run
    # changing the Background image and using the scale function in order to make the image fill the whole screen, basically increasing the image size to the (width, height) defined above as the size of the window
    BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
    pygame.display.set_caption("Ultimate Space Invaders") #change the window name 
    run = True # to identify if the game is running or not
    FPS = 120 #set the framerate to 120 fps
    level = 0 #start at level 0, but once we start playing, add 1 to be at level 1
    lives = 5 #start with 5 lives
    main_font = pygame.font.Font("assets/font.ttf", 20) #defines the font and the size of text in the game mode
    lost_font = pygame.font.Font("assets/font.ttf", 30) #same for when we lose 

    enemies = []
    wave_length = 5
    enemy_vel = 1 #define enemy speed as 1 in the beginning

    player_vel = 5 #define the speed of the player. Every time you press a directional key, the player moves 5 pixels 
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock() #set the speed of the game to 120 fps, 120 times per second the game will check for updates.

    lost = False
    lost_count = 0

    def redraw_window(): #function to redraw everything in the window in 120 fps, so that every object's position is updated
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255)) #draw the number of lives we have, using a RGB code for the color white
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255)) # draw levels

        WIN.blit(lives_label, (10, 10)) #defines the position of the lives counter
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10)) #position of the levels counter, by aligning it according to the width, so if we change the width, it will still be alligned

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost: #draw the message if we have lost
            lost_label = lost_font.render("GAME OVER", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) #center the text in the middle of our window

        pygame.display.update() 

    while run:
        clock.tick(FPS) #linked with the clock function, checking for new updates 120 times per second while the game is running
        redraw_window()

        if lives <= 0 or player.health <= 0: #if there are no more lives, or no more health, create the state where we lost, the message is defined above. 
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 1.5: #make the "GAME OVER" text appear for 3 seconds (1.5x120fps = 3 seconds).
                run = False #while the text apprars, the loop is cut here, and so the game doesn't continue running
                main_menu() #send the player back to the main menu when lost
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5 #every wave, the number of enemies is increasd by 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"])) # spawns a random enemy, in a radnom place within our x coordinates of the screen. The y coordinates are limited to above the screen, so that enemies spawn outside and appear on the screen later when they come down
                enemies.append(enemy)

        for event in pygame.event.get(): #60 times every second, this loop will check if there has been any actions corresponding to the code
            if event.type == pygame.QUIT: #if the quit button is clicked, it will stop checking for updates and stop the game from running coming back to the start window.
                run = False 
                main_menu() #send the player back to the main menu when he quits the playing mode

        keys = pygame.key.get_pressed() #calls a dictionnary with all the keys, and tells us if they are getting pressed or not
        if keys[pygame.K_a] and player.x - player_vel > 0: #Press key A to go left. Put a restriction so that it doesn't go off the screen.
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #Press key D to go right + restriction using the width of our ship image 
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #Press key W to go up + restriction
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: #Press key S to go down + restriction using the height of our ship image
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1: #create a randomizer so that the enemy has a 50% probability to shoot every second
                enemy.shoot()

            if collide(enemy, player): # if the enemy and the player collide, the health of the player is reduced by 10, and the enemy disapears
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT: #if an enemy goes past the boarder of our screen, take out one life from the counter
                lives -= 1 
                enemies.remove(enemy) #once the enemy has disapeared, take it out of the list so that it doesn't spawn again

        player.move_lasers(-laser_vel, enemies) #here the velocity of the player's laser is negative, so that it goes up instead of down

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

    
def credits(): #create the credits accessible from the main menu
    pygame.display.set_caption("credits") #change window name
    while True:
        credits_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black") #black background
        
        #create the different texts that will appear in this section, as well as their color and placement. 
        credits_TEXT = get_font(20).render("This game has been created by:", True, "#b745cc")
        credits_RECT = credits_TEXT.get_rect(center=(375, 260)) # use the rect function to position the text, and center it around the x coordinate 375
        credits_OSCAR = get_font(25).render("Oscar Zenker", True, "#b745cc") #define the names, and their color
        credits_RUPAYA = get_font(25).render("Rupaya Goel", True, "#b745cc")
        credits_GAVIN = get_font(25).render("Gavin John Robert Campbell", True, "#b745cc")
        SCREEN.blit(credits_TEXT, credits_RECT)
        SCREEN.blit(credits_RUPAYA,(235,360)) #draw the names at specific (x,y) coordinates
        SCREEN.blit(credits_GAVIN,(55,430))
        SCREEN.blit(credits_OSCAR,(225,500))

        credits_BACK = Button(image=None, pos=(375, 660), #create the button that leads back to the main menu
                            text_input="BACK", font=get_font(30), base_color="#b745cc", hovering_color="White") #add in the hovering functionality defined above to make it change color to white when we hover above it

        credits_BACK.changeColor(credits_MOUSE_POS)
        credits_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #if we quit the game from the credits page, the pygame window is closed
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if credits_BACK.checkForInput(credits_MOUSE_POS): #if we use the back button, we are sent back to the main menu
                    main_menu()

        pygame.display.update()
        
def main_menu(): #create the main menu screen
    pygame.display.set_caption("Main Menu") #when coming back to the menu, the window name is changed again to Main Menu
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos() #get the mouse's position so we know when we are hovering above text so it can change color

        #create the text for the main menu, as well as the buttons' text, its position, and its color
        MENU_TEXT = get_font(25).render("Welcome to", True, "#b745cc") 
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100))
        MENU_NAME = get_font(30).render("Ultimate Space Invaders", True, "#b745cc") 
        

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(375, 300), #create the PLAY text, and put the translucid rectangle over it that acts as the surface we can click on, and hover our mouse over to make the PLAY text change color
                            text_input="PLAY", font=get_font(35), base_color="White", hovering_color="#b745cc")
        credits_BUTTON = Button(image=pygame.image.load("assets/credits Rect.png"), pos=(375, 475), #same as for PLAY
                            text_input="CREDITS", font=get_font(35), base_color="White", hovering_color="#b745cc")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(375, 650), #same as for PLAY
                            text_input="QUIT", font=get_font(35), base_color="White", hovering_color="#b745cc")

        SCREEN.blit(MENU_TEXT, MENU_RECT)
        SCREEN.blit(MENU_NAME, (35, 150)) #draw the text on the screen

        for button in [PLAY_BUTTON, credits_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS) #link the hovering function with the mouse positon, so it only changes color when the mouse is within the translucid rectangle's area
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #if the red quit button is clicked, the pygame window is closed
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS): #if the play button is clicked, the main() is launched, and the game can start
                    main()
                if credits_BUTTON.checkForInput(MENU_MOUSE_POS): #if the credits button is clicked, the credits window is opened
                    credits()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):#if the quit button is clicked, the pygame window is closed.
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()