import pygame, math, random
import retrogamelib as rgl

def flip_images(images):
    new = []
    for i in images:
        new.append(pygame.transform.flip(i, 1, 0))
    return new

def scale_images(images, scale):
    new = []
    for i in images:
        new.append(pygame.transform.scale(i, (int(i.get_width()*scale), int(i.get_height()*scale))))
    return new

def spritesheet(image, size):
    images = []
    img = rgl.util.load_image(image)
    for y in range(img.get_height()/size[1]):
        for x in range(img.get_width()/size[0]):
            i = pygame.Surface(size)
            i.fill((1, 48, 6))
            i.set_colorkey((1, 48, 6), pygame.RLEACCEL)
            i.blit(img, (-x*size[0], -y*size[1]))
            images.append(i)
    return images

class Camera(object):
    
    def __init__(self, engine, width):
        self.width = width
        self.rect = pygame.Rect(0, 0, 256, 240)
        engine.camera = self
        self.bounds = 120
    
    def update(self):
        if self.player.rect.left > self.rect.right-self.bounds:
            self.rect.right = self.player.rect.left+self.bounds
        if self.player.rect.right < self.rect.left+self.bounds:
            self.rect.left = self.player.rect.right-self.bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.width:
            self.rect.right = self.width
    
    def translate(self, rect):
        return pygame.Rect(rect.x - self.rect.x, rect.y - self.rect.y,
            rect.w, rect.h)

class Object(rgl.gameobject.Object):
    
    def __init__(self, engine):
        rgl.gameobject.Object.__init__(self, self.groups)
        self.engine = engine
        self.offset = (0, 0)
        self.always_update = True
        if not hasattr(self, "non_stationary"):
            self.non_stationary = []
    
    def move(self, dx, dy):
        if dx != 0:
            self.move_one_axis(dx, 0)
        if dy != 0:
            self.move_one_axis(0, dy)

    def move_one_axis(self, dx, dy):
        self.rect.move_ip(dx, dy)
        tiles = self.check_collisions()
        for t in tiles:
            if t.rect.colliderect(self.rect):
                self.on_collision(dx, dy, t)
        for n in self.non_stationary:
            if n.rect.colliderect(self.rect):
                self.on_collision(dx, dy, n)
    
    def on_collision(self, dx, dy, tile):
        if tile.slant == 0:
            self.respond(dx, dy, tile)
        else:
            self.slant_respond(dx, dy, tile)
    
    def respond(self, dx, dy, t):
        if dx > 0 and t.on_end[2]:
            self.rect.right = t.rect.left
        if dx < 0 and t.on_end[3]:
            self.rect.left = t.rect.right
        if dy > 0 and t.on_end[0]:
            self.rect.bottom = t.rect.top
        if dy < 0 and t.on_end[1]:
            self.rect.top = t.rect.bottom
    
    def slant_respond(self, dx, dy, tile):
        top = None
        if tile.slant < 0:
            if self.rect.left >= tile.rect.left:
                x = self.rect.left - tile.rect.left
                top = tile.rect.top+x-2
        if tile.slant > 0:
            if self.rect.right <= tile.rect.right:
                x = tile.rect.right - self.rect.right
                top = tile.rect.top+x-2
        if top:
            if self.rect.bottom > top:
                self.rect.bottom = top
                if self.rect.bottom < tile.rect.top:
                    self.rect.bottom = tile.rect.top
    
    def draw(self, surface):
        surface.blit(self.image, self.engine.camera.translate(self.rect.move(*self.offset)))
        
    def check_collisions(self):
        tiles = self.engine.tiles
        collide_tiles = []
        pos_tile = int(self.rect.centerx / 24), int(self.rect.bottom / 24)
        w = int(self.rect.w/12)*2
        h = int(self.rect.h/12)*2
        for x in xrange(pos_tile[0]-w, pos_tile[0]+w):
            for y in xrange(pos_tile[1]-h, pos_tile[1]+h):
                if x < 0 or x >= len(tiles[0]) or \
                   y < 0 or y >= len(tiles):
                    continue

                tile = tiles[y][x]
                if not tile:
                    continue
                if tile.rect.colliderect(self.rect) and tile.alive():
                    collide_tiles.append(tile)
        
        collide_tiles.sort()
        return collide_tiles

