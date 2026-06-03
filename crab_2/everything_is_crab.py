"""
╔══════════════════════════════════════════════════════════════════╗
║          🦀  EVERYTHING IS CRAB  🦀                              ║
║          Roguelite de Evolução Animal                            ║
║          Inspirado no jogo original da Steam (2026)             ║
╚══════════════════════════════════════════════════════════════════╝

COMO JOGAR:
  - Você começa como um blobinho azul frágil
  - Ande pelo mapa comendo FRUTAS (verdes) e COGUMELOS (roxos)
  - Coma animais MENORES que você para ganhar XP e evoluir
  - FUJA de animais maiores!
  - A cada nível você escolhe UMA evolução (nova parte do corpo)
  - Sobreviva até o timer zerar para vencer!

CONTROLES:
  Mouse / WASD / Setas  → mover a criatura
  ESC                   → sair

DEPENDÊNCIA:
  pip install pygame   (use: py -3.12 -m pip install pygame)
  py -3.12 everything_is_crab.py
"""

import pygame
import random
import math
import sys

# ══════════════════════════════════════════════
#  CONFIGURAÇÕES GERAIS
# ══════════════════════════════════════════════

LARGURA     = 960
ALTURA      = 640
FPS         = 60

# Duração de cada run em segundos (como no jogo original ~20 min, aqui 3 min para demo)
DURACAO_RUN = 180

# ══════════════════════════════════════════════
#  PALETA DE CORES
# ══════════════════════════════════════════════

C_FUNDO         = (34,  45,  28)   # verde musgo escuro (savana/floresta)
C_GRAMA1        = (42,  58,  32)
C_GRAMA2        = (38,  52,  28)
C_PLAYER        = (80,  140, 220)  # azul blob inicial
C_FRUTA         = (80,  200,  60)  # verde brilhante
C_COGUMELO      = (180,  80, 200)  # roxo
C_CARNE         = (220,  80,  60)  # vermelho (carne de animal morto)
C_TEXTO         = (240, 235, 210)
C_HUD_BG        = (20,  20,  20, 180)
C_XP_BAR        = (100, 220, 100)
C_XP_BG         = (40,  40,  40)
C_VIDA_BAR      = (220,  60,  60)
C_AVISO         = (255, 80,   40)

# Cores dos animais do ecossistema
CORES_ANIMAIS = [
    (220, 160,  60),   # amarelo-laranja (herbívoro)
    (160, 220,  80),   # verde claro (pequeno)
    (200,  80, 100),   # vermelho (predador)
    (100, 180, 220),   # azul claro (aquático)
    (240, 180,  40),   # dourado
    (160, 100, 200),   # roxo
    (200, 200,  80),   # amarelo
]

# ══════════════════════════════════════════════
#  EVOLUÇÕES DISPONÍVEIS
#  Cada evolução tem: nome, descrição, efeito (dict de bônus)
# ══════════════════════════════════════════════

EVOLUCOES = [
    # ── Movimento ─────────────────────────────────────────────────
    {"nome": "Patas Ágeis",       "desc": "+40% velocidade",          "tipo": "visual", "vel": 1.4,  "icone": "🦵"},
    {"nome": "Nadadeiras",        "desc": "+25% velocidade",          "tipo": "visual", "vel": 1.25, "icone": "🐟"},
    {"nome": "Asas",              "desc": "+60% velocidade",          "tipo": "visual", "vel": 1.6,  "icone": "🦋"},

    # ── Combate ────────────────────────────────────────────────────
    {"nome": "Garras Afiadas",    "desc": "+50% dano de ataque",      "tipo": "visual", "dano": 1.5, "icone": "⚔️"},
    {"nome": "Ferrão Venenoso",   "desc": "+80% dano, veneno",        "tipo": "visual", "dano": 1.8, "veneno": True, "icone": "☠️"},
    {"nome": "Concha Dura",       "desc": "+80 vida máxima",          "tipo": "visual", "vida": 80,  "icone": "🐚"},
    {"nome": "Pinças de Caranguejo","desc":"+60% dano, +20 vida",     "tipo": "visual", "dano": 1.6, "vida": 20, "icone": "🦀"},
    {"nome": "Espinhos",          "desc": "reflete 20% do dano",      "tipo": "visual", "espinhos": True, "icone": "🌵"},

    # ── Coleta ─────────────────────────────────────────────────────
    {"nome": "Bico Grande",       "desc": "+50% XP de comida",        "tipo": "visual", "xp_bonus": 1.5, "icone": "🐦"},
    {"nome": "Tromba",            "desc": "raio de coleta x2",        "tipo": "visual", "raio_coleta": 2.0, "icone": "🐘"},
    {"nome": "Língua Longa",      "desc": "raio de coleta x1.5",      "tipo": "visual", "raio_coleta": 1.5, "icone": "🦎"},

    # ── Sobrevivência ──────────────────────────────────────────────
    {"nome": "Pele Grossa",       "desc": "+30% redução de dano",     "tipo": "visual", "def": 0.7,  "icone": "🦏"},
    {"nome": "Regeneração",       "desc": "regen +2 vida/seg",        "tipo": "visual", "regen": 2,  "icone": "💚"},
    {"nome": "Camuflagem",        "desc": "inimigos te veem 40% menos","tipo": "visual","camuflagem": True, "icone": "🌿"},

    # ── Tamanho ────────────────────────────────────────────────────
    {"nome": "Corpo Maior",       "desc": "+30% tamanho, +50 vida",   "tipo": "visual", "tamanho": 1.3, "vida": 50, "icone": "📏"},
    {"nome": "Carcinização",      "desc": "Vira Caranguejo! tudo+",   "tipo": "visual", "dano": 1.3, "vel": 1.1, "vida": 30, "icone": "🦀"},
]


