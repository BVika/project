import pygame
from pygame.locals import *
import random
pygame.init()
clock = pygame.time.Clock()
#частота кадра
fps = 60

screen_width = 864
screen_height = 750

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('FLAPPY GHOST')

#определим шрифт
font = pygame.font.SysFont('Bauhaus 93', 60)
#цвет шрифта
white = (255, 255, 255)

#игровые переменные
ground_scroll = 0
scroll_speed = 4
#полет
flying = False
game_over = False
#зазор между трубами
pipe_gap= 150
#частота труб
pip_frequency = 1500 #миллисекунды
#последняя труба
last_pip = pygame.time.get_ticks() - pip_frequency
#для счетчика
score = 0
pass_pipe = False

#изображение фона
bg = pygame.image.load('img/bg.jpeg')
#земля
ground_img = pygame.image.load('img/ground.png')
#кнопка рестарт
button_img = pygame.image.load('img/restart.png')

#для вывода очков на экран
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#для сброса переменных в случае конца игры

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height/2)
    score=0
    return score

#птица

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images=[]
        self.index = 0
        #счетчик
        self.counter =0
        for num in range (1, 4):

            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect =self.image.get_rect()
        self.rect.center = [x, y]
        #скорость птицы
        self.vel = 0
        self.clicked = False
    # гравитация
    def update(self):
        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 600:
                self.rect.y += int(self.vel)
        if game_over ==False:
            #прыжки
            # мышь нажата
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked =True
                self.vel = -10
            # мышь отпущена
            if pygame.mouse.get_pressed()[0] == 0 :
                self.clicked = False

            #анимация
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index +=1
                #чтобы индекс не выходил за рамки имеющихся кадров
                if self.index >= len(self.images):
                    self.index = 0

            self.image = self.images[self.index]

            #поворот птицы
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

#трубы
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        #позиция 1 труба свеху, -1 снизу
        if position == 1:
            self.image = pygame.transform.flip(self. image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap/2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap/2)]

    #чтобы трубы двигались
    def update(self):
        self.rect.x -= scroll_speed
        #чтобы удалить трубы которые уходят за кадр
        if self.rect.right < 0:
            self.kill()

#кнопка рестарт
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action =False

        #положение мыши
        pos = pygame.mouse.get_pos()
        #нажала ли мышь на кнопку
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #изображение кнопки
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action




bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy =Bird(100, int(screen_height/2))

bird_group.add(flappy)

#создание кнопки перезапуска
button = Button(screen_width//2 - 50, screen_height//2 - 100, button_img)


#окно
run =True
while run:
    clock.tick((fps))

    #для отображения изображения
    screen.blit(bg, (0, 0))
    #изображение птицы
    bird_group.draw(screen)
    bird_group.update()
    #изображение труб
    pipe_group.draw(screen)
    #прокрутка земли
    screen.blit(ground_img, (ground_scroll, 600))

    #проверка прошел ли игрок трубу
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
            and  bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score = score + 1
                pass_pipe = False


    draw_text(str(score), font, white, int(screen_width/2), 20)




            #поиск столкновений птицы с трубами
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    #прверка не ударилась ли птица о землю
    if flappy.rect.bottom >= 600:
        game_over = True
        flying = False

    if game_over == False and flying == True:
        #дополнительные трубы
        time_now = pygame.time.get_ticks()
        if time_now - last_pip > pip_frequency:
            pip_height = random.randint(-100, 100)
            # экземпляр нижней трубы
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pip_height, -1)
            # экземпляр вверхней трубы
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pip_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pip = time_now


        #для перемещения пространства
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0
        #обновление труб
        pipe_group.update()

    #проверка закончина ли игра
    if game_over == True:
        if button.draw() == True:
            game_over =False
            score = reset_game()

    #чтобы окно не исчезала пока пользовател сам не захочет выйти
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #чтобы игра началась с щелчка мыши
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

pygame.quit()