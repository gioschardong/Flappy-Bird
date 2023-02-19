import pygame
from sys import exit
import random

pygame.init()
clock = pygame.time.Clock()

# Tela
altura_janela = 720
largura_janela = 551
janela = pygame.display.set_mode((largura_janela, altura_janela))

# Imagens
passaro_imgs = [pygame.image.load("assets/bird_down.png"),
                pygame.image.load("assets/bird_mid.png"),
                pygame.image.load("assets/bird_up.png")]

ceu_img = pygame.image.load("assets/background.png")

chao_img = pygame.image.load("assets/ground.png")

topo_cano_img = pygame.image.load("assets/pipe_top.png")

base_cano_img = pygame.image.load("assets/pipe_bottom.png")

game_over_img = pygame.image.load("assets/game_over.png")

start_img = pygame.image.load("assets/start.png")

# Game
velocidade_scroll = 1
posicao_inicial_passaro = (100, 250)
score = 0
font = pygame.font.SysFont('arial black', 26)
parar_jogo = True


class Passaro(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = passaro_imgs[0]
        self.rect = self.image.get_rect()
        self.rect.center = posicao_inicial_passaro
        self.image_index = 0
        self.vel = 0
        self.flap = False
        self.alive = True

    def update(self, user_input):
        # Animação Passaro
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = passaro_imgs[self.image_index // 10]

        # Gravidade e Flaps
        self.vel += 0.5
        if self.vel > 7:
            self.vel = 7
        if self.rect.y < 500:
            self.rect.y += int(self.vel)
        if self.vel == 0:
            self.flap = False

        # Rotação Passaro
        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        # Interação do Usuário
        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7


class Cano(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type

    def update(self):
        # Movimentação dos canos
        self.rect.x -= velocidade_scroll
        if self.rect.x <= -largura_janela:
            self.kill()

        # Pontos
        global score
        if self.pipe_type == 'bottom':
            if posicao_inicial_passaro[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True
            if posicao_inicial_passaro[0] > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1


class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = chao_img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        # Movimentação do Chão
        self.rect.x -= velocidade_scroll
        if self.rect.x <= -largura_janela:
            self.kill()


def quit_game():
    # Exit Game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


# Game Main Method
def main():
    global score

    # Inicializar Passaro
    bird = pygame.sprite.GroupSingle()
    bird.add(Passaro())

    # Set Canos
    pipe_timer = 0
    pipes = pygame.sprite.Group()

    # Inicializar chão
    x_pos_ground, y_pos_ground = 0, 520
    ground = pygame.sprite.Group()
    ground.add(Ground(x_pos_ground, y_pos_ground))

    run = True
    while run:
        # Sair
        quit_game()

        # Reset Frame
        janela.fill((0, 0, 0))

        # Interação Usuário
        user_input = pygame.key.get_pressed()

        # Desenhar Background
        janela.blit(ceu_img, (0, 0))

        # Spawn Ground
        if len(ground) <= 2:
            ground.add(Ground(largura_janela, y_pos_ground))

        # Desenhar - Canos / Passaro / Chão
        pipes.draw(janela)
        ground.draw(janela)
        bird.draw(janela)

        # Mostrar Pontos
        score_text = font.render(
            'Score: ' + str(score), True, pygame.Color(255, 255, 255))
        janela.blit(score_text, (20, 20))

        # Update - Canos / Chão / Passaro
        if bird.sprite.alive:
            pipes.update()
            ground.update()
        bird.update(user_input)

        # Detectar colisão
        collision_pipes = pygame.sprite.spritecollide(
            bird.sprites()[0], pipes, False)
        collision_ground = pygame.sprite.spritecollide(
            bird.sprites()[0], ground, False)
        if collision_pipes or collision_ground:
            bird.sprite.alive = False
            if collision_ground:
                janela.blit(game_over_img, (largura_janela // 2 - game_over_img.get_width() // 2,
                                            altura_janela // 2 - game_over_img.get_height() // 2))
                if user_input[pygame.K_r]:
                    score = 0
                    break

        # Criar Canos
        if pipe_timer <= 0 and bird.sprite.alive:
            x_top, x_bottom = 550, 550
            y_top = random.randint(-600, -480)
            y_bottom = y_top + \
                random.randint(90, 130) + base_cano_img.get_height()
            pipes.add(Cano(x_top, y_top, topo_cano_img, 'top'))
            pipes.add(Cano(x_bottom, y_bottom, base_cano_img, 'bottom'))
            pipe_timer = random.randint(180, 250)
        pipe_timer -= 1

        clock.tick(60)
        pygame.display.update()


# Menu
def menu():
    global parar_jogo

    while parar_jogo:
        quit_game()

        # Desenhar Menu
        janela.fill((0, 0, 0))
        janela.blit(ceu_img, (0, 0))
        janela.blit(chao_img, Ground(0, 520))
        janela.blit(passaro_imgs[0], (100, 250))
        janela.blit(start_img, (largura_janela // 2 - start_img.get_width() // 2,
                                altura_janela // 2 - start_img.get_height() // 2))

        # Interação Usuário
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            main()

        pygame.display.update()


menu()
