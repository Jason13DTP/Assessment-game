"""
Python Assessment game
"""

#Imports
import arcade, random, math, os

#Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Game"

VIEWPORT_MARGIN = 40

PLAYER_MOVEMENT_SPEED = 1
PLAYER_DASH_SPEED = 3
PLAYER_KNOCKBACK = 6

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

        self.character_face_direction = "right"

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        main_path = f"Assets/Images/{name_folder}"
        
        self.idle_textures = []
        for i in range(3):
            texture = load_texture_pair(f"{main_path}/idle_{i}.png")
            self.idle_textures.append(texture)

        self.walk_textures = []
        for i in range(5):
            texture = load_texture_pair(f"{main_path}/walk_{i}.png")
            self.walk_textures.append(texture)
        
        init_texture = arcade.load_texture(f"{main_path}/idle_0.png")
        self.set_hit_box(init_texture.hit_box_points)


class PlayerCharacter(Entity):
    """Player Sprite"""

    def __init__(self, name_folder):

        #Sets up parent class
        super().__init__(name_folder="Player")

    def update_animations(self, delta_time: float = 1 / 60):
        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING
        
        # Idle animation
        if self.change_x == 0:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.idle_textures[self.cur_texture][self.facing_direction]

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.facing_direction]


class Enemy(Entity):
    """Enemy Sprite"""

    def __init__(self, name_folder):

        #Sets up parent class
        super().__init__(name_folder="Enemy")

        self.should_update_walk = 0

    def update_animations(self, delta_time: float = 1 / 60):
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING
        
        if self.change_x == 0:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.idle_textures[self.cur_texture][self.facing_direction]

        # Walking animation
        if self.should_update_walk == 3:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
            self.should_update_walk = 0
            return

        self.should_update_walk += 1
    

class myGame(arcade.Window):
    """
    Main Class
    """

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(
            SCREEN_WIDTH, 
            SCREEN_HEIGHT, 
            SCREEN_TITLE, 
            center_window = True
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

        #Player health
        self.player_max_health = 100
        self.player_health = 100

        #Player attack
        self.attack = None
        self.can_attack = None

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

        self.player_sprite = PlayerCharacter("Player")
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        enemy = Enemy("Enemy")
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
        
        print(self.player_sprite.center_x, self.player_sprite.center_y)

        ###ATTACK###

        if self.attack == True:
            pass


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

            #Checks for collision between the player and enemy
            if self.invincible != True:
                enemy_collision = arcade.check_for_collision(
                    self.player_sprite, enemy)
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