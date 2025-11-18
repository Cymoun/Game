import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join


pygame.init()

# Music n shi
pygame.mixer.init()
pygame.mixer.music.load("Documents\\GitHub\\Game\\Music\\Deltarune - Glacier.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loop 
# also, if ("Music\[song name]") doesn't work, try using double backslash, 
# because if you only use 1, it sometimes doesn't get decoded
# do it like this instead ("Music\\[song name]")

pygame.display.set_caption("Platformer")

swidth, sheight = 800, 600
FPS = 60
player_v = 5

window = pygame.display.set_mode((swidth, sheight))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

# Loading the sprite sheets
def load_sprite_sheets(dir1, width, height, direction=False):
    path = join("Documents", "GitHub", "Game", "MainCharacters", dir1)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("Documents", "GitHub", "Game", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


# for the player
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("NinjaFrog", 32, 32, True)
    ANIM_DELAY = 3

# for the movement (I think it is)
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.count = 0  


    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

# to determine the direction were facing, like if left then the animation goes left or sum shi like that
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

# called once every frame, moves the chr in the right direction, handles the animation and updates it type shi
    def loop(self, fps):
        self.y_vel += min(1 , (self.fall_count /  fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0 
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= 1
    
    
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIM_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update() 

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

# for the objects of the game
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)




# to get the background image by tiles instead of just one giant image, oh and also switchable bg or so they say it is
def get_background(name):
    image = pygame.image.load(join("Documents", "GitHub", "Game", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(swidth // width + 1):
        for j in range(sheight // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()



def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            
            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

# for the movement itself (key pressing detection)
def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -player_v * 2)
    collide_right = collide(player, objects, player_v * 2)


    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(player_v)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(player_v)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    

def main(window):
    clock =  pygame.time.Clock()
    background, bg_image = get_background('Brown.png')

    block_size = 96

    player = Player(100, 100, 50, 50)
    floor = [Block(i * block_size, sheight - block_size, block_size) 
             for i in range(-swidth // block_size, (swidth * 2) // block_size)]
    objects = [*floor, Block(0, sheight - block_size * 2, block_size),
               Block(block_size * 3, sheight - block_size * 3, block_size),
               Block(block_size * 6, sheight - block_size * 3, block_size),
               Block(block_size * 4, sheight - block_size * 3, block_size),
               Block(block_size * 5, sheight - block_size * 3, block_size),
               Block(block_size * 6, sheight - block_size * 2, block_size),
               Block(block_size * 6, sheight - block_size * 5, block_size),
               Block(block_size * 5, sheight - block_size * 5, block_size),
               Block(block_size * 4, sheight - block_size * 5, block_size),
               Block(block_size * 3, sheight - block_size * 5, block_size),
               Block(block_size * 2, sheight - block_size * 5, block_size),]
    
    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)     

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()


        player.loop(FPS)
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= swidth - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel



    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)