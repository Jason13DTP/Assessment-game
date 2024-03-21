"""
Python Assessment game
"""

#Imports
import arcade, random, math, os, arcade.gui

#Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Game"

VIEWPORT_MARGIN = 40

PLAYER_MOVEMENT_SPEED = 2
PLAYER_DASH_SPEED = 6
KNOCKBACK = 12

ENEMY_MOVEMENT_SPEED = 0.5

#Constants for scaling
TILE_SCALING = 0.1
CHARACTER_SCALING = 1
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = SCREEN_HEIGHT / 2

RIGHT_FACING = 0
LEFT_FACING = 1
#DOWN_FACING = 2
#UP_FACING = 3

LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemy"
LAYER_NAME_WALLS = "Wall"
LAYER_NAME_ATTACK = "Attack"

#Lists
direction = [0, 0]


#Functions

def load_texture_pair(filename):
    """Loads a texture pair"""
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

#Class
class Entity(arcade.Sprite):
    
    def __init__(self, name_folder):
        super().__init__()

        self.facing_direction = RIGHT_FACING
        self.cur_texture = 0
        self.frame_time = 10
        self.next_frame = 0
        self.scale = CHARACTER_SCALING

        main_path = f"Assets/Images/{name_folder}"
        
        self.idle_textures = []
        for i in range(3):
            texture = load_texture_pair(f"{main_path}/idle_{i}.png")
            self.idle_textures.append(texture)

        self.walk_textures = []
        for i in range(0, 6):
            texture = load_texture_pair(f"{main_path}/walk_{i}.png")
            self.walk_textures.append(texture)
        
        init_texture = arcade.load_texture(f"{main_path}/idle_0.png")
        self.set_hit_box(init_texture.hit_box_points)

        self.texture = self.walk_textures[0][0]


class PlayerCharacter(Entity):
    """Player Sprite"""
    def __init__(self, name_folder):
        #Sets up parent class
        super().__init__(name_folder="Player")

        
        
    def update_animation(self, delta_time: float = 1 / 60):
        # Figure out if we need to flip face left or right
        if self.change_x > 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x < 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 2:
                    self.cur_texture = 0
                self.texture = self.idle_textures[self.cur_texture][self.facing_direction]
                self.next_frame = 0
        else:
            # Walking animation
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 5:
                    self.cur_texture = 0
                self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
                self.next_frame = 0
            


class Enemy(Entity):
    """Enemy Sprite"""

    def __init__(self, name_folder):

        #Sets up parent class
        super().__init__(name_folder="Enemy")

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x > 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x < 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING
        
        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 2:
                    self.cur_texture = 0
                self.texture = self.idle_textures[self.cur_texture][self.facing_direction]
                self.next_frame = 0
        else:
            # Walking animation
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 5:
                    self.cur_texture = 0
                self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
                self.next_frame = 0

class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class StartButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.close_window()
        window = gameView()
        window.setup()
        arcade.run()

class MainMenu(arcade.Window):
    """The main menu of the game"""

    def __init__(self):
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            "UIFlatButton Example",
            center_window = True,
            )

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = StartButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        # Again, method 1. Use a child class to handle events.
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

