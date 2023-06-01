import os
import random
import pygame
# constants
W, H = 288, 512
FPS = 30
# Setup
pygame.init()
SCREEN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Flappy Bird--By 夏小雨")
CLOCK = pygame.time.Clock()
# bird = pygame.image.load('/Users/zhouwenmao/PycharmProjects/Flappy Bird/assets/sprites/red-mid.png')
# bgpic = pygame.image.load('/Users/zhouwenmao/PycharmProjects/Flappy Bird/assets/sprites/day.png')
# guide = pygame.image.load('/Users/zhouwenmao/PycharmProjects/Flappy Bird/assets/sprites/guide.png')
# floor = pygame.image.load('/Users/zhouwenmao/PycharmProjects/Flappy Bird/assets/sprites/floor.png')
# pipe = pygame.image.load('/Users/zhouwenmao/PycharmProjects/Flappy Bird/assets/sprites/red-pipe.png')
# gameover = pygame.image.load('/Users/zhouwenmao/PycharmProjects/Flappy Bird/assets/sprites/gameover.png')
IMAGE = {}
for image in os.listdir('../assets/sprites'):
    name, extension = os.path.splitext(image)
    path = os.path.join('../assets/sprites', image)
    IMAGE[name] = pygame.image.load(path)

start = pygame.mixer.Sound('../assets/audio/start.wav')
die = pygame.mixer.Sound('../assets/audio/die.wav')
hit = pygame.mixer.Sound('../assets/audio/hit.wav')
score = pygame.mixer.Sound('../assets/audio/score.wav')
flap_music = pygame.mixer.Sound('../assets/audio/flap.wav')
FLOOR_Y = H - IMAGE['floor'].get_height()


def main():
    while True:
        IMAGE['bgpic'] = IMAGE[random.choice(['day', 'night'])]
        color = random.choice(['red', 'yellow', 'blue'])
        IMAGE['birds'] = [IMAGE[color + '-up'], IMAGE[color + '-down'], IMAGE[color + '-mid']]
        pipe = IMAGE[random.choice(['red-pipe', 'green-pipe'])]
        IMAGE['pipes'] = [pipe, pygame.transform.flip(pipe, False, True)]  # 将管道倒置
        start.play()
        menu_window()
        result = game_window()
        end_window(result)


def menu_window():
    floor_gap = IMAGE['floor'].get_width() - W
    floor_x = 0
    guide_x = (W - IMAGE['guide'].get_width()) / 2
    guide_y = (H - IMAGE['floor'].get_height() - IMAGE['guide'].get_height()) / 2
    bird_x = (W - IMAGE['birds'][0].get_width()) / 2
    bird_y = (H - IMAGE['floor'].get_height() - IMAGE['birds'][0].get_height()) / 2
    birds_y_vel = 1  # 小鸟的上下移动速度
    bird_y_range = [bird_y - 8, bird_y + 8]
    idx = 0
    frames = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        floor_x -= 4
        if floor_x <= -floor_gap:
            floor_x = 0
        bird_y += birds_y_vel
        if bird_y < bird_y_range[0] or bird_y > bird_y_range[1]:
            birds_y_vel *= -1
        idx += 1
        idx %= len(frames)
        SCREEN.blit(IMAGE['bgpic'], (0, 0))
        SCREEN.blit(IMAGE['floor'], (floor_x, FLOOR_Y))
        SCREEN.blit(IMAGE['guide'], (guide_x, guide_y))
        SCREEN.blit(IMAGE['birds'][frames[idx]], (bird_x, bird_y))
        pygame.display.update()
        CLOCK.tick(FPS)  # 注意图层顺序，先写的先显示，后写的往上逐渐叠加
