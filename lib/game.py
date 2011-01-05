import retrogamelib as rgl
import pygame, random, time, os
from retrogamelib.constants import *

from objects import *
from engine import *
rgl.util.set_global_sound_volume(0.6)

def get_time(lvl):
    time = 10000.0
    if os.path.exists("level%d.high" % lvl):
        score = open("level%d.high" % lvl, "rU").read()
        time = float(score.split("\n")[0])
    return time

class Game(object):
    
    def __init__(self, level):
        self.objects = rgl.gameobject.Group()
        self.non_stationary = rgl.gameobject.Group()
        self.players = rgl.gameobject.Group()
        self.springs = rgl.gameobject.Group()
        self.baddies = rgl.gameobject.Group()
        self.rocks = rgl.gameobject.Group()
        self.fruit = rgl.gameobject.Group()
        self.water = rgl.gameobject.Group()
        self.spikes = rgl.gameobject.Group()
        self.bombs = rgl.gameobject.Group()
        
        Player.groups = [self.objects, self.players]
        Player.non_stationary = self.non_stationary
        Platform.groups = [self.objects]
        MovingPlatform.groups = [self.objects, self.non_stationary]
        MovingPlatform.non_stationary = self.players
        Deco.groups = [self.objects]
        Spring.groups = [self.objects, self.springs]
        Rock.groups = [self.objects, self.rocks]
        Gopher.groups = [self.objects, self.baddies]
        Bird.groups = [self.objects, self.baddies]
        Plant.groups = [self.objects, self.baddies]
        Fish.groups = [self.objects, self.baddies]
        Frog.groups = [self.objects, self.baddies]
        OldGuy.groups = [self.objects, self.baddies]
        Fruit.groups = [self.objects, self.fruit]
        Water.groups = [self.objects, self.water]
        Spikes.groups = [self.objects, self.water]
        Particle.groups = [self.objects]
        TextMessage.groups = [self.objects]
        Bomb.groups = [self.objects, self.bombs]
        Explosion.groups = [self.objects]
        
        self.level = level
        self.checkpoint = None
        self.passed_checkpoint = False
        self.score = 0
        self.boss_fight = False
        self.engine = Engine(self, self.level)
        self.engine.parse_level()
        w = self.engine.world
        if self.level >= 5:
            w = 2
        self.background = rgl.util.load_image("data/background-%d.png" % w)
        self.back_hills = rgl.util.load_image("data/hills-back.png")
        self.front_hills = rgl.util.load_image("data/hills-front-%d.png" % self.engine.world)
        self.cloud = rgl.util.load_image("data/cloud.png")
        self.end_screen = rgl.util.load_image("data/level-complete.png")
        self.flake = pygame.Surface((8, 8))
        self.flake.set_colorkey((0, 0, 0), pygame.RLEACCEL)
        pygame.draw.circle(self.flake, (255, 255, 255), (4, 4), 2)
        self.camera = Camera(self.engine, self.engine.image.get_width()*24)
        self.player = Player(self.engine)
        self.clouds = []
        for i in range(10):
            self.clouds.append([random.choice([1.0, 0.8, 0.75, 0.6, 0.5, 0.4, 0.3])*2, [i*25, random.randrange(75)]])
        self.clouds.sort()
        self.clouds.reverse()
        self.font_white = rgl.font.Font(NES_FONT, (255, 255, 255))
        self.font_black = rgl.font.Font(NES_FONT, (1, 1, 1))
        self.won = False
        self.snow = []
        for y in range(256/64):
            for x in range(240/64):
                self.snow.append([random.choice([1.0, 0.8, 0.75, 0.6, 0.5, 0.4, 0.3])*2, [(x*64)+random.randrange(-10, 10), (y*64)+random.randrange(-10, 10)]])
        self.paused = 0
        if self.engine.music == 1:
            rgl.util.play_music("data/od-green_groove.mod", -1, 0.7)
        if self.engine.music == 2:
            rgl.util.play_music("data/od-nkpng.mod", -1, 1)
        if self.engine.music == 3:
            rgl.util.play_music("data/od-fs.mod", -1, 1)
        if self.engine.music == 4:
            rgl.util.play_music("data/od-endorfin.mod", -1, 1)
        if self.engine.music == 5:
            rgl.util.play_music("data/od-irony.mod", -1, 1)
        self.start_time = time.time()
        self.time = (time.time()-self.start_time)
    
    def end_level(self):
        pos = -256
        rgl.util.play_music("data/end.mod")
        while 1:
            if pos < 0:
                pos += 12
            if pos > 0:
                pos = 0
            rgl.clock.tick()
            rgl.button.handle_input()
            if rgl.button.is_pressed(START):
                break
            surface = rgl.display.get_surface()
            surface.blit(self.end_capture, (0, 0))
            surface.blit(self.end_screen, (pos, 0))
            energy = self.player.energy*2
            self.total_score = (self.score + (self.engine.image.get_width()-self.etime)) * (energy/2)
            self.render_text(surface, "Time: %0.01f" % self.time, (128-pos, 115), 1)
            self.render_text(surface, "Score: %04d" % self.score, (128-pos, 130), 1)
            self.render_text(surface, "Energy: %02d" % energy, (128-pos, 145), 1)
            self.render_text(surface, "Total: %06d" % self.total_score, (128-pos, 170), 1)
            self.render_text(surface, "Press Start!", (128-pos, 200), 1)
            rgl.display.update()
        t = get_time(self.level)
        if self.time < t:
            open("level%d.high" % self.level, "wb").write(str(self.time))
        pygame.mixer.music.stop()
    
    def restart(self):
        self.score = 0
        for obj in self.objects:
            Object.kill(obj)
        self.engine.parse_level()
        self.camera = Camera(self.engine, self.engine.image.get_width()*24)
        if self.passed_checkpoint:
            self.player = Player(self.engine, self.checkpoint.rect.x)
            self.oldguy.rect.right = self.checkpoint.rect.x - 128
        else:
            self.start_time = time.time()
            self.player = Player(self.engine, 4)
        self.won = False
    
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
        self.running = True
        while self.running:
            self.update()
            if self.won:
                break
            self.handle_input()
            if self.won:
                break
            self.draw()
    
    def update(self):
        rgl.clock.tick()
        if not self.paused:
            self.camera.player = self.player
            self.camera.update()
            for obj in self.objects:
                if (obj.rect.right >= self.camera.rect.left and obj.rect.left <= self.camera.rect.right) or obj.always_update:
                    obj.update()
                    obj.always_update = True
                if obj.rect.right < self.camera.rect.left:
                    if isinstance(obj, Baddie) and not isinstance(obj, OldGuy):
                        obj.kill()
            if self.player.rect.top >= 240 and not self.player.dying:
                self.player.die()
            if self.player.rect.top > 240 and self.player.dying and self.player.dy > 0:
                self.player.kill()
            if self.player.rect.left >= self.engine.image.get_width()*24:
                self.etime = self.time
                self.end_level()
                self.running = False
                self.won = True
            if not self.won:
                self.time = (time.time()-self.start_time)
            for s in self.springs:
                if s.rect.colliderect(self.player.rect) and \
                    self.player.rect.bottom < s.rect.top+(self.player.dy*2) and \
                    self.player.dy > 0 and not self.player.dying:
                    self.player.rect.bottom = s.rect.top
                    rgl.util.play_sound("data/spring.ogg")
                    self.player.jumping = True
                    self.player.dy = -13
                    s.anim_time = 3
                    self.player.sliding = False
            for r in self.rocks:
                for b in self.baddies:
                    if b.rect.colliderect(r.rect) and not r.dying and not b.dying:
                        r.hit()
                        b.hit()
                        if b.dying:
                            self.score += 50
                        rgl.util.play_sound("data/hit.ogg")
            for f in self.fruit:
                if self.player.rect.colliderect(f.rect):
                    f.kill()
                    TextMessage(self.engine, "+25", f.rect.center)
                    rgl.util.play_sound("data/powerup.ogg")
                    self.score += 25
                    self.player.energy += 15
                    if self.player.energy > 50:
                        self.player.energy = 50
            for b in self.baddies:
                if b.rect.colliderect(self.player.rect) and not b.dying and not self.player.dying:
                    self.player.die()
            for s in self.spikes:
                if s.rect.colliderect(self.player.rect) and not self.player.dying:
                    self.player.die()
            for b in self.bombs:
                if b.rect.colliderect(self.player.rect) and not self.player.dying:
                    self.player.die()
                    b.kill()
            if self.player.dx > 0:
                self.oldguy.speed = 2
            if self.player.dx > 2:
                self.oldguy.speed = 3
            margin = 24
            if self.boss_fight == True:
                margin = -64
            if self.oldguy.rect.right < self.player.rect.left-128-margin:
                self.oldguy.speed = 4
            if self.first_time:
                self.oldguy.speed -= 1
            if self.player.rect.left < 48:
                self.oldguy.speed = 0
            if self.boss_fight == True:
                if self.oldguy.speed < 3:
                    self.oldguy.speed += 1
                if len(self.bombs) < 5 and not random.randrange(15):
                    Bomb(self.engine, self.oldguy.rect.topleft)
            if self.checkpoint:
                if not self.passed_checkpoint:
                    if self.player.rect.x > self.checkpoint.rect.x:
                        self.passed_checkpoint = True
                        TextMessage(self.engine, "Checkpoint!", self.player.rect.midtop)
    
    def handle_input(self):
        rgl.button.handle_input()
        
        if self.player.alive() and not self.paused:
            self.player.moving = False
            if rgl.button.is_held(LEFT):
                self.player.accelerate(-self.player.move_speed, 0)
            elif rgl.button.is_held(RIGHT):
                self.player.accelerate(self.player.move_speed, 0)
            else:
                if not self.player.jumping:
                    self.player.decelerate(self.player.decel, 0)
                else:
                    self.player.decelerate(0.999, 0)
            self.player.energy -= abs(self.player.dx)*0.075
            
            if rgl.button.is_pressed(A_BUTTON):
                self.player.jump()
            if rgl.button.is_held(A_BUTTON):
                self.player.fall_speed = 0.8
            else:
                self.player.fall_speed = 1.2
            if rgl.button.is_pressed(B_BUTTON):
                self.player.shoot()
            if rgl.button.is_held(A_BUTTON) and rgl.button.is_pressed(SELECT) and rgl.button.is_held(B_BUTTON):
                self.passed_checkpoint = True
                self.restart()
    
        if rgl.button.is_pressed(SELECT):
            if self.paused:
                self.running = False
            else:
                self.restart()
        if rgl.button.is_pressed(START) and self.player.alive():
            self.paused ^= 1
            if self.paused:
                self.ptime = time.time()
            else:
                self.start_time -= self.ptime-time.time()
        if self.player.energy <= 0:
            self.player.energy = 0
            self.player.die()

    def draw(self):
        surface = rgl.display.get_surface()
        if not self.paused and not self.won:
            surface.blit(self.background, (0, 0))
            
            xpos = -((self.camera.rect.x+128)/8) % 256
            surface.blit(self.back_hills, (xpos, 50))
            surface.blit(self.back_hills, (xpos+256, 50))
            surface.blit(self.back_hills, (xpos-256, 50))
            
            xpos = -(self.camera.rect.x/3.5) % 256
            surface.blit(self.front_hills, (xpos, 50))
            surface.blit(self.front_hills, (xpos+256, 50))
            surface.blit(self.front_hills, (xpos-256, 50))
            for cloud in self.clouds:
                cloud[1][0] -= 0.2
                surface.blit(self.cloud, (-(self.camera.rect.x-(cloud[1][0]*5))/cloud[0]/3 % (256+64) - 64, cloud[1][1]))
            if self.level >= 5:
                for snow in self.snow:
                    snow[1][0] -= 0.2
                    snow[1][1] += 0.5
                    if snow[1][1] > 240:
                        snow[1][1] = 0
                    surface.blit(self.flake, (-(self.camera.rect.x-(snow[1][0]*5)) % 264 - 8, snow[1][1]))

            for obj in self.objects:
                if (obj.rect.right >= self.camera.rect.left and obj.rect.left <= self.camera.rect.right):
                    obj.draw(surface)
            self.render_text(surface, "score", (108, 8))
            self.render_text(surface, "%06d" % self.score, (108, 20))
            self.render_text(surface, "time", (214, 8), 1)
            self.render_text(surface, "%03.01f" % self.time, (214, 20), 1)
            pygame.draw.rect(surface, (0, 0, 0), (9, 9, 77, 17))
            if self.player.energy > 0:
                pygame.draw.rect(surface, (255, int(255*(self.player.energy/50)), 0), (10, 10, self.player.energy*1.5, 15))
            if not self.player.alive() and not self.won:
                self.render_text(surface, "Press Select to try again", (128, 120), 1)
            if self.won:
                self.render_text(surface, "Nice, you won!", (128, 120), 1)
        if self.paused:
            self.render_text(surface, "paused", (128, 120), 1)
            self.render_text(surface, "press select to quit", (128, 134), 1)
        
        self.end_capture = surface.copy()
        rgl.display.update()
