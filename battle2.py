import math
import pygame as pg
from pygame.math import Vector2
pg.init()
backdrop = (240,250,230)
cam_x = 0
cam_y = 0
zoom = 2
screen_width = 600
screen_height = 400
zoom_radius = 300
grid_spacing = 100
boundary_size = 1000
screen = pg.display.set_mode((screen_width,screen_height))
bullets = []
players = []
# Teams = (Name, Deaths, Kills, Players)
teams = [['Bannanas',0,0,[0]],['Apples',0,0,[1,2]]]

#up,right,down,left,fire,aim1,aim2
controls = ((pg.K_w,pg.K_d,pg.K_s,pg.K_a,pg.K_SPACE,pg.K_c,pg.K_v),(pg.K_UP,pg.K_RIGHT,pg.K_DOWN,pg.K_LEFT,pg.K_COMMA,pg.K_n,pg.K_m),(pg.K_i,pg.K_l,pg.K_k,pg.K_j,pg.K_LEFTBRACKET,pg.K_o,pg.K_p))

def closest_player(pos,not_included = 0,is_max = False):
    distances = []
    for i in players:
        if i.team == not_included:
            distances.append(10000000)
        else:
            distances.append(math.dist([i.x,i.y],pos))
    if is_max:
        return players[distances.index(max(distances))]
    else:
        return players[distances.index(min(distances))]



def draw_bullets():
    for i in bullets:
        i.draw()


def draw_grid():
    for i in range(math.ceil((screen_width)/grid_spacing)):
        x = (grid_spacing-((cam_x/zoom) % grid_spacing))+(i*grid_spacing)
        pg.draw.line(screen,[i * 0.4 for i in backdrop],[x,0],[x,screen_height],5)
    for i in range(math.ceil((screen_height)/grid_spacing)):
        y = ((cam_y/zoom) % grid_spacing)+(i*grid_spacing)
        pg.draw.line(screen,[i * 0.4 for i in backdrop],[0,y],[screen_width,y],5)


def collide_bullets():
    for b in bullets:
        for p in players:
            if not b.came_from.team == p.team:
                if math.dist([b.x,b.y],[p.x,p.y]) < (p.type.size+b.bullet_type.size):
                    p.health -= b.bullet_type.damage
                    del bullets[bullets.index(b)]
                    

def bullet_despawn():
    for i in bullets:
        if i.time_left <= 0:
            del bullets[bullets.index(i)]


def player_respawn():
    for i in players:
        i.respawn()


def adjust_camera():
    global cam_x
    global cam_y
    global zoom
    x = []
    for i in players:
        x.append(i.x)
    cam_x += ((min(x)+max(x))/2-cam_x)*0.05
    y = []
    for i in players:
        y.append(i.y)
    cam_y += ((min(y)+max(y))/2-cam_y)*0.05
    farthest_player = closest_player((cam_x,cam_y),0,True)
    most_dist = math.dist((farthest_player.x,farthest_player.y),(cam_x,cam_y))
    zoom += ((((math.ceil(most_dist/zoom_radius)*zoom_radius)/screen_height)*2)-zoom)*0.05
    


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
    pg.draw.circle(screen,color,[(pos[0]-cam_x)/zoom+(screen_width/2),screen_height-((pos[1]-cam_y)/zoom+(screen_height/2))],round(size/zoom))


def draw_line(pos1,pos2,size,color):
    pg.draw.line(screen,color,[(pos1[0]-cam_x)/zoom+(screen_width/2),screen_height-((pos1[1]-cam_y)/zoom+(screen_height/2))],[(pos2[0]-cam_x)/zoom+(screen_width/2),screen_height-((pos2[1]-cam_y)/zoom+(screen_height/2))],round(size/zoom))


class BulletGroup:
    def __init__(self,damage,amount,spread,speed,size,color,homing,life_span) -> None:
        self.damage = damage
        self.amount = amount
        self.spread = spread
        self.speed = speed
        self.size = size
        self.color = color
        self.homing = homing
        self.life_span = life_span


