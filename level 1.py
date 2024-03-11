"""
Python Assessment game
"""

#Imports
import arcade, time

#Constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Game"
PLAYER_MOVEMENT_SPEED = 5
PLAYER_DASH_SPEED = 15

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

        #Dash ability
        self.dashing = None
        self.dash_start = 0

        arcade.set_background_color(arcade.csscolor.DIM_GRAY)

    def setup(self):
        """Sets up / restarts the game."""

        #Initializes the scene
        self.scene = arcade.Scene()

        #Creates the sprite lists
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Enemy")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        

        #Player sprite
        #player_img = "Assets\Images\player.png"
        player_img = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(player_img, CHARACTER_SCALING)
        self.player_sprite.center_x = 800
        self.player_sprite.center_y = 450
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

    def on_key_press(self, key, modifiers):
        """When a key is pressed/held down."""

        if key == arcade.key.SPACE:
            self.dashing = True
        if key == arcade.key.W:
            self.player_sprite.change_y += PLAYER_MOVEMENT_SPEED
            direction[0] = 1
        elif key == arcade.key.S:
            self.player_sprite.change_y += -PLAYER_MOVEMENT_SPEED
            direction[0] = -1
        elif key == arcade.key.D:
            self.player_sprite.change_x += PLAYER_MOVEMENT_SPEED
            direction[1] = 1
        elif key == arcade.key.A:
            self.player_sprite.change_x += -PLAYER_MOVEMENT_SPEED
            direction[1] = -1

        

    def on_key_release(self, key, modifiers):
        """When a held key is released."""

        if key == arcade.key.W:
            self.player_sprite.change_y -= PLAYER_MOVEMENT_SPEED
            direction[0] = 0
        elif key ==  arcade.key.S:
            self.player_sprite.change_y -= -PLAYER_MOVEMENT_SPEED
            direction[0] = 0
        elif key ==  arcade.key.D:
            self.player_sprite.change_x -= PLAYER_MOVEMENT_SPEED
            direction[1] = 0
        elif key ==  arcade.key.A:
            self.player_sprite.change_x -= -PLAYER_MOVEMENT_SPEED
            direction[1] = 0
        

        

    def on_update(self, delta_time):
        """Runs the game"""

        if self.dashing == True:
            self.player_sprite.change_y = PLAYER_DASH_SPEED * direction[0]
            self.player_sprite.change_x = PLAYER_DASH_SPEED * direction[1]
            self.dash_start += 1
            if self.dash_start == 20:
                self.dashing = False
                self.dash_start = 0
                if self.dashing == False:
                    self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED * direction[0]
                    self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED * direction[1]

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