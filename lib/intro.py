import retrogamelib as rgl
import pygame, random, sys, os
from retrogamelib.constants import *

from objects import spritesheet, flip_images

class Intro(object):
    
    def __init__(self):
        load_image = rgl.util.load_image
        self.oldman1 = spritesheet("data/lawn-mower.png", (96, 96))
        self.bubbman1 = spritesheet("data/bubbman.png", (24, 26))[:3]
        self.bubbman2 = flip_images(self.bubbman1)
        self.ground = spritesheet("data/grass-2.png", (24, 24))[1]
        self.fg = load_image("data/hills-front-1.png")
        self.fg2 = load_image("data/hills-back.png")
        self.bg = load_image("data/background-1.png")
        self.font_white = rgl.font.Font(NES_FONT, (255, 255, 255))
        self.font_black = rgl.font.Font(NES_FONT, (1, 1, 1))
        self.frame = 0
        self.pos = 0
        self.bpos = [200, 240-26-20]
        self.opos = [0, 240-96-20]
        self.ochasing = True
        self.run_away = False
        self.stopped = None
        self.boom = rgl.util.play_sound("data/motor.ogg", 0.5)
        self.boom.stop()

    def loop(self):
        self.running = True
        self.ypos = 256
        pygame.mixer.music.stop()
        while self.running:
            self.frame += 1
            rgl.clock.tick()
            rgl.button.handle_input()
            screen = rgl.display.get_surface()
            screen.blit(self.bg, (0, 0))
            xpos = (self.pos/4) % 256
            screen.blit(self.fg2, (xpos, 50))
            screen.blit(self.fg2, (xpos+256, 50))
            screen.blit(self.fg2, (xpos-256, 50))
            xpos = (self.pos/2) % 256
            screen.blit(self.fg, (xpos, 50))
            screen.blit(self.fg, (xpos+256, 50))
            screen.blit(self.fg, (xpos-256, 50))
            for x in range(256/24 + 2):
                p = self.pos % 256
                screen.blit(self.ground, (((x*24 - 24) + p % 24), 240-24))
            if rgl.button.is_pressed(START) or rgl.button.is_pressed(A_BUTTON):
                self.running = False
            bframe = 0
            oframe = 0
            if self.bpos[0] > 128 and not self.run_away:
                self.bpos[0] -= 3
                bframe = self.frame/4%2 + 1
            else:
                if self.stopped == None:
                    self.stopped = 60
                self.stopped -= 1
                if self.stopped == 30:
                    rgl.util.play_sound("data/yell.ogg")
                if self.stopped < 30:
                    self.render_text(screen, "Get off my lawn!!", (128+self.opos[0], 100), 1)
                if self.stopped <= 0:
                    self.run_away = True
            if self.run_away:
                self.bpos[0] += 3
                self.opos[0] += 3
                bframe = self.frame/4%2 + 1
                oframe = self.frame/4%2
                self.bubbman2 = self.bubbman1
                if not pygame.mixer.get_busy():
                    self.boom.play(-1)
            if self.opos[0] > 280:
                self.running = False
            if self.opos[0] > 270:
                self.boom.stop()
            screen.blit(self.bubbman2[bframe], self.bpos)
            screen.blit(self.oldman1[oframe], self.opos)
            rgl.display.update()
        self.boom.stop()

    def render_text(self, surface, text, pos, center=False):
        ren1 = self.font_black.render(text)
        ren2 = self.font_white.render(text)
        p = pos
        if center:
            p = (pos[0] - ren1.get_width()/2, pos[1])
        surface.blit(ren1, (p[0], p[1]+1))
        surface.blit(ren1, (p[0], p[1]-1))
        surface.blit(ren1, (p[0]+1, p[1]))
        surface.blit(ren1, (p[0]-1, p[1]))
        surface.blit(ren2, (p[0], p[1]))
        del ren1, ren2
