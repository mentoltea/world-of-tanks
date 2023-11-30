import pygame
from random import randint as rnd
import random
import math
import webbrowser

#import keyboard




#read settings
try:
    line = ''
    with open('settings.txt') as f:
        for i in f:
            line += i
        f.close()

        step = 0
        RES_FORM = [0,0]
        line2 = ''
        for i in line: #
            if i == '\n' or i == '$':
                if step == 0:
                    fullscreen = int(line2)
                elif step == 1:
                    FPS = int(line2)
                elif step == 2:
                    TICK = int(line2)
                elif step == 3:
                    RES_FORM[0] = int(line2)
                elif step == 4:
                    RES_FORM[1] = int(line2)
                elif step == 5:
                    WIN_X = int(line2)
                elif step == 6:
                    WIN_Y = int(line2)
    
                step += 1
                line2 = ''
            else:
                line2 += i
        print('настройки загружены')
    
    
except:
    print('ошибка загрузки настроек. настройки сброшены.')
    fullscreen = 0
    FPS = 60
    TICK = 60
    RES_FORM = (284,160)
    WIN_X = 1136
    WIN_Y = 640
    
FPS_COUNTER = 0
TICK_COUNTER = 0
#FPS всегда <= TICK



#K_xy = 16/9

pygame.init()
pygame.mixer.init()

if fullscreen:
    flags = pygame.FULLSCREEN
    wn = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0], flags, vsync=1)
    RES_CURRENT = pygame.display.get_desktop_sizes()[0]
else:
    wn = pygame.display.set_mode((WIN_X,WIN_Y), vsync=1)
    RES_CURRENT = (WIN_X, WIN_Y)

K_X_MOUSE = RES_FORM[0]/RES_CURRENT[0]
K_Y_MOUSE = RES_FORM[1]/RES_CURRENT[1]

pygame.display.set_caption("World Of Tanks 2")

clock = pygame.time.Clock()

window = pygame.Surface((RES_FORM[0], RES_FORM[1]))

class background_class():
    def __init__(self, layers_count):
        self.layers = []
        for i in range(0, layers_count):
            self.layers.append(pygame.Surface((RES_FORM[0], RES_FORM[1])))
        #layer0 walls
        #layer1 tanks
        #layer2 support layer
        #layer3 tanks2
        #(0,0,0) - clear color
    def clear(self, layer=None):
        if layer == None:
            for i in self.layers:
                i.fill((0,0,0))
        else:
            self.layers[layer].fill((0,0,0))
    def get_surf(self, layer):
        return self.layers[layer]
    def set_surf(self, layer, Surf):
        self.layers[layer] = Surf
    def add_surf(self, layer, Surf, x=0, y=0):
        self.layers[layer].blit(Surf, (x,y))

background = background_class(4)


def get_flip_x(Surf):
    return pygame.transform.flip(Surf, True, False)

def get_trans(Surf, size, angle, topleft):
    def r(image, angle, topleft):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

        return rotated_image, new_rect.topleft
    def trans(Surf, w, h):
        return pygame.transform.scale(Surf, (w,h))
    return r(trans(Surf, size[0], size[1]), angle, topleft)

def get_trans_old(Surf, width, height, angle):
    return pygame.transform.rotate(pygame.transform.scale(Surf, (int(round(width)), int(round(height)))), int(round(angle)))

def back_update():
    background.clear()
    for i in back_objects_to_draw:
        temp = get_trans(i[0], i[1], i[2], i[3])
        background.add_surf(0, temp[0], temp[1][0], temp[1][1])
        background.add_surf(3, temp[0], temp[1][0], temp[1][1])
    back_objects_to_draw.clear()

    for i in solid_back_draw:
        pygame.draw.rect(background.get_surf(2), (255,i[0],i[0]), (i[1],i[2], i[3][0], i[3][1]))
    solid_back_draw.clear()
    
    for i in players:
        i.draw_back()
        
    for i in back_tanks_to_draw:
        temp = get_trans(i[0], i[1], i[2], i[3])
        background.add_surf(1, temp[0], temp[1][0], temp[1][1])
        background.add_surf(3, temp[0], temp[1][0], temp[1][1])
    back_tanks_to_draw.clear()
        


