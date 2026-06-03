"""
╔══════════════════════════════════════════════════════════════════╗
║        🦀  EVERYTHING IS CRAB  — Versão Melhorada  🦀           ║
║        Roguelite de Evolução Animal                              ║
╚══════════════════════════════════════════════════════════════════╝

COMO JOGAR:
  - Você começa como um blobinho azul frágil num ecossistema hostil
  - WASD / Setas  → mover
  - Coma FRUTAS 🍎 e COGUMELOS 🍄 para ganhar XP
  - Mate animais MENORES para carne e XP bônus
  - FUJA de animais maiores!
  - A cada nível escolha 1 de 3 EVOLUÇÕES
  - A cada 60s aparece um BOSS — derrote-o para ganhar evolução rara!
  - Sobreviva 3 minutos para vencer 🏆

DEPENDÊNCIA:
  py -3.12 -m pip install pygame
  py -3.12 everything_is_crab.py
"""

import pygame
import random
import math
import sys

# ══════════════════════════════════════════════
#  CONFIGURAÇÕES
# ══════════════════════════════════════════════
LARGURA      = 1024
ALTURA       = 680
FPS          = 60
DURACAO_RUN  = 180   # segundos

# ══════════════════════════════════════════════
#  PALETA
# ══════════════════════════════════════════════
C_FUNDO      = (28, 42, 22)
C_GRAMA_A    = (38, 58, 28)
C_GRAMA_B    = (48, 70, 32)
C_TERRA      = (80, 60, 40)
C_PLAYER     = (70, 130, 220)
C_FRUTA      = (60, 210, 60)
C_COGUMELO   = (170, 70, 210)
C_CARNE      = (210, 70, 50)
C_TEXTO      = (240, 235, 210)
C_HUD_BG     = (15, 15, 20)
C_XP         = (80, 210, 110)
C_VIDA       = (210, 55, 55)
C_AVISO      = (255, 70, 30)
C_BOSS_HUD   = (200, 30, 30)
C_OURO       = (255, 210, 40)

CORES_ANIMAIS = [
    (220,155,50),(150,215,75),(195,70,95),
    (90,175,225),(235,175,35),(145,90,200),(195,200,70),
    (255,120,40),(40,190,160),(230,80,150),
]

# ══════════════════════════════════════════════
#  POOL DE EVOLUÇÕES  (45 no total)
# ══════════════════════════════════════════════
# Cada entrada: nome, desc, icone, raridade (1=comum,2=rara,3=épica), efeitos
EVOLUCOES = [
    # ── MOVIMENTO ────────────────────────────────────────────────────
    {"nome":"Patas Ágeis",       "icone":"🦵","rar":1,"desc":"+35% velocidade",        "vel":1.35},
    {"nome":"Nadadeiras",        "icone":"🐟","rar":1,"desc":"+25% velocidade",        "vel":1.25},
    {"nome":"Asas de Morcego",   "icone":"🦇","rar":2,"desc":"+65% velocidade",        "vel":1.65},
    {"nome":"Propulsão",         "icone":"🚀","rar":3,"desc":"+100% velocidade",       "vel":2.0},
    {"nome":"Pernas de Saltador","icone":"🦘","rar":2,"desc":"+50% vel + dash",        "vel":1.5,"dash":True},

    # ── COMBATE ───────────────────────────────────────────────────────
    {"nome":"Garras Afiadas",    "icone":"⚔️","rar":1,"desc":"+50% dano",             "dano":1.5},
    {"nome":"Ferrão Venenoso",   "icone":"☠️","rar":2,"desc":"+80% dano + veneno",    "dano":1.8,"veneno":True},
    {"nome":"Pinças de Caranguejo","icone":"🦀","rar":2,"desc":"+60% dano +20 vida",  "dano":1.6,"vida":20},
    {"nome":"Mandíbulas",        "icone":"🦈","rar":1,"desc":"+40% dano",             "dano":1.4},
    {"nome":"Chifres",           "icone":"🦏","rar":1,"desc":"+45% dano",             "dano":1.45},
    {"nome":"Bico de Abutre",    "icone":"🦅","rar":2,"desc":"+70% dano",             "dano":1.7},
    {"nome":"Presas de Sabre",   "icone":"🐯","rar":3,"desc":"+120% dano",            "dano":2.2},
    {"nome":"Esporão de Osso",   "icone":"🦴","rar":2,"desc":"+55% dano",             "dano":1.55},

    # ── DEFESA / VIDA ─────────────────────────────────────────────────
    {"nome":"Concha Dura",       "icone":"🐚","rar":1,"desc":"+80 vida máx",          "vida":80},
    {"nome":"Pele Grossa",       "icone":"🦛","rar":1,"desc":"-30% dano recebido",    "def":0.70},
    {"nome":"Armadura de Osso",  "icone":"💀","rar":2,"desc":"-50% dano recebido",    "def":0.50},
    {"nome":"Escamas de Dragão", "icone":"🐉","rar":3,"desc":"-65% dano recebido",    "def":0.35},
    {"nome":"Espinhos",          "icone":"🌵","rar":2,"desc":"Reflete 25% do dano",   "espinhos":True},
    {"nome":"Corpo Maior",       "icone":"📏","rar":2,"desc":"+35% tamanho +60 vida", "tamanho":1.35,"vida":60},
    {"nome":"Blob Gordo",        "icone":"🫧","rar":1,"desc":"+50 vida máx",          "vida":50},
    {"nome":"Carapaça",          "icone":"🦞","rar":2,"desc":"+100 vida +def leve",   "vida":100,"def":0.85},

    # ── REGENERAÇÃO / SUPORTE ─────────────────────────────────────────
    {"nome":"Regeneração",       "icone":"💚","rar":2,"desc":"Regen +3 vida/s",       "regen":3},
    {"nome":"Regen Épica",       "icone":"💗","rar":3,"desc":"Regen +8 vida/s",       "regen":8},
    {"nome":"Boca Gulosa",       "icone":"👄","rar":1,"desc":"+40% XP de comida",     "xp_bonus":1.4},
    {"nome":"Língua Longa",      "icone":"🦎","rar":1,"desc":"Raio de coleta x1.6",   "raio_coleta":1.6},
    {"nome":"Tromba Sugadora",   "icone":"🐘","rar":2,"desc":"Raio de coleta x2.2",   "raio_coleta":2.2},
    {"nome":"Bico Grande",       "icone":"🦜","rar":1,"desc":"+50% XP de comida",     "xp_bonus":1.5},

    # ── ESPECIAIS ─────────────────────────────────────────────────────
    {"nome":"Camuflagem",        "icone":"🌿","rar":2,"desc":"Inimigos te veem menos","camuflagem":True},
    {"nome":"Aura de Fogo",      "icone":"🔥","rar":3,"desc":"Queima inimigos perto", "aura_fogo":True},
    {"nome":"Veneno em Área",    "icone":"🧪","rar":3,"desc":"Nuvem de veneno ao redor","aura_veneno":True},
    {"nome":"Olho de Aguia",     "icone":"👁️","rar":2,"desc":"Vê inimigos mais longe","percep":1.7},
    {"nome":"Carcinização",      "icone":"🦀","rar":3,"desc":"VIRA CARANGUEJO: tudo+","dano":1.3,"vel":1.15,"vida":40,"def":0.88},
    {"nome":"Membrana Solar",    "icone":"☀️","rar":3,"desc":"Regen +5/s + +20% vel", "regen":5,"vel":1.2},
    {"nome":"Células Regenerativas","icone":"🔬","rar":3,"desc":"Cura 30% vida ao subir nível","cura_nivel":True},
    {"nome":"Instinto Predador", "icone":"🐺","rar":3,"desc":"+80% dano +30% vel",    "dano":1.8,"vel":1.3},
]

