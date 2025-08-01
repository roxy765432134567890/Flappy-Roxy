import pygame
import sys
import random
import os

# === Constants ===
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
JUMP_VELOCITY = -10
PIPE_WIDTH = 70
GAP_SIZE = 150
PIPE_SPEED = 3
BASE_HEIGHT = 100
FONT_NAME = pygame.font.get_default_font()
HS_FILE = "highscore.txt"

# === Helper: High score persistence ===
def load_highscore():
    if os.path.exists(HS_FILE):
        try:
            with open(HS_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_highscore(score):
    try:
        with open(HS_FILE, "w") as f:
            f.write(str(score))
    except:
        pass

# === Bird class ===
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.vel = 0
        self.alive = True

    def flap(self):
        self.vel = JUMP_VELOCITY

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel

        # Floor collision
        if self.y + self.radius >= HEIGHT - BASE_HEIGHT / 2:
            self.y = HEIGHT - BASE_HEIGHT / 2 - self.radius
            self.alive = False

        # Ceiling clamp
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vel = 0

    def draw(self, surf):
        # Simple circle as bird
        pygame.draw.circle(surf, (255, 235, 59), (int(self.x), int(self.y)), self.radius)
        # Eye
        eye_x = int(self.x + 5)
        eye_y = int(self.y - 3)
        pygame.draw.circle(surf, (0, 0, 0), (eye_x, eye_y), 3)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

# === Pipe class ===
class Pipe:
    def __init__(self, x):
        self.x = x
        self.top_height = random.randint(50, HEIGHT - GAP_SIZE - 150)
        self.bottom_y = self.top_height + GAP_SIZE
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, surf):
        green = (46, 139, 87)
        # Top pipe
        pygame.draw.rect(surf, green, (self.x, 0, PIPE_WIDTH, self.top_height))
        # Bottom pipe
        pygame.draw.rect(surf, green, (self.x, self.bottom_y, PIPE_WIDTH, HEIGHT - self.bottom_y - BASE_HEIGHT/2))

        # Caps (optional)
        cap_height = 10
        pygame.draw.rect(surf, (34, 117, 65), (self.x, self.top_height - cap_height, PIPE_WIDTH, cap_height))
        pygame.draw.rect(surf, (34, 117, 65), (self.x, self.bottom_y, PIPE_WIDTH, cap_height))

    def is_offscreen(self):
        return self.x + PIPE_WIDTH < 0

    def collides_with(self, bird: Bird):
        brect = bird.get_rect()
        # Top pipe rect
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.bottom_y, PIPE_WIDTH, HEIGHT - self.bottom_y - BASE_HEIGHT/2)
        return brect.colliderect(top_rect) or brect.colliderect(bottom_rect)

# === Main game ===
def draw_text(surf, text, size, x, y, center=True, color=(50, 50, 50)):
    font = pygame.font.Font(FONT_NAME, size)
    render = font.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surf.blit(render, rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Roxy (Python)")
    clock = pygame.time.Clock()

    highscore = load_highscore()
    bird = Bird(80, HEIGHT / 2)
    pipes = []
    score = 0
    frame_count = 0
    game_over = False

    # Background gradient surface (precompute)
    bg = pygame.Surface((WIDTH, HEIGHT))
    for i in range(HEIGHT):
        t = i / HEIGHT
        # interpolate between two colors
        r = int(112 + (255 - 112) * t)
        g = int(197 + (255 - 197) * t)
        b = int(206 + (255 - 206) * t)
        pygame.draw.line(bg, (r, g, b), (0, i), (WIDTH, i))

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_highscore(highscore)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if bird.alive:
                        bird.flap()
                    else:
                        # restart
                        bird = Bird(80, HEIGHT / 2)
                        pipes = []
                        score = 0
                        frame_count = 0
                        game_over = False
                if event.key == pygame.K_ESCAPE:
                    save_highscore(highscore)
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if bird.alive:
                    bird.flap()
                else:
                    bird = Bird(80, HEIGHT / 2)
                    pipes = []
                    score = 0
                    frame_count = 0
                    game_over = False

        if bird.alive:
            bird.update()

            # Pipe generation
            if frame_count % 90 == 0:
                pipes.append(Pipe(WIDTH + 10))

            # Update pipes
            for pipe in pipes:
                pipe.update()
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                    score += 1
                    pipe.passed = True
                if pipe.collides_with(bird):
                    bird.alive = False
                    game_over = True

            # Clean offscreen
            pipes = [p for p in pipes if not p.is_offscreen()]

        # Update high score
        if score > highscore:
            highscore = score

        # === Draw ===
        screen.blit(bg, (0, 0))

        # Pipes
        for pipe in pipes:
            pipe.draw(screen)

        # Base
        base_y = HEIGHT - int(BASE_HEIGHT / 2)
        pygame.draw.rect(screen, (220, 220, 220), (0, base_y, WIDTH, BASE_HEIGHT / 2))
        pygame.draw.rect(screen, (200, 200, 200), (0, base_y + BASE_HEIGHT / 2, WIDTH, 4))

        # Bird
        bird.draw(screen)

        # Score
        draw_text(screen, f"Score: {score}", 32, WIDTH // 2, 50)
        draw_text(screen, f"High Score: {highscore}", 18, 10, 10, center=False)

        if game_over:
            draw_text(screen, "GAME OVER", 48, WIDTH // 2, HEIGHT // 2 - 30)
            draw_text(screen, "Press Space / Click to restart", 20, WIDTH // 2, HEIGHT // 2 + 10)
            draw_text(screen, f"Final Score: {score}", 24, WIDTH // 2, HEIGHT // 2 + 50)

        pygame.display.flip()
        frame_count += 1

if __name__ == "__main__":
    main()
