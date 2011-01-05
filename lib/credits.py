import retrogamelib as rgl
import pygame, random, sys, os
from retrogamelib.constants import *

from objects import spritesheet

class Credits(object):
    
    def __init__(self):
        load_image = rgl.util.load_image
        self.oldman1 = spritesheet("data/lawn-mower.png", (96, 96))
        self.bubbman1 = spritesheet("data/bubbman.png", (24, 26))[1:][:2]
        self.oldman2 = spritesheet("data/oldman.png", (24, 26))
        self.bubbman2 = spritesheet("data/lawn-mower2.png", (96, 96))
        self.ground = spritesheet("data/grass-2.png", (24, 24))[1]
        self.fg = load_image("data/hills-front-1.png")
        self.fg2 = load_image("data/hills-back.png")
        self.bg = load_image("data/background-2.png")
        self.font_white = rgl.font.Font(NES_FONT, (255, 255, 255))
        self.font_black = rgl.font.Font(NES_FONT, (1, 1, 1))
        self.frame = 0
        self.pos = 0
        self.bubbmanpos = -128
        self.oldmanpos = -256
        self.ochasing = True
        self.transitioning = True
        self.shake = 0
        self.credits = [
            "Created by",
            "pymike",
            "",
            "",
            "",
            "Music by",
            "Operation D",
            "",
            "",
            "",
            "Sounds mixed with",
            "SFXR by DrPetter",
            "",
            "",
            "",
            "Graphics created with",
            "The Gimp 2",
            "",
            "",
            "",
            "Programmed in",
            "the python language"
            "",
            "",
            "",
            "Graphics library",
            "pygame and retrogamelib",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Thanks for playing!!"
            ]
        
        
    def loop(self):
        self.running = True
        self.ypos = 256
        pygame.mixer.music.stop()
        while self.running:
            if rgl.button.is_pressed(A_BUTTON) or rgl.button.is_pressed(START):
                self.running = False
                return
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
            if self.transitioning:
                self.draw_first(screen)
            else:
                self.draw_second(screen)
            s = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(s, (self.shake, 0))
            #if not self.frame % 2:
            rgl.display.update()

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

    def draw_first(self, screen):
        if self.oldmanpos < 256+64 and self.ochasing:
            self.bubbmanpos += 4
            self.oldmanpos += 4
            if self.oldmanpos >= 256+64:
                self.shake = 10
                rgl.util.play_sound("data/boom3.ogg")
        else:
            if abs(self.shake) > 0:
                if self.shake < 0:
                    d = 1
                else:
                    d = -1
                self.shake = abs(self.shake) - 0.25
                self.shake = self.shake*d
            else:
                if self.ochasing:
                    rgl.util.play_music("data/od-special_s.mod", -1, 0.7)
                self.ochasing = False
                if self.oldmanpos > 0:
                    self.pos -= 8
                    self.shake = 0
                    self.oldmanpos -= 4
                    self.bubbmanpos -= 4
                else:
                    self.transitioning = False
        bframe = 0
        oframe = 0
        if self.ochasing:
            bframe = self.frame/4%2
            oframe = self.frame/2%2
            screen.blit(self.oldman1[bframe], (self.oldmanpos, 240-20-96))
            screen.blit(self.bubbman1[oframe], (self.bubbmanpos, 240-20-26))
        else:
            bframe = self.frame/4%2
            oframe = self.frame/2%2
            screen.blit(self.bubbman2[bframe], (self.oldmanpos, 240-20-96))
            screen.blit(self.oldman2[oframe], (self.bubbmanpos, 240-20-26))

    def draw_second(self, screen):
        self.ypos -= .5
        if self.ypos < -len(self.credits)*12 - 24:
            self.running = False
        self.pos -= 4
        screen.blit(self.oldman2[self.frame/2%2], (128, 240-20-26))
        screen.blit(self.bubbman2[self.frame/4%2], (0, 240-20-96))
        y = 0
        for t in self.credits:
            self.render_text(screen, t, (128, y+self.ypos), 1)
            y += 12