class gameView(arcade.Window):
    """
    Main Class
    """

    def __init__(self):
        
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            "Game",
            center_window = True,
        )

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)


        #Scene
        self.scene = None

        #Tile map
        self.tile_map = None

        #Physics engine
        self.physics_engine = None

        self.end_of_map = 0

        self.score = 0

        #Key pressed
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.last_direction = 0

        #Player health
        self.player_max_health = 100
        self.player_health = 100

        #Player attack
        self.attack = None
        self.can_attack = True
        self.attack_start = 0
        self.attack_damage = 5

        #Dash ability
        self.dashing = None
        self.dash_start = 0

        #Dash cooldown
        self.dash_cooldown = -1
        self.can_dash = None
        
        #Dash indicator level
        self.dash_indicator_level = 0

        #Time stop ability
        self.time_stop = False

        #Player knockback
        self.knockback = None
        self.knockback_time = 0
        self.invincible = None
        self.invincible_time = 0

        #Enemy health
        self.enemy_max_health = 20
        self.enemy_health = 20

        #Enemy attack
        self.enemy_attack = 5

        #Enemy following player
        self.enemy_follow = None

        arcade.set_background_color(arcade.csscolor.DIM_GRAY)

    def setup(self):
        """Sets up / restarts the game."""

        #Set up map
        map_name = "Assets/level1.tmx"
        
        layer_options = {
            "Wall": {
                "use_spatial_hash": True,
            },
            "Ground": {
                "use_spatial_hash": False,
            }
        }

        #Load in tile map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        #Initializes the scene
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.score = 0

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        self.player_sprite = PlayerCharacter(LAYER_NAME_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        enemy = Enemy(LAYER_NAME_ENEMIES)
        enemy.center_x = 120
        enemy.center_y = 120
        self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)

        
        

        #Creates the physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls = self.scene[LAYER_NAME_WALLS],
        )
        


    def on_draw(self):
        """Renders the screen."""
        #clears the existing screen
        self.clear()

        #Draws the sprites
        self.scene.draw()

        #Player health display
        health_text = f"Health: {self.player_health}/{self.player_max_health}"
        arcade.draw_text(health_text, 10, 10, arcade.color.WHITE, 18)

        #Cooldown indicator
        indicator_img = f"Assets/Dash indicator/Dash_level_{self.dash_indicator_level + 1}.png"
        self.cooldown_sprite = arcade.Sprite(indicator_img, 2)
        self.cooldown_sprite.center_x = SCREEN_WIDTH
        self.cooldown_sprite.center_y = 30
        self.scene.add_sprite("Cooldown", self.cooldown_sprite)

        if self.attack == False:
            self.attack_sprite.remove_from_sprite_lists()


    def update_player_speed(self):
        """Moves the player according to the direction they are facing"""
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            direction[1] = 1
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
            direction[1] = -1
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            direction[0] = -1
            self.last_direction = -1
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            direction[0] = 1
            self.last_direction = 1

        if self.right_pressed and self.left_pressed:
            self.player_sprite.change_x = 0
            direction[0] = 0
        if self.up_pressed and self.down_pressed:
            self.player_sprite.change_y = 0
            direction[1] = 0
            
        if not self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = 0
            direction[0] = 0
        if not self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = 0
            direction[1] = 0

    def on_key_press(self, key, modifiers):
        """When a key is pressed/held down."""

        if key == arcade.key.SPACE:
            if self.can_dash == True:
                self.dashing = True
        
        if key == arcade.key.G:
            self.time_stop = not self.time_stop

        if key == arcade.key.F:
            if self.can_attack == True:
                self.attack = True
            
        if key == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()
        elif key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()

        

    def on_key_release(self, key, modifiers):
        """When a held key is released."""
        
        if key == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()
        elif key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()

    def on_update(self, delta_time):
        """Runs the game"""

        self.physics_engine.update()

        
        self.scene.update_animation(
            [
                LAYER_NAME_PLAYER,
                LAYER_NAME_ENEMIES
            ]
        )

        self.scene.update([LAYER_NAME_ENEMIES])

        ###ATTACK###
        attack_img = "Assets/Images/Stuff/swing.png"
        self.attack_sprite = arcade.Sprite(attack_img, CHARACTER_SCALING)

        if self.last_direction == 1:
            self.attack_sprite = arcade.Sprite(attack_img, CHARACTER_SCALING)
            self.attack_sprite.center_x = self.player_sprite.center_x + 10
            self.attack_sprite.center_y = self.player_sprite.center_y
        elif self.last_direction == -1:
            self.attack_sprite = arcade.Sprite(attack_img, CHARACTER_SCALING, flipped_horizontally=True)
            self.attack_sprite.center_x = self.player_sprite.center_x - 10
            self.attack_sprite.center_y = self.player_sprite.center_y



        if self.attack == True:
            self.scene.add_sprite(LAYER_NAME_ATTACK, self.attack_sprite)
            self.can_attack = False
            
            if self.attack_start < 20:
                self.attack_start += 1
            else:
                self.attack_start = 0
                self.attack = False
                self.can_attack = True
            



        ###DASHING ABILITY###

        #Dashing ability
        if self.dashing == True:
            self.player_sprite.change_y = PLAYER_DASH_SPEED * direction[1]
            self.player_sprite.change_x = PLAYER_DASH_SPEED * direction[0]
            self.dash_start += 1
            self.dash_indicator_level = 0
            if self.dash_start == 10:
                self.dashing = False
                self.dash_cooldown = -1
                self.dash_start = 0
                if self.dashing == False:
                    self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED * direction[1]
                    self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED * direction[0]

        #Dash cooldown
        if self.dash_cooldown < 300:
            self.dash_cooldown += 1
            self.can_dash = False
            for i in range (0, 5):
                if self.dash_cooldown == i * 60:
                    self.dash_indicator_level = i
        if self.dash_cooldown == 300:
            self.dash_indicator_level = 5
            self.can_dash = True


        ###ENEMY###
            
        #Enemy following player
        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            enemy.center_x += enemy.change_x
            enemy.center_y += enemy.change_y

            #Records the enemy's position
            start_x = enemy.center_x
            start_y = enemy.center_y

            #Records the player's position
            dest_x = self.player_sprite.center_x
            dest_y = self.player_sprite.center_y

            #Calculates the x and y distance between the enemy and the player
            dist_x = int(dest_x - start_x)
            dist_y = int(dest_y - start_y)
            #Using trig to find the angle difference between the player and enemy
            angle = math.atan2(dist_y, dist_x)


            ###COLLISION###
            enemy_hit = arcade.check_for_collision(
                self.attack_sprite, enemy
            )
            if enemy_hit == True:
                self.enemy_health -= self.attack_damage
                enemy.center_x -= math.cos(angle) * KNOCKBACK
                enemy.center_y -= math.sin(angle) * KNOCKBACK
            print(self.enemy_health)


            #Checks for collision between the player and enemy
            if self.invincible != True:
                enemy_collision = arcade.check_for_collision(
                    self.player_sprite, enemy
            )
            else:
                enemy_collision = False

            #Variable that stops all enemies from following the player
            if self.time_stop != True:
                self.enemy_follow = True
            if self.time_stop == True:
                self.enemy_follow = False

            #Making the enemy follow the player precicely using trig
            if self.enemy_follow == True:
                enemy.change_x = math.cos(angle) * ENEMY_MOVEMENT_SPEED
                enemy.change_y = math.sin(angle) * ENEMY_MOVEMENT_SPEED
            #Stops the enemy if there is collision
            elif self.enemy_follow == False:
                enemy.change_x = 0
                enemy.change_y = 0

            ###KNOCKBACK AND INVINCIBLITY###
                
            #Creates player knockback if enemy collides with the player
            if enemy_collision == True:
                self.player_health -= self.enemy_attack
                self.knockback_time = 0
                self.knockback = True
                self.invincible = True
            
            #Sets how far the knockback is going to be
            if self.knockback == True:
                if self.knockback_time < 5:
                    self.player_sprite.center_x += math.cos(angle) * KNOCKBACK
                    self.player_sprite.center_y += math.sin(angle) * KNOCKBACK
                    self.knockback_time += 1
                if self.knockback_time == 5:
                    self.knockback = False

            #Sets how long the invincible period is
            if self.invincible == True:
                if self.invincible_time < 60:
                    self.invincible = True
                    self.invincible_time += 1
                if self.invincible_time == 60:
                    self.invincible = False
                    self.invincible_time = 0






#Functions
def main():
    """
    Main function
    """
    MainMenu()
    arcade.run()


#Main code
if __name__ == "__main__":
    main()