# ══════════════════════════════════════════════
#  UTILITÁRIOS
# ══════════════════════════════════════════════

def dist(ax, ay, bx, by):
    """Distância euclidiana entre dois pontos."""
    return math.hypot(bx - ax, by - ay)

def interpola(a, b, t):
    """Interpola linear entre a e b, t em [0,1]."""
    return a + (b - a) * t

def interpola_cor(ca, cb, t):
    """Interpolação de cor RGB."""
    return tuple(int(interpola(ca[i], cb[i], t)) for i in range(3))

def draw_text_shadow(surf, texto, fonte, cor, x, y, sombra=(0,0,0)):
    """Desenha texto com sombra para legibilidade."""
    s = fonte.render(texto, True, sombra)
    surf.blit(s, (x+2, y+2))
    t = fonte.render(texto, True, cor)
    surf.blit(t, (x, y))

def escolher_evolucoes(qtd=3):
    """Seleciona aleatoriamente 'qtd' evoluções do pool global."""
    return random.sample(EVOLUCOES, min(qtd, len(EVOLUCOES)))


# ══════════════════════════════════════════════
#  CLASSE: Particula
# ══════════════════════════════════════════════

class Particula:
    """Faísca visual de curta duração para feedback de eventos."""

    def __init__(self, x, y, cor, vel=3.0, vida=35):
        self.x   = float(x)
        self.y   = float(y)
        self.cor = cor
        ang      = random.uniform(0, 2*math.pi)
        v        = random.uniform(vel*0.4, vel)
        self.vx  = math.cos(ang)*v
        self.vy  = math.sin(ang)*v
        self.vida     = vida
        self.vida_max = vida
        self.r   = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.04   # gravidade suave
        self.vida -= 1

    def draw(self, surf):
        alpha = int(255 * self.vida / self.vida_max)
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.cor, alpha), (self.r, self.r), self.r)
        surf.blit(s, (int(self.x)-self.r, int(self.y)-self.r))

    @property
    def morta(self): return self.vida <= 0


# ══════════════════════════════════════════════
#  CLASSE: Comida
# ══════════════════════════════════════════════

class Comida:
    """
    Item coletável no chão: fruta, cogumelo ou carne.
    Frutas e cogumelos reaparecem periodicamente;
    carne é dropada ao matar um animal.
    """

    def __init__(self, x, y, tipo="fruta"):
        self.x    = float(x)
        self.y    = float(y)
        self.tipo = tipo   # "fruta", "cogumelo", "carne"
        self.raio = 9
        # XP concedido ao coletar
        self.xp   = {"fruta": 8, "cogumelo": 15, "carne": 25}[tipo]
        # animação de flutuação
        self.fase = random.uniform(0, 2*math.pi)

    def draw(self, surf, tick):
        """Desenha o item com leve flutuação vertical."""
        bob = math.sin(tick * 0.06 + self.fase) * 3
        cx  = int(self.x)
        cy  = int(self.y + bob)

        if self.tipo == "fruta":
            # círculo verde com detalhe
            pygame.draw.circle(surf, C_FRUTA, (cx, cy), self.raio)
            pygame.draw.circle(surf, (50, 160, 40), (cx, cy), self.raio, 2)
            # cabinho
            pygame.draw.line(surf, (80, 120, 40), (cx, cy - self.raio),
                             (cx + 3, cy - self.raio - 5), 2)

        elif self.tipo == "cogumelo":
            # chapéu
            pygame.draw.ellipse(surf, C_COGUMELO,
                                (cx - self.raio, cy - self.raio,
                                 self.raio*2, int(self.raio*1.3)))
            # caule
            pygame.draw.rect(surf, (220, 200, 200),
                             (cx - 4, cy, 8, self.raio))
            # pintas brancas
            for dx, dy in [(-4,-4),(3,-6),(0,-2)]:
                pygame.draw.circle(surf, (255,255,255), (cx+dx, cy+dy), 2)

        else:  # carne
            pygame.draw.circle(surf, C_CARNE, (cx, cy), self.raio)
            pygame.draw.circle(surf, (180, 50, 30), (cx, cy), self.raio, 2)
            # osso simplificado
            pygame.draw.line(surf, (240,220,200),
                             (cx-5, cy-5), (cx+5, cy+5), 2)


# ══════════════════════════════════════════════
#  CLASSE: Animal  (NPC do ecossistema)
# ══════════════════════════════════════════════

