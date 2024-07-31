 import pygame
import os
import time
import random
import pickle

pygame.font.init()

LARGURA_TELA = 500
ALTURA_TELA = 800
IMAGEM_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('imgspaulinho', 'fundojogo2.jpg')), (LARGURA_TELA, ALTURA_TELA))
IMAGEM_MOTO = pygame.transform.scale(pygame.image.load(os.path.join('imgspaulinho', 'imagem_2023-10-18_180504876-removebg-preview.png')), (70, 70))
IMAGEM_CANO_TOPO = pygame.transform.scale(pygame.image.load(os.path.join('imgspaulinho', 'cone_transito-removebg-preview.png')), (70, 400))
IMAGEM_CANO_BASE = pygame.transform.scale(pygame.image.load(os.path.join('imgspaulinho', 'cone_transito-removebg-preview.png')), (70, 400))
IMAGEM_CHAO = pygame.transform.scale(pygame.image.load(os.path.join('imgspaulinho', 'imagem_2023-10-18_180001950-removebg-preview.png   ')), (LARGURA_TELA, 100))
FONTE = pygame.font.SysFont('comicsans', 100)

class Moto:
    IMGS = IMAGEM_MOTO
    ROTACAO_MAX = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tempo = 0
        self.velocidade = 0
        self.angulo = 0
        self.altura = self.y
        self.imagem = self.IMGS

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        if deslocamento >= 16:
            deslocamento = 16

        if deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < self.altura + 50:
            if self.angulo < self.ROTACAO_MAX:
                self.angulo = self.ROTACAO_MAX
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        self.imagem = pygame.transform.rotate(self.IMGS, self.angulo)
        tela.blit(self.imagem, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cone:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base =  0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO_TOPO, False, True)
        self.CANO_BASE = IMAGEM_CANO_BASE
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, moto):
        moto_mask = moto.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        topo_offset = (self.x - moto.x, self.pos_topo - round(moto.y))
        base_offset = (self.x - moto.x, self.pos_base - round(moto.y))

        b_point = moto_mask.overlap(base_mask, base_offset)
        t_point = moto_mask.overlap(topo_mask, topo_offset)

        if b_point or t_point:
            return True

        return False


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA

        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, moto, cones, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for cone in cones:
        cone.desenhar(tela)

    chao.desenhar(tela)
    moto.desenhar(tela)

    texto = FONTE.render(f"pontos : {pontos}", 1, (255, 255, 0))
    tela.blit(texto, (LARGURA_TELA - 10 - texto.get_width(), 10))

    pygame.display.update()


def main():
    moto = Moto(230, 350)
    chao = Chao(685)
    cones = [Cone(700)]
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    relogio = pygame.time.Clock()
    pontos = 0
    rodando = True

    while rodando:
        relogio.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    moto.pular()

        moto.mover()
        chao.mover()

        adicionar_cone = False
        cones_remover = []
        for cone in cones:
            if cone.colidir(moto):
                rodando = False
                pygame.quit()
                quit()

            if not cone.passou and cone.x < moto.x:
                cone.passou = True
                pontos += 1
                adicionar_cone = True

            if cone.x + cone.CANO_TOPO.get_width() < 0:
                cones_remover.append(cone)

            cone.mover()

        if adicionar_cone:
            cones.append(Cone(700))

        for cone in cones_remover:
            cones.remove(cone)

        if moto.y + moto.imagem.get_height() >= 730:
            rodando = False
            pygame.quit()
            quit()

        desenhar_tela(tela, moto, cones, chao, pontos)

main()