class Bullet:
    def __init__(self,x,y,dir,bullet_type,came_from) -> None:
        self.x = x
        self.y = y
        self.vel = Vector2()
        self.vel.from_polar((bullet_type.speed,dir))
        self.bullet_type = bullet_type
        if not self.bullet_type.speed == 0:
            self.vel += came_from.vel*0.5
        self.came_from = came_from
        self.time_left = bullet_type.life_span
    def move(self) -> None:
        self.x += self.vel.x
        self.y += self.vel.y
        self.time_left -= 1
        if not self.bullet_type.homing == 0:
            if not len(players) == 1:
                max_turn = self.bullet_type.homing
                toward = closest_player([self.x,self.y],self.came_from.team)

                between = Vector2((toward.x-self.x),(toward.y-self.y))
                between.scale_to_length(self.bullet_type.homing)
                new = self.vel + between
                new.scale_to_length(self.vel.length())
                self.vel = new
    def draw(self) -> None:
        draw_circle([self.x,self.y],self.bullet_type.size,self.bullet_type.color)

 



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
                for i in range(self.type.fires.amount):
                    bullets.append(Bullet(self.x+self.barrel.x,self.y+self.barrel.y,(Vector2(0,0).angle_to(self.barrel))+((i-(self.type.fires.amount/2)+0.5)*self.type.fires.spread),self.type.fires,self))
        if key_down(controls[self.movement][5]):
            self.barrel.rotate_ip(5)
        if key_down(controls[self.movement][6]):
            self.barrel.rotate_ip(-5)
        self.x += self.vel.x
        self.y += self.vel.y
        if math.dist((0,0),(self.x,self.y)) > boundary_size-self.type.size:
            new = Vector2(self.x,self.y)
            new.scale_to_length(boundary_size-self.type.size)
            self.x = new.x
            self.y = new.y
        self.vel.x *= self.type.drift
        self.vel.y *= self.type.drift
        if self.timer != 0:
            self.timer -= 1
    def draw(self) -> None:
        draw_circle([self.x,self.y],self.type.size,[i * (self.health/self.type.max_health) for i in self.type.color])
        draw_line([self.x,self.y],[self.x+self.barrel.x,self.y+self.barrel.y],self.type.size//3,[i * (self.health/self.type.max_health) for i in self.type.color])
        draw_circle([self.x+self.barrel.x,self.y+self.barrel.y],self.type.size//6,[i * (self.health/self.type.max_health) for i in self.type.color])
    def respawn(self) -> None:
        if self.health  <= 0:
            self.x = cam_x
            self.y = cam_y
            self.health = self.type.max_health
            




#Bullet Types
normal_bullet = BulletGroup(10,1,0,10,12,(40,200,40),0.4,240)
large_bullet = BulletGroup(30,1,0,8,12,(40,60,100),0.1,300)
homing_bullet = BulletGroup(3,1,0,20,10,(20,120,100),0.7,100)
bullet_spread = BulletGroup(4,10,4,10,8,(150,150,150),0,180)
mine = BulletGroup(100,1,0,0,100,(240,50,50),0,1000)

#Player Characters
shotgun = Group(30,60,6,0.4,50,(240,240,40),bullet_spread)
average_char = Group(25,50,3,0.7,30,(200,30,30),normal_bullet)
tank = Group(35,100,4,0.7,80,(60,20,200),large_bullet)
destroyer = Group(20,10,3,0.8,6,(60,255,30),homing_bullet)
mine_layer = Group(40,110,2,0.6,100,(255,128,20),mine)


players.append(Player(tank,'Bannanas',0,0,0))
#players.append(Player(tank,'Apples',0,50,1))
players.append(Player(average_char,'Apples',50,50,1))


fps = 60
fps_clock = pg.time.Clock()
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False


    move_players()
    screen.fill((0,0,0))
    draw_circle((0,0),boundary_size,backdrop)
    #draw_grid()
    adjust_camera()
    draw_bullets()
    draw_players()
    move_bullets()
    bullet_despawn()
    collide_bullets()
    player_respawn()
    pg.display.update()
    fps_clock.tick(fps)
pg.quit()