def act():
    global message_printed
    for i in objects:
        i.draw_back()
    back_update()
    alive = [1,1,1,1]
    count = 4
    for i in players:
        if not i.is_alive:
            alive[players.index(i)]=0
            count -=1
        i.act()
    if count <=1 and not message_printed:
        print('Победитель - Игрок №{}. Нажмите R, чтобы перезапустить.'.format(alive.index(1)))
        message_printed = abs(message_printed-1)
    for i in projects:
        i.act()
    
def window_update():
    wn.fill((0,0,0))
    window.fill((255,255,255))

    window.blit(bg, (0,0))

    for i in players:
        i.draw()
    for i in objects:
        i.draw()
    
    for i in objects_to_draw:
        temp = get_trans(i[0], i[1], i[2], i[3])
        window.blit(temp[0], temp[1])
    for i in projects:
        i.draw(window)
    objects_to_draw.clear()

    #pygame.draw.rect(window, (255,0,0), (50,50, 4, 2))
    if back_show>=0:
        window.blit(background.get_surf(back_show), (0,0))
    
    wn.blit(get_trans_old(window, RES_CURRENT[0], RES_CURRENT[1], 0), (0,0))


def save_settings():
    with open('settings.txt', 'w') as f:
        #print(str(fullscreen)+'\n'+str(FPS)+'\n'+str(TICK)+'\n'+str(RES_FORM[0])+'\n'+str(RES_FORM[1])+'\n'+str(WIN_X)+'\n'+str(WIN_Y)+'\n$')
        f.write(str(fullscreen)+'\n'+str(FPS)+'\n'+str(TICK)+'\n'+str(RES_FORM[0])+'\n'+str(RES_FORM[1])+'\n'+str(WIN_X)+'\n'+str(WIN_Y)+'\n$')
        f.close()

def level_restart():
    global objects, projects, players, message_printed
    message_printed = 0
    objects = []
    projects = []
    players = [ player(0, 20, 20, TANK_SPEED, 0, TANK_ROT_SPEED, 1, pygame.image.load('assets/models/t1.png'), pygame.image.load('assets/back_models/t1.png')),
                player(1, 220, 20, TANK_SPEED, 0, TANK_ROT_SPEED, -1, pygame.image.load('assets/models/t2.png'), pygame.image.load('assets/back_models/t2.png')),
                player(2, 20, 120, TANK_SPEED, 0, TANK_ROT_SPEED, 1, pygame.image.load('assets/models/t3.png'), pygame.image.load('assets/back_models/t3.png')),
                player(3, 220, 120, TANK_SPEED, 0, TANK_ROT_SPEED, -1, pygame.image.load('assets/models/t4.png'), pygame.image.load('assets/back_models/t4.png'))]
    
    for i in range(12):
        objects.append( random.choice([solid_object(i, rnd(10,230), rnd(30,90), 'hush', rnd(-359,359), hush_model[0], hush_model[1], True),
                        solid_object(i, rnd(10,230), rnd(30,90), 'stone', rnd(-359,359), stone_model[0], stone_model[1], False),
                        solid_object(i, rnd(10,230), rnd(30,90), 'stone', rnd(-359,359), stone_model2[0], stone_model2[1], False) ]))
    for i in range(10):
        objects.append( random.choice([solid_object(i+12, rnd(70,150), rnd(10,150), 'hush', rnd(-359,359), hush_model[0], hush_model[1], True),
                        solid_object(i+12, rnd(70,150), rnd(10,150), 'stone', rnd(-359,359), stone_model[0], stone_model[1], False),
                        solid_object(i+12, rnd(70,150), rnd(10,150), 'stone', rnd(-359,359), stone_model2[0], stone_model2[1], False) ]))

