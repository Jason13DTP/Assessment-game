"""
Python Assessment game
"""

# Imports
import arcade
import arcade.gui
import math
import os


# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Game"

VIEWPORT_MARGIN = 40

PLAYER_MOVEMENT_SPEED = 2
PLAYER_DASH_SPEED = 6
KNOCKBACK = 12

# Constants for scaling
TILE_SCALING = 0.1
CHARACTER_SCALING = 1
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = SCREEN_HEIGHT / 2

RIGHT_FACING = 0
LEFT_FACING = 1

LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemy"
LAYER_NAME_WALLS = "Wall"
LAYER_NAME_ATTACK = "Attack"

# Lists

direction = [0, 0]


# Functions

def load_texture_pair(filename):
    """Loads a texture pair"""
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


# Class

class Entity(arcade.Sprite):
    """Parent class for entities"""

    def __init__(self, name_folder):

        super().__init__(hit_box_algorithm=None)

        self.facing_direction = RIGHT_FACING
        self.cur_texture = 0
        self.frame_time = 10
        self.next_frame = 0
        self.scale = CHARACTER_SCALING

        # Main path for the images of the sprites
        main_path = f"Assets/Images/{name_folder}"

        # Adds the frames of the idle animation to a list
        self.idle_textures = []
        for i in range(3):
            texture = load_texture_pair(f"{main_path}/idle_{i}.png")
            self.idle_textures.append(texture)

        # Adds the frames of the walk animation to a list
        self.walk_textures = []
        for i in range(0, 6):
            texture = load_texture_pair(f"{main_path}/walk_{i}.png")
            self.walk_textures.append(texture)

        if name_folder == "Player":
            # Adds the frames of the attack animation to a list
            self.attack_textures = []
            for i in range(0, 6):
                texture = load_texture_pair(f"{main_path}/attack_{i}.png")
                self.attack_textures.append(texture)

        # Sets the initial texture for the sprites
        init_texture = arcade.load_texture(f"{main_path}/idle_0.png")
        self.set_hit_box(init_texture.hit_box_points)
        self.texture = self.walk_textures[0][0]


class PlayerCharacter(Entity):
    """Player Sprite"""

    def __init__(self, name_folder):
        # Sets up parent class
        super().__init__(name_folder="Player")

    def update_animation(self, delta_time: float = 1 / 60):
        #  Figure out if we need to flip face left or right
        if self.change_x > 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x < 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        #  Attack animation
        if self.change_x == 100:
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 5:
                    self.cur_texture = 0
                self.texture = self.attack_textures[
                    self.cur_texture
                ][self.facing_direction]
                self.next_frame = 0

        #  Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 2:
                    self.cur_texture = 0
                self.texture = (
                    self.idle_textures[
                        self.cur_texture
                    ][self.facing_direction])
                self.next_frame = 0

        else:
            #  Walking animation
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 5:
                    self.cur_texture = 0
                self.texture = (
                    self.walk_textures[
                        self.cur_texture]
                    [self.facing_direction])
                self.next_frame = 0


class Enemy(Entity):
    """Enemy Sprite"""

    def __init__(self, name_folder):

        # Sets up parent class
        super().__init__(name_folder="Enemy")

    def update_animation(self, delta_time: float = 1 / 60):
        # Determines if the player is facing left or right
        if self.change_x > 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x < 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        #  Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 2:
                    self.cur_texture = 0
                self.texture = (
                    self.idle_textures[
                        self.cur_texture
                    ][self.facing_direction])
                self.next_frame = 0

        else:
            #  Walking animation
            self.next_frame += 1
            if self.next_frame == self.frame_time:
                self.cur_texture += 1
                if self.cur_texture > 5:
                    self.cur_texture = 0
                self.texture = (
                    self.walk_textures[
                        self.cur_texture
                    ][self.facing_direction])
                self.next_frame = 0


