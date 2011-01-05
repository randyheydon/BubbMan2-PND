import retrogamelib as rgl
import pygame, random, sys, os
from retrogamelib.constants import *

import game, credits, intro
from objects import spritesheet

class WorldMap(object):
    
    def __init__(self):
        load_image = rgl.util.load_image
        self.icon = spritesheet("data/bubbman.png", (24, 26))[0]
        self.font_white = rgl.font.Font(NES_FONT, (255, 255, 255))
        self.font_black = rgl.font.Font(NES_FONT, (1, 1, 1))
        self.spots = []
        self.w_levels = 8
        self.dist = 256/self.w_levels
        for i in range(self.w_levels):
            self.spots.append([i*self.dist + 6, 166])
        self.spot_imgs = [
            load_image("data/spot-1.png"), 
            load_image("data/spot-2.png")]
        self.map = load_image("data/worldmap.png")
        self.logo = load_image("data/world-logo.png")
        self.frame = 0
        if not os.path.exists("prog.sav"):
            self.unlocked = 1
            open("prog.sav", "wb").write(str(self.unlocked))
        else:
            self.unlocked = int(open("prog.sav", "rU").read())
        self.num_levels = 0
        for i in range(8):
            if os.path.exists("data/level%d.png" % (i+1)):
                self.num_levels += 1
            else:
                break
        self.pos = self.unlocked-1
        if self.unlocked > 1:
            self.first_time = False
        else:
            self.first_time = True
        
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
        
    def start_game(self):
        g = game.Game(self.pos+1)
        if self.pos == self.w_levels-1:
            g.boss_fight = True
        g.first_time = self.first_time
        g.loop()
        rgl.button.handle_input()
        if g.won:
            self.pos += 1
            if g.boss_fight:
                credits.Credits().loop()
            if self.pos >= self.unlocked and self.pos < self.num_levels:
                self.unlocked += 1
                open("prog.sav", "wb").write(str(self.unlocked))
                self.first_time = False
            else:
                self.pos -= 1
        rgl.util.play_music("data/od-special_s.mod", -1, 0.7)
        
    def loop(self):
        self.running = True
        while self.running:
            rgl.clock.tick()
            rgl.button.handle_input()
            if rgl.button.is_pressed(LEFT):
                if self.pos > 0:
                    self.pos -= 1
                    rgl.util.play_sound("data/throw.ogg")
            if rgl.button.is_pressed(RIGHT):
                if self.pos < self.unlocked-1:
                    self.pos += 1
                    rgl.util.play_sound("data/throw.ogg")
            if rgl.button.is_pressed(A_BUTTON) or rgl.button.is_pressed(START):
                rgl.util.play_sound("data/jump.ogg")
                self.start_game()
            if rgl.button.is_pressed(B_BUTTON) or rgl.button.is_pressed(SELECT):
                rgl.util.play_sound("data/spring.ogg")
                self.running = False

            self.frame += 1
            self.spot = self.spot_imgs[self.frame/12%2]
            screen = rgl.display.get_surface()
            screen.blit(self.map, (0, 0))
            for s in self.spots:
                screen.blit(self.spot, s)
            screen.blit(self.icon, (self.pos*self.dist + 6, 150))
            screen.blit(self.logo, (0, 0))
            self.render_text(screen, "Level %d" % (self.pos+1), (128, 210), 1)
            
            
            time = game.get_time(self.pos+1)
            if time >= 10000.0:
               time = "---" 
            else:
                time = "%0.01f" % time
            self.render_text(screen, "Best time: %s" % time, (128, 224), 1)
            rgl.display.update()
