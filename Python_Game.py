import arcade

# Constanten
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Puffer The Fish"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 10
PLAYER_JUMP_SPEED = 20
GRAVITY = 1

LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 64
PLAYER_START_Y = 128

LEVELS = 10

def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        ]

class PlayerCharacter(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = CHARACTER_SCALING

        self.idle_texture_pair = load_texture_pair(f"resources/images/PUFFERFISH_RECHTS.png")

        self.texture = self.idle_texture_pair[0]

    def update_animation(self, delta_time: float = 1/60):
        if self.change_x < 0:
            self.idle_texture_pair = load_texture_pair(f"resources/images/PUFFERFISH.png")
        elif self.change_x > 0:
            self.idle_texture_pair = load_texture_pair(f"resources/images/PUFFERFISH_RECHTS.png")
        elif self.change_x == 0:
            self.idle_texture_pair = load_texture_pair(f"resources/images/PUFFERFISH_RECHTS.png")
        self.texture = self.idle_texture_pair[0]
        return
class GameView(arcade.View):

    def __init__(self):

        super().__init__()

        self.time_taken = 0

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        self.player_list = None
        self.wall_list = None
        self.coin_list = None
        self.enemy_list = None
        self.lives_list = None
        self.end_list = None
        self.spikes_list = None

        self.player_sprite = None

        self.physics_engine = None

        self.view_bottom = 0
        self.view_left = 0

        self.score = 0
        self.lives = 3

        self.level = 1

        self.window.set_mouse_visible(False)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self, level):
        #Dit is de setup functie, deze functie word opgeroepen als je een level start en hiermee reset je dus een level
        self.view_bottom = 0
        self.view_left = 0

        #Hier worden de lists gemaakt
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.lives_list = arcade.SpriteList()
        self.end_list = arcade.SpriteList()
        self.spikes_list = arcade.SpriteList()

        #Hier word het poppetje aangemaakt en dan in de player list gedaan
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        #Het inladen van de map

        map_name = f"resources/maps/level_{level}.tmx"
        platform_layer_name = 'Platforms'
        coins_layer_name = 'Coins'
        enemy_layer_name = 'Enemy'
        lives_layer_name = 'Lives'
        end_layer_name = 'End'
        spikes_layer_name = 'Spikes'

        my_map = arcade.tilemap.read_tmx(map_name)

        self.wall_list = arcade.tilemap.process_layer(map_object=my_map, layer_name=platform_layer_name, scaling=TILE_SCALING, use_spatial_hash=True)

        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING, use_spatial_hash=True)
        self.window.max_score += len(self.coin_list)
        moving_enemy_list = arcade.tilemap.process_layer(my_map, enemy_layer_name, TILE_SCALING)

        self.lives_list = arcade.tilemap.process_layer(my_map, lives_layer_name, TILE_SCALING, use_spatial_hash=True)

        self.end_list = arcade.tilemap.process_layer(my_map, end_layer_name, TILE_SCALING, use_spatial_hash=True)

        self.spikes_list = arcade.tilemap.process_layer(my_map, spikes_layer_name, TILE_SCALING, use_spatial_hash=True)

        for enemy in moving_enemy_list:
            enemy.change_x = 2
            self.enemy_list.append(enemy)

        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)
    def on_draw(self):
        #Dit is de draw functie, deze functie tekent alle elementen op het scherm

        #Hier word het renderen gestart
        arcade.start_render()

        #Hier worden de verschillende lists getekend
        self.player_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.enemy_list.draw()
        self.lives_list.draw()
        self.end_list.draw()
        self.spikes_list.draw()

        #Hier word het scoreboard getekend
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 30 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

        level_text = f"Level: {self.level}/{LEVELS}"
        arcade.draw_text(level_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

        lives_text = f"Lives: {self.lives}"
        arcade.draw_text(lives_text, self.view_left + SCREEN_WIDTH - 80, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)


    def process_keychange(self):
        # Boven naar Beneden
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.can_jump() and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True

        # Links en Rechts
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        #Deze functie houd bij of een key word in gedrukt.

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

        if key == arcade.key.ESCAPE:
            # pass self, the current view, to preserve this view's state
            pause = PauseView(self)
            pause.view_left = self.view_left
            pause.view_bottom = self.view_bottom
            self.window.show_view(pause)

    def on_key_release(self, key, modifiers):
        #Deze functie houd bij of een key los word gelaten.

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_update(self, delta_time):
        #Deze functie update telkens het spel, het spel heeft 60 updates per seconde.
        self.time_taken += delta_time

        self.player_list.update_animation(delta_time)

        #Dit update de physics engine
        self.physics_engine.update()

        self.enemy_list.update()

            # Check each enemy
        for enemy in self.enemy_list:
                # If the enemy hit a wall, reverse
            if len(arcade.check_for_collision_with_list(enemy, self.wall_list)) > 0:
                enemy.change_x *= -1

        #Dit maakt een variabele die bijhoud of de player een coin aanraakt
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        #Deze for loop haalt de coin uit de coin list als die coin aangeraakt word door de speler en voegt vervolgens 1 punt toe aan de score
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1

        lives_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.lives_list)

        for lives in lives_hit_list:
            lives.remove_from_sprite_lists()
            self.lives += 1
        
        changed = False 

        if len(arcade.check_for_collision_with_list(self.player_sprite, self.spikes_list)) > 0:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            self.lives -= 1

            # Camera naar de start
            self.view_left = 0
            self.view_bottom = 0
            changed = True

        if len(arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)) > 0:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            self.lives -= 1

            # Camera naar de start
            self.view_left = 0
            self.view_bottom = 0
            changed = True

        if self.level == LEVELS:
            if len(arcade.check_for_collision_with_list(self.player_sprite, self.end_list)) > 0:
                view = GameFinishView()
                view.time_taken = self.time_taken
                view.score = self.score
                view.level = self.level
                self.window.set_mouse_visible(True)
                self.window.show_view(view)
        else:
            if len(arcade.check_for_collision_with_list(self.player_sprite, self.end_list)) > 0:
                self.level += 1

                # Load the next level
                self.setup(self.level)

                # Set the camera to the start
                self.view_left = 0
                self.view_bottom = 0
                changed = True

        # Is de speler van de map gedonderd?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            self.lives -= 1

            # Camera naar de start
            self.view_left = 0
            self.view_bottom = 0
            changed = True

        #Hieronder word de viewport aangepast zodat het beeld mee scrolled met de speler

        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:

            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

        #Als het aantal levens 0 of kleiner is dan ben je gameover en krijg je het gameover screen.
        if self.lives <= 0:
            view = GameOverView()
            view.time_taken = self.time_taken
            view.score = self.score
            view.level = self.level
            self.window.set_mouse_visible(True)
            self.window.show_view(view)