class Animal:
    """
    Criatura do ecossistema.
    Pode ser presa (foge do jogador se menor) ou predador (persegue se maior).
    Cada animal tem tamanho, vida, velocidade e cor únicos.
    """

    def __init__(self, x, y, nivel=1):
        self.x      = float(x)
        self.y      = float(y)
        self.nivel  = nivel
        # tamanho baseado no nível (1..5)
        self.raio   = 10 + nivel * 5
        self.vida   = self.raio * 4
        self.vida_max = self.vida
        self.vel    = random.uniform(0.8, 1.6) * (1 + 0.1 * nivel)
        self.cor    = random.choice(CORES_ANIMAIS)
        self.cor2   = interpola_cor(self.cor, (255,255,255), 0.3)
        # IA: direção de movimento atual
        self.ang    = random.uniform(0, 2*math.pi)
        self.timer_dir = 0    # quando chega a 0, muda de direção
        self.alvo_x = None    # posição do jogador quando persegue/foge
        self.alvo_y = None
        self.vivo   = True
        self.fase   = random.uniform(0, 2*math.pi)  # para animação
        self.xp_drop = nivel * 20   # XP dado ao morrer

    def update(self, jogador, tick):
        """
        Atualiza IA: persegue se maior que jogador, foge se menor.
        Movimentação por vetores com aleatoriedade.
        """
        if not self.vivo:
            return

        dx = jogador.x - self.x
        dy = jogador.y - self.y
        d  = math.hypot(dx, dy)

        # Raio de percepção do animal
        percepcao = 200 if self.nivel >= jogador.nivel else 150

        if d < percepcao:
            if self.raio > jogador.raio * 1.1:
                # Maior: persegue o jogador
                self.ang = math.atan2(dy, dx) + random.uniform(-0.2, 0.2)
            else:
                # Menor: foge do jogador
                self.ang = math.atan2(-dy, -dx) + random.uniform(-0.3, 0.3)
        else:
            # Deambula aleatoriamente
            self.timer_dir -= 1
            if self.timer_dir <= 0:
                self.ang      = random.uniform(0, 2*math.pi)
                self.timer_dir = random.randint(40, 100)

        # Move na direção atual
        self.x += math.cos(self.ang) * self.vel
        self.y += math.sin(self.ang) * self.vel

        # Mantém dentro do mapa
        self.x = max(self.raio, min(LARGURA - self.raio, self.x))
        self.y = max(self.raio + 50, min(ALTURA - self.raio - 50, self.y))

    def receber_dano(self, dano):
        """Aplica dano e verifica morte."""
        self.vida -= dano
        if self.vida <= 0:
            self.vivo = False

    def draw(self, surf, tick):
        """Desenha o animal com corpo oval, olhos e detalhe de nível."""
        if not self.vivo:
            return

        cx, cy = int(self.x), int(self.y)
        r      = self.raio

        # Corpo principal (elipse ligeiramente achatada)
        pygame.draw.ellipse(surf, self.cor,
                            (cx-r, cy-int(r*0.75), r*2, int(r*1.5)))
        # Destaque superior
        pygame.draw.ellipse(surf, self.cor2,
                            (cx-int(r*0.6), cy-int(r*0.65), int(r*1.2), int(r*0.55)))

        # Olhos (2 olhos simples)
        for lado in (-1, 1):
            ex = cx + lado * int(r*0.35)
            ey = cy - int(r*0.2)
            pygame.draw.circle(surf, (255,255,220), (ex, ey), max(2, r//4))
            pygame.draw.circle(surf, (20,20,20),    (ex+lado, ey+1), max(1, r//7))

        # Barra de vida mini (só aparece se tomou dano)
        if self.vida < self.vida_max:
            bw = r*2
            bh = 4
            bx = cx - r
            by = cy - r - 8
            pygame.draw.rect(surf, (60,20,20),   (bx, by, bw, bh))
            pygame.draw.rect(surf, C_VIDA_BAR,
                             (bx, by, int(bw * self.vida/self.vida_max), bh))

        # Indicador de nível (pontinhos)
        for i in range(self.nivel):
            pygame.draw.circle(surf, (255,220,50),
                               (cx - (self.nivel-1)*4 + i*8, cy + r + 5), 3)


# ══════════════════════════════════════════════
#  CLASSE: Jogador
# ══════════════════════════════════════════════

class Jogador:
    """
    A criatura controlada pelo jogador.

    Começa como um blob azul simples.
    A cada evolução escolhida, ganha partes visuais e bônus de stats.
    O visual é construído proceduralmente a partir da lista de evoluções.
    """

    def __init__(self):
        # Posição inicial no centro do mapa
        self.x = float(LARGURA // 2)
        self.y = float(ALTURA  // 2)

        # Stats base
        self.raio       = 18
        self.raio_base  = 18
        self.vida       = 100
        self.vida_max   = 100
        self.vel_base   = 2.2
        self.vel        = self.vel_base
        self.dano       = 15
        self.nivel      = 1
        self.xp         = 0
        self.xp_prox    = 60   # XP para o próximo nível

        # Bônus de evoluções acumulados
        self.mult_vel       = 1.0
        self.mult_dano      = 1.0
        self.mult_def       = 1.0     # multiplicador de dano recebido
        self.mult_xp        = 1.0
        self.mult_raio_col  = 1.0     # raio de coleta de comida
        self.regen_tick     = 0       # acumula para regeneração
        self.regen_por_seg  = 0
        self.tem_espinhos   = False
        self.tem_veneno     = False
        self.tem_camuflagem = False

        # Lista de evoluções escolhidas (para visualização)
        self.evolucoes_ativas: list[dict] = []

        # Estado
        self.vivo         = True
        self.invencivel   = 0    # frames de invencibilidade após levar dano
        self.atacando     = 0   # cooldown de ataque
        self.tick_local   = 0

    # ── Stats dinâmicos ─────────────────────────────────────────────

    @property
    def raio_coleta(self):
        """Raio efetivo de coleta de comida."""
        return (self.raio + 20) * self.mult_raio_col

    @property
    def velocidade(self):
        return self.vel_base * self.mult_vel

    # ── Aplicar evolução ────────────────────────────────────────────

    def aplicar_evolucao(self, evo):
        """
        Aplica os efeitos de uma evolução escolhida.
        Atualiza stats e registra para visualização.
        """
        self.evolucoes_ativas.append(evo)

        if "vel"          in evo: self.mult_vel      *= evo["vel"]
        if "dano"         in evo: self.mult_dano     *= evo["dano"]
        if "def"          in evo: self.mult_def      *= evo["def"]
        if "xp_bonus"     in evo: self.mult_xp       *= evo["xp_bonus"]
        if "raio_coleta"  in evo: self.mult_raio_col *= evo["raio_coleta"]
        if "regen"        in evo: self.regen_por_seg += evo["regen"]
        if "espinhos"     in evo: self.tem_espinhos   = True
        if "veneno"       in evo: self.tem_veneno     = True
        if "camuflagem"   in evo: self.tem_camuflagem = True

        if "vida" in evo:
            self.vida_max += evo["vida"]
            self.vida     += evo["vida"]

        if "tamanho" in evo:
            self.raio      = int(self.raio_base * evo["tamanho"])
            self.raio_base = self.raio

        self.nivel += 1

    # ── Ganhar XP ───────────────────────────────────────────────────

    def ganhar_xp(self, qtd):
        """
        Adiciona XP aplicando o multiplicador de bônus.
        Retorna True se subiu de nível (para disparar tela de evolução).
        """
        self.xp += int(qtd * self.mult_xp)
        if self.xp >= self.xp_prox:
            self.xp       -= self.xp_prox
            self.xp_prox   = int(self.xp_prox * 1.35)
            return True   # subiu de nível!
        return False

    # ── Receber dano ────────────────────────────────────────────────

    def receber_dano(self, dano):
        """Aplica dano com redução de defesa e invencibilidade temporária."""
        if self.invencivel > 0:
            return
        dano_real = max(1, int(dano * self.mult_def))
        self.vida -= dano_real
        self.invencivel = 45   # ~0.75s de invencibilidade
        if self.vida <= 0:
            self.vida  = 0
            self.vivo  = False

    # ── Atualização ─────────────────────────────────────────────────

    def update(self, teclas, tick):
        """Move o jogador e aplica regeneração."""
        if not self.vivo:
            return

        self.tick_local += 1
        if self.invencivel > 0: self.invencivel -= 1
        if self.atacando  > 0: self.atacando   -= 1

        # Movimento por teclado
        dx, dy = 0, 0
        if teclas[pygame.K_LEFT]  or teclas[pygame.K_a]: dx -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx += 1
        if teclas[pygame.K_UP]    or teclas[pygame.K_w]: dy -= 1
        if teclas[pygame.K_DOWN]  or teclas[pygame.K_s]: dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        v  = self.velocidade
        self.x = max(self.raio, min(LARGURA  - self.raio, self.x + dx * v))
        self.y = max(self.raio + 50, min(ALTURA - self.raio - 50, self.y + dy * v))

        # Regeneração (se tiver a evolução)
        if self.regen_por_seg > 0:
            self.regen_tick += 1
            if self.regen_tick >= FPS:
                self.regen_tick = 0
                self.vida = min(self.vida_max, self.vida + self.regen_por_seg)

    # ── Desenho ─────────────────────────────────────────────────────

    def draw(self, surf, tick):
        """
        Desenha o jogador.
        O corpo base é um blob arredondado azul.
        Evoluções adicionam partes visuais extras (patas, garras, asas etc.)
        """
        if not self.vivo:
            return

        cx, cy = int(self.x), int(self.y)
        r      = self.raio
        t      = self.tick_local

        # Efeito de piscar quando invencível
        if self.invencivel > 0 and (self.invencivel // 5) % 2 == 0:
            return

        # Cor do corpo: azul base → muda conforme evoluções
        cor_corpo = C_PLAYER
        # Se tiver carcinização → laranja-avermelhado
        nomes = [e["nome"] for e in self.evolucoes_ativas]
        if "Carcinização" in nomes:
            cor_corpo = (210, 60, 20)
        elif "Camuflagem" in nomes:
            cor_corpo = (80, 140, 60)
        elif "Ferrão Venenoso" in nomes:
            cor_corpo = (100, 180, 60)

        cor2 = interpola_cor(cor_corpo, (255,255,255), 0.3)

        # ── Asas (se tiver) ──────────────────────────────────────────
        if "Asas" in nomes:
            bat = math.sin(t * 0.18) * 18
            for lado in (-1, 1):
                pts = [
                    (cx, cy - r//2),
                    (cx + lado*(r + int(bat)), cy - r - 15),
                    (cx + lado*(r + 8), cy),
                ]
                pygame.draw.polygon(surf, (180, 120, 220), pts)
                pygame.draw.polygon(surf, (140, 80, 180), pts, 2)

        # ── Patas (se tiver Patas Ágeis) ─────────────────────────────
        if "Patas Ágeis" in nomes or "Carcinização" in nomes:
            for i in range(3):
                for lado in (-1, 1):
                    ang_p  = math.radians(lado * (30 + i*25))
                    osc    = math.sin(t*0.12 + i*0.9) * 10 * lado
                    ang_p += math.radians(osc)
                    ox = cx + lado * int(r * 0.6)
                    oy = cy + (i-1) * int(r * 0.4)
                    fx = ox + math.cos(ang_p) * r * 0.9
                    fy = oy + math.sin(ang_p) * r * 0.9
                    pygame.draw.line(surf, cor2,
                                     (ox, oy), (int(fx), int(fy)),
                                     max(2, r//7))

        # ── Espinhos ─────────────────────────────────────────────────
        if "Espinhos" in nomes:
            for ang_s in range(0, 360, 45):
                ar = math.radians(ang_s)
                sx = cx + math.cos(ar) * r
                sy = cy + math.sin(ar) * r
                ex = cx + math.cos(ar) * (r + 10)
                ey = cy + math.sin(ar) * (r + 10)
                pygame.draw.line(surf, (180, 220, 80),
                                 (int(sx), int(sy)), (int(ex), int(ey)), 2)

        # ── Corpo principal ───────────────────────────────────────────
        # Levemente distorcido (blob orgânico)
        pygame.draw.circle(surf, cor_corpo, (cx, cy), r)
        pygame.draw.circle(surf, cor2,      (cx, cy - r//4), int(r*0.6))

        # ── Garras / Pinças ───────────────────────────────────────────
        if any(n in nomes for n in ["Garras Afiadas","Pinças de Caranguejo","Carcinização"]):
            for lado in (-1, 1):
                gx = cx + lado * (r + 8)
                gy = cy - 5
                ab = int(math.sin(t*0.08) * 6) * lado
                pygame.draw.circle(surf, cor_corpo, (gx, gy), r//2)
                pygame.draw.line(surf, cor2, (gx, gy-4),
                                 (gx + lado*8, gy - 10 - ab), max(2,r//6))
                pygame.draw.line(surf, cor2, (gx, gy+2),
                                 (gx + lado*8, gy + 6 + ab), max(2,r//6))

        # ── Ferrão ────────────────────────────────────────────────────
        if "Ferrão Venenoso" in nomes:
            pygame.draw.polygon(surf, (80,200,40), [
                (cx, cy - r - 2),
                (cx - 5, cy - r - 14),
                (cx + 5, cy - r - 14),
            ])

        # ── Olhos ─────────────────────────────────────────────────────
        for lado in (-1, 1):
            ex = cx + lado * int(r*0.38)
            ey = cy - int(r*0.28)
            pygame.draw.circle(surf, (255,255,220), (ex, ey), max(3, r//4))
            pygame.draw.circle(surf, (20,20,20),    (ex+lado, ey+1), max(1, r//8))

        # ── Nadadeiras ────────────────────────────────────────────────
        if "Nadadeiras" in nomes:
            for lado in (-1, 1):
                ondula = int(math.sin(t*0.15) * 6) * lado
                pts = [
                    (cx, cy),
                    (cx + lado*(r+4), cy - 8 + ondula),
                    (cx + lado*(r+4), cy + 8 + ondula),
                ]
                pygame.draw.polygon(surf, cor2, pts)

        # ── Aura de veneno ────────────────────────────────────────────
        if "Ferrão Venenoso" in nomes:
            s = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            alpha_v = 40 + int(20 * math.sin(t * 0.1))
            pygame.draw.circle(s, (80,200,40,alpha_v), (r*2, r*2), r*2)
            surf.blit(s, (cx - r*2, cy - r*2))


# ══════════════════════════════════════════════
#  TELA DE ESCOLHA DE EVOLUÇÃO
# ══════════════════════════════════════════════

def tela_evolucao(surf, clock, fonte_tit, fonte_norm, fonte_peq):
    """
    Para o jogo e exibe 3 cartas de evolução para o jogador escolher.
    Retorna o índice (0,1,2) da carta escolhida.
    """
    opcoes = escolher_evolucoes(3)

    # Dimensões das cartas
    cw, ch = 220, 280
    gap    = 30
    total  = cw*3 + gap*2
    cx_ini = (LARGURA - total) // 2
    cy_ini = (ALTURA  - ch)   // 2

    selecionado = None
    hover       = -1
    tick        = 0

    while selecionado is None:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: selecionado = 0
                if ev.key == pygame.K_2: selecionado = 1
                if ev.key == pygame.K_3: selecionado = 2
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                for i in range(3):
                    cx = cx_ini + i*(cw+gap)
                    if cx <= mx <= cx+cw and cy_ini <= my <= cy_ini+ch:
                        selecionado = i

        mx, my = pygame.mouse.get_pos()
        hover = -1
        for i in range(3):
            cx = cx_ini + i*(cw+gap)
            if cx <= mx <= cx+cw and cy_ini <= my <= cy_ini+ch:
                hover = i

        tick += 1

        # Fundo escurecido semi-transparente
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        # Título
        txt = fonte_tit.render("✨ EVOLUÇÃO! Escolha uma parte:", True, (255, 220, 80))
        surf.blit(txt, (LARGURA//2 - txt.get_width()//2, cy_ini - 55))
        sub = fonte_peq.render("Clique na carta  ou  tecle 1 / 2 / 3", True, (180, 180, 180))
        surf.blit(sub, (LARGURA//2 - sub.get_width()//2, cy_ini - 25))

        # Cartas
        for i, evo in enumerate(opcoes):
            cx = cx_ini + i*(cw+gap)
            is_hover = (i == hover)
            cy_card  = cy_ini - (12 if is_hover else 0)   # levanta no hover

            # Fundo da carta
            cor_card = (50, 60, 80) if not is_hover else (70, 85, 110)
            pygame.draw.rect(surf, cor_card,
                             (cx, cy_card, cw, ch), border_radius=14)
            # Borda
            cor_borda = (255, 200, 50) if is_hover else (100, 120, 150)
            pygame.draw.rect(surf, cor_borda,
                             (cx, cy_card, cw, ch), 3, border_radius=14)

            # Número da tecla
            num_t = fonte_tit.render(str(i+1), True, (200,200,200))
            surf.blit(num_t, (cx + 10, cy_card + 8))

            # Ícone grande centralizado
            ico = fonte_tit.render(evo["icone"], True, (255,255,255))
            surf.blit(ico, (cx + cw//2 - ico.get_width()//2, cy_card + 40))

            # Nome
            nome_t = fonte_norm.render(evo["nome"], True, (255, 230, 100))
            surf.blit(nome_t, (cx + cw//2 - nome_t.get_width()//2, cy_card + 115))

            # Descrição (quebra de linha manual se necessário)
            desc = evo["desc"]
            desc_t = fonte_peq.render(desc, True, (200, 210, 220))
            surf.blit(desc_t, (cx + cw//2 - desc_t.get_width()//2, cy_card + 148))

            # Linha separadora
            pygame.draw.line(surf, cor_borda,
                             (cx+15, cy_card+135), (cx+cw-15, cy_card+135), 1)

            # Preview dos bônus
            y_bonus = cy_card + 175
            for chave, label in [("vel","⚡ Vel"), ("dano","⚔️ Dano"),
                                  ("vida","❤️ Vida"), ("def","🛡️ Def")]:
                if chave in evo:
                    val = evo[chave]
                    if isinstance(val, float):
                        s = f"{label} x{val:.1f}"
                    else:
                        s = f"{label} +{val}"
                    bt = fonte_peq.render(s, True, (150, 220, 150))
                    surf.blit(bt, (cx + cw//2 - bt.get_width()//2, y_bonus))
                    y_bonus += 20

        pygame.display.flip()
        clock.tick(FPS)

    return opcoes[selecionado]


# ══════════════════════════════════════════════
#  TELA DE GAME OVER / VITÓRIA
# ══════════════════════════════════════════════

def tela_fim(surf, clock, fonte_tit, fonte_norm, fonte_peq, ganhou, nivel, tempo):
    """Exibe resultado final e aguarda tecla para sair."""
    esperando = True
    tick = 0
    while esperando:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.KEYDOWN:
                esperando = False
            if ev.type == pygame.MOUSEBUTTONDOWN:
                esperando = False

        tick += 1
        surf.fill((10, 8, 5) if not ganhou else (20, 35, 10))

        # Título
        if ganhou:
            msg   = "🦀 VOCÊ SOBREVIVEU! 🦀"
            cor_m = (100, 230, 100)
        else:
            msg   = "☠️  VOCÊ FOI DEVORADO...  ☠️"
            cor_m = (220, 80, 60)

        pulse = 1 + 0.05*math.sin(tick*0.07)
        txt   = fonte_tit.render(msg, True, cor_m)
        surf.blit(txt, (LARGURA//2 - txt.get_width()//2, ALTURA//2 - 80))

        # Stats
        for i, linha in enumerate([
            f"Nível atingido: {nivel}",
            f"Tempo sobrevivido: {int(tempo)}s",
        ]):
            t = fonte_norm.render(linha, True, C_TEXTO)
            surf.blit(t, (LARGURA//2 - t.get_width()//2, ALTURA//2 + i*35))

        hint = fonte_peq.render("[ Pressione qualquer tecla para sair ]", True, (140,140,140))
        surf.blit(hint, (LARGURA//2 - hint.get_width()//2, ALTURA//2 + 110))

        pygame.display.flip()
        clock.tick(FPS)


# ══════════════════════════════════════════════
#  FUNÇÃO: desenhar_fundo
# ══════════════════════════════════════════════

def desenhar_fundo(surf, tick):
    """
    Desenha o chão do ecossistema com variações de grama,
    manchas de terra e elementos decorativos.
    """
    surf.fill(C_FUNDO)

    # Manchas irregulares de grama mais clara (geradas 1x, usadas sempre)
    # Usamos seed fixo para as manchas não "pularem"
    rng = random.Random(1337)
    for _ in range(60):
        mx = rng.randint(0, LARGURA)
        my = rng.randint(50, ALTURA - 50)
        mr = rng.randint(20, 70)
        s  = pygame.Surface((mr*2, mr*2), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*C_GRAMA1, 120), (0,0,mr*2,mr*2))
        surf.blit(s, (mx-mr, my-mr))

    # Pedrinhas decorativas
    rng2 = random.Random(42)
    for _ in range(20):
        px = rng2.randint(20, LARGURA-20)
        py = rng2.randint(80, ALTURA-80)
        pr = rng2.randint(3,8)
        pygame.draw.circle(surf, (90,85,75), (px,py), pr)


# ══════════════════════════════════════════════
#  FUNÇÃO: desenhar_hud
# ══════════════════════════════════════════════

def desenhar_hud(surf, fonte_norm, fonte_peq, jogador, tempo_rest):
    """Desenha barras de vida, XP, nível, timer e lista de evoluções."""

    # ── Barra de vida ─────────────────────────────────────────────
    bx, by = 15, 10
    bw, bh = 200, 18
    pygame.draw.rect(surf, C_XP_BG,   (bx, by, bw, bh), border_radius=5)
    fill_v = int(bw * jogador.vida / max(1, jogador.vida_max))
    pygame.draw.rect(surf, C_VIDA_BAR, (bx, by, fill_v, bh), border_radius=5)
    pygame.draw.rect(surf, (200,80,80), (bx, by, bw, bh), 2, border_radius=5)
    txt_v = fonte_peq.render(f"❤️ {int(jogador.vida)}/{jogador.vida_max}", True, C_TEXTO)
    surf.blit(txt_v, (bx+5, by+1))

    # ── Barra de XP ───────────────────────────────────────────────
    by2 = by + bh + 6
    pygame.draw.rect(surf, C_XP_BG,  (bx, by2, bw, 12), border_radius=5)
    fill_x = int(bw * jogador.xp / max(1, jogador.xp_prox))
    pygame.draw.rect(surf, C_XP_BAR, (bx, by2, fill_x, 12), border_radius=5)
    pygame.draw.rect(surf, (80,200,80), (bx, by2, bw, 12), 2, border_radius=5)
    txt_x = fonte_peq.render(f"XP {jogador.xp}/{jogador.xp_prox}", True, C_TEXTO)
    surf.blit(txt_x, (bx+5, by2))

    # ── Nível ─────────────────────────────────────────────────────
    txt_n = fonte_norm.render(f"Nível {jogador.nivel}", True, (255,220,80))
    surf.blit(txt_n, (bx + bw + 12, by))

    # ── Timer ─────────────────────────────────────────────────────
    mins = int(tempo_rest) // 60
    segs = int(tempo_rest) % 60
    cor_timer = (220, 80, 60) if tempo_rest < 30 else C_TEXTO
    txt_t = fonte_norm.render(f"⏱ {mins}:{segs:02d}", True, cor_timer)
    surf.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 12))

    # ── Evoluções ativas (canto direito) ──────────────────────────
    ex = LARGURA - 10
    ey = 10
    tit = fonte_peq.render("Evoluções:", True, (180,180,180))
    surf.blit(tit, (ex - tit.get_width(), ey))
    ey += 16
    for evo in jogador.evolucoes_ativas[-8:]:   # mostra as 8 últimas
        te = fonte_peq.render(f"{evo['icone']} {evo['nome']}", True, (200,220,160))
        surf.blit(te, (ex - te.get_width(), ey))
        ey += 15

    # ── Controles (bottom) ────────────────────────────────────────
    ctrl = fonte_peq.render("WASD / Setas → mover  |  Toque nos animais menores para atacar",
                             True, (110,130,100))
    surf.blit(ctrl, (LARGURA//2 - ctrl.get_width()//2, ALTURA - 18))


# ══════════════════════════════════════════════
#  LOOP PRINCIPAL
# ══════════════════════════════════════════════

def main():
    pygame.init()
    surf  = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Everything is Crab 🦀")
    clock = pygame.time.Clock()

    # Fontes
    try:
        fonte_tit  = pygame.font.SysFont("segoeuiemoji", 26, bold=True)
        fonte_norm = pygame.font.SysFont("segoeuiemoji", 20)
        fonte_peq  = pygame.font.SysFont("segoeuiemoji", 15)
    except Exception:
        fonte_tit  = pygame.font.SysFont(None, 28, bold=True)
        fonte_norm = pygame.font.SysFont(None, 22)
        fonte_peq  = pygame.font.SysFont(None, 16)

    # ── Inicializa entidades ────────────────────────────────────────
    jogador    = Jogador()
    particulas: list[Particula] = []

    # Spawn inicial de comida
    comidas: list[Comida] = []
    for _ in range(20):
        tipo = random.choice(["fruta","fruta","cogumelo"])
        comidas.append(Comida(
            random.randint(30, LARGURA-30),
            random.randint(80, ALTURA-80),
            tipo
        ))

    # Spawn inicial de animais (nível 1-2)
    animais: list[Animal] = []
    for _ in range(12):
        nivel_a = random.choices([1,2,3], weights=[60,30,10])[0]
        animais.append(Animal(
            random.randint(50, LARGURA-50),
            random.randint(80, ALTURA-80),
            nivel_a
        ))

    # Timers
    tick              = 0
    inicio            = pygame.time.get_ticks()
    timer_spawn_comida= 0
    timer_spawn_animal= 0
    pausado           = False   # True durante tela de evolução

    # ── LOOP PRINCIPAL ──────────────────────────────────────────────
    rodando = True
    while rodando:

        # ─ Tempo restante ─────────────────────────────────────────
        elapsed     = (pygame.time.get_ticks() - inicio) / 1000
        tempo_rest  = max(0, DURACAO_RUN - elapsed)

        # ─ Eventos ────────────────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    rodando = False

        teclas = pygame.key.get_pressed()

        # ─ Lógica ─────────────────────────────────────────────────

        jogador.update(teclas, tick)

        # Atualiza animais
        for a in animais:
            a.update(jogador, tick)

        # ── Coleta de comida ──────────────────────────────────────
        coletadas = []
        for c in comidas:
            if dist(jogador.x, jogador.y, c.x, c.y) < jogador.raio_coleta:
                subiu = jogador.ganhar_xp(c.xp)
                for _ in range(8):
                    cor_p = C_FRUTA if c.tipo=="fruta" else C_COGUMELO if c.tipo=="cogumelo" else C_CARNE
                    particulas.append(Particula(c.x, c.y, cor_p, vel=2.5))
                coletadas.append(c)

                if subiu:
                    # Pausa e mostra tela de evolução
                    evo = tela_evolucao(surf, clock, fonte_tit, fonte_norm, fonte_peq)
                    jogador.aplicar_evolucao(evo)
                    for _ in range(25):
                        particulas.append(Particula(
                            jogador.x, jogador.y,
                            (255,220,50), vel=4
                        ))

        comidas = [c for c in comidas if c not in coletadas]

        # ── Combate jogador ↔ animais ─────────────────────────────
        for a in animais:
            if not a.vivo:
                continue
            d = dist(jogador.x, jogador.y, a.x, a.y)
            colide = d < jogador.raio + a.raio - 4

            if colide:
                if jogador.raio >= a.raio * 0.9 and jogador.atacando == 0:
                    # Jogador é grande o suficiente: ataca o animal
                    dano_j = int(jogador.dano * jogador.mult_dano)
                    a.receber_dano(dano_j)
                    jogador.atacando = 20   # cooldown entre ataques

                    for _ in range(6):
                        particulas.append(Particula(a.x, a.y, a.cor, vel=3))

                    if not a.vivo:
                        # Animal morreu: drop de carne + XP
                        comidas.append(Comida(a.x, a.y, "carne"))
                        subiu = jogador.ganhar_xp(a.xp_drop)
                        for _ in range(18):
                            particulas.append(Particula(a.x, a.y, a.cor, vel=4))
                        if subiu:
                            evo = tela_evolucao(surf, clock, fonte_tit, fonte_norm, fonte_peq)
                            jogador.aplicar_evolucao(evo)

                elif a.raio > jogador.raio * 1.1:
                    # Animal é maior: machuca o jogador
                    dano_a = a.nivel * 8
                    jogador.receber_dano(dano_a)
                    for _ in range(6):
                        particulas.append(Particula(jogador.x, jogador.y,
                                                    (255,80,80), vel=3))

                    # Espinhos: reflete dano
                    if jogador.tem_espinhos:
                        a.receber_dano(int(dano_a * 0.2))

        # Remove animais mortos
        animais = [a for a in animais if a.vivo]

        # ── Spawn periódico de comida ─────────────────────────────
        timer_spawn_comida += 1
        if timer_spawn_comida > 200 and len(comidas) < 25:
            timer_spawn_comida = 0
            tipo_c = random.choices(["fruta","cogumelo"], weights=[70,30])[0]
            comidas.append(Comida(
                random.randint(30, LARGURA-30),
                random.randint(80, ALTURA-80),
                tipo_c
            ))

        # ── Spawn periódico de animais ────────────────────────────
        timer_spawn_animal += 1
        intervalo = max(120, 300 - jogador.nivel * 15)
        if timer_spawn_animal > intervalo and len(animais) < 18:
            timer_spawn_animal = 0
            # Nível dos novos animais sobe com o tempo de jogo
            max_nivel = min(5, 1 + int(elapsed / 30))
            nivel_a   = random.randint(1, max_nivel)
            # Spawn nas bordas para não aparecer em cima do jogador
            lado = random.randint(0,3)
            if lado == 0: ax, ay = random.randint(0,LARGURA), 60
            elif lado == 1: ax, ay = random.randint(0,LARGURA), ALTURA-60
            elif lado == 2: ax, ay = 20, random.randint(60,ALTURA-60)
            else: ax, ay = LARGURA-20, random.randint(60,ALTURA-60)
            animais.append(Animal(ax, ay, nivel_a))

        # ── Partículas ────────────────────────────────────────────
        for p in particulas:
            p.update()
        particulas = [p for p in particulas if not p.morta]

        # ── Verifica fim de jogo ──────────────────────────────────
        if not jogador.vivo:
            tela_fim(surf, clock, fonte_tit, fonte_norm, fonte_peq,
                     False, jogador.nivel, elapsed)
            rodando = False
            continue

        if tempo_rest <= 0:
            tela_fim(surf, clock, fonte_tit, fonte_norm, fonte_peq,
                     True, jogador.nivel, elapsed)
            rodando = False
            continue

        # ─ Desenho ────────────────────────────────────────────────

        # 1. Fundo
        desenhar_fundo(surf, tick)

        # 2. Comida
        for c in comidas:
            c.draw(surf, tick)

        # 3. Animais
        for a in animais:
            a.draw(surf, tick)

        # 4. Partículas
        for p in particulas:
            p.draw(surf)

        # 5. Jogador
        jogador.draw(surf, tick)

        # 6. HUD
        desenhar_hud(surf, fonte_norm, fonte_peq, jogador, tempo_rest)

        # 7. Aviso de perigo (se animal grande estiver perto)
        for a in animais:
            if a.raio > jogador.raio * 1.2:
                if dist(jogador.x, jogador.y, a.x, a.y) < 160:
                    if (tick//15) % 2 == 0:
                        av = fonte_norm.render("⚠️ PERIGO! FUJA!", True, C_AVISO)
                        surf.blit(av, (LARGURA//2 - av.get_width()//2, 50))
                    break

        pygame.display.flip()
        clock.tick(FPS)
        tick += 1

    pygame.quit()
    sys.exit()


# ══════════════════════════════════════════════
#  ENTRADA
# ══════════════════════════════════════════════

if __name__ == "__main__":
    main()