# Evoluções épicas exclusivas de boss (não aparecem no pool normal)
EVOLUCOES_BOSS = [
    {"nome":"Coroa do Rei",      "icone":"👑","rar":3,"desc":"Todos stats +25%",      "dano":1.25,"vel":1.25,"vida":60,"def":0.80},
    {"nome":"Coração de Boss",   "icone":"💢","rar":3,"desc":"+200 vida + regen 10/s","vida":200,"regen":10},
    {"nome":"Fúria Primordial",  "icone":"⚡","rar":3,"desc":"+150% dano",            "dano":2.5},
    {"nome":"Escudo Divino",     "icone":"🛡️","rar":3,"desc":"-80% dano recebido",   "def":0.20},
    {"nome":"Omega Caranguejo",  "icone":"🦀","rar":3,"desc":"A FORMA FINAL",         "dano":2.0,"vel":1.4,"vida":150,"def":0.60},
]

# ══════════════════════════════════════════════
#  UTILITÁRIOS
# ══════════════════════════════════════════════

def dist(ax,ay,bx,by): return math.hypot(bx-ax,by-ay)

def ipcor(ca,cb,t):
    return tuple(max(0,min(255,int(ca[i]+(cb[i]-ca[i])*t))) for i in range(3))

def draw_shadow(surf,text,font,cor,x,y,sh=(0,0,0),offx=2,offy=2):
    surf.blit(font.render(text,True,sh),(x+offx,y+offy))
    surf.blit(font.render(text,True,cor),(x,y))

def draw_bar(surf,x,y,w,h,val,maximo,cor,bg=(40,40,40),radius=5):
    pygame.draw.rect(surf,bg,(x,y,w,h),border_radius=radius)
    fill=max(0,int(w*val/max(1,maximo)))
    if fill>0:
        pygame.draw.rect(surf,cor,(x,y,fill,h),border_radius=radius)
    pygame.draw.rect(surf,ipcor(cor,(255,255,255),0.3),(x,y,w,h),2,border_radius=radius)

def escolher_evo_pool(qtd=3,apenas_raras=False):
    pool=[e for e in EVOLUCOES if not apenas_raras or e["rar"]>=2]
    pesos=[{1:10,2:3,3:1}[e["rar"]] for e in pool]
    escolhidos=[]
    pool_c=list(zip(pool,pesos))
    for _ in range(min(qtd,len(pool_c))):
        total=sum(p for _,p in pool_c)
        r=random.uniform(0,total)
        acc=0
        for i,(e,p) in enumerate(pool_c):
            acc+=p
            if r<=acc:
                escolhidos.append(e)
                pool_c.pop(i)
                break
    return escolhidos


# ══════════════════════════════════════════════
#  PARTÍCULA
# ══════════════════════════════════════════════

class Particula:
    def __init__(self,x,y,cor,vel=3,vida=40,grav=0.05,raio=None):
        self.x,self.y=float(x),float(y)
        self.cor=cor
        a=random.uniform(0,2*math.pi)
        v=random.uniform(vel*0.4,vel)
        self.vx=math.cos(a)*v; self.vy=math.sin(a)*v
        self.vida=vida; self.vida_max=vida
        self.r=raio or random.randint(2,5)
        self.grav=grav
    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.vy+=self.grav; self.vida-=1
    def draw(self,surf):
        if self.vida<=0: return
        a=int(255*self.vida/self.vida_max)
        s=pygame.Surface((self.r*2,self.r*2),pygame.SRCALPHA)
        pygame.draw.circle(s,(*self.cor,a),(self.r,self.r),self.r)
        surf.blit(s,(int(self.x)-self.r,int(self.y)-self.r))
    @property
    def morta(self): return self.vida<=0


# ══════════════════════════════════════════════
#  COMIDA
# ══════════════════════════════════════════════

class Comida:
    def __init__(self,x,y,tipo="fruta"):
        self.x=float(x); self.y=float(y)
        self.tipo=tipo
        self.raio=10
        self.xp={"fruta":8,"cogumelo":16,"carne":28}[tipo]
        self.fase=random.uniform(0,2*math.pi)
    def draw(self,surf,tick):
        bob=math.sin(tick*0.07+self.fase)*3
        cx,cy=int(self.x),int(self.y+bob)
        r=self.raio
        if self.tipo=="fruta":
            pygame.draw.circle(surf,C_FRUTA,(cx,cy),r)
            pygame.draw.circle(surf,(30,160,30),(cx,cy),r,2)
            pygame.draw.line(surf,(60,120,30),(cx,cy-r),(cx+3,cy-r-6),2)
            pygame.draw.circle(surf,(180,255,150),(cx-3,cy-3),3)
        elif self.tipo=="cogumelo":
            pygame.draw.ellipse(surf,C_COGUMELO,(cx-r,cy-r,r*2,int(r*1.2)))
            pygame.draw.rect(surf,(225,205,205),(cx-4,cy,8,r-2))
            for dx2,dy2 in [(-4,-5),(3,-7),(0,-3)]:
                pygame.draw.circle(surf,(255,255,255),(cx+dx2,cy+dy2),2)
        else:
            pygame.draw.circle(surf,C_CARNE,(cx,cy),r)
            pygame.draw.circle(surf,(160,40,20),(cx,cy),r,2)
            pygame.draw.line(surf,(240,220,200),(cx-5,cy-5),(cx+5,cy+5),2)
            pygame.draw.line(surf,(240,220,200),(cx+5,cy-5),(cx-5,cy+5),2)


# ══════════════════════════════════════════════
#  ANIMAL  (NPC)
# ══════════════════════════════════════════════