class StartScreen(arcade.View):
    def on_show(self):
        #Dit word gerunned als we naar dit scherm switchen.
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # De viewport word gereset.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        #Teken dit scherm
        arcade.start_render()
        arcade.draw_text("PUFFER THE FISH", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to start", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        #Als op de muis geklikt word start de game.
        game_view = GameView()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)

class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.time_taken = 0
        self.level = 0
    def on_show(self):
        #Dit word gerunned als we naar dit scherm switchen.
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # De viewport word gereset.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        #Teken dit scherm
        arcade.start_render()

        arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click or press enter to try again", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

        time_taken_formatted = f"{round(self.time_taken, 2)} seconds"
        arcade.draw_text(f"Time: {time_taken_formatted}",
                         SCREEN_WIDTH/2,
                         200,
                         arcade.color.GRAY,
                         font_size=15,
                         anchor_x="center")
        total_score = int(self.score * self.level / self.time_taken * 3.141592653589793 * 100)

        arcade.draw_text(f"Total Score: {total_score}",
                         SCREEN_WIDTH/2,
                         100,
                         arcade.color.GRAY,
                         font_size=15,
                         anchor_x="center")

        output_total = f"Kibbeling: {self.score}/{self.window.max_score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

        level_total = f"Level: {self.level}/{LEVELS}"
        arcade.draw_text(level_total, 10, 28, arcade.color.WHITE, 14)

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ENTER:  # Opnieuw beginnen
            game_view = GameView()
            game_view.setup(game_view.level)
            self.window.show_view(game_view)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        #Als op de muis geklikt word de game gerestart.
        game_view = GameView()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)

class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.view_left = 0
        self.view_bottom = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.ORANGE)

        # De viewport word gezet.
        arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)
    def on_draw(self):
        arcade.start_render()

        # Teken de speler
        player_sprite = self.game_view.player_sprite
        player_sprite.draw()

        # Een oranje filter over de speler
        arcade.draw_lrtb_rectangle_filled(left=player_sprite.left,
                                          right=player_sprite.right,
                                          top=player_sprite.top,
                                          bottom=player_sprite.bottom,
                                          color=arcade.color.ORANGE + (200,))

        arcade.draw_text("PAUSED", SCREEN_WIDTH/2 + self.view_left, SCREEN_HEIGHT/2 + self.view_bottom+50,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        # Tekst die laat zien wat je moet doen
        arcade.draw_text("Press Esc. to continue",
                         SCREEN_WIDTH/2 + self.view_left, SCREEN_HEIGHT/2 + self.view_bottom,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press enter to restart",
                         SCREEN_WIDTH/2 + self.view_left, SCREEN_HEIGHT/2 + self.view_bottom-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:   # Verder gaan
            arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:  # Opnieuw beginnen
            game_view = GameView()
            game_view.setup(game_view.level)
            self.window.show_view(game_view)

class GameFinishView(arcade.View):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.time_taken = 0
        self.level = 0
    def on_show(self):
        #Dit word gerunned als we naar dit scherm switchen.
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # De viewport word gereset.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        #Teken dit scherm
        arcade.start_render()

        arcade.draw_text("Finished", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

        time_taken_formatted = f"{round(self.time_taken, 2)} seconds"
        arcade.draw_text(f"Time: {time_taken_formatted}",
                         SCREEN_WIDTH/2,
                         200,
                         arcade.color.GRAY,
                         font_size=15,
                         anchor_x="center")
        total_score = int(self.score * (LEVELS+1) / self.time_taken * 3.141592653589793 * 100)

        arcade.draw_text(f"Total Score: {total_score}",
                         SCREEN_WIDTH/2,
                         100,
                         arcade.color.GRAY,
                         font_size=15,
                         anchor_x="center")

        output_total = f"Kibbeling: {self.score}/{self.window.max_score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        #Als op de muis geklikt word de game gerestart.
        game_view = GameView()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)

def main():
    #Dit is de main functie die word opgeroepen als je de game opent
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.max_score = 0
    start_view = StartScreen()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()

