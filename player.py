import time

import pygame
import math
import numpy as np

from network import Network

RED = [255, 0, 0]
WHITE = [255, 255, 255]
GREEN = [0, 255, 0]
ACCELERATION = 0.5
MAX_VELOCITY = 40
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 400
EPSILON = MAX_VELOCITY/10

class Player():

    def __init__(self, X, Y, RADIUS, COLOR, WALL):
        self.starting_point = (X, Y)
        self.end_point = (SCREEN_WIDTH - X, Y)
        self.screen = pygame.display.get_surface()
        self.pos_x = X
        self.pos_y = Y
        self.radius = RADIUS
        self.color = COLOR
        self.angle = math.pi / 2
        self.wall = WALL
        self.directions = ["RIGHT", "UPRIGHT", "UP", "UPLEFT", "LEFT"]
        self.detectors = [0, 0, 0, 0, 0]
        self.is_dead = False
        self.angle_distance = 0
        self.fitness = 0
        self.velocity = 0
        self.summed_velocity = 0
        self.summed_detectors = [0, 0, 0, 0, 0]
        self.average_detectors = [0, 0, 0, 0, 0]
        self.iteration = 1
        self.average_speed = 0
        self.lap = 0
        self.net = Network([6, 5, 3])
        self.stop_time = time.time()
        self.spawn_time = time.time()
        self.death_time = None
        self.draw()

    def update(self):
        self.draw()
        self.get_detectors(self.wall)
        if not self.is_dead:
            self.summed_velocity+=self.velocity
            self.summed_detectors = [self.summed_detectors[i]+self.detectors[i] for i in range(len(self.detectors))]
            self.average_speed = self.summed_velocity/self.iteration
            self.average_detectors = [self.summed_detectors[i]/self.iteration for i in range(len(self.detectors))]
            self.iteration += 1
            self.calculate_fitness()
        if self.velocity == 0:
            if time.time() - self.stop_time > 3:
                self.die()


    def draw(self):
        pygame.draw.circle(self.screen, WHITE,
                           (self.pos_x, self.pos_y), self.radius)
        pygame.draw.circle(self.screen, self.color,
                           (self.pos_x, self.pos_y), self.radius, 1)
        pygame.draw.line(self.screen, self.color,
                         (self.pos_x, self.pos_y),
                         (self.pos_x + (math.cos(self.angle) * self.radius),
                          self.pos_y - (math.sin(self.angle) * self.radius)), 1)

    def show(self):
        pygame.draw.circle(self.screen, GREEN,
                           (self.pos_x, self.pos_y), self.radius)

    def get_detectors(self, wall):
        for x in range(len(self.detectors)):
            self.detectors[x] = self.get_detector(wall, self.angle - math.pi / 2 + x * math.pi / 4)

    def get_detector(self, wall, angle):
        w, h = self.screen.get_size()
        a = 1
        while a < 700:
            point = (self.pos_x + (math.cos(angle) * a),
                     self.pos_y - (math.sin(angle)) * a)
            if point[0] >= w or point[0] <= 0 or point[1] >= h or point[1] <= 0:
                break
            if wall.object.collidepoint(point):
                break

            # self.draw_detector(point)
            a += 1
        return a - self.radius

    def draw_detector(self, point):
        pygame.draw.line(self.screen, self.color,
                         (self.pos_x, self.pos_y),
                         point, 1)

    def turn_right(self):
        if not self.is_dead:
            self.angle -= math.pi / 30

    def turn_left(self):
        if not self.is_dead:
            self.angle += math.pi / 30

    def move(self):
        if not self.is_dead:
            self.velocity += ACCELERATION
            if self.velocity > MAX_VELOCITY:
                self.velocity = MAX_VELOCITY
            self.pos_x += int(math.cos(self.angle) * self.velocity)
            self.pos_y -= int(math.sin(self.angle) * self.velocity)

    def stop(self):
        if self.velocity != 0:
            self.stop_time = time.time()
        self.velocity -= ACCELERATION*2/3
        if self.velocity<0:
            self.velocity = 0
        self.pos_x += int(math.cos(self.angle) * self.velocity)
        self.pos_y -= int(math.sin(self.angle) * self.velocity)

    def collision(self, wall):
        w, h = self.screen.get_size()
        if self.pos_x - self.radius <= 0 or self.pos_x + self.radius >= w:
            return True
        if self.pos_y - self.radius <= 0 or self.pos_y + self.radius >= h:
            return True
        if self.intersect(wall):
            return True
        return False

    def intersect(self, wall):
        delta_x = self.pos_x - max(wall.left, min(self.pos_x, wall.left + wall.width));
        delta_y = self.pos_y - max(wall.top, min(self.pos_y, wall.top + wall.height));
        return (delta_x * delta_x + delta_y * delta_y) < (self.radius * self.radius);

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.death_time = time.time()
            #self.stop()
            self.velocity = 0
            #self.calculate_fitness()

    def calculate_fitness(self):
        self.angle_distance = angle_between((self.pos_x, self.pos_y), getmiddle(SCREEN_WIDTH, SCREEN_HEIGHT),
                                            self.starting_point) + self.lap * 180
        if math.fabs(self.angle_distance - (self.lap + 1) * 180) < EPSILON:
            pygame.draw.circle(self.screen, RED,
                               (self.pos_x, self.pos_y), self.radius)
            temp_point = self.starting_point
            self.starting_point = self.end_point
            self.end_point = temp_point
            self.lap += 1
        self.fitness = self.angle_distance - (5 * (time.time() - self.spawn_time))

    def calculate_alt_fitness(self):
        if self.detectors[0] != 0:
            self.fitness = 5*self.get_distance()/self.detectors[0]

    def make_decision(self):
        detectors = self.detectors.copy()
        detectors.append(self.velocity)
        inputs = np.ndarray(shape=(6, 1))
        for a in range(len(detectors)):
            inputs[a] = detectors[a]
        outputs = self.net.feed_forward(inputs)
        if outputs[0] < 0.5:
            self.turn_left()
        if outputs[1] < 0.5:
            self.turn_right()
        if outputs[2] < 0.5:
            self.move()
        else:
            self.stop()

    def get_distance(self):
        if self.is_dead:
            return self.average_speed*(self.death_time - self.spawn_time)
        else:
            return self.average_speed * (time.time() - self.spawn_time)

def angle_between(p0, p1, p2):
    a = (p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2
    b = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
    c = (p2[0] - p0[0]) ** 2 + (p2[1] - p0[1]) ** 2
    return math.acos((a + b - c) / math.sqrt(4 * a * b)) * 180 / math.pi


def getmiddle(w, h):
    return int(w / 2), int(h / 2)