class Animal:
    """Criatura do ecossistema com IA simples de perseguir/fugir."""
    def __init__(self,x,y,nivel=1):
        self.x=float(x); self.y=float(y)
        self.nivel=nivel
        self.raio=10+nivel*6
        self.vida=self.raio*5; self.vida_max=self.vida
        self.vel=random.uniform(0.7,1.5)*(1+nivel*0.12)
        self.cor=random.choice(CORES_ANIMAIS)
        self.cor2=ipcor(self.cor,(255,255,255),0.35)
        self.ang=random.uniform(0,2*math.pi)
        self.timer_dir=random.randint(30,80)
        self.vivo=True
        self.fase=random.uniform(0,2*math.pi)
        self.xp_drop=nivel*22
        self.tick_local=random.randint(0,60)
        # número de "patas" visual (1-3 pares)
        self.num_patas=random.randint(1,3)
        self.tem_cauda=random.random()<0.5
        self.tem_chifre=random.random()<0.3

    def update(self,jx,jy,jr,percepcao_bonus=1.0):
        if not self.vivo: return
        dx=jx-self.x; dy=jy-self.y; d=math.hypot(dx,dy)
        perc=180*percepcao_bonus if self.nivel<3 else 220*percepcao_bonus
        if d<perc:
            if self.raio>jr*1.1:
                self.ang=math.atan2(dy,dx)+random.uniform(-0.15,0.15)
            else:
                self.ang=math.atan2(-dy,-dx)+random.uniform(-0.25,0.25)
        else:
            self.timer_dir-=1
            if self.timer_dir<=0:
                self.ang=random.uniform(0,2*math.pi)
                self.timer_dir=random.randint(40,100)
        self.x+=math.cos(self.ang)*self.vel
        self.y+=math.sin(self.ang)*self.vel
        self.x=max(self.raio,min(LARGURA-self.raio,self.x))
        self.y=max(self.raio+55,min(ALTURA-self.raio-55,self.y))
        self.tick_local+=1

    def hit(self,dano):
        self.vida-=dano
        if self.vida<=0: self.vivo=False

    def draw(self,surf):
        if not self.vivo: return
        cx,cy=int(self.x),int(self.y); r=self.raio; t=self.tick_local

        # Cauda
        if self.tem_cauda:
            ang_c=self.ang+math.pi+math.sin(t*0.1)*0.4
            tx=cx+math.cos(ang_c)*(r+8)
            ty=cy+math.sin(ang_c)*(r+8)
            pygame.draw.line(surf,self.cor,(cx,cy),(int(tx),int(ty)),max(2,r//5))

        # Patas animadas
        for i in range(self.num_patas):
            for lado in(-1,1):
                ba=math.radians(lado*(40+i*30))
                osc=math.sin(t*0.13+i*0.9)*12*lado
                ar=self.ang+ba+math.radians(osc)
                ox=cx+lado*int(r*0.55); oy=cy+(i-self.num_patas//2)*int(r*0.4)
                fx=ox+math.cos(ar)*r*0.85; fy=oy+math.sin(ar)*r*0.85
                pygame.draw.line(surf,self.cor2,(ox,oy),(int(fx),int(fy)),max(1,r//7))

        # Corpo
        pygame.draw.ellipse(surf,self.cor,(cx-r,cy-int(r*0.75),r*2,int(r*1.5)))
        pygame.draw.ellipse(surf,self.cor2,(cx-int(r*0.55),cy-int(r*0.6),int(r*1.1),int(r*0.55)))

        # Chifre
        if self.tem_chifre:
            pygame.draw.polygon(surf,ipcor(self.cor,(255,255,200),0.5),[
                (cx,cy-r-2),(cx-4,cy-r-14),(cx+4,cy-r-14)])

        # Olhos
        for lado in(-1,1):
            ex=cx+lado*int(r*0.33); ey=cy-int(r*0.22)
            pygame.draw.circle(surf,(255,250,220),(ex,ey),max(2,r//4))
            pygame.draw.circle(surf,(15,15,15),(ex+lado,ey+1),max(1,r//8))

        # Barra de vida mini
        if self.vida<self.vida_max:
            draw_bar(surf,cx-r,cy-r-10,r*2,5,self.vida,self.vida_max,C_VIDA,(60,20,20),3)

        # Pontinhos de nível
        for i in range(self.nivel):
            pygame.draw.circle(surf,(255,210,40),(cx-(self.nivel-1)*5+i*10,cy+r+7),3)


# ══════════════════════════════════════════════
#  BOSS
# ══════════════════════════════════════════════

class Boss:
    """
    Inimigo especial enorme com múltiplas fases.
    Fase 1: persegue; Fase 2 (50% vida): fica mais rápido e dispara projéteis.
    """
    NOMES=[
        ("Kraken Ancestral",(60,80,200)),
        ("Urso-Goblin Rei",(140,80,30)),
        ("Hidra Venenosa",(60,180,60)),
        ("Leviatã do Abismo",(20,100,160)),
        ("Golem de Ossos",(200,190,160)),
    ]

    def __init__(self,index=0):
        nome_info=Boss.NOMES[index % len(Boss.NOMES)]
        self.nome=nome_info[0]
        self.cor=nome_info[1]
        self.cor2=ipcor(self.cor,(255,255,255),0.35)

        # Spawn nas bordas
        lado=random.randint(0,3)
        if lado==0: self.x,self.y=random.randint(100,LARGURA-100),80.0
        elif lado==1: self.x,self.y=random.randint(100,LARGURA-100),float(ALTURA-80)
        elif lado==2: self.x,self.y=80.0,random.randint(100,ALTURA-100)
        else: self.x,self.y=float(LARGURA-80),random.randint(100,ALTURA-100)

        self.raio=52
        self.vida_max=600+index*120
        self.vida=float(self.vida_max)
        self.vel=0.9+index*0.1
        self.dano_contato=30
        self.ang=0.0
        self.fase=1          # 1 ou 2
        self.tick=0
        self.vivo=True
        self.projéteis:list[Projetil]=[]
        self.timer_proj=0
        self.invencivel=0
        self.num_cabecas=random.randint(1,3)  # visual
        self.tem_tentaculos=random.random()<0.5

    def update(self,jx,jy):
        if not self.vivo: return
        self.tick+=1
        if self.invencivel>0: self.invencivel-=1

        # Transição de fase
        if self.fase==1 and self.vida<self.vida_max*0.5:
            self.fase=2
            self.vel*=1.5
            self.dano_contato=int(self.dano_contato*1.4)

        # Movimento em direção ao jogador (com leve ziguezague)
        dx=jx-self.x; dy=jy-self.y; d=math.hypot(dx,dy)
        if d>1:
            zigzag=math.sin(self.tick*0.06)*0.5
            self.ang=math.atan2(dy,dx)+zigzag
        self.x+=math.cos(self.ang)*self.vel
        self.y+=math.sin(self.ang)*self.vel
        self.x=max(self.raio,min(LARGURA-self.raio,self.x))
        self.y=max(self.raio+55,min(ALTURA-self.raio-55,self.y))

        # Fase 2: dispara projéteis a cada 90 frames
        if self.fase==2:
            self.timer_proj+=1
            if self.timer_proj>=90:
                self.timer_proj=0
                # Dispara em leque de 5 projéteis
                for k in range(5):
                    ang_p=math.atan2(jy-self.y,jx-self.x)+math.radians(-40+k*20)
                    self.projéteis.append(Projetil(self.x,self.y,ang_p,self.cor,7))

        # Atualiza projéteis
        for p in self.projéteis: p.update()
        self.projéteis=[p for p in self.projéteis if not p.morto]

    def hit(self,dano):
        if self.invencivel>0: return
        self.vida-=dano
        self.invencivel=8
        if self.vida<=0:
            self.vida=0; self.vivo=False

    def draw(self,surf):
        if not self.vivo: return
        cx,cy=int(self.x),int(self.y); r=self.raio; t=self.tick

        # Aura pulsante
        aura_r=r+20+int(math.sin(t*0.07)*8)
        cor_aura=self.cor2 if self.fase==1 else (255,80,20)
        s=pygame.Surface((aura_r*2,aura_r*2),pygame.SRCALPHA)
        pygame.draw.circle(s,(*cor_aura,50),(aura_r,aura_r),aura_r)
        surf.blit(s,(cx-aura_r,cy-aura_r))

        # Tentáculos (se tiver)
        if self.tem_tentaculos:
            for i in range(6):
                base_ang=i*(2*math.pi/6)+t*0.02
                for seg in range(4):
                    r1=(seg+1)*(r//4)
                    r2=(seg+2)*(r//4)
                    ondula=math.sin(t*0.08+i+seg*0.5)*20
                    a1=base_ang+math.radians(ondula)
                    a2=base_ang+math.radians(ondula+5)
                    x1=cx+math.cos(a1)*r1; y1=cy+math.sin(a1)*r1
                    x2=cx+math.cos(a2)*r2; y2=cy+math.sin(a2)*r2
                    pygame.draw.line(surf,ipcor(self.cor,(0,0,0),0.3),
                                     (int(x1),int(y1)),(int(x2),int(y2)),3)

        # Corpo principal
        cor_body=self.cor if self.fase==1 else ipcor(self.cor,(255,50,50),0.4)
        pygame.draw.circle(surf,cor_body,(cx,cy),r)
        pygame.draw.circle(surf,self.cor2,(cx,cy-r//4),int(r*0.65))

        # Múltiplas cabeças
        for i in range(self.num_cabecas):
            if self.num_cabecas==1:
                offsets=[(0,0)]
            elif self.num_cabecas==2:
                offsets=[(-r//2,-r//3),(r//2,-r//3)]
            else:
                offsets=[(0,-r//2),(-r//2,r//4),(r//2,r//4)]
            ox,oy=offsets[i]
            hcx=cx+ox; hcy=cy+oy
            hr=max(10,r//3)
            pygame.draw.circle(surf,cor_body,(hcx,hcy),hr)
            # Olhos furiosos
            for lado in(-1,1):
                ex=hcx+lado*hr//3; ey=hcy-hr//4
                pygame.draw.circle(surf,(255,50,50),(ex,ey),max(3,hr//3))
                pygame.draw.circle(surf,(0,0,0),(ex,ey),max(1,hr//6))

        # Espinhos ao redor (fase 2)
        if self.fase==2:
            for k in range(12):
                ang_s=math.radians(k*30+t*2)
                sx=cx+math.cos(ang_s)*r
                sy=cy+math.sin(ang_s)*r
                ex2=cx+math.cos(ang_s)*(r+14)
                ey2=cy+math.sin(ang_s)*(r+14)
                pygame.draw.line(surf,(255,120,20),(int(sx),int(sy)),(int(ex2),int(ey2)),3)

        # Projéteis
        for p in self.projéteis: p.draw(surf)

        # Barra de vida do boss (grande, no topo da tela)
        bx=LARGURA//2-200; by=ALTURA-45
        draw_bar(surf,bx,by,400,22,self.vida,self.vida_max,C_BOSS_HUD,(40,10,10),6)
        txt_b=_fonte_peq_global.render(f"👹 {self.nome}  ({'⚡FASE 2' if self.fase==2 else 'Fase 1'})",
                                       True,(255,160,160))
        surf.blit(txt_b,(LARGURA//2-txt_b.get_width()//2,by-18))

    def draw_projéteis(self,surf):
        for p in self.projéteis: p.draw(surf)


# ══════════════════════════════════════════════
#  PROJÉTIL (do Boss)
# ══════════════════════════════════════════════

class Projetil:
    def __init__(self,x,y,ang,cor,vel=6):
        self.x=float(x); self.y=float(y)
        self.ang=ang; self.vel=vel; self.cor=cor
        self.raio=8; self.vivo=True
        self.tick=0
    def update(self):
        self.x+=math.cos(self.ang)*self.vel
        self.y+=math.sin(self.ang)*self.vel
        self.tick+=1
        if (self.x<0 or self.x>LARGURA or self.y<0 or self.y>ALTURA
                or self.tick>200):
            self.vivo=False
    def draw(self,surf):
        if not self.vivo: return
        cx,cy=int(self.x),int(self.y)
        # trilha
        for i in range(1,4):
            trail_x=cx-int(math.cos(self.ang)*i*5)
            trail_y=cy-int(math.sin(self.ang)*i*5)
            s=pygame.Surface((self.raio*2,self.raio*2),pygame.SRCALPHA)
            pygame.draw.circle(s,(*self.cor,80-i*20),(self.raio,self.raio),self.raio-i)
            surf.blit(s,(trail_x-self.raio,trail_y-self.raio))
        pygame.draw.circle(surf,self.cor,(cx,cy),self.raio)
        pygame.draw.circle(surf,(255,255,200),(cx,cy),self.raio,2)
    @property
    def morto(self): return not self.vivo


# ══════════════════════════════════════════════
#  JOGADOR
# ══════════════════════════════════════════════

class Jogador:
    def __init__(self):
        self.x=float(LARGURA//2); self.y=float(ALTURA//2)
        self.raio=18; self.raio_base=18
        self.vida=100; self.vida_max=100
        self.vel_base=2.2
        self.dano=15
        self.nivel=1
        self.xp=0; self.xp_prox=60

        # Multiplicadores
        self.mult_vel=1.0; self.mult_dano=1.0
        self.mult_def=1.0; self.mult_xp=1.0
        self.mult_raio_col=1.0

        # Flags especiais
        self.regen_ps=0; self.regen_tick=0
        self.tem_espinhos=False; self.tem_veneno=False
        self.tem_camuflagem=False; self.tem_dash=False
        self.tem_aura_fogo=False; self.tem_aura_veneno=False
        self.mult_percepcao=1.0
        self.cura_nivel=False

        self.evos_ativas:list[dict]=[]
        self.vivo=True
        self.invencivel=0; self.atacando=0
        self.tick=0

        # Dash
        self.dash_vel=0.0; self.dash_ang=0.0; self.dash_cooldown=0

    @property
    def raio_coleta(self): return (self.raio+22)*self.mult_raio_col
    @property
    def vel(self): return self.vel_base*self.mult_vel

    def aplicar_evo(self,evo):
        self.evos_ativas.append(evo)
        if "vel"         in evo: self.mult_vel     *=evo["vel"]
        if "dano"        in evo: self.mult_dano    *=evo["dano"]
        if "def"         in evo: self.mult_def     *=evo["def"]
        if "xp_bonus"    in evo: self.mult_xp      *=evo["xp_bonus"]
        if "raio_coleta" in evo: self.mult_raio_col*=evo["raio_coleta"]
        if "regen"       in evo: self.regen_ps     +=evo["regen"]
        if "espinhos"    in evo: self.tem_espinhos  =True
        if "veneno"      in evo: self.tem_veneno    =True
        if "camuflagem"  in evo: self.tem_camuflagem=True
        if "dash"        in evo: self.tem_dash      =True
        if "aura_fogo"   in evo: self.tem_aura_fogo =True
        if "aura_veneno" in evo: self.tem_aura_veneno=True
        if "percep"      in evo: self.mult_percepcao*=evo["percep"]
        if "cura_nivel"  in evo: self.cura_nivel    =True
        if "vida" in evo:
            self.vida_max+=evo["vida"]; self.vida+=evo["vida"]
        if "tamanho" in evo:
            self.raio=int(self.raio_base*evo["tamanho"])
            self.raio_base=self.raio
        self.nivel+=1
        if self.cura_nivel:
            self.vida=min(self.vida_max,int(self.vida+self.vida_max*0.3))

    def ganhar_xp(self,qtd):
        self.xp+=int(qtd*self.mult_xp)
        if self.xp>=self.xp_prox:
            self.xp-=self.xp_prox
            self.xp_prox=int(self.xp_prox*1.32)
            return True
        return False

    def hit(self,dano):
        if self.invencivel>0: return
        d=max(1,int(dano*self.mult_def))
        self.vida-=d; self.invencivel=50
        if self.vida<=0: self.vida=0; self.vivo=False

    def update(self,teclas):
        if not self.vivo: return
        self.tick+=1
        if self.invencivel>0: self.invencivel-=1
        if self.atacando>0: self.atacando-=1
        if self.dash_cooldown>0: self.dash_cooldown-=1

        dx,dy=0,0
        if teclas[pygame.K_LEFT]  or teclas[pygame.K_a]: dx-=1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx+=1
        if teclas[pygame.K_UP]    or teclas[pygame.K_w]: dy-=1
        if teclas[pygame.K_DOWN]  or teclas[pygame.K_s]: dy+=1
        if dx!=0 and dy!=0: dx*=0.7071; dy*=0.7071

        # Dash (Shift)
        if self.tem_dash and teclas[pygame.K_LSHIFT] and self.dash_cooldown==0 and (dx or dy):
            self.dash_vel=12.0
            self.dash_ang=math.atan2(dy,dx)
            self.dash_cooldown=60
            self.invencivel=max(self.invencivel,15)

        if self.dash_vel>0:
            self.x+=math.cos(self.dash_ang)*self.dash_vel
            self.y+=math.sin(self.dash_ang)*self.dash_vel
            self.dash_vel=max(0,self.dash_vel-1.5)
        else:
            self.x+=dx*self.vel; self.y+=dy*self.vel

        self.x=max(self.raio,min(LARGURA-self.raio,self.x))
        self.y=max(self.raio+55,min(ALTURA-self.raio-55,self.y))

        # Regen
        if self.regen_ps>0:
            self.regen_tick+=1
            if self.regen_tick>=FPS:
                self.regen_tick=0
                self.vida=min(self.vida_max,self.vida+self.regen_ps)

    # ── Visual ───────────────────────────────────────────────────────
    def draw(self,surf):
        if not self.vivo: return
        if self.invencivel>0 and (self.invencivel//5)%2==0: return
        cx,cy=int(self.x),int(self.y); r=self.raio; t=self.tick
        nomes=[e["nome"] for e in self.evos_ativas]

        # Cor base
        cor=C_PLAYER
        if "Carcinização" in nomes or "Omega Caranguejo" in nomes:
            cor=(210,55,15)
        elif "Aura de Fogo" in nomes:
            cor=(220,90,20)
        elif "Ferrão Venenoso" in nomes or "Veneno em Área" in nomes:
            cor=(80,200,50)
        elif "Camuflagem" in nomes:
            cor=(70,140,55)
        elif "Instinto Predador" in nomes:
            cor=(180,30,30)
        cor2=ipcor(cor,(255,255,255),0.35)

        # ── Aura de fogo ──────────────────────────────────────────────
        if self.tem_aura_fogo:
            for i in range(3):
                ar=r+8+i*6+int(math.sin(t*0.15+i)*4)
                s=pygame.Surface((ar*2,ar*2),pygame.SRCALPHA)
                pygame.draw.circle(s,(255,100,20,30-i*8),(ar,ar),ar)
                surf.blit(s,(cx-ar,cy-ar))

        # ── Aura de veneno ────────────────────────────────────────────
        if self.tem_aura_veneno:
            av=r+15+int(math.sin(t*0.1)*5)
            s=pygame.Surface((av*2,av*2),pygame.SRCALPHA)
            pygame.draw.circle(s,(80,220,40,35),(av,av),av)
            surf.blit(s,(cx-av,cy-av))

        # ── Dash trail ────────────────────────────────────────────────
        if self.dash_vel>2:
            for i in range(1,5):
                tx=cx-int(math.cos(self.dash_ang)*i*8)
                ty=cy-int(math.sin(self.dash_ang)*i*8)
                s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
                pygame.draw.circle(s,(*cor,50-i*10),(r,r),r-i*2)
                surf.blit(s,(tx-r,ty-r))

        # ── Asas ──────────────────────────────────────────────────────
        if "Asas de Morcego" in nomes or "Propulsão" in nomes:
            bat=math.sin(t*0.2)*22
            for lado in(-1,1):
                pts=[(cx,cy-r//2),
                     (cx+lado*(r+int(bat)),cy-r-18),
                     (cx+lado*(r+10),cy+5)]
                pygame.draw.polygon(surf,(160,100,200),pts)
                pygame.draw.polygon(surf,(120,60,160),pts,2)

        # ── Patas / Pinças ────────────────────────────────────────────
        tem_patas=any(n in nomes for n in ["Patas Ágeis","Carcinização","Pernas de Saltador",
                                            "Omega Caranguejo","Pinças de Caranguejo"])
        if tem_patas:
            for i in range(3):
                for lado in(-1,1):
                    ba=math.radians(lado*(30+i*28))
                    osc=math.sin(t*0.14+i)*12*lado
                    ar=ba+math.radians(osc)+math.pi/2
                    ox=cx+lado*int(r*0.6); oy=cy+(i-1)*int(r*0.42)
                    fx=ox+math.cos(ar)*r*0.95; fy=oy+math.sin(ar)*r*0.95
                    pygame.draw.line(surf,cor2,(ox,oy),(int(fx),int(fy)),max(2,r//6))

        # ── Espinhos ──────────────────────────────────────────────────
        if self.tem_espinhos:
            for k in range(8):
                ar=math.radians(k*45+t*1.5)
                sx=cx+math.cos(ar)*r; sy=cy+math.sin(ar)*r
                ex2=cx+math.cos(ar)*(r+12); ey2=cy+math.sin(ar)*(r+12)
                pygame.draw.line(surf,(160,230,60),(int(sx),int(sy)),(int(ex2),int(ey2)),2)

        # ── Corpo ─────────────────────────────────────────────────────
        pygame.draw.circle(surf,cor,(cx,cy),r)
        # padrão orgânico
        pygame.draw.circle(surf,cor2,(cx,cy-r//4),int(r*0.62))
        # contorno
        pygame.draw.circle(surf,ipcor(cor,(0,0,0),0.25),(cx,cy),r,2)

        # ── Garras / Pinças ───────────────────────────────────────────
        tem_garras=any(n in nomes for n in ["Garras Afiadas","Pinças de Caranguejo",
                                             "Mandíbulas","Carcinização","Presas de Sabre",
                                             "Instinto Predador","Omega Caranguejo"])
        if tem_garras:
            for lado in(-1,1):
                gx=cx+lado*(r+10); gy=cy-4
                ab=int(math.sin(t*0.1)*7)*lado
                pygame.draw.circle(surf,cor,(gx,gy),r//2)
                pygame.draw.line(surf,cor2,(gx,gy-4),(gx+lado*10,gy-12-ab),max(2,r//5))
                pygame.draw.line(surf,cor2,(gx,gy+2),(gx+lado*10,gy+8+ab),max(2,r//5))

        # ── Chifre ────────────────────────────────────────────────────
        if any(n in nomes for n in ["Chifres","Presas de Sabre","Fúria Primordial"]):
            pygame.draw.polygon(surf,ipcor(cor,(255,220,100),0.4),[
                (cx,cy-r-3),(cx-5,cy-r-16),(cx+5,cy-r-16)])
            if "Chifres" in nomes:  # duplo
                for lado in(-1,1):
                    pygame.draw.polygon(surf,ipcor(cor,(255,220,100),0.4),[
                        (cx+lado*8,cy-r+2),(cx+lado*3,cy-r-12),(cx+lado*13,cy-r-12)])

        # ── Ferrão ────────────────────────────────────────────────────
        if self.tem_veneno or "Ferrão Venenoso" in nomes:
            pygame.draw.polygon(surf,(60,210,30),[
                (cx,cy-r-1),(cx-5,cy-r-15),(cx+5,cy-r-15)])

        # ── Nadadeiras ────────────────────────────────────────────────
        if "Nadadeiras" in nomes:
            for lado in(-1,1):
                ond=int(math.sin(t*0.17)*7)*lado
                pts=[(cx,cy),(cx+lado*(r+5),cy-9+ond),(cx+lado*(r+5),cy+9+ond)]
                pygame.draw.polygon(surf,cor2,pts)

        # ── Coroa (evolução de boss) ───────────────────────────────────
        if "Coroa do Rei" in nomes:
            pts=[(cx-12,cy-r-2),(cx-12,cy-r-14),(cx-6,cy-r-8),
                 (cx,cy-r-18),(cx+6,cy-r-8),(cx+12,cy-r-14),(cx+12,cy-r-2)]
            pygame.draw.polygon(surf,C_OURO,pts)
            pygame.draw.polygon(surf,(200,160,20),pts,2)

        # ── Olhos ─────────────────────────────────────────────────────
        n_olhos=3 if "Olho de Aguia" in nomes else 2
        olho_pos=[(-int(r*0.35),-int(r*0.28)),(int(r*0.35),-int(r*0.28))]
        if n_olhos==3: olho_pos.append((0,-int(r*0.5)))
        for ox2,oy2 in olho_pos:
            ex=cx+ox2; ey=cy+oy2
            pygame.draw.circle(surf,(255,250,200),(ex,ey),max(3,r//4))
            pupila_cor=(200,0,0) if "Instinto Predador" in nomes or "Fúria Primordial" in nomes else (15,15,15)
            pygame.draw.circle(surf,pupila_cor,(ex+(1 if ox2>0 else -1),ey+1),max(1,r//7))


# ══════════════════════════════════════════════
#  TELA DE EVOLUÇÃO
# ══════════════════════════════════════════════

_fonte_peq_global=None   # referência global para o Boss usar

def tela_evolucao(surf,clock,ft,fn,fp,boss_evo=False):
    """Mostra 3 cartas de evolução; retorna a escolhida."""
    global _fonte_peq_global
    opcoes=random.sample(EVOLUCOES_BOSS,min(3,len(EVOLUCOES_BOSS))) if boss_evo else escolher_evo_pool(3)
    cw,ch=230,300; gap=28
    total=cw*3+gap*2; cx_ini=(LARGURA-total)//2; cy_ini=(ALTURA-ch)//2
    sel=None; hover=-1; tick=0

    while sel is None:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_1: sel=0
                elif ev.key==pygame.K_2: sel=1
                elif ev.key==pygame.K_3: sel=2
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                mx,my=ev.pos
                for i in range(3):
                    ccx=cx_ini+i*(cw+gap)
                    if ccx<=mx<=ccx+cw and cy_ini<=my<=cy_ini+ch: sel=i

        mx,my=pygame.mouse.get_pos(); hover=-1
        for i in range(3):
            ccx=cx_ini+i*(cw+gap)
            if ccx<=mx<=ccx+cw and cy_ini<=my<=cy_ini+ch: hover=i
        tick+=1

        ov=pygame.Surface((LARGURA,ALTURA),pygame.SRCALPHA)
        ov.fill((0,0,0,190)); surf.blit(ov,(0,0))

        tit_txt="⚡ BOSS DERROTADO! Evolução Épica:" if boss_evo else "✨ EVOLUÇÃO! Escolha:"
        tit=ft.render(tit_txt,True,C_OURO if boss_evo else (255,220,70))
        surf.blit(tit,(LARGURA//2-tit.get_width()//2,cy_ini-58))
        sub=fp.render("Clique na carta ou tecle 1 / 2 / 3",True,(170,170,170))
        surf.blit(sub,(LARGURA//2-sub.get_width()//2,cy_ini-28))

        for i,evo in enumerate(opcoes):
            ccx=cx_ini+i*(cw+gap)
            is_h=(i==hover)
            cy_c=cy_ini-(14 if is_h else 0)
            rar=evo["rar"]
            cor_card=(55,45,70) if rar==3 else ((50,65,80) if rar==2 else (45,58,45))
            cor_borda=(220,170,30) if rar==3 else ((80,160,220) if rar==2 else (90,160,90))
            if is_h: cor_borda=ipcor(cor_borda,(255,255,255),0.3)

            pygame.draw.rect(surf,cor_card,(ccx,cy_c,cw,ch),border_radius=16)
            pygame.draw.rect(surf,cor_borda,(ccx,cy_c,cw,ch),3,border_radius=16)

            # Raridade
            rar_label=["","⚪ Comum","🔵 Rara","🟣 Épica"][rar]
            rt=fp.render(rar_label,True,cor_borda)
            surf.blit(rt,(ccx+cw//2-rt.get_width()//2,cy_c+8))

            # Número
            nt=ft.render(str(i+1),True,(180,180,180))
            surf.blit(nt,(ccx+10,cy_c+8))

            # Ícone
            ico=ft.render(evo["icone"],True,(255,255,255))
            surf.blit(ico,(ccx+cw//2-ico.get_width()//2,cy_c+38))

            # Nome
            nmt=fn.render(evo["nome"],True,(255,228,90))
            surf.blit(nmt,(ccx+cw//2-nmt.get_width()//2,cy_c+110))

            pygame.draw.line(surf,cor_borda,(ccx+12,cy_c+138),(ccx+cw-12,cy_c+138),1)

            # Descrição
            dt=fp.render(evo["desc"],True,(195,210,220))
            surf.blit(dt,(ccx+cw//2-dt.get_width()//2,cy_c+148))

            # Bônus listados
            yb=cy_c+175
            for chv,lbl,corf in [("vel","⚡Vel",(220,220,80)),("dano","⚔️Dano",(220,100,80)),
                                   ("vida","❤️Vida",(220,80,80)),("def","🛡️Def",(80,180,220)),
                                   ("regen","💚Regen",(80,210,110))]:
                if chv in evo:
                    v=evo[chv]
                    st=f"{lbl} {'x'+str(v) if isinstance(v,float) else '+'+str(v)}"
                    bt=fp.render(st,True,corf)
                    surf.blit(bt,(ccx+cw//2-bt.get_width()//2,yb)); yb+=18

        pygame.display.flip(); clock.tick(FPS)
    if sel is not None and sel<len(opcoes): return opcoes[sel]
    return opcoes[0]


# ══════════════════════════════════════════════
#  FUNDO DO MAPA
# ══════════════════════════════════════════════

_fundo_surf=None

def criar_fundo():
    """Gera a superfície de fundo uma única vez (desempenho)."""
    global _fundo_surf
    _fundo_surf=pygame.Surface((LARGURA,ALTURA))
    _fundo_surf.fill(C_FUNDO)
    rng=random.Random(2024)
    # Manchas de grama
    for _ in range(80):
        mx=rng.randint(0,LARGURA); my=rng.randint(55,ALTURA-55)
        mr=rng.randint(25,80)
        s=pygame.Surface((mr*2,mr*2),pygame.SRCALPHA)
        c=C_GRAMA_A if rng.random()<0.5 else C_GRAMA_B
        pygame.draw.ellipse(s,(*c,110),(0,0,mr*2,mr*2))
        _fundo_surf.blit(s,(mx-mr,my-mr))
    # Pedras
    for _ in range(30):
        px=rng.randint(20,LARGURA-20); py=rng.randint(80,ALTURA-80)
        pr=rng.randint(4,10)
        pygame.draw.circle(_fundo_surf,(85,78,68),(px,py),pr)
    # Flores decorativas
    for _ in range(40):
        fx=rng.randint(20,LARGURA-20); fy=rng.randint(80,ALTURA-80)
        for k in range(5):
            ar=math.radians(k*72)
            px2=int(fx+math.cos(ar)*5); py2=int(fy+math.sin(ar)*5)
            cor_f=rng.choice([(220,200,50),(200,80,180),(255,150,50)])
            pygame.draw.circle(_fundo_surf,cor_f,(px2,py2),3)
        pygame.draw.circle(_fundo_surf,(255,240,100),(fx,fy),2)

def desenhar_fundo(surf):
    if _fundo_surf: surf.blit(_fundo_surf,(0,0))


# ══════════════════════════════════════════════
#  HUD
# ══════════════════════════════════════════════

def desenhar_hud(surf,fn,fp,j,tempo_rest,boss_ativo):
    # Vida
    draw_bar(surf,15,12,210,19,j.vida,j.vida_max,C_VIDA,(40,15,15))
    surf.blit(fp.render(f"❤️ {int(j.vida)}/{j.vida_max}",True,C_TEXTO),(20,14))
    # XP
    draw_bar(surf,15,35,210,12,j.xp,j.xp_prox,C_XP,(25,40,25))
    surf.blit(fp.render(f"XP {j.xp}/{j.xp_prox}",True,C_TEXTO),(20,36))
    # Nível
    surf.blit(fn.render(f"Nível {j.nivel}",True,C_OURO),(232,12))
    # Timer
    m=int(tempo_rest)//60; s=int(tempo_rest)%60
    cc=C_AVISO if tempo_rest<30 else C_TEXTO
    tt=fn.render(f"⏱ {m}:{s:02d}",True,cc)
    surf.blit(tt,(LARGURA//2-tt.get_width()//2,12))
    # Dash cooldown
    if j.tem_dash:
        dc=max(0,j.dash_cooldown/60)
        clr=(150,150,150) if dc>0 else (100,220,255)
        dt=fp.render(f"DASH {'...' if dc>0 else 'PRONTO'} [Shift]",True,clr)
        surf.blit(dt,(LARGURA//2-dt.get_width()//2,34))
    # Evoluções (direita)
    ex=LARGURA-12; ey=12
    surf.blit(fp.render("Evoluções:",True,(160,160,160)),(ex-fp.size("Evoluções:")[0],ey)); ey+=16
    for evo in j.evos_ativas[-10:]:
        rar=evo["rar"]
        cc2=[(180,180,180),(80,160,220),(180,80,220)][rar-1]
        te=fp.render(f"{evo['icone']} {evo['nome']}",True,cc2)
        surf.blit(te,(ex-te.get_width(),ey)); ey+=15
    # Dica
    dica="WASD/Setas → mover" + ("  |  Shift → Dash" if j.tem_dash else "")
    surf.blit(fp.render(dica,True,(100,120,90)),(LARGURA//2-fp.size(dica)[0]//2,ALTURA-16))


# ══════════════════════════════════════════════
#  TELA FIM
# ══════════════════════════════════════════════

def tela_fim(surf,clock,ft,fn,fp,ganhou,nivel,elapsed,bosses_mortos):
    tick=0
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return
            if ev.type in(pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN): return
        tick+=1
        surf.fill((8,5,3) if not ganhou else (12,25,8))
        msg="🏆 VOCÊ SOBREVIVEU! 🏆" if ganhou else "💀  VOCÊ FOI DEVORADO...  💀"
        mc=(90,220,90) if ganhou else (220,70,50)
        draw_shadow(surf,msg,ft,mc,LARGURA//2-ft.size(msg)[0]//2,ALTURA//2-90)
        for i,(linha,cor3) in enumerate([
            (f"Nível atingido: {nivel}",(255,220,100)),
            (f"Tempo: {int(elapsed)}s",(200,200,200)),
            (f"Bosses derrotados: {bosses_mortos}",(200,100,220)),
        ]):
            t=fn.render(linha,True,cor3)
            surf.blit(t,(LARGURA//2-t.get_width()//2,ALTURA//2+i*36))
        h=fp.render("[ Qualquer tecla para sair ]",True,(120,120,120))
        surf.blit(h,(LARGURA//2-h.get_width()//2,ALTURA//2+130))
        pygame.display.flip(); clock.tick(FPS)


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════

def main():
    global _fonte_peq_global
    pygame.init()
    surf=pygame.display.set_mode((LARGURA,ALTURA))
    pygame.display.set_caption("Everything is Crab 🦀")
    clock=pygame.time.Clock()

    try:
        ft=pygame.font.SysFont("segoeuiemoji",27,bold=True)
        fn=pygame.font.SysFont("segoeuiemoji",20)
        fp=pygame.font.SysFont("segoeuiemoji",15)
    except Exception:
        ft=pygame.font.SysFont(None,29,bold=True)
        fn=pygame.font.SysFont(None,22)
        fp=pygame.font.SysFont(None,16)
    _fonte_peq_global=fp

    criar_fundo()

    # Entidades
    jogador=Jogador()
    particulas:list[Particula]=[]

    comidas:list[Comida]=[]
    for _ in range(22):
        tipo=random.choices(["fruta","cogumelo"],[70,30])[0]
        comidas.append(Comida(random.randint(30,LARGURA-30),random.randint(80,ALTURA-80),tipo))

    animais:list[Animal]=[]
    for _ in range(14):
        n=random.choices([1,2,3],[60,30,10])[0]
        animais.append(Animal(random.randint(50,LARGURA-50),random.randint(80,ALTURA-80),n))

    boss:Boss|None=None
    boss_index=0
    bosses_mortos=0
    timer_boss=FPS*60      # primeiro boss após 60s
    boss_aviso=0           # contagem para mostrar aviso antes do boss

    tick=0
    inicio=pygame.time.get_ticks()
    t_comida=0; t_animal=0
    rodando=True

    while rodando:
        elapsed=(pygame.time.get_ticks()-inicio)/1000
        tempo_rest=max(0,DURACAO_RUN-elapsed)

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: rodando=False
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: rodando=False

        teclas=pygame.key.get_pressed()
        jogador.update(teclas)

        # Atualiza animais
        for a in animais:
            a.update(jogador.x,jogador.y,jogador.raio,jogador.mult_percepcao)

        # Atualiza boss
        if boss and boss.vivo:
            boss.update(jogador.x,jogador.y)

        # ── Coleta de comida ──────────────────────────────────────────
        coletadas=[]
        for c in comidas:
            if dist(jogador.x,jogador.y,c.x,c.y)<jogador.raio_coleta:
                subiu=jogador.ganhar_xp(c.xp)
                for _ in range(8):
                    cc2=C_FRUTA if c.tipo=="fruta" else C_COGUMELO if c.tipo=="cogumelo" else C_CARNE
                    particulas.append(Particula(c.x,c.y,cc2,2.5))
                coletadas.append(c)
                if subiu:
                    evo=tela_evolucao(surf,clock,ft,fn,fp)
                    jogador.aplicar_evo(evo)
                    for _ in range(25): particulas.append(Particula(jogador.x,jogador.y,C_OURO,4))
        comidas=[c for c in comidas if c not in coletadas]

        # ── Combate jogador × animais ─────────────────────────────────
        for a in animais:
            if not a.vivo: continue
            d=dist(jogador.x,jogador.y,a.x,a.y)
            if d<jogador.raio+a.raio-4:
                if jogador.raio>=a.raio*0.88 and jogador.atacando==0:
                    dj=int(jogador.dano*jogador.mult_dano)
                    a.hit(dj); jogador.atacando=18
                    for _ in range(6): particulas.append(Particula(a.x,a.y,a.cor,3))
                    if not a.vivo:
                        comidas.append(Comida(a.x,a.y,"carne"))
                        subiu=jogador.ganhar_xp(a.xp_drop)
                        for _ in range(18): particulas.append(Particula(a.x,a.y,a.cor,4))
                        if subiu:
                            evo=tela_evolucao(surf,clock,ft,fn,fp)
                            jogador.aplicar_evo(evo)
                elif a.raio>jogador.raio*1.08:
                    jogador.hit(a.nivel*7)
                    for _ in range(5): particulas.append(Particula(jogador.x,jogador.y,(255,60,60),3))
                    if jogador.tem_espinhos: a.hit(int(a.nivel*7*0.25))

            # Aura de fogo: dano em área
            if jogador.tem_aura_fogo and d<jogador.raio+a.raio+30:
                a.hit(1)   # dano leve contínuo

            # Aura de veneno
            if jogador.tem_aura_veneno and d<jogador.raio+a.raio+45:
                a.hit(0.5)

        animais=[a for a in animais if a.vivo]

        # ── Combate jogador × boss ────────────────────────────────────
        if boss and boss.vivo:
            db=dist(jogador.x,jogador.y,boss.x,boss.y)
            if db<jogador.raio+boss.raio-5:
                if jogador.atacando==0:
                    dj=int(jogador.dano*jogador.mult_dano*1.2)
                    boss.hit(dj); jogador.atacando=15
                    for _ in range(8): particulas.append(Particula(boss.x,boss.y,boss.cor,3.5))
                jogador.hit(boss.dano_contato)
                for _ in range(5): particulas.append(Particula(jogador.x,jogador.y,(255,50,50),3))

            # Projéteis do boss
            for p in boss.projéteis:
                if dist(jogador.x,jogador.y,p.x,p.y)<jogador.raio+p.raio:
                    jogador.hit(18); p.vivo=False
                    for _ in range(6): particulas.append(Particula(jogador.x,jogador.y,(255,100,20),3))

            if not boss.vivo:
                bosses_mortos+=1
                for _ in range(40): particulas.append(Particula(boss.x,boss.y,boss.cor,5,60))
                for _ in range(10): comidas.append(Comida(
                    boss.x+random.randint(-40,40),
                    boss.y+random.randint(-40,40),"carne"))
                evo=tela_evolucao(surf,clock,ft,fn,fp,boss_evo=True)
                jogador.aplicar_evo(evo)
                boss=None

        # ── Timer de boss ─────────────────────────────────────────────
        if boss is None:
            timer_boss-=1
            if timer_boss<=FPS*5: boss_aviso=1    # aviso 5s antes
            if timer_boss<=0:
                boss=Boss(boss_index); boss_index+=1
                timer_boss=FPS*60; boss_aviso=0    # próximo boss em 60s

        # ── Spawns periódicos ─────────────────────────────────────────
        t_comida+=1
        if t_comida>180 and len(comidas)<28:
            t_comida=0
            tipo=random.choices(["fruta","cogumelo"],[72,28])[0]
            comidas.append(Comida(random.randint(30,LARGURA-30),random.randint(80,ALTURA-80),tipo))

        t_animal+=1
        intervalo=max(100,280-jogador.nivel*14)
        if t_animal>intervalo and len(animais)<20:
            t_animal=0
            max_n=min(5,1+int(elapsed/25))
            n=random.randint(1,max_n)
            lado=random.randint(0,3)
            if lado==0: ax2,ay2=random.randint(0,LARGURA),60
            elif lado==1: ax2,ay2=random.randint(0,LARGURA),ALTURA-60
            elif lado==2: ax2,ay2=20,random.randint(60,ALTURA-60)
            else: ax2,ay2=LARGURA-20,random.randint(60,ALTURA-60)
            animais.append(Animal(ax2,ay2,n))

        # Partículas
        for p in particulas: p.update()
        particulas=[p for p in particulas if not p.morta]

        # Fim de jogo
        if not jogador.vivo:
            tela_fim(surf,clock,ft,fn,fp,False,jogador.nivel,elapsed,bosses_mortos)
            rodando=False; continue
        if tempo_rest<=0:
            tela_fim(surf,clock,ft,fn,fp,True,jogador.nivel,elapsed,bosses_mortos)
            rodando=False; continue

        # ── DESENHO ───────────────────────────────────────────────────
        desenhar_fundo(surf)

        for c in comidas: c.draw(surf,tick)
        for a in animais: a.draw(surf)
        for p in particulas: p.draw(surf)
        jogador.draw(surf)
        if boss and boss.vivo: boss.draw(surf)

        desenhar_hud(surf,fn,fp,jogador,tempo_rest,boss is not None and boss.vivo)

        # Aviso de boss chegando
        if boss_aviso and (tick//20)%2==0:
            av=fn.render("⚠️ BOSS CHEGANDO! ⚠️",True,C_AVISO)
            surf.blit(av,(LARGURA//2-av.get_width()//2,55))

        # Aviso de perigo (animal grande perto)
        if not boss:
            for a in animais:
                if a.raio>jogador.raio*1.2 and dist(jogador.x,jogador.y,a.x,a.y)<170:
                    if (tick//12)%2==0:
                        av2=fn.render("⚠️ PERIGO! FUJA!",True,C_AVISO)
                        surf.blit(av2,(LARGURA//2-av2.get_width()//2,55))
                    break

        pygame.display.flip()
        clock.tick(FPS)
        tick+=1

    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()