class Player(Object):
    
    def __init__(self, engine, x=4):
        Object.__init__(self, engine)
        self.right_images = spritesheet("data/bubbman.png", (24, 26))
        self.left_images = flip_images(self.right_images)
        self.images = self.right_images
        self.image = self.images[0]
        self.rect = pygame.Rect(0, 0, 12, 22)
        self.offset = (-(24-self.rect.w)/2, -2)
        self.rect.topleft = (x, 0)
        self.dx = 0.0
        self.dy = 0.0
        self.max_run = 4.0
        self.max_jump = 10.0
        self.fall_speed = 0.8
        self.jumping = False
        self.facing = 1
        self.frame = 0
        self.moving = False
        self.move_speed = 0.5
        self.attached = None
        self.land_pos = 0
        self.shoot_timer = 0
        self.dying = False
        self.accel = 0.8
        self.decel = 0.9
        self.energy = 50
        for i in range(240/16):
            self.move(0, 16)
    
    def die(self):
        if not self.dying:
            self.dying = True
            self.dy = -10
            rgl.util.play_sound("data/die.ogg")
    
    def jump(self):
        if not self.jumping:
            rgl.util.play_sound("data/jump.ogg", 0.8)
            self.jumping = True
            self.dy = -8
        if self.sliding != 0:
            rgl.util.play_sound("data/jump.ogg", 0.8)
            self.facing = self.sliding
            self.dx = self.sliding*6
            self.dy = -9
            self.jumping = True
            self.sliding = 0
    
    def shoot(self):
        if not self.sliding and self.shoot_timer <= 0:
            rgl.util.play_sound("data/throw.ogg")
            self.shoot_timer = 6
    
    def accelerate(self, dx, dy):
        self.dx += dx
        self.dy += dy
        if dx != 0:
            self.moving = True
        if dx < 0:
            self.facing = -1
        if dx > 0:
            self.facing = 1
        if self.dx > self.max_run:
            self.dx = self.max_run
        if self.dx < -self.max_run:
            self.dx = -self.max_run
        if self.dy > self.max_jump:
            self.dy = self.max_jump
    
    def decelerate(self, dx, dy):
        if dx != 0:
            self.dx *= dx
        if dy != 0:
            self.dy *= dy
    
    def update(self):
        if self.engine.world == 1:
            self.decel = 0.8
            self.move_speed = 0.5
        else:
            self.decel = 0.925
            self.move_speed = 0.1
        if not self.dying:
            self.shoot_timer -= 1
            self.frame += 1
            if self.attached:
                dx = self.attached.dx + self.dx
            else:
                dx = self.dx
            self.move(dx, self.dy)
            if self.rect.left < 0:
                self.rect.left = 0
                self.dx = 0
            self.accelerate(0, self.fall_speed)
            if self.dy > self.fall_speed + self.max_run + 2:
                self.jumping = True
            if self.facing > 0:
                self.images = self.right_images
            else:
                self.images = self.left_images
            
            frame = 0
            if self.moving:
                frame = self.frame/2%3 + 1
            if self.jumping:
                frame = 4
                self.move_speed = 0.3
                self.attached = None
            else:
                self.move_speed = 0.5
            if self.shoot_timer > 0:
                frame = 7
            if self.shoot_timer == 3:
                Rock(self.engine, self.rect.center, self.facing)
            if self.shoot_timer > 3:
                frame = 6
            if self.sliding:
                frame = 5
        else:
            self.frame += 1
            frame = self.frame/4%2 + 8
            self.rect.move_ip(0, self.dy)
            self.dy += 0.5
        self.image = self.images[int(frame)]
    
    def on_collision(self, dx, dy, tile):
        if tile.slant == 0:
            self.respond(dx, dy, tile)
            if dx != 0 and (tile.on_end[2] or tile.on_end[3]):
                if self.dy >= -2 and self.jumping and not isinstance(tile, MovingPlatform):
                    if self.dy > 0.5:
                        self.dy = 0.5
                    if dx > 0:
                        self.sliding = -1
                        self.facing = 1
                    if dx < 0:
                        self.sliding = 1
                        self.facing = -1
                    self.dx = self.facing*1.1
                else:
                    if self.dx > 0 and tile.on_end[2]:
                        self.dx = 0
                    if self.dx < 0 and tile.on_end[3]:
                        self.dx = 0
            else:
                self.sliding = 0
            if dy < 0 and not isinstance(tile, Water):
                self.dy = 0
            if dy > 0:
                if not isinstance(tile, Water):
                    self.dy = self.max_run
                    self.jumping = False
                    if isinstance(tile, MovingPlatform):
                        self.attached = tile
                    elif isinstance(tile, Spikes):
                        self.die()
                if isinstance(tile, Water):
                    self.jumping = True
                    if self.rect.bottom < (tile.rect.top + self.max_jump*1.5):
                        self.jumping = False
                        self.dy = 2
        else:
            self.slant_respond(dx, dy, tile)
            if dy > 0:
                self.dy = self.max_run
                self.jumping = False

