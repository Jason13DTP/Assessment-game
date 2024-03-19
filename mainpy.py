import arcade, random, math, os

#Constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Game"

#Scaling
TILE_SCALING = 0.25
CHARACTER_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

PLAYER_START_X = SPRITE_PIXEL_SIZE * TILE_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING * 1

RIGHT_FACING = 0
LEFT_FACING = 1

PLAYER_MOVEMENT_SPEED = 5

LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemies"
LAYER_NAME_BULLETS = "Bullets"

def load_texture(filename):
    return arcade.load_texture(filename)


class Entity(arcade.Sprite):
    def __init__(self, name_folder):
        super().__init__()

        # Default to facing right
        self.facing_direction = RIGHT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        
        main_path = f"Assets/Images/{name_folder}"

        # Load textures for idle
        self.idle_textures = []
        for i in range(3):
            texture = load_texture(f"{main_path}/idle{i}.png")
            self.walk_textures.append(texture)

        # Load textures for walking
        self.walk_textures = []
        for i in range(5):
            texture = load_texture(f"{main_path}/walk{i}.png")
            self.walk_textures.append(texture)


class PlayerCharacter(Entity):
    """Player Sprite"""

    def __init__(self):

        # Set up parent class
        super().__init__("Player")


    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Idle animation
        self.cur_texture += 1
        if self.cur_texture > 2:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.facing_direction]

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 4:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.facing_direction]


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """
        Initializer for the game
        """

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shoot_pressed = False
        self.jump_needs_reset = False

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our 'physics' engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        self.end_of_map = 0

        # Keep track of the score
        self.score = 0

        # Shooting mechanics
        self.can_shoot = False
        self.shoot_timer = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.shoot_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Setup the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Map name
        map_name = ":resources:tiled_maps/map_with_ladders.json"

        # Layer Specific Options for the Tilemap
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
        }

        # Load in TileMap
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initiate New Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score
        self.score = 0

        # Shooting mechanics
        self.can_shoot = True
        self.shoot_timer = 0

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = (
            self.tile_map.tile_width * TILE_SCALING * PLAYER_START_X
        )
        self.player_sprite.center_y = (
            self.tile_map.tile_height * TILE_SCALING * PLAYER_START_Y
        )
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # Add bullet spritelist to Scene
        self.scene.add_sprite_list(LAYER_NAME_BULLETS)

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_PLATFORMS]
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.BLACK,
            18,
        )

        # Draw hit boxes.
        # for wall in self.wall_list:
        #     wall.draw_hit_box(arcade.color.BLACK, 3)
        #
        # self.player_sprite.draw_hit_box(arcade.color.RED, 3)

    def process_keychange(self):
        """
        Called when we change a key up/down, or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif (
                self.physics_engine.can_jump(y_distance=10)
                and not self.jump_needs_reset
            ):
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        if key == arcade.key.Q:
            self.shoot_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        if key == arcade.key.Q:
            self.shoot_pressed = False

        self.process_keychange()

    def center_camera_to_player(self, speed=0.2):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered, speed)

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        if self.can_shoot:
            if self.shoot_pressed:
                arcade.play_sound(self.shoot_sound)
                bullet = arcade.Sprite(
                    ":resources:images/space_shooter/laserBlue01.png",
                    SPRITE_SCALING_LASER,
                )

                if self.player_sprite.facing_direction == RIGHT_FACING:
                    bullet.change_x = BULLET_SPEED
                else:
                    bullet.change_x = -BULLET_SPEED

                bullet.center_x = self.player_sprite.center_x
                bullet.center_y = self.player_sprite.center_y

                self.scene.add_sprite(LAYER_NAME_BULLETS, bullet)

                self.can_shoot = False
        else:
            self.shoot_timer += 1
            if self.shoot_timer == SHOOT_SPEED:
                self.can_shoot = True
                self.shoot_timer = 0

        # Update Animations
        self.scene.update_animation(
            delta_time,
            [
                LAYER_NAME_COINS,
                LAYER_NAME_BACKGROUND,
                LAYER_NAME_PLAYER,
                LAYER_NAME_ENEMIES,
            ],
        )

        # Update moving platforms, enemies, and bullets
        self.scene.update(
            [LAYER_NAME_MOVING_PLATFORMS, LAYER_NAME_ENEMIES, LAYER_NAME_BULLETS]
        )

        # See if the enemy hit a boundary and needs to reverse direction.
        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            if (
                enemy.boundary_right
                and enemy.right > enemy.boundary_right
                and enemy.change_x > 0
            ):
                enemy.change_x *= -1

            if (
                enemy.boundary_left
                and enemy.left < enemy.boundary_left
                and enemy.change_x < 0
            ):
                enemy.change_x *= -1

        for bullet in self.scene[LAYER_NAME_BULLETS]:
            hit_list = arcade.check_for_collision_with_lists(
                bullet,
                [
                    self.scene[LAYER_NAME_ENEMIES],
                    self.scene[LAYER_NAME_PLATFORMS],
                    self.scene[LAYER_NAME_MOVING_PLATFORMS],
                ],
            )

            if hit_list:
                bullet.remove_from_sprite_lists()

                for collision in hit_list:
                    if (
                        self.scene[LAYER_NAME_ENEMIES]
                        in collision.sprite_lists
                    ):
                        # The collision was with an enemy
                        collision.health -= BULLET_DAMAGE

                        if collision.health <= 0:
                            collision.remove_from_sprite_lists()
                            self.score += 100

                        # Hit sound
                        arcade.play_sound(self.hit_sound)

                return

            if (bullet.right < 0) or (
                bullet.left
                > (self.tile_map.width * self.tile_map.tile_width) * TILE_SCALING
            ):
                bullet.remove_from_sprite_lists()

        player_collision_list = arcade.check_for_collision_with_lists(
            self.player_sprite,
            [
                self.scene[LAYER_NAME_COINS],
                self.scene[LAYER_NAME_ENEMIES],
            ],
        )

        # Loop through each coin we hit (if any) and remove it
        for collision in player_collision_list:

            if self.scene[LAYER_NAME_ENEMIES] in collision.sprite_lists:
                arcade.play_sound(self.game_over)
                self.setup()
                return
            else:
                # Figure out how many points this coin is worth
                if "Points" not in collision.properties:
                    print("Warning, collected a coin without a Points property.")
                else:
                    points = int(collision.properties["Points"])
                    self.score += points

                # Remove the coin
                collision.remove_from_sprite_lists()
                arcade.play_sound(self.collect_coin_sound)

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()