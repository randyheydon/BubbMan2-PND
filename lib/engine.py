import retrogamelib as rgl
from objects import *

class Engine(object):
    
    def __init__(self, game, level):
        self.level = level
        self.tiles = []
        self.image = rgl.util.load_image("data/level%d.png" % level, colorkey=None)
        if self.level >= 6:
            self.world = 2
        else:
            self.world = 1
        if self.level <= 4:
            self.music = 1
        if self.level == 5:
            self.music = 5
        if self.level == 6:
            self.music = 2
        if self.level == 7:
            self.music = 3
        if self.level == 8:
            self.music = 4
        self.pos = [0, 0]
        self.game = game

    def parse_level(self):
        self.image = rgl.util.load_image("data/level%d.png" % self.level, colorkey=None)
        tiles = []
        self.tiles = []
        platforms = [[0, 0, 0], [150, 150, 150]]
        for y in range(self.image.get_height()):
            tiles.append([])
            for x in range(self.image.get_width()):
                color = list(self.image.get_at((x, y))[:-1])
                if color in platforms:
                    on_end = [False]*4
                    is_slant = False
                    under_slant = 0
                    if self.get_at(x, y-1) not in platforms:
                        on_end[0] = True
                    if self.get_at(x, y+1) not in platforms:
                        on_end[1] = True
                    if self.get_at(x-1, y) not in platforms:
                        on_end[2] = True
                    if self.get_at(x+1, y) not in platforms:
                        on_end[3] = True
                    if color == platforms[1]:
                        is_slant = True
                    if self.get_at(x, y-1) == platforms[1]:
                        if self.get_at(x-1, y-1) not in platforms:
                            under_slant = -1
                        if self.get_at(x+1, y-1) not in platforms:
                            under_slant = 1
                    p = Platform(self, (x*24, y*24), on_end, is_slant, under_slant)
                    tiles[-1].append(p)
                elif color == [255, 255, 0]:
                    tiles[-1].append(Spikes(self, (x*24, y*24)))
                elif color == [255, 0, 255]:
                    w = Water(self, (x*24, y*24))
                    tiles[-1].append(w)
                else:
                    tiles[-1].append(None)
                if color == [125, 125, 125]:
                    MovingPlatform(self, (x*24, y*24), 1)
                if color == [100, 100, 100]:
                    MovingPlatform(self, (x*24, y*24), 1).speed = -1
                if color == [75, 75, 75]:
                    MovingPlatform(self, (x*24, y*24), 0)
                if color == [0, 200, 0]:
                    Deco(self, (x*24 + 12, y*24 + 26), "tree-%d" % self.world)
                if color == [0, 150, 0]:
                    Deco(self, (x*24 + 12, y*24 + 26), "bush-%d" % self.world)
                if color == [220, 220, 220]:
                    Spring(self, (x*24, y*24 + 2))
                if color == [0, 0, 255]:
                    Gopher(self, (x*24, y*24))
                if color == [0, 0, 200]:
                    Bird(self, (x*24, y*24))
                if color == [0, 0, 150]:
                    Plant(self, (x*24, y*24))
                if color == [0, 100, 0]:
                    Fish(self, (x*24, 240+(240-(y*24))))
                if color == [0, 0, 50]:
                    Frog(self, (x*24, y*24))
                if color == [255, 0, 0]:
                    Fruit(self, (x*24 + 12, y*24 + 12), "cherry")
                if color == [200, 0, 0]:
                    Fruit(self, (x*24 + 12, y*24 + 12), "pineapple")
                if color == [255, 200, 0]:
                    self.game.checkpoint = Checkpoint((x*24, y*24))
        self.tiles = tiles
        self.game.oldguy = OldGuy(self, (-48, 0))

    def get_at(self, x, y):
        try:
            return list(self.image.get_at((x, y)))[:-1]
        except:
            return [0, 0, 0]