class player():
    def __init__(self, idn, x, y, speed, angle, rotation_speed, rot_dir, model, back_model):
        self.idn = idn
        if self.idn == 0:
            self.col = (255,0,0)
        elif self.idn == 1:
            self.col = (0,0,255)
        elif self.idn == 2:
            self.col = (255,255,0)
        elif self.idn == 3:
            self.col = (0,255,0)
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.rot_speed = rotation_speed
        self.rot_dir = rot_dir # -1/1
        self.button = 0
        self.prev_button = 0
        self.is_alive = True
        self.model = model
        self.back_model = back_model

    def act(self):
        if self.is_alive:
            root2 = math.sqrt(2)
            LX = 8 * 2
            LY = 8 * 2
            t0x = self.x + 8 + LX/2*root2*math.cos((self.angle+45)/180*math.pi)
            t0y = self.y + 8 - LX/2*root2*math.sin((self.angle+45)/180*math.pi)

            a = self.angle+180
            
            t1x = t0x - LX*math.sin(a/180*math.pi)
            t1y = t0y - LX*math.cos(a/180*math.pi)

            tgx = (t1x+t0x)/2
            tgy = (t1y+t0y)/2

            t2x = t1x + LY*math.sin((90-a)/180*math.pi)
            t2y = t1y - LY*math.cos((90-a)/180*math.pi)

            t3x = t0x + LY*math.sin((90-a)/180*math.pi)
            t3y = t0y - LY*math.cos((90-a)/180*math.pi)

            tl = (min(max(int(t0x), 0), RES_FORM[0]-1), min(max(int(t0y), 0), RES_FORM[1]-1))
            tr = (min(max(int(t1x), 0), RES_FORM[0]-1), min(max(int(t1y), 0), RES_FORM[1]-1))
            gun = (min(max(int(tgx), 0), RES_FORM[0]-1), min(max(int(tgy), 0), RES_FORM[1]-1))

            
            pygame.draw.polygon(background.get_surf(3), (255,0,0), [(t0x,t0y), (t1x,t1y),
                                                    (t2x,t2y), (t3x,t3y)], 1)
            pygame.draw.circle(background.get_surf(3), (255,255,255), (t0x,t0y), 2)
            pygame.draw.circle(background.get_surf(3), (255,0,255), (t1x,t1y), 2)
            pygame.draw.circle(background.get_surf(3), (0,255,255), (tgx,tgy), 2)
            
            pygame.draw.circle(background.get_surf(3), (0,0,255), (t2x,t2y), 2)
            pygame.draw.circle(background.get_surf(3), (0,255,0), (t3x,t3y), 2)

            if self.button == 1 and self.prev_button == 0:
                self.shoot()
                self.rot_dir *= -1

            elif self.button == 1:
                next_x = self.x + self.speed * math.cos(self.angle/180*math.pi)
                next_y = self.y - self.speed * math.sin(self.angle/180*math.pi)

            
                if background.get_surf(1).get_at(tl) == (0,0,0) and background.get_surf(1).get_at(tr) == (0,0,0) and (background.get_surf(1).get_at(gun) == (0,0,0) or background.get_surf(1).get_at(gun)==self.col):
                    if background.get_surf(0).get_at(tl) == (0,0,0) and background.get_surf(0).get_at(tr) == (0,0,0) and (background.get_surf(0).get_at(gun) == (0,0,0) or background.get_surf(1).get_at(gun)==self.col):
                        if next_x >= 0 and next_x+16 <= RES_FORM[0]:
                            self.x = next_x

                        if next_y >= 0 and next_y+16 <= RES_FORM[1]:
                            self.y = next_y
                else:
                    col = background.get_surf(1).get_at(gun)
                    if col == (0,0,0):
                        col = background.get_surf(1).get_at(tl)
                        if col == (0,0,0):
                            col = background.get_surf(1).get_at(tr)
                    if col == (255,0,0):
                        idn = 0
                    if col == (0,0,255):
                        idn = 1
                    if col == (255,255,0):
                        idn = 2
                    if col == (0,255,0):
                        idn = 3

                    if idn != self.idn:
                        next_x = self.x + self.speed * math.cos(self.angle/180*math.pi) /4
                        next_y = self.y - self.speed * math.sin(self.angle/180*math.pi) /4
                        if next_x >= 0 and next_x+16 <= RES_FORM[0]:
                            self.x = next_x
                            players[idn].x += self.speed * math.cos(self.angle/180*math.pi) /3

                        if next_y >= 0 and next_y+16 <= RES_FORM[1]:
                            self.y = next_y
                            players[idn].y -= self.speed * math.sin(self.angle/180*math.pi) /3
                    
                    
                    
                    

                
            else:
                self.angle += self.rot_speed * self.rot_dir
                if self.angle >=360:
                    self.angle -= 360
                elif self.angle <= -360:
                    self.angle += 360
            self.prev_button = self.button
    def shoot(self):
        projects.append( projectile(len(projects), self.x+8+10*math.cos(self.angle/180*math.pi), self.y+8-10*math.sin(self.angle/180*math.pi), 2, self.angle) )

    def draw(self):
        objects_to_draw.append( (self.model, self.model.get_size(), self.angle, (self.x,self.y)) )
        
    def draw_back(self):
        back_tanks_to_draw.append( (self.back_model, self.back_model.get_size(), self.angle, (self.x,self.y)) ) 

