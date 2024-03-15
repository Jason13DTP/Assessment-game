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
ENEMY_MOVEMENT_SPEED = 1

#Constants for scaling
CHARACTER_SCALING = .5
TILE_SCALING = 0.25

#Lists
direction = [0, 0]


#Class
class myGame(arcade.Window):
    """
    Main Class
    """

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        #Player sprite variable
        self.player_sprite = None

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

        #Enemy health
        self.enemy_max_health = 20
        self.enemy_health = 20

        #Player attack
        self.player_attack = None

        #Dash ability
        self.dashing = None
        self.dash_start = 0

        #Dash cooldown
        self.dash_cooldown = 0
        self.can_dash = None
        
        #Dash indicator level
        self.dash_indicator_level = 0

        #Time stop ability
        self.time_stop = None

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
        self.enemy_sprite.center_x = 800
        self.enemy_sprite.center_y = 450
        self.scene.add_sprite("Enemy", self.enemy_sprite)


        #Player sprite
        #player_img = "Assets\Images\player.png"
        player_img = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(player_img, CHARACTER_SCALING)
        self.player_sprite.center_x = 800
        self.player_sprite.center_y = 450
        self.scene.add_sprite("Player", self.player_sprite)


        #Cooldown indicator
        indicator_img = f"Assets/Dash indicator/Dash_level_{self.dash_indicator_level + 1}.png"
        self.cooldown_sprite = arcade.Sprite(indicator_img, 2)
        self.cooldown_sprite.center_x = 1570
        self.cooldown_sprite.center_y = 30
        self.scene.add_sprite("Cooldown", self.cooldown_sprite)

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
        arcade.draw_text(
            health_text,
            10,
            10,
            arcade.color.WHITE,
            18,
        )


    def update_player_speed(self):
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
        
        
        
        #Dashing ability
        if self.dashing == True:
            self.player_sprite.change_y = PLAYER_DASH_SPEED * direction[0]
            self.player_sprite.change_x = PLAYER_DASH_SPEED * direction[1]
            self.dash_start += 1
            if self.dash_start == 10:
                self.dashing = False
                self.dash_cooldown = 0
                self.dash_start = 0
                if self.dashing == False:
                    self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED * direction[0]
                    self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED * direction[1]

        #Dash cooldown
        if self.dash_cooldown < 300:
            self.dash_cooldown += 1
            self.can_dash = False
            for i in range (1, 6):
                if self.dash_cooldown == i * 50:
                    self.dash_indicator_level = i
        if self.dash_cooldown == 300:
            self.can_dash = True


        #Enemy following player
        self.enemy_sprite.center_x += self.enemy_sprite.change_x
        self.enemy_sprite.center_y += self.enemy_sprite.change_y

        start_x = self.enemy_sprite.center_x
        start_y = self.enemy_sprite.center_y

        dest_x = self.player_sprite.center_x
        dest_y = self.player_sprite.center_y

        dist_x = int(dest_x - start_x)
        dist_y = int(dest_y - start_y)
        angle = math.atan2(dist_y, dist_x)
        dist_total = int(math.sqrt((dist_x**2 + dist_y**2)))


        print(dist_total, dist_x, dist_y)

        if dist_total <= 32 and dist_x != 0 and dist_y != 0:
            self.enemy_sprite.change_x = 0 
            self.enemy_sprite.change_y = 0 
        
        if self.time_stop != True and abs(dist_x) > 32 and abs(dist_y) > 32:
            self.enemy_sprite.change_x = math.cos(angle) * ENEMY_MOVEMENT_SPEED
            self.enemy_sprite.change_y = math.sin(angle) * ENEMY_MOVEMENT_SPEED

        
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