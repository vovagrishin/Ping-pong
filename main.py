import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Pong")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
COLORS = [RED, BLUE, GREEN, WHITE]

# Класс для эффектов частиц
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = random.choice(COLORS)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(1, 3)
        self.lifetime = 30

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.lifetime -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# Класс для ракетки
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 100)
        self.speed = 5
        self.color = WHITE

    def move(self, up=True):
        if up and self.rect.top > 0:
            self.rect.y -= self.speed
        elif not up and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

# Класс для мяча
class Ball:
    def __init__(self):
        self.reset()
        self.particles = []
        self.hit_animation = 0

    def reset(self):
        self.rect = pygame.Rect(WIDTH//2 - 10, HEIGHT//2 - 10, 20, 20)
        self.speed_x = 5 * random.choice([-1, 1])
        self.speed_y = 5 * random.choice([-1, 1])
        self.color = WHITE

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Анимация удара
        if self.hit_animation > 0:
            self.hit_animation -= 1

        # Обновление частиц
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for p in self.particles:
            p.update()

    def create_particles(self):
        for _ in range(20):
            self.particles.append(Particle(self.rect.centerx, self.rect.centery))

    def draw(self):
        # Рисуем анимацию удара
        if self.hit_animation > 0:
            pygame.draw.circle(screen, RED, self.rect.center, 15 + self.hit_animation, 3)
        
        pygame.draw.ellipse(screen, self.color, self.rect)
        
        # Рисуем частицы
        for p in self.particles:
            p.draw()

# Класс для меню
class Menu:
    def __init__(self):
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.selected = 0
        self.options = ["Continue", "Restart", "Quit"]
        self.difficulty_levels = ["Easy", "Medium", "Hard"]
        self.show_difficulty = False

    def draw(self):
        screen.fill(BLACK)
        
        if self.show_difficulty:
            text = self.font.render("Select Difficulty", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 100))
            
            for i, level in enumerate(self.difficulty_levels):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(level, True, color)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 200 + i*50))
        else:
            text = self.font.render("PAUSED", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 100))
            
            for i, option in enumerate(self.options):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(option, True, color)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 200 + i*50))

# Основные объекты
player = Paddle(50, HEIGHT//2 - 50)
ai = Paddle(WIDTH - 70, HEIGHT//2 - 50)
ball = Ball()
menu = Menu()
clock = pygame.time.Clock()

# Игровые переменные
paused = False
score_player = 0
score_ai = 0
difficulty = 1  # 0 - Easy, 1 - Medium, 2 - Hard

# Музыка и звуки
pygame.mixer.music.load("menu.mp3")  # Добавьте файл
pygame.mixer.music.set_volume(0.1)
hit_sound = pygame.mixer.Sound("hit.wav")  # Добавьте файл

def adjust_difficulty():
    if difficulty == 0:
        ai.speed = 3
        ball.speed_x = 4
    elif difficulty == 1:
        ai.speed = 5
        ball.speed_x = 6
    else:
        ai.speed = 7
        ball.speed_x = 8

def main_loop():
    global paused, score_player, score_ai, difficulty
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                if paused:
                    if event.key == pygame.K_DOWN:
                        menu.selected = (menu.selected + 1) % len(menu.options)
                    if event.key == pygame.K_UP:
                        menu.selected = (menu.selected - 1) % len(menu.options)
                    if event.key == pygame.K_RETURN:
                        if menu.show_difficulty:
                            difficulty = menu.selected
                            adjust_difficulty()
                            menu.show_difficulty = True
                        else:
                            if menu.selected == 0:  # Continue
                                paused = False
                            elif menu.selected == 1:  # Restart
                                score_player = 0
                                score_ai = 0
                                ball.reset()
                            elif menu.selected == 2:  # Quit
                                running = False

        if not paused:
            # Управление игроком
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                player.move(up=True)
            if keys[pygame.K_s]:
                player.move(up=False)

            # ИИ противника
            if ai.rect.centery < ball.rect.centery:
                ai.move(up=False)
            elif ai.rect.centery > ball.rect.centery:
                ai.move(up=True)

            # Обновление мяча
            ball.update()

            # Столкновения
            if ball.rect.colliderect(player.rect) or ball.rect.colliderect(ai.rect):
                ball.speed_x *= -1.1
                ball.speed_y *= 1.1
                ball.create_particles()
                ball.hit_animation = 10
                hit_sound.play()

            if ball.rect.top <= 0 or ball.rect.bottom >= HEIGHT:
                ball.speed_y *= -1
                ball.create_particles()

            # Подсчет очков
            if ball.rect.left <= 0:
                score_ai += 1
                ball.reset()
            if ball.rect.right >= WIDTH:
                score_player += 1
                ball.reset()

        # Отрисовка
        screen.fill(BLACK)
        
        # Рисуем игровые объекты
        player.draw()
        ai.draw()
        ball.draw()
        
        # Рисуем интерфейс
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score_player} : {score_ai}", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 10))
        
        # Рисуем меню при паузе
        if paused:
            menu.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    adjust_difficulty()
    pygame.mixer.music.play(-1)
    main_loop()