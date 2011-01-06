import retrogamelib as rgl
import pygame, random, sys
from retrogamelib.constants import *

import worldmap, intro

class Menu(object):
    
    def __init__(self):
        rgl.display.init(2, "BubbMan 2", NESRES)
        intro.Intro().loop()
        self.font_white = rgl.font.Font(NES_FONT, (255, 255, 255))
        self.font_black = rgl.font.Font(NES_FONT, (1, 1, 1))
        self.menu1 = rgl.dialog.Menu(self.font_white, [" Start Game", " Controls", " Quit Game"])
        self.background = rgl.util.load_image("data/background-1.png")
        self.foreground1 = rgl.util.load_image("data/hills-back.png")
        self.foreground2 = rgl.util.load_image("data/hills-front-1.png")
        self.logo = rgl.util.load_image("data/logo.png")
        rgl.util.play_music("data/od-special_s.mod", -1, 0.7)
        self.cloud = rgl.util.load_image("data/cloud.png")
        self.clouds = []
        for i in range(10):
            self.clouds.append([random.choice([1.0, 0.8, 0.75, 0.6, 0.5, 0.4, 0.3])*2, [i*25, random.randrange(75)]])
        self.clouds.sort()
        self.clouds.reverse()
        self.help = 0
        self.help_text = [
            "Controls:",
            "",
            "A Button = Z Key   ",
            "B Button = X Key   ",
            "Start    = Enter   ",
            "Select   = R. Shift",
            "",
            "Press start!",
        ]
      
    def start_game(self):
        worldmap.WorldMap().loop()
    
    def exit_game(self):
        pygame.quit()
        sys.exit()
       
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
        
    def loop(self):
        pos = -256
        while 1:
            if pos < 0:
                pos += 12
            if pos > 0:
                pos = 0
            rgl.clock.tick()
            rgl.button.handle_input()
            
            if not self.help:
                if rgl.button.is_pressed(DOWN):
                    self.menu1.move_cursor(1)
                    rgl.util.play_sound("data/throw.ogg")
                if rgl.button.is_pressed(UP):
                    self.menu1.move_cursor(-1)
                    rgl.util.play_sound("data/throw.ogg")
            if rgl.button.is_pressed(A_BUTTON) or rgl.button.is_pressed(START):
                rgl.util.play_sound("data/jump.ogg")
                if self.menu1.option == 0:
                    self.start_game()
                if self.menu1.option == 1:
                    self.help ^= 1
                if self.menu1.option == 2:
                    self.exit_game()
            
            screen = rgl.display.get_surface()
            screen.blit(self.background, (0, 0))
            screen.blit(self.foreground1, (0, 50))
            screen.blit(self.foreground2, (0, 75))
            for cloud in self.clouds:
                cloud[1][0] -= 0.2
                screen.blit(self.cloud, ((cloud[1][0]*5)/cloud[0]/3 % (256+64) - 64, cloud[1][1]))
            screen.blit(self.logo, (pos, 0))
            
            if self.help:
                y = 120
                for text in self.help_text:
                    self.render_text(screen, text, (128, y), 1)
                    y += 12
            else:
                self.render_text(screen, "copyright 2009", (128-pos, 120), 1)
                self.render_text(screen, "created by pymike", (128-pos, 134), 1)
                pygame.draw.rect(screen, (0, 0, 0), (75-pos, 170, 115, 50))
                pygame.draw.rect(screen, (255, 255, 255), (76-pos, 171, 113, 48), 1)
                self.menu1.draw(screen, (130-pos-(len("Start Option")*8)/2, 180))
            rgl.display.update()