class solid_object():
    def __init__(self, idn, x, y, typ, angle, model, back_model, destructable):
        self.typ = typ
        self.idn = idn
        self.x = x
        self.y = y
        self.angle = angle
        self.model = model
        self.back_model = back_model
        self.destr = destructable
    def delete(self):
        objects.remove(self)
    def draw(self):
        objects_to_draw.append( (self.model, self.model.get_size(), self.angle, (self.x,self.y)) )

    def draw_back(self):
        back_objects_to_draw.append( (self.back_model, self.back_model.get_size(), self.angle, (self.x,self.y)) )
        if self.typ == 'hush':
            solid_back_draw.append( (self.idn, self.x, self.y, self.model.get_size()) )

class projectile():
    def __init__(self, idn, x, y, speed, angle):
        self.idn = idn
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        # 4 / 2
    def draw(self, surf):
        
        t1x = self.x + 4*math.cos(self.angle/180*math.pi)
        t1y = self.y - 4*math.sin(self.angle/180*math.pi)

        t2x = t1x - 2*math.sin(self.angle/180*math.pi)
        t2y = t1y - 2*math.cos(self.angle/180*math.pi)

        t3x = self.x - 2*math.sin(self.angle/180*math.pi)
        t3y = self.y - 2*math.cos(self.angle/180*math.pi)
        
        pygame.draw.polygon(window, (0,0,0), [(self.x, self.y),
                                              (t1x, t1y),
                                              (t2x, t2y),
                                              (t3x, t3y)])
    def act(self):
        self.x += self.speed * math.cos(self.angle/180*math.pi)
        self.y -= self.speed * math.sin(self.angle/180*math.pi)
        if self.x <0 or self.x > RES_FORM[0] or self.y < 0 or self.y > RES_FORM[1]:
            projects.remove(self)
        elif background.get_surf(1).get_at((int(min(max(self.x,0),RES_FORM[0]-1)),int(min(max(self.y,0),RES_FORM[1]-1))))!=(0,0,0):
            col = background.get_surf(1).get_at((int(min(max(self.x,0),RES_FORM[0]-1)),int(min(max(self.y,0),RES_FORM[1]-1))))
            if col == (255,0,0):
                players[0].is_alive = 0
                players[0].model = destroyed_model
            elif col == (0,255,0):
                players[3].is_alive = 0
                players[3].model = destroyed_model
            elif col == (0,0,255):
                players[1].is_alive = 0
                players[1].model = destroyed_model
            elif col == (255,255,0):
                players[2].is_alive = 0
                players[2].model = destroyed_model
            projects.remove(self)
        elif background.get_surf(0).get_at((int(self.x),int(self.y)))!=(0,0,0):
            col = background.get_surf(2).get_at((int(self.x),int(self.y)))
            idn = col[2]
            for i in objects:
                if i.idn==idn:
                    if i.destr == 1:
                        i.delete()
                    else:
                        break
            projects.remove(self)





run = 1
rerun = 0
back_show = -1

TANK_SPEED = 0.8
TANK_ROT_SPEED = 2.5


objects_to_draw = []
back_objects_to_draw = []
back_tanks_to_draw = []
solid_back_draw = []
objects = []
projects = []
players = [ player(0, 20, 20, TANK_SPEED, 0, TANK_ROT_SPEED, 1, pygame.image.load('assets/models/t1.png'), pygame.image.load('assets/back_models/t1.png')),
            player(1, 220, 20, TANK_SPEED, 0, TANK_ROT_SPEED, -1, pygame.image.load('assets/models/t2.png'), pygame.image.load('assets/back_models/t2.png')),
            player(2, 20, 120, TANK_SPEED, 0, TANK_ROT_SPEED, 1, pygame.image.load('assets/models/t3.png'), pygame.image.load('assets/back_models/t3.png')),
            player(3, 220, 120, TANK_SPEED, 0, TANK_ROT_SPEED, -1, pygame.image.load('assets/models/t4.png'), pygame.image.load('assets/back_models/t4.png'))]
