import math
import pygame as pg
from pygame.math import Vector2


pg.init()
cam_x = 0
cam_y = 0
screen_width = 600
screen_height = 400
screen = pg.display.set_mode((screen_width,screen_height))
bullets = []
players = []

#up,right,down,left,fire,aim1,aim2
controls = ((pg.K_w,pg.K_d,pg.K_s,pg.K_a,pg.K_SPACE,pg.K_c,pg.K_v),(pg.K_UP,pg.K_RIGHT,pg.K_DOWN,pg.K_LEFT,pg.K_COMMA,pg.K_n,pg.K_m))

def closest_player(pos,not_included = 0):
    distances = []
    for i in players:
        if i == not_included:
            distances.append(10000000)
        else:
            distances.append(math.dist([i.x,i.y],pos))
    return players[distances.index(min(distances))]



def draw_bullets():
    for i in bullets:
        i.draw()


def move_bullets():
    for i in bullets:
        i.move()


def draw_players():
    for i in players:
        i.draw()


def move_players():
    for i in players:
        i.move()


def key_down(key):
    return pg.key.get_pressed()[key]


def draw_circle(pos,size,color):
    pg.draw.circle(screen,color,[pos[0]+(screen_width/2),screen_height-(pos[1]+(screen_height/2))],size)


def draw_line(pos1,pos2,size,color):
    pg.draw.line(screen,color,[pos1[0]+(screen_width/2),screen_height-(pos1[1]+(screen_height/2))],[pos2[0]+(screen_width/2),screen_height-(pos2[1]+(screen_height/2))],size)


class BulletGroup:
    def __init__(self,damage,amount,spread,speed,size,color,homing) -> None:
        self.damage = damage
        self.amount = amount
        self.spread = spread
        self.speed = speed
        self.size = size
        self.color = color
        self.homing = homing


class Bullet:
    def __init__(self,x,y,dir,bullet_type,came_from) -> None:
        self.x = x
        self.y = y
        self.vel = Vector2()
        self.vel.from_polar((bullet_type.speed,dir))
        self.bullet_type = bullet_type
        self.came_from = came_from
    def move(self) -> None:
        self.x += self.vel.x
        self.y += self.vel.y
        if not self.bullet_type.homing == 0:
            if not len(players) == 1:
                max_turn = self.bullet_type.homing
                closest = closest_player([self.x,self.y],self.came_from)
                want_dir = Vector2(self.x,self.y).angle_to(Vector2(closest.x,closest.y))
                current_dir = Vector2(0,0).angle_to(self.vel)
                if want_dir >= current_dir+180:
                    current_dir += 360
                elif want_dir < current_dir-180:
                    want_dir += 360  
                dir_diff = want_dir - current_dir
                if dir_diff < -max_turn:
                    dir_diff = -max_turn
                if dir_diff > max_turn:
                    dir_diff = max_turn
                self.vel.rotate_ip(dir_diff)
    def draw(self) -> None:
        draw_circle([self.x-cam_x,self.y-cam_y],self.bullet_type.size,self.bullet_type.color)
 



class Group:
    def __init__(self,size,max_health,move_speed,drift,reload_time,color,bullet_type) -> None:
        self.size = size
        self.max_health = max_health
        self.move_speed = move_speed
        self.drift = drift
        self.reload_time = reload_time
        self.color = color
        self.fires = bullet_type
        


class Player:
    def __str__(self) -> str:
        return f'{self.x,self.y} pos, {self.vel} vel, {players.index(self)+1} number'
    def __init__(self,group,team,x,y,control_scheme) -> None:
        self.team = team
        self.type = group
        self.x = x
        self.y = y
        self.health = group.max_health
        self.movement = control_scheme
        self.vel = Vector2(0,0)
        self.barrel = Vector2()
        self.barrel.from_polar((self.type.size*2,0))
        self.timer = 0
    def move(self) -> None:
        if key_down(controls[self.movement][0]):
            self.vel.y += self.type.move_speed
        if key_down(controls[self.movement][1]):
            self.vel.x += self.type.move_speed
        if key_down(controls[self.movement][2]):
            self.vel.y -= self.type.move_speed
        if key_down(controls[self.movement][3]):
            self.vel.x -= self.type.move_speed
        if key_down(controls[self.movement][4]):
            if self.timer == 0:
                self.timer = self.type.reload_time
                bullets.append(Bullet(self.x-cam_x+self.barrel.x,self.y-cam_y+self.barrel.y,Vector2(0,0).angle_to(self.barrel),self.type.fires,self))
        if key_down(controls[self.movement][5]):
            self.barrel.rotate_ip(5)
        if key_down(controls[self.movement][6]):
            self.barrel.rotate_ip(-5)
        self.x += self.vel.x
        self.y += self.vel.y
        self.vel.x *= self.type.drift
        self.vel.y *= self.type.drift
        if self.timer != 0:
            self.timer -= 1
    def draw(self) -> None:
        draw_circle([self.x-cam_x,self.y-cam_y],self.type.size,self.type.color)
        draw_line([self.x-cam_x,self.y-cam_y],[self.x-cam_x+self.barrel.x,self.y-cam_y+self.barrel.y],self.type.size//3,self.type.color)
        draw_circle([self.x-cam_x+self.barrel.x,self.y-cam_y+self.barrel.y],self.type.size//6,self.type.color)




#Bullet Types
normal_bullet = BulletGroup(10,1,0,10,6,(40,200,40),20)
large_bullet = BulletGroup(20,0,0,8,12,(40,60,100),0)

#Player Characters
average_char = Group(25,50,3,0.7,10,(200,30,30),normal_bullet)
tank = Group(35,100,2,0.6,80,(60,20,200),large_bullet)


players.append(Player(average_char,1,0,0,0))
players.append(Player(tank,2,0,50,1))


fps = 60
fps_clock = pg.time.Clock()
running = True
while running:
    print(Vector2(300,200).angle_to(Vector2(pg.mouse.get_pos())))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False


    move_players()
    screen.fill((0,0,0))
    draw_players()
    draw_bullets()
    move_bullets()
    pg.draw.circle(screen,(255,255,255),(300,200),30)
    pg.draw.circle(screen,(255,255,255),pg.mouse.get_pos(),30)
    pg.display.update()
    fps_clock.tick(fps)
pg.quit()