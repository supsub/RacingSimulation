import time
import pygame
import random

from player import Player
from wall import Wall

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 400
PLAYER_SIZE = 10
FPS = 30
OPEN_SPACE = 100
# ================COLORS========================================================
PINK = [255, 135, 255]
WHITE = [255, 255, 255]
YELLOW = [255, 255, 0]
BLACK = [0, 0, 0]


# ==============================================================================
class Game():

    def __init__(self):

        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 20)
        self.population_counter = 1
        self.average_fitness = 0
        self.update_text()
        self.population_size = 50
        self.inherit_pool = 5
        self.death_counter = 0
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.screen.blit(self.textsurface, (int(-100), int(SCREEN_HEIGHT / 2)))
        self.running = True
        self.wall = Wall(OPEN_SPACE, OPEN_SPACE, SCREEN_WIDTH - 2 * OPEN_SPACE,
                         SCREEN_HEIGHT - 2 * OPEN_SPACE, BLACK)
        self.players = []
        

    def spawn_player(self):
        self.players.append(Player(int(OPEN_SPACE / 2), int(SCREEN_HEIGHT / 2 - PLAYER_SIZE / 2),
                                   PLAYER_SIZE, BLACK, self.wall))

    def manage_hotkeys(self, player):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            player.turn_left()
        if pressed[pygame.K_RIGHT]:
            player.turn_right()
        if pressed[pygame.K_SPACE]:
            player.move()
        else:
            player.stop()

    def random_directions(self, player):
        player.move()
        if random.random() < 0.5:
            player.turn_left()
        else:
            player.turn_right()

    def check_collision(self, player):
        if not player.is_dead:
            if (player.collision(self.wall)):
                player.die()
            #    self.players.remove(player)

    def manage_quit(self):
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                self.running = False
                pygame.quit()

    def adjustFPS(self):
        pygame.time.wait(int(1000 / FPS))

    def player_loop(self):
        self.spawn_player()
        while self.running:
            self.draw_background()
            for player in self.players:
                player.update()
                self.manage_hotkeys(player)
                self.check_collision(player)
            self.update_pygame()
            self.manage_quit()
            self.adjustFPS()

    def update_pygame(self):
        pygame.display.update()

    def manage_population(self):
        if self.death_counter == self.population_size:
            parents = self.get_best_ancestors()
            self.show_best_ancestors(parents)
            self.create_new_population(parents)
            self.update_text()

    def create_new_population(self, parents):
        nets = [p.net for p in parents]
        self.death_counter = 0
        self.players = []
        self.spawn_players()
        for player in self.players:
            player.net.set_weights(nets)
            player.net.set_biases(nets)
        self.population_counter += 1

    def show_best_ancestors(self, parents):
        for a in range(self.inherit_pool):
            parents[a].show()
        self.update_pygame()
        time.sleep(1)

    def get_best_ancestors(self):
        best_ancestors = sorted(self.players, key=lambda x: x.fitness, reverse=True)[:self.inherit_pool]
        self.average_fitness = sum([x.fitness for x in best_ancestors])/len(best_ancestors)
        return best_ancestors

    def update_text(self):
        self.textsurface = self.myfont.render("Population: {}| Fitness:{}"
                                              .format(str(self.population_counter),
                                                      str(self.average_fitness)), False, (255, 255, 255))
    def spawn_players(self):
        for a in range(self.population_size):
            self.spawn_player()

    def set_death_counter(self):
        self.death_counter = sum(p.is_dead == True for p in self.players)
        print(self.death_counter)

    def update_players(self):
        for player in self.players:
            if time.time() - player.spawn_time > 10:
                if player.fitness < 2 or time.time() - player.spawn_time > 20:
                    player.die()
            player.update()
            player.make_decision()
            self.check_collision(player)

    def draw_background(self):
        self.screen.fill(WHITE)
        self.wall.draw()
        self.screen.blit(self.textsurface, (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2)))

    def computer_loop(self):
        self.spawn_players()
        while self.running:
            self.draw_background()
            self.update_players()
            self.set_death_counter()
            self.manage_population()
            self.update_pygame()
            self.manage_quit()
            self.clock.tick()
