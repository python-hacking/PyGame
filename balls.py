#!/usr/bin/env python
# coding: utf

import pygame
import random

FULL_ANGLE = 360
SIZE = 640, 480
NUM_BALLS = 3
TICK_INTERVAL = 100
GRAVITY_CONST = 7

def intn(*arg):
    return map(int,arg)

def Init(sz):
    '''Turn PyGame on'''
    global screen, screenrect
    pygame.init()
    screen = pygame.display.set_mode(sz)
    screenrect = screen.get_rect()

class GameMode:
    '''Basic game mode class'''
    def __init__(self):
        self.background = pygame.Color("black")

    def Events(self,event):
        '''Event parser'''
        pass

    def Draw(self, screen):
        screen.fill(self.background)

    def Logic(self, screen):
        '''What to calculate'''
        pass

    def Leave(self):
        '''What to do when leaving this mode'''
        pass

    def Init(self):
        '''What to do when entering this mode'''
        pass

class Ball:
    '''Simple ball class'''

    def __init__(self, filename, pos = (0.0, 0.0), speed = (0.0, 0.0)):
        '''Create a ball from image'''
        self.fname = filename
        self.surface = pygame.image.load(filename)
        self.orig_surface = pygame.image.load(filename)
        self.rect = self.surface.get_rect()
        self.speed = speed
        self.pos = pos
        self.newpos = pos
        self.active = True

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def action(self):
        '''Proceed some action'''
        if self.active:
            global Run
            self.pos = self.pos[0]+self.speed[0], self.pos[1]+self.speed[1] + Run.gravity_acceleration / 2
            self.speed = (self.speed[0], self.speed[1] + Run.gravity_acceleration)

    def logic(self, surface):
        x,y = self.pos
        dx, dy = self.speed
        if x < self.rect.width/2:
            x = self.rect.width/2
            dx = -dx
        elif x > surface.get_width() - self.rect.width/2:
            x = surface.get_width() - self.rect.width/2
            dx = -dx
        if y < self.rect.height/2:
            y = self.rect.height/2
            dy = -dy
        elif y > surface.get_height() - self.rect.height/2:
            y = surface.get_height() - self.rect.height/2
            dy = -dy
        self.pos = x,y
        self.speed = dx,dy
        self.rect.center = intn(*self.pos)

class BallWithSizeAndRotation(Ball):
    def __init__(self, factor = 1, rot_speed = 0, *args, **kwargs):
        Ball.__init__(self, *args, **kwargs)
        self.factor = factor
        self.cur_rotation = 0
        self.rot_speed = rot_speed
        self.surface = pygame.transform.rotozoom(self.orig_surface, 0, self.factor)
        self.rect = self.surface.get_rect()
    def action(self):
        if self.active:
            self.cur_rotation = (self.cur_rotation + self.rot_speed) % FULL_ANGLE
            print "before " + str(self.surface.get_height())
            self.surface = pygame.transform.rotozoom(self.orig_surface, self.cur_rotation, self.factor)
            print "after" + str(self.surface.get_height())
            self.rect = self.surface.get_rect()
        Ball.action(self)

class Universe:
    '''Game universe'''

    def __init__(self, msec, tickevent = pygame.USEREVENT):
        '''Run a universe with msec tick'''
        self.msec = msec
        self.tickevent = tickevent

    def Start(self):
        '''Start running'''
        pygame.time.set_timer(self.tickevent, self.msec)

    def Finish(self):
        '''Shut down an universe'''
        pygame.time.set_timer(self.tickevent, 0)

class GameWithObjects(GameMode):

    def __init__(self, objects=[]):
        GameMode.__init__(self)
        self.objects = objects
        self.gravity_acceleration = GRAVITY_CONST

    def locate(self, pos):
        return [obj for obj in self.objects if obj.rect.collidepoint(pos)]

    def Events(self, event):
        global Game
        GameMode.Events(self, event)
        if event.type == Game.tickevent:
            for obj in self.objects:
                obj.action()

    def Logic(self, surface):
        GameMode.Logic(self, surface)
        for obj in self.objects:
            obj.logic(surface)

    def Draw(self, surface):
        GameMode.Draw(self, surface)
        for obj in self.objects:
            obj.draw(surface)

class GameWithDnD(GameWithObjects):

    def __init__(self, *argp, **argn):
        GameWithObjects.__init__(self, *argp, **argn)
        self.oldpos = 0,0
        self.drag = None

    def Events(self, event):
        global Game
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = self.locate(event.pos)
            if click:
                self.drag = click[0]
                self.drag.active = False
                self.oldpos = event.pos
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                if self.drag:
                    self.drag.pos = event.pos
                    self.drag.speed = event.rel
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drag:
                self.drag.active = True
                self.drag = None
        GameWithObjects.Events(self, event)

Init(SIZE)
Game = Universe(TICK_INTERVAL)

Run = GameWithDnD()
for i in xrange(NUM_BALLS):
    x, y = random.randrange(screenrect.w), random.randrange(screenrect.h)
    dx, dy = 1 + random.random() * 5, 1 + random.random() * 5
    Run.objects.append(BallWithSizeAndRotation(.5 + random.random(),
                                               (-1) ** random.randrange(2) * random.randrange(FULL_ANGLE / 4), 
                                               "ball.gif",
                                               (x,y),
                                               (dx,dy) ))

Game.Start()
Run.Init()
again = True
while True:
    event = pygame.event.wait()
#     print pygame.event.event_name(event.type)
    if event.type == pygame.QUIT:
        break
    Run.Events(event)
    Run.Logic(screen)
    Run.Draw(screen)
    pygame.display.flip()
Game.Finish()
pygame.quit()