message_printed = 0

destroyed_model = pygame.image.load('assets/models/d.png')
hush_model = (pygame.image.load('assets/models/h.png'), pygame.image.load('assets/back_models/h.png'))
stone_model = (pygame.image.load('assets/models/st.png'), pygame.image.load('assets/back_models/st.png'))
stone_model2 = (pygame.image.load('assets/models/st2.png'), pygame.image.load('assets/back_models/st2.png'))
bg, a = get_trans(get_trans_old(pygame.image.load('assets/bg.png'), RES_FORM[0], RES_FORM[1], 0), RES_FORM, 0, (0,0))
del a

for i in range(12):
    objects.append( random.choice([solid_object(i, rnd(10,230), rnd(30,90), 'hush', rnd(-359,359), hush_model[0], hush_model[1], True),
                    solid_object(i, rnd(10,230), rnd(30,90), 'stone', rnd(-359,359), stone_model[0], stone_model[1], False),
                    solid_object(i, rnd(10,230), rnd(30,90), 'stone', rnd(-359,359), stone_model2[0], stone_model2[1], False) ]))
for i in range(10):
    objects.append( random.choice([solid_object(i+12, rnd(70,150), rnd(10,150), 'hush', rnd(-359,359), hush_model[0], hush_model[1], True),
                    solid_object(i+12, rnd(70,150), rnd(10,150), 'stone', rnd(-359,359), stone_model[0], stone_model[1], False),
                    solid_object(i+12, rnd(70,150), rnd(10,150), 'stone', rnd(-359,359), stone_model2[0], stone_model2[1], False) ]))
"""for i in range(5):
    objects.append( random.choice([solid_object(i, rnd(30,200), rnd(30,100), rnd(-359,359), hush_model[0], hush_model[1], True),
                    solid_object(i, rnd(30,200), rnd(30,100), rnd(-359,359), stone_model[0], stone_model[1], False),
                    solid_object(i, rnd(30,200), rnd(30,100), rnd(-359,359), stone_model2[0], stone_model2[1], False) ]))"""
    
#self, idn, x, y, speed, angle, rotation_speed, rot_dir, model
#self, idn, x, y, typ, angle, model, back_model, destructable




# [0]Surf [1]size (w,h) [2]angle [3]topleft (x,y)

print("Игрок 1 - Left Shift\nИгрок 2 - Space\nИгрок 3 - Right Shift\nИгрок 4 - Enter\n")


while run:
    clock.tick(TICK)
    TICK_COUNTER += 1
    FPS_COUNTER += 1
    if TICK_COUNTER >= TICK:
        TICK_COUNTER = 0
    if FPS_COUNTER >= FPS*10:
        FPS_COUNTER = 0

    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_0] and TICK_COUNTER%4==0:
        back_show = -1
    if keys[pygame.K_1] and TICK_COUNTER%4==0:
        back_show = 0
    if keys[pygame.K_2] and TICK_COUNTER%4==0:
        back_show = 1
    if keys[pygame.K_3] and TICK_COUNTER%4==0:
        back_show = 2
    if keys[pygame.K_4] and TICK_COUNTER%4==0:
        back_show = 3
    
    if keys[pygame.K_r] and TICK_COUNTER%4==0:
        level_restart()
    
    if keys[pygame.K_LSHIFT]:
        players[0].button = 1
    else:
        players[0].button = 0

    if keys[pygame.K_SPACE]:
        players[2].button = 1
    else:
        players[2].button = 0

    if keys[pygame.K_RSHIFT]:
        players[3].button = 1
    else:
        players[3].button = 0

    if keys[pygame.K_BACKSPACE]:
        players[1].button = 1
    else:
        players[1].button = 0

    

    
    act()
    if FPS_COUNTER%round(TICK/FPS)==0:
        window_update()
    
    pygame.display.update()
    
save_settings()
pygame.quit()
if rerun==1:
    webbrowser.open('main.py')
    quit()