def game_window():
    flap_music.play()
    floor_gap = IMAGE['floor'].get_width() - W
    floor_x = 0
    bird = Bird(W*0.2,H*0.4)
    distance = 150
    pipes_gap = 130
    n_pairs = 4
    scores = 0
    pipe_group = pygame.sprite.Group()
    for i in range(n_pairs):
        pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
        pipe_up = Pipe(W + i * distance, pipe_y, True)
        pipes_down = Pipe(W + i * distance, pipe_y - pipes_gap, False)
        pipe_group.add(pipe_up)
        pipe_group.add(pipes_down)
    while True:
        flap = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    flap = True
                    flap_music.play()
        floor_x -= 4
        if floor_x <= - floor_gap:
            floor_x = 0
        bird.update(flap)
        first_pipe_up = pipe_group.sprites()[0]
        first_pipe_down = pipe_group.sprites()[1]
        if first_pipe_up.rect.right < 0:
            pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
            new_pipe_up = Pipe(first_pipe_up.rect.x + n_pairs * distance, pipe_y, True)
            new_pipe_down = Pipe(first_pipe_down.rect.x + n_pairs * distance, pipe_y - pipes_gap, False)
            pipe_group.add(new_pipe_up)
            pipe_group.add(new_pipe_down)
            first_pipe_up.kill()
            first_pipe_down.kill()
        pipe_group.update()
        if bird.rect.y > FLOOR_Y or bird.rect.y < 0 or pygame.sprite.spritecollideany(bird, pipe_group):
            bird.dying = True
            hit.play()
            die.play()
            result = {'bird': bird, 'pipe_group': pipe_group, 'score': scores}
            return result
        if bird.rect.left + first_pipe_up.x_vel < first_pipe_up.rect.centerx < bird.rect.left:
            score.play()
            scores += 1
        SCREEN.blit(IMAGE['bgpic'], (0, 0))
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGE['floor'], (floor_x, FLOOR_Y))
        show_score(scores)
        SCREEN.blit(bird.image, bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)


def end_window(result):
    gameover_y = (H - IMAGE['floor'].get_height() - IMAGE['gameover'].get_height()) / 2
    gameover_x = (W - IMAGE['gameover'].get_width()) / 2
    bird = result['bird']
    pipe_group = result['pipe_group']
    while True:
        if bird.dying:
            bird.go_die()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return
        SCREEN.blit(IMAGE['bgpic'], (0, 0))
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGE['floor'], (0, FLOOR_Y))
        SCREEN.blit(IMAGE['gameover'], (gameover_x, gameover_y))
        show_score(result['score'])
        SCREEN.blit(bird.image, bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)


def show_score(scores):
    scores_str = str(scores)
    n = len(scores_str)
    w = IMAGE['0'].get_width() * 1.1
    x = (W - n * w) / 2
    y = H * 0.1
    for number in scores_str:
        SCREEN.blit(IMAGE[number], (x, y))
        x += w


class Bird:
    def __init__(self, x, y):
        self.frames = [0] * 5 + [1] * 5 + [2] * 5 + [1] * 5
        self.idx = 0
        self.images = IMAGE['birds']
        self.image = self.images[self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_vel = -10
        self.max_y_vel = 10
        self.gravity = 1
        self.rotate = 45
        self.max_rotate = -20
        self.rotate_vel = -3
        self.y_vel_after_flap = -10
        self.rotate_after_flap = 45
        self.dying = False
    def update(self, flap=False):
        if flap:
            self.y_vel = self.y_vel_after_flap
            self.rotate = self.rotate_after_flap
        self.y_vel = min(self.y_vel + self.gravity, self.max_y_vel)
        self.rect.y += self.y_vel
        self.rotate = max(self.rotate + self.rotate_vel, self.max_rotate)
        self.idx += 1
        self.idx %= len(self.frames)
        self.image = self.images[self.frames[self.idx]]
        self.image = pygame.transform.rotate(self.image, self.rotate)

    def go_die(self):
        if self.rect.y < FLOOR_Y:
            self.rect.y += self.max_y_vel
            self.rotate = -90
            self.image = self.images[self.frames[self.idx]]
            self.image = pygame.transform.rotate(self.image, self.rotate)
        else:
            self.dying = False


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, upwards=True):
        pygame.sprite.Sprite.__init__(self)
        if upwards:
            self.image = IMAGE['pipes'][0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.top = y
        else:
            self.image = IMAGE['pipes'][1]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_vel = -4
    def update(self):
        self.rect.x += self.x_vel
main()