class InstructionView(arcade.View):
    """Screen showing instructions and controls """

    def on_show_view(self):
        #  Swithes the background color when this view is shown
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_draw(self):
        # Clears the existing view
        self.clear()

        # Draws the texts in the instruction screen
        arcade.draw_text(
            "Fun game",
            self.window.width / 2,
            self.window.height / 2+100,
            arcade.color.WHITE,
            font_size=60,
            anchor_x="center"
        )
        arcade.draw_text(
            "WASD to move, J to attack, K to dash",
            self.window.width / 2,
            self.window.height / 2+20,
            arcade.color.WHITE,
            font_size=35,
            anchor_x="center"
        )
        arcade.draw_text(
            "Enemy cannot be damaged until all orbs are collected",
            self.window.width / 2,
            self.window.height / 2-40,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center"
        )
        arcade.draw_text(
            "Click to start",
            self.window.width / 2,
            self.window.height / 2-95,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center"

        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # Runs the game when the user presses mouse
        game_view = gameView()
        game_view.setup()
        self.window.show_view(game_view)


class gameOverView(arcade.View):
    """Screen shown when player dies"""

    def __init__(self):
        super().__init__()

    def on_draw(self):
        # Clears the existing screen
        self.clear()

        # Draws the text in the game over screen
        arcade.draw_text(
            "Game Over",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            font_size=40,
            anchor_x="center"
        )
        arcade.draw_text(
            "Click to retry",
            self.window.width / 2,
            self.window.height / 2-75,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center"
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # Restarts the game when the user presses mouse
        game_view = gameView()
        game_view.setup()
        self.window.show_view(game_view)


class gameWinView(arcade.View):
    """Screen shown when the player beats the game"""

    def __init__(self):
        super().__init__()

    def on_draw(self):
        # Clears the existing screen
        self.clear()

        # Draws the text in the winning screen
        arcade.draw_text(
            "You win!",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            font_size=40,
            anchor_x="center"
        )
        arcade.draw_text(
            "Click to leave",
            self.window.width / 2,
            self.window.height / 2-75,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center"
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # Closes the game when the user presses mouse
        self.window.close()


class gameView(arcade.View):
    """The main game"""

    def __init__(self):
        super().__init__()

        # Changes the directory of the game
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Scene
        self.scene = None

        # Default level is level 1
        self.level = 1

        # Tile map
        self.tile_map = None

        # Physics engine
        self.physics_engine = None

        # Score
        self.score = 0
        self.max_score = 0

        # Key pressed
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.last_direction = 0

        # Player health
        self.player_max_health = 20
        self.player_health = 20

        # Player attack
        self.attack = False
        self.can_attack = True
        self.attack_sprite_list = None
        self.attack_start = 0
        self.attack_damage = 5

        # Dash ability
        self.dashing = None
        self.dash_start = 0

        # Dash cooldown
        self.dash_cooldown = 0
        self.can_dash = None

        # Dash indicator level
        self.dash_indicator_level = 0

        # Time stop ability
        self.time_stop = False

        # Player knockback
        self.knockback = None
        self.knockback_time = 0
        self.enemy_knockback_time = 0
        self.invincible = None
        self.invincible_time = 0

        # Enemy health
        self.enemy_max_health = 100
        self.enemy_health = 100

        # Enemy speed
        self.enemy_speed = 0

        # Enemy hit
        self.enemy_hit = None

        # Enemy attack
        self.enemy_attack = 5

        # Enemy following player
        self.enemy_follow = None

        # Sets the background color during the main game plays
        arcade.set_background_color(arcade.csscolor.DIM_GRAY)

    def setup(self):
        """Sets up / restarts the game."""

        # Setups the map to the correct level
        map_name = f"Assets/level{self.level}.tmx"

        # Resets the score to 0
        self.score = 0

        # Changes difficulty variables for each level
        # In higher levels, enemy is faster, has more health
        # And there are more coins to collect
        if self.level == 1:
            self.max_score = 1
            self.enemy_health = self.enemy_max_health = 10
            self.enemy_speed = 0.5
        elif self.level == 2:
            self.max_score = 10
            self.enemy_health = self.enemy_max_health = 25
            self.enemy_speed = 0.7
        elif self.level == 3:
            self.max_score = 20
            self.enemy_health = self.enemy_max_health = 100
            self.enemy_speed = 1.1

        # Gives certain layers spacial hash for collision detection
        layer_options = {
            "Wall": {
                "use_spatial_hash": True,
            },
            "Ground": {
                "use_spatial_hash": False,
            },
            "Text": {
                "use_spatial_hash": False,
            },
            "Coins": {
                "use_spatial_hash": True,
            },
        }

        # Load in tile map
        self.tile_map = (
            arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        )

        # Initializes the scene
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Adds the player sprite through the PlayerCharacter class
        self.player_sprite = PlayerCharacter(LAYER_NAME_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Adds the enemy sprite through the Enemy class
        enemy = Enemy(LAYER_NAME_ENEMIES)
        enemy.center_x = 120
        enemy.center_y = 120
        self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)

        # Adds the attack sprite to a sprite list in the scene
        self.scene.add_sprite_list(LAYER_NAME_ATTACK)

        # Creates the physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls=self.scene[LAYER_NAME_WALLS],
        )

    def on_draw(self):
        """Renders the screen."""
        # clears the existing screen
        self.clear()

        # Draws the objects and sprites in the screen
        self.scene.draw()

        # Player health display
        player_health_text = (
            f"Player Health: {self.player_health}/{self.player_max_health}"
        )

        # Enemy health display
        enemy_health_text = (
            f"Enemy Health: {self.enemy_health}/{self.enemy_max_health}"
        )

        # Score display
        score_text = (
            f"Orbs collected: {self.score}/{self.max_score}"
        )

        # Draws the displays from above to the screen
        arcade.draw_text(player_health_text, 10, 10, arcade.color.WHITE, 18)
        arcade.draw_text(enemy_health_text, 10, 40, arcade.color.WHITE, 18)
        arcade.draw_text(score_text, 10, 70, arcade.color.WHITE, 18)

        # Cooldown indicator
        indicator_img = f"""
        Assets/Dash indicator/Dash_level_{self.dash_indicator_level + 1}.png
        """
        self.cooldown_sprite = arcade.Sprite(indicator_img, 2)
        self.cooldown_sprite.center_x = SCREEN_WIDTH - 64
        self.cooldown_sprite.center_y = 30
        self.scene.add_sprite("Cooldown", self.cooldown_sprite)

    def update_player_speed(self):
        """Moves the player according to the direction they are facing"""
        # Checks for what key the player presses and adds the current
        # x and y directions to a list as positive and negative values
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

        # When the user presses opposite direction keys at the same
        # time, the direction becomes 0
        if self.right_pressed and self.left_pressed:
            self.player_sprite.change_x = 0
            direction[0] = 0
        if self.up_pressed and self.down_pressed:
            self.player_sprite.change_y = 0
            direction[1] = 0

        # Resets the direction to 0 when no direction key is pressed
        if not self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = 0
            direction[0] = 0
        if not self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = 0
            direction[1] = 0

    def on_key_press(self, key, modifiers):
        """When a key is pressed/held down."""
        # Dash button
        if key == arcade.key.K:
            if self.can_dash:
                self.dashing = True

        # Time stop button
        # This is for debugging purposes so the enemy stops chasing me
        if key == arcade.key.G:
            self.time_stop = not self.time_stop

        # Attack button
        if key == arcade.key.J:
            if self.can_attack:
                self.attack = True

        # Movement buttons
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
        # Tells the code when the user has stopped pressing the
        # movement buttons
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
        # Updates the physics engine
        self.physics_engine.update()

        # Updates the animations for players and enemies
        self.scene.update_animation(
            [
                LAYER_NAME_PLAYER,
                LAYER_NAME_ENEMIES
            ]
        )

        # Updates the scene for the enemies layer
        self.scene.update([LAYER_NAME_ENEMIES])

        # Adds the coins that collides with the player to a list
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        #  Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            #  Removes the coin that was collided with from sprite list
            coin.remove_from_sprite_lists()
            self.score += 1

        # Attack section

        # Sets the attacking sprite as the image
        attack_img = "Assets/Images/Stuff/swing.png"
        self.attack_sprite = arcade.Sprite(attack_img, CHARACTER_SCALING)

        # Runs if the player is attacking
        if self.attack:
            # Sets the sprite for when player is facing right
            if self.last_direction == 1:
                self.attack_sprite = arcade.Sprite(
                    attack_img,
                    CHARACTER_SCALING
                )

                # Offsets the position of the sprite to the right
                self.attack_sprite.center_x = self.player_sprite.center_x + 10
                self.attack_sprite.center_y = self.player_sprite.center_y

            # Flips the sprite when the player is facing left
            elif self.last_direction == -1:
                self.attack_sprite = arcade.Sprite(
                    attack_img,
                    CHARACTER_SCALING,
                    flipped_horizontally=True
                )

                # Offsets the position of the sprite to the left
                self.attack_sprite.center_x = self.player_sprite.center_x - 10
                self.attack_sprite.center_y = self.player_sprite.center_y

            # Sets the sprite list to a variable
            self.attack_sprite_list = self.scene.get_sprite_list(
                LAYER_NAME_ATTACK
            )

            # Prevents the player from attacking with no cooldown
            self.can_attack = False

            # Repeats so that the sprite stays on the screen
            if self.attack_start < 10:
                # Adds the sprite to the screen when attack starts
                if self.attack_start == 0:
                    self.attack_sprite_list.append(self.attack_sprite)
                self.attack_start += 1

            # Removes the sprite and resets variables
            else:
                self.attack_start = 0
                self.attack = False
                self.can_attack = True
                # Removes the attackk sprite
                if self.attack_sprite_list:
                    self.attack_sprite_list.pop(0)

        # Dashing Section

        # Runs when the user presses dash
        if self.dashing:
            # Increases the player's velocity towards their facing
            # x and y direction
            self.player_sprite.change_x = PLAYER_DASH_SPEED * direction[0]
            self.player_sprite.change_y = PLAYER_DASH_SPEED * direction[1]

            # Adds 1 to the variable as longs as the player is dashing
            self.dash_start += 1

            # Resets the dashing meter to empty
            self.dash_indicator_level = 0

            # Stops the player from dashing after set amount of ticks
            if self.dash_start == 20:
                # Resets the variables
                self.dashing = False
                self.dash_cooldown = 0
                self.dash_start = 0
                # Sets the player speed back to normal after dash
                if not self.dashing:
                    self.player_sprite.change_y = (
                        PLAYER_MOVEMENT_SPEED * direction[1]
                    )
                    self.player_sprite.change_x = (
                        PLAYER_MOVEMENT_SPEED * direction[0]
                    )

        # Dash cooldown
        if self.dash_cooldown < 180:
            self.dash_cooldown += 1
            # Prevents the player from dashing before the cooldown is
            # finished
            self.can_dash = False

            # Updates the cooldown indicator
            for i in range(0, 5):
                if self.dash_cooldown == i * 30:
                    self.dash_indicator_level = i

        # When the cooldown is finished, allow the player to dash again
        if self.dash_cooldown == 180:
            self.dash_indicator_level = 5
            self.can_dash = True

        # Enemy

        # Enemy following player
        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            enemy.center_x += enemy.change_x
            enemy.center_y += enemy.change_y

            # Records the enemy's position
            start_x = enemy.center_x
            start_y = enemy.center_y

            # Records the player's position
            dest_x = self.player_sprite.center_x
            dest_y = self.player_sprite.center_y

            # Calculates the x and y distance between the enemy and the player
            dist_x = int(dest_x - start_x)
            dist_y = int(dest_y - start_y)
            # Using trig to find the angle difference between player and enemy
            angle = math.atan2(dist_y, dist_x)

            # Collision

            # Allows the player to attack the enemy only after all
            # coins are collected and the max score is met
            if self.score == self.max_score:
                enemy_hit_contact = arcade.check_for_collision(
                    self.attack_sprite, enemy
                )

                # Damages the enemy when the enemy is hit
                if enemy_hit_contact:
                    self.enemy_hit = True
                    self.enemy_health -= self.attack_damage

                # Knocks back the enemy when it is hit
                if self.enemy_hit:
                    # Enemy will have knockback until value is reached
                    if self.enemy_knockback_time < 3:
                        self.enemy_knockback_time += 1
                        enemy.center_x -= math.cos(angle) * KNOCKBACK
                        enemy.center_y -= math.sin(angle) * KNOCKBACK
                    # Stops the enemy knockback and resets variables
                    if self.enemy_knockback_time == 3:
                        self.enemy_knockback_time = 0
                        self.enemy_hit = False

            # Checks for collision between the player and enemy
            # only if the player is not invincible
            if not self.invincible:
                enemy_collision = arcade.check_for_collision(
                    self.player_sprite, enemy
                )
            # Enemy collision is always false when player is invincible
            else:
                enemy_collision = False

            # Stops the enemy from following the player when time stop
            # buttons is pressed, used for debugging
            if not self.time_stop:
                self.enemy_follow = True
            if self.time_stop:
                self.enemy_follow = False

            # Making the enemy follow the player
            if self.enemy_follow:
                enemy.change_x = math.cos(angle) * self.enemy_speed
                enemy.change_y = math.sin(angle) * self.enemy_speed

            # Player knockback and invincibility

            # Runs is the player collides with the enemy
            if enemy_collision:
                # Player's health goes down
                self.player_health -= self.enemy_attack
                # Resets the knockback timer
                self.knockback_time = 0
                self.knockback = True
                self.invincible = True

            # Runs when player collides with the enemy
            if self.knockback:
                # Keeps player knockback until value is reached
                if self.knockback_time < 5:
                    self.player_sprite.center_x += math.cos(angle) * KNOCKBACK
                    self.player_sprite.center_y += math.sin(angle) * KNOCKBACK
                    self.knockback_time += 1
                # Stops the knockback
                if self.knockback_time == 5:
                    self.knockback = False

            # Sets how long the invincible period is
            if self.invincible:
                if self.invincible_time < 60:
                    self.invincible = True
                    self.invincible_time += 1
                if self.invincible_time == 60:
                    self.invincible = False
                    self.invincible_time = 0

        # Displays the game over screen when the player dies
        if self.player_health <= 0:
            view = gameOverView()
            self.window.show_view(view)

        # Shows the winning screen when the player beats level 3
        if self.level == 3 and self.enemy_health <= 0:
            view = gameWinView()
            self.window.show_view(view)
        # Displays the next level if level 3 is not reached yet
        elif self.enemy_health <= 0:
            self.level += 1
            self.setup()


# Functions
def main():
    """
    Main function
    """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Scuffed game")
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


# Main code
if __name__ == "__main__":
    main()
