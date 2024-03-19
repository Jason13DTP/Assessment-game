"""
Python Assessment game
"""

#Imports
import arcade, random, math

#Constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Game"

PLAYER_MOVEMENT_SPEED = 5
PLAYER_DASH_SPEED = 15
PLAYER_KNOCKBACK = 30

ENEMY_MOVEMENT_SPEED = 1

#Constants for scaling
TILE_SCALING = 0.25
CHARACTER_SCALING = TILE_SCALING * 2
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

PLAYER_START_X = SPRITE_PIXEL_SIZE * TILE_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING * 1

RIGHT_FACING = 0
LEFT_FACING = 1
#DOWN_FACING = 2
#UP_FACING = 3

LAYER_NAME_PLAYER = "Player"

#Lists
direction = [0, 0]


#Functions
def load_texture(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return arcade.load_texture(filename)



#Class
class PlayerCharacter(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):

        #Sets up parent class
        super().__init__()

        #Default facing direction
        self.character_face_direction = "right"

        # Set initial position
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

        #Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        main_path = "Assets/Images/Player"

        #Load texture for idle standing
        self.idle_texture = []
        for i in range (3):
            texture = load_texture(f"{main_path}/Idle/{self.character_face_direction}_{i}.png")
            self.idle_texture.append(texture)

        self.walk_textures = []
        for i in range(5):
            texture = load_texture(f"{main_path}/Move/{self.character_face_direction}_{i}.png")
            self.walk_textures.append(texture)

        #Set the initial texture
            self.texture = self.idle_texture[0]

    def update_animation(self, delta_time: float = 1 / 60):
        """Update the animation of the character"""

        if self.change_x < 0 and self.character_face_direction == "right":
            self.character_face_direction = "left"
        elif self.change_x > 0 and self.character_face_direction == "left":
            self.character_face_direction = "right"
        
        
        
        # Idle animation
        
        if self.change_x == 0:
            self.texture = self.idle_texture[self.character_face_direction]


        #Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.cur_texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class myGame(arcade.Window):
    """
    Main Class
    """

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        #Player sprite variable
        self.player_sprite = None
        self.player_img = None

        #Scene
        self.scene = None

        #Physics engine
        self.physics_engine = None

        #Key pressed
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        #Player health
        self.player_max_health = 100
        self.player_health = 100

        #Player attack
        self.player_attack = None

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

        #Animations
        self.idle_up_textures = []
        self.idle_down_textures = []
        self.idle_left_textures = []
        self.idle_right_textures = []
        self.walk_up_textures = []
        self.walk_down_textures = []
        self.walk_left_textures = []
        self.walk_right_textures = []

        self.face_direction = RIGHT_FACING

        self.cur_texture_index = 0
        self.frame_delay = 5
        self.is_attacking = False


        arcade.set_background_color(arcade.csscolor.DIM_GRAY)

    def setup(self):
        """Sets up / restarts the game."""

        #Initializes the scene
        self.scene = arcade.Scene()

        #Sets up the camera
        self.gui_camera = arcade.Camera(self.width, self.height)

        #Creates the sprite lists
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Enemy")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        
        #Enemy sprite
        enemy_img = ":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png"
        self.enemy_sprite = arcade.Sprite(enemy_img, CHARACTER_SCALING)
        self.enemy_sprite.center_x = 400
        self.enemy_sprite.center_y = 450
        self.scene.add_sprite("Enemy", self.enemy_sprite)


        #Player sprite
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)
        

        #Creates the physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
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
        self.cooldown_sprite.center_x = 1570
        self.cooldown_sprite.center_y = 30
        self.scene.add_sprite("Cooldown", self.cooldown_sprite)


    def update_player_speed(self):
        """Moves the player according to the direction they are facing"""
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            direction[0] = 1
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
            direction[0] = -1
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            direction[1] = -1
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            direction[1] = 1

        if self.right_pressed and self.left_pressed:
            self.player_sprite.change_x = 0
            direction[1] = 0
        if self.up_pressed and self.down_pressed:
            self.player_sprite.change_y = 0
            direction[0] = 0
            
        if not self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = 0
            direction[1] = 0
        if not self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = 0
            direction[0] = 0

    def on_key_press(self, key, modifiers):
        """When a key is pressed/held down."""

        if key == arcade.key.SPACE:
            if self.can_dash == True:
                self.dashing = True
        
        if key == arcade.key.G:
            self.time_stop = not self.time_stop
            
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

        print(PlayerCharacter().character_face_direction)
        
        ###DASHING ABILITY###

        #Dashing ability
        if self.dashing == True:
            self.player_sprite.change_y = PLAYER_DASH_SPEED * direction[0]
            self.player_sprite.change_x = PLAYER_DASH_SPEED * direction[1]
            self.dash_start += 1
            self.dash_indicator_level = 0
            if self.dash_start == 10:
                self.dashing = False
                self.dash_cooldown = -1
                self.dash_start = 0
                if self.dashing == False:
                    self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED * direction[0]
                    self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED * direction[1]

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


        ###ENEMY FOLLOWING PLAYER###
            
        #Enemy following player
        self.enemy_sprite.center_x += self.enemy_sprite.change_x
        self.enemy_sprite.center_y += self.enemy_sprite.change_y

        #Records the enemy's position
        start_x = self.enemy_sprite.center_x
        start_y = self.enemy_sprite.center_y

        #Records the player's position
        dest_x = self.player_sprite.center_x
        dest_y = self.player_sprite.center_y

        #Calculates the x and y distance between the enemy and the player
        dist_x = int(dest_x - start_x)
        dist_y = int(dest_y - start_y)
        #Using trig to find the angle difference between the player and enemy
        angle = math.atan2(dist_y, dist_x)


        ###COLLISION###

        #Checks for collision between the player and enemy
        if self.invincible != True:
            enemy_collision = arcade.check_for_collision(self.player_sprite, self.enemy_sprite)
        else:
            enemy_collision = False

        #Variable that stops all enemies from following the player
        if self.time_stop != True:
            self.enemy_follow = True
        if self.time_stop == True:
            self.enemy_follow = False

        #Making the enemy follow the player precicely using trig
        if self.enemy_follow == True:
            self.enemy_sprite.change_x = math.cos(angle) * ENEMY_MOVEMENT_SPEED
            self.enemy_sprite.change_y = math.sin(angle) * ENEMY_MOVEMENT_SPEED
        #Stops the enemy if there is collision
        elif self.enemy_follow == False:
            self.enemy_sprite.change_x = 0
            self.enemy_sprite.change_y = 0

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
                self.player_sprite.center_x += math.cos(angle) * PLAYER_DASH_SPEED
                self.player_sprite.center_y += math.sin(angle) * PLAYER_DASH_SPEED
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

        
        #Updates animation
            self.scene.update_animation(
                delta_time, ["Player", "Enemy", "Walls"]
            )

        self.physics_engine.update()



#Functions
def main():
    """
    Main function
    """
    window = myGame()
    window.setup()
    arcade.run()


#Main code
if __name__ == "__main__":
    main()