class Platform(Object):
    
    def __init__(self, engine, pos, on_end, is_slant=False, under_slant=False):
        Object.__init__(self, engine)
        self.images = spritesheet("data/grass-%d.png" % (engine.world+1), (24, 24))
        self.on_end = on_end
        i = 6
        if self.on_end[1]:
            i = 11
        if self.on_end[0]:
            i = 1
        if self.on_end[2]:
            i = 5
            if self.on_end[1]:
                i = 10
            if self.on_end[0]:
                i = 0
        if self.on_end[3]:
            i = 7
            if self.on_end[1]:
                i = 12
            if self.on_end[0]:
                i = 2
            if self.on_end[2]:
                i = 9
                if self.on_end[0]:
                    i = 4
        self.slant = 0
        if is_slant:
            if on_end[2]:
                i = 3
                self.slant = 1
            if on_end[3]:
                i = 8
                self.slant = -1
        if under_slant < 0:
            i = 13
        if under_slant > 0:
            i = 14
        self.image = self.images[i]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.h = 13
        self.offset = (0, -3)
        self.rect.y += 3

class Spikes(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = spritesheet("data/spikes.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.y += 10
        self.rect.h -= 10
        self.slant = 0
        self.on_end = [True]*4

class MovingPlatform(Object):
    
    def __init__(self, engine, pos, orient):
        Object.__init__(self, engine)
        self.on_end = [True]*4
        self.image = rgl.util.load_image("data/moving-platform-%d.png" % engine.world)
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.h = self.rect.h-8
        self.offset = (0, -3)
        self.rect.y += 3
        self.frame = 0
        
        self.orient = orient
        if self.orient == 0:
            self.orig = self.rect.x
        else:
            self.orig = self.rect.y
        self.slant = 0
        self.speed = 1
        self.dx = self.dy = 0

    def update(self):
        self.frame += 0.1
        if self.speed > 0:
            p = self.orig + math.sin(self.frame)*24
        else:
            p = self.orig - math.sin(self.frame)*24
        if self.orient == 0:
            diff = p - self.rect.x
            self.move(diff, 0)
            self.dx = diff
        else:
            diff = p - self.rect.y
            self.move(0, diff)
            self.dy = diff

    def on_collision(self, dx, dy, tile):
        if not tile.dying:
            if dy < 0:
                tile.rect.bottom = self.rect.top
            if dy > 0:
                tile.rect.top = self.rect.bottom
            if dx < 0:
                tile.rect.right = self.rect.left
            if dx > 0:
                tile.rect.left = self.rect.right

class Deco(Object):
    
    def __init__(self, engine, pos, image):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/%s.png" % image)
        self.rect = self.image.get_rect(midbottom=pos)
        self.rect.w = 24
        self.z = -2

    def update(self):
        self.move(0, 5)

    def on_collision(self, dx, dy, tile):
        if tile.slant == 0:
            self.respond(dx, dy, tile)

class Spring(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = spritesheet("data/spring.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.anim_time = 0
        self.z = 1
    
    def update(self):
        self.move(0, 4)
        self.image = self.images[0]
        self.anim_time -= 1
        if self.anim_time > 0:
            self.image = self.images[1]

class Rock(Object):
    
    def __init__(self, engine, pos, facing):
        Object.__init__(self, engine)
        self.images = spritesheet("data/rock.png", (8, 8))
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.rect.move_ip(12*facing, 0)
        self.dy = -3
        self.dx = 8*facing
        self.angle = 0
        self.dying = False
        self.facing = facing
    
    def update(self):
        self.dy += 0.8
        self.rect.move_ip(self.dx, self.dy)
        if self.rect.y > 240:
            self.kill()
        self.angle += self.dx*3
        self.image = pygame.transform.rotate(self.images[0], self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def hit(self):
        if not self.dying:
            self.dx = -self.facing*2
            self.dy = -5
            self.dying = True

class Bomb(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = spritesheet("data/bomb.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.rect.w = 16
        self.rect.h = 16
        self.offset = (-4, -4)
        self.dy = -10
        self.dx = random.choice([6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.angle = 0
        self.frame = 0
        self.always_update = True

    def update(self):
        self.frame += 1
        self.dy += 0.5
        if self.dy > 5:
            self.dy = 5
        self.dx *= 0.99
        self.move(self.dx, self.dy)
        if self.rect.y > 240:
            self.kill()
        self.angle += self.dx*3
        self.image = self.images[self.frame/4%2]

    def on_collision(self, dx, dy, tile):
        self.kill()
    
    def kill(self):
        Object.kill(self)
        Explosion(self.engine, self.rect.center)
        rgl.util.play_sound("data/boom1.ogg", 0.8)

class Particle(Object):
    
    def __init__(self, engine, pos, dx, dy):
        Object.__init__(self, engine)
        self.images = spritesheet("data/particle-%d.png" % self.engine.world, (12, 12))
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.dy = -1*dy
        self.dx = random.randrange(-1, 3)*dx
        self.angle = 0.0
    
    def update(self):
        self.dy += 0.8
        self.rect.move_ip(self.dx, self.dy)
        if self.rect.y > 240:
            self.kill()
        self.angle += self.dx*3
        self.image = pygame.transform.rotate(self.images[0], self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Explosion(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = spritesheet("data/exp.png", (48, 48))
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.frame = 0
    
    def update(self):
        self.frame += 1
        if self.frame > 24:
            self.kill()
        self.image = self.images[self.frame/2%2]

class Baddie(Object):
        
    def __init__(self, engine):
        Object.__init__(self, engine)
        self.dx = -1
        self.speed = 1
        self.frame = 0
        self.hitframe = 0
        self.hp = 1
        self.dying = False
        self.die_dy = -5
        self.z = 1
        self.always_update = False
        self.dy = 0
    
    def update(self):
        if self.dying:
            self.die_dy += 0.8
            self.image = self.images[2]
            self.rect.move_ip(0, self.die_dy)
        else:
            self.hitframe -= 1
            self.move(self.dx*self.speed, self.dy)
            self.image = self.images[self.frame/4%2]
            if self.hitframe > 0:
                self.image = self.images[-1]
            self.frame += 1
        if self.rect.y > 240:
            self.kill()
    
    def on_collision(self, dx, dy, tile):
        if tile.slant != 0:
            self.slant_respond(dx, dy, tile)
        else:
            self.respond(dx, dy, tile)
            if dx != 0:
                self.dx = -self.dx

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            if self.hp <= 0:
                self.dying = True
                rgl.util.play_sound("data/die.ogg")
    
    def do_ai(self, player):
        pass

class Gopher(Baddie):
    
    def __init__(self, engine, pos):
        Baddie.__init__(self, engine)
        self.images = spritesheet("data/gopher.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.w -= 8
        self.speed = 1
        self.hp = 1
        self.dy = 5
        self.offset = (-(self.image.get_width()-self.rect.w)/2, 0)

class Bird(Baddie):
    
    def __init__(self, engine, pos):
        Baddie.__init__(self, engine)
        self.images = spritesheet("data/bird.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.h -= 12
        self.offset = (0, -(self.image.get_height()-self.rect.h)/2)
        self.speed = 1
        self.hp = 1
        self.dx = 0
        self.dy = 0
    
    def update(self):
        self.rect.move_ip(-3, 3)
        Baddie.update(self)

class Plant(Baddie):
    
    def __init__(self, engine, pos):
        Baddie.__init__(self, engine)
        self.images = spritesheet("data/plant.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 1
        self.hp = 100
        self.dx = 0
        self.dy = 4
        self.rect.y += 5
    
class Fish(Baddie):
    
    def __init__(self, engine, pos):
        Baddie.__init__(self, engine)
        self.images = spritesheet("data/fish.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.w -= 16
        self.rect.x += 8
        self.offset = (-(self.image.get_width()-self.rect.w)/2, 0)
        self.speed = 1
        self.hp = 1
        self.hp = 1
        self.dy = 5
        self.always_update = True
    
    def update(self):
        if self.dying:
            self.die_dy += 0.8
            self.image = self.images[random.randrange(0, 3)]
            self.rect.move_ip(5, self.die_dy)
        else:
            self.frame += 1
            self.dy += 0.5
            if self.rect.y > 240+128:
                self.dy = -15
            if self.dy > 0:
                frame = self.frame/4%2 + 2
            else:
                frame = self.frame/4%2
            self.image = self.images[frame]
            self.rect.move_ip(0, self.dy)

class Frog(Baddie):
    
    def __init__(self, engine, pos):
        Baddie.__init__(self, engine)
        self.images = spritesheet("data/frog.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.w -= 6
        self.offset = (-(self.image.get_width()-self.rect.w)/2, 0)
        self.speed = 1
        self.hp = 1
        self.dy = 5
        self.speed = 0
        self.in_air = True
    
    def update(self):
        Baddie.update(self)
        if not self.dying:
            self.frame += 1
            self.dy += 0.5
            if self.dy > 10:
                self.dy = -5
                self.in_air = True
            frame = 0
            if self.in_air:
                self.move(-2, 0)
                frame = 1
            self.move(0, self.dy)
            self.image = self.images[frame]

    def on_collision(self, dx, dy, tile):
        if tile.slant != 0:
            self.slant_respond(dx, dy, tile)
        else:
            self.respond(dx, dy, tile)
            if dx != 0:
                self.dx = -self.dx
        if dy > 0:
            self.in_air = False

class OldGuy(Baddie):
    
    def __init__(self, engine, pos):
        Baddie.__init__(self, engine)
        self.images = spritesheet("data/lawn-mower.png", (96, 96))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topright=pos)
        self.rect.bottom = 252
        self.speed = 2
        self.hp = 100000000
        self.dy = 0
        self.dx = 1
        self.frame = 0
        self.always_update = True
        self.z = -1
        
    def update(self):
        self.frame += 1
        self.move(self.speed, 0)
        self.image = self.images[self.frame/4%2]
    
    def on_collision(self, dx, dy, t):
        if t.alive():
            t.kill()
            if not t.alive():
                if not random.randrange(1):
                    rgl.util.play_sound("data/boom%d.ogg" % random.choice([1, 2]), 0.4)
                Particle(self.engine, t.rect.topleft, -1, 8)
                Particle(self.engine, t.rect.topright, 1, 8)
                Particle(self.engine, t.rect.bottomleft, -1, 4)
                Particle(self.engine, t.rect.bottomright, 1, 4)
        
class Fruit(Object):
    
    def __init__(self, engine, pos, image):
        Object.__init__(self, engine)
        self.images = spritesheet("data/%s.png" % image, (24, 24))
        self.image = self.images[0]
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.rect.center = pos
        self.frame = 0
        self.draw_rect = self.image.get_rect(center = self.rect.center)
    
    def update(self):
        self.frame += 0.25
        self.image = pygame.transform.rotate(self.images[0], math.sin(self.frame)*25)
        self.draw_rect = self.image.get_rect(center = self.rect.center)

    def draw(self, surface):
        surface.blit(self.image, self.engine.camera.translate(self.draw_rect))

class TextMessage(Object):
    
    def __init__(self, engine, text, pos):
        Object.__init__(self, engine)
        self.image = pygame.Surface((len(text)*9 + 2, 10))
        self.image.fill((255, 0, 255))
        self.image.set_colorkey((255, 0, 255))
        self.engine.game.render_text(self.image, text, (1, 1))
        self.rect = self.image.get_rect(center = pos)
        self.z = 3
        self.life = 20
    
    def update(self):
        self.rect.move_ip(0, -1)
        self.life -= 1
        if self.life <= 0:
            self.kill()

class Water(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = spritesheet("data/water.png", (24, 24))
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.y += 10
        self.offset = (0, -4)
        self.frame = 0
        self.z = 2
        self.on_end = [False]*4
        self.slant = 0
    
    def update(self):
        self.image = self.images[self.frame/4%3]
        self.frame += 1
    
    def kill(self):
        self.rect.move_ip(0, 2)

class Checkpoint(object):
    
    def __init__(self, pos):
        self.rect = pygame.Rect(pos[0], pos[1], 24, 24)
