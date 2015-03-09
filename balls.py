#!/usr/bin/env python
# coding: utf

import pygame
import random
import copy
from symbol import factor

FULL_ANGLE = 360
SIZE = 640, 480
NUM_BALLS = 2
TICK_INTERVAL = 100
GRAVITY_CONST = 7#0
OBJ_IMAGE_NAME = "ball.gif"
EPS = 1e-2

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

    def __init__(self, filename, pos = (0.0, 0.0), speed = (0.0, 0.0), other = None):
        '''Create a ball from image'''
        self.fname = filename
        if not other:
            self.surface = pygame.image.load(filename)
            self.orig_surface = pygame.image.load(filename)
        else:
            self.orig_surface = other.orig_surface.copy()
            self.surface = other.surface.copy()
        self.rect = self.surface.get_rect()
        self.speed = speed
        self.pos = pos
        self.newpos = pos
        self.active = True
        self.processed = False
        
    def clone(other):
        obj = Ball("", other.pos, other.speed, other)
        return obj
        
    def offset(self, other):
        """Position of the other Ball / object relative to self"""
        return (other.pos[0] - self.pos[0], other.pos[1] - self.pos[1])
        
    def intersect(self, other):
        self_mask = pygame.mask.from_surface(self.surface)
        print "count 1 = " + str(self_mask.count())
        other_mask = pygame.mask.from_surface(other.surface)
        print "count 2 = " + str(other_mask.count())
        return self_mask.overlap(other_mask, intn(*self.offset(other)))

    def draw(self, surface, all):
        for obj in all:
            if self.intersect(obj):
                print "DRAWING WRONG"
        surface.blit(self.surface, self.rect)

    def update(self, backwards = False, factor = 1):
        global Run
        sign = -1 if backwards else +1
        self.pos = self.pos[0] + sign * self.speed[0] * factor, \
            self.pos[1] + sign * self.speed[1] * factor + sign * Run.gravity_acceleration * factor ** 2 / 2
        self.speed = (self.speed[0], self.speed[1] + sign * Run.gravity_acceleration * factor)


    def action(self):
        '''Proceed some action'''
        if self.active:
            self.update()

    def logic(self, surface, objects):
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
        # before doing that we should really save all objects' states
        # because we use speeds and position to calculate
        # speed vector changes for other objects
        # but for 2 objects it's OK
        for obj in objects:
            if self.intersect(obj):
                print "overlap" + str(random.randrange(234))
                l, r = 0, 1
                print "start binsearch"
                while (r - l > EPS):
                    m = (l + r) / 2.
                    middle_1 = BallWithSizeAndRotation.clone(self)
                    middle_2 = BallWithSizeAndRotation.clone(obj)
                    middle_1.update(True, m)
                    middle_2.update(True, m)
                    print "intersect " + str(m)
                    if middle_1.intersect(middle_2):
                        l = m
                    else:
                        r = m
                    print 'OK'
                print "binsearch OK"
                self.pos = middle_1.pos
                obj.pos = middle_2.pos
                self.speed = -self.speed[0], -self.speed[1]
                obj.speed = -obj.speed[0], -obj.speed[1]
                if self.intersect(obj):
                    print "didn't help!"
                obj.rect.center = intn(*obj.pos)
                obj.processed = True
        self.rect.center = intn(*self.pos)
        


class BallWithSizeAndRotation(Ball):
    def __init__(self, factor = 1, rot_speed = 0, *args, **kwargs):
        Ball.__init__(self, *args, **kwargs)
        self.factor = factor
        self.cur_rotation = 0
        self.rot_speed = rot_speed
        self.surface = pygame.transform.rotozoom(self.orig_surface, 0, self.factor)
        self.rect = self.surface.get_rect()
        
    def clone(other):
        obj = Ball.clone(other)
        obj.factor = other.factor
        obj.cur_rotation = other.cur_rotation
        obj.rot_speed = other.rot_speed
        return obj
        
    def action(self):
        if self.active:
            self.cur_rotation = (self.cur_rotation + self.rot_speed) % FULL_ANGLE
            self.surface = pygame.transform.rotozoom(self.orig_surface, self.cur_rotation, self.factor)
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
        all = set(self.objects)
        for obj in self.objects:
            obj.processed = False
        for obj in self.objects:
            if not obj.processed:
                obj.logic(surface, all - set([obj]))
                obj.processed = True

    def Draw(self, surface):
        GameMode.Draw(self, surface)
        for obj in self.objects:
            obj.draw(surface, set(self.objects) - set([obj]))

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
    dx, dy = 0, 0
    Run.objects.append(BallWithSizeAndRotation(1, #.5 + random.random(),
                                               0, #(-1) ** random.randrange(2) * random.randrange(FULL_ANGLE / 4), 
                                               OBJ_IMAGE_NAME,
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
