"""
╔══════════════════════════════════════════════════════════════════╗
║     🦀  EVERYTHING IS CRAB  — SIMPLIFIED EDITION  🦀            ║
║     Roguelite Twin-Stick Shooter com Parry e Efeitos Visuais    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pygame
import random
import math
import sys
from enum import Enum

# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════════
LARGURA = 1280
ALTURA = 720
FPS = 60
DURACAO_RUN = 600

# Cores (todas com valores 0-255)
class Colors:
    BG = (15, 20, 25)
    BG_DARK = (10, 12, 18)
    PLAYER = (70, 150, 230)
    PLAYER_CRAB = (210, 70, 40)
    ENEMY = (200, 50, 50)
    ENEMY_BOSS = (100, 30, 150)
    BULLET = (255, 220, 80)
    MEAT = (180, 50, 40)
    XP = (100, 255, 100)
    HP = (255, 80, 80)
    GOLD = (255, 215, 0)
    DASH_TRAIL = (100, 200, 255)
    TEXT = (240, 240, 240)
    PARRY = (80, 200, 255)
    CHAIN_LIGHTNING = (100, 200, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    SHADOW = (0, 0, 0, 80)


# ═══════════════════════════════════════════════════════════════════
# UPGRADES
# ═══════════════════════════════════════════════════════════════════

LEVEL_UPGRADES = [
    {"nome": "🔫 Dano +", "desc": "+20% de dano", "dano": 1.2, "icone": "⚔️", "rar": 1},
    {"nome": "🔫 Dano ++", "desc": "+40% de dano", "dano": 1.4, "icone": "⚔️", "rar": 2},
    {"nome": "🔫 Dano +++", "desc": "+60% de dano", "dano": 1.6, "icone": "⚔️", "rar": 3},
    {"nome": "📈 Cadência +", "desc": "Taxa de tiro +30%", "fire_rate": 0.7, "icone": "⚡", "rar": 2},
    {"nome": "📈 Cadência ++", "desc": "Taxa de tiro +60%", "fire_rate": 0.5, "icone": "⚡", "rar": 3},
    {"nome": "🎯 Precisão", "desc": "Projéteis +30% mais rápido", "bullet_speed": 1.3, "icone": "🎯", "rar": 2},
    {"nome": "💥 Impacto", "desc": "Projéteis +50% maiores", "bullet_size": 1.5, "icone": "💥", "rar": 2},
    {"nome": "🦵 Velocidade +", "desc": "+25% velocidade", "speed": 1.25, "icone": "🏃", "rar": 1},
    {"nome": "🦵 Velocidade ++", "desc": "+50% velocidade", "speed": 1.5, "icone": "🏃", "rar": 2},
    {"nome": "💨 Dash +", "desc": "Dash -30% de cooldown", "dash_cooldown": 0.7, "icone": "💨", "rar": 2},
    {"nome": "❤️ Vida +", "desc": "+25 de vida máxima", "max_hp": 25, "icone": "❤️", "rar": 1},
    {"nome": "🛡️ Defesa +", "desc": "-15% dano recebido", "defense": 0.85, "icone": "🛡️", "rar": 2},
    {"nome": "💚 Regeneração", "desc": "+3 vida/segundo", "regen": 3, "icone": "💚", "rar": 2},
    {"nome": "💰 Ganância", "desc": "+30% XP e moedas", "xp_bonus": 1.3, "coin_bonus": 1.3, "icone": "💰", "rar": 2},
    {"nome": "💢 Raiva", "desc": "+30% dano por 10s ao tomar dano", "rage": True, "icone": "💢", "rar": 3},
    {"nome": "❄️ Congelante", "desc": "Tiros reduzem velocidade inimiga", "freeze": True, "icone": "❄️", "rar": 3},
    {"nome": "⚡ Elétrico", "desc": "Dano em cadeia (com efeito visual de raio)", "chain": True, "icone": "⚡", "rar": 3},
]

BOSS_UPGRADES = [
    {"nome": "🩸 Vampirismo", "desc": "30% do dano vira vida", "efeito": "vampirismo"},
    {"nome": "⚡ Raio Duplo", "desc": "Dispara 2 projéteis", "efeito": "double_shot"},
    {"nome": "💥 Explosão", "desc": "Projéteis explodem", "efeito": "explosive"},
    {"nome": "🌀 Ricochete", "desc": "Projéteis ricocheteiam", "efeito": "ricochet"},
    {"nome": "⚙️ Metralhadora", "desc": "Taxa de tiro +100%", "efeito": "fast_shoot"},
    {"nome": "🔫 Penetração", "desc": "Atravessa inimigos", "efeito": "pierce"},
    {"nome": "🛡️ Escudo", "desc": "Escudo que absorve dano", "efeito": "shield"},
    {"nome": "🐚 Carcinização", "desc": "Vira caranguejo lendário", "efeito": "crab"},
]


# ═══════════════════════════════════════════════════════════════════
# EFEITO DE RAIO (Chain Lightning)
# ═══════════════════════════════════════════════════════════════════

class LightningEffect:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.life = 10
        self.segments = []
        
        dx = end_x - start_x
        dy = end_y - start_y
        dist = math.hypot(dx, dy)
        steps = int(dist / 10) + 3
        
        prev_x, prev_y = start_x, start_y
        for i in range(steps):
            t = i / steps
            x = start_x + dx * t
            y = start_y + dy * t
            if 0 < t < 1:
                x += random.uniform(-15, 15)
                y += random.uniform(-15, 15)
            self.segments.append((x, y))
            
    def update(self):
        self.life -= 1
        
    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(255 * self.life / 10)
        for i in range(len(self.segments) - 1):
            # Desenha raio principal
            pygame.draw.line(surf, (100, 200, 255, alpha), 
                           (int(self.segments[i][0]), int(self.segments[i][1])),
                           (int(self.segments[i+1][0]), int(self.segments[i+1][1])), 3)
            # Efeito de brilho
            pygame.draw.line(surf, (255, 255, 255, alpha//2),
                           (int(self.segments[i][0]), int(self.segments[i][1])),
                           (int(self.segments[i+1][0]), int(self.segments[i+1][1])), 1)
                           
    @property
    def is_alive(self):
        return self.life > 0


# ═══════════════════════════════════════════════════════════════════
# EFEITO DE PARRY
# ═══════════════════════════════════════════════════════════════════

class ParryEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 15
        self.size = 30
        
    def update(self):
        self.life -= 1
        self.size += 3
        
    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(200 * self.life / 15)
        for i in range(3):
            size = self.size - i * 5
            if size > 0:
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (80, 200, 255, alpha - i*30), (size, size), size)
                surf.blit(s, (int(self.x)-size, int(self.y)-size))
                
        for angle in range(0, 360, 45):
            rad = math.radians(angle + self.life * 10)
            ex = self.x + math.cos(rad) * self.size
            ey = self.y + math.sin(rad) * self.size
            pygame.draw.line(surf, (80, 200, 255), (int(self.x), int(self.y)), (int(ex), int(ey)), 3)
                
    @property
    def is_alive(self):
        return self.life > 0


# ═══════════════════════════════════════════════════════════════════
# PROJÉTIL
# ═══════════════════════════════════════════════════════════════════

class Bullet:
    def __init__(self, x, y, angle, damage, speed=15, size=6, color=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = damage
        self.speed = speed
        self.size = size
        self.color = color if color else (255, 220, 80)
        self.life = 120
        self.trail = []
        self.parried = False

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

    def draw(self, surf):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = 100 - i * 20
            size = self.size - i
            if size > 0:
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha), (size, size), size)
                surf.blit(s, (int(tx)-size, int(ty)-size))
                
        color = (80, 200, 255) if self.parried else self.color
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), self.size//2)

    @property
    def is_alive(self):
        return self.life > 0 and 0 < self.x < LARGURA and 0 < self.y < ALTURA

    @property
    def rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


# ═══════════════════════════════════════════════════════════════════
# PROJÉTIL INIMIGO
# ═══════════════════════════════════════════════════════════════════

class EnemyBullet:
    def __init__(self, x, y, angle, damage):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = damage
        self.speed = 7
        self.size = 6
        self.life = 90

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(surf, (200, 50, 200), (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(surf, (255, 100, 255), (int(self.x), int(self.y)), self.size//2)

    @property
    def is_alive(self):
        return self.life > 0 and 0 < self.x < LARGURA and 0 < self.y < ALTURA

    @property
    def rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


# ═══════════════════════════════════════════════════════════════════
# PARTÍCULA
# ═══════════════════════════════════════════════════════════════════

class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.vx, self.vy = velocity
        self.color = color
        self.size = random.randint(2, 5)
        self.life = random.randint(15, 30)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(255 * self.life / self.max_life)
        size = int(self.size * self.life / self.max_life)
        if size > 0:
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha), (size, size), size)
            surf.blit(s, (int(self.x)-size, int(self.y)-size))

    @property
    def is_alive(self):
        return self.life > 0


# ═══════════════════════════════════════════════════════════════════
# INIMIGO (único tipo: rápido e fraco)
# ═══════════════════════════════════════════════════════════════════

class Enemy:
    def __init__(self, x, y, size=20):
        self.x = x
        self.y = y
        self.size = size
        self.max_health = int(size * 2.5)
        self.health = self.max_health
        self.speed = 2.8
        self.damage = int(size / 4)
        self.xp_value = int(size * 1.2)
        self.coin_value = random.randint(5, 15)
        self.color = (200, 50, 50)
        
        self.angle = random.uniform(0, math.pi * 2)
        self.animation_phase = random.uniform(0, math.pi * 2)
        self.knockback = 0
        self.knockback_angle = 0
        self.frozen_timer = 0

    def update(self, player_x, player_y):
        speed_mult = 0.5 if self.frozen_timer > 0 else 1.0

        if self.frozen_timer > 0:
            self.frozen_timer -= 1

        if self.knockback > 0:
            self.x += math.cos(self.knockback_angle) * 10
            self.y += math.sin(self.knockback_angle) * 10
            self.knockback -= 1
        else:
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.angle = math.atan2(dy, dx)
                self.x += math.cos(self.angle) * self.speed * speed_mult
                self.y += math.sin(self.angle) * self.speed * speed_mult

        margin = self.size + 20
        self.x = max(margin, min(LARGURA - margin, self.x))
        self.y = max(margin + 40, min(ALTURA - margin - 40, self.y))
        self.animation_phase += 0.1

    def take_damage(self, damage, has_freeze=False):
        self.health -= damage
        self.knockback = 8
        if has_freeze:
            self.frozen_timer = 60
        return self.health <= 0

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        size = self.size

        if self.frozen_timer > 0:
            ice_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(ice_surf, (100, 200, 255, 80), (size, size), size)
            surf.blit(ice_surf, (x - size, y - size))

        shadow_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (size//2, size, size, size//2))
        surf.blit(shadow_surf, (x - size, y - size//2))

        body_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        
        for i in range(size, 0, -2):
            alpha = int(200 * (1 - i / size))
            c = (min(255, self.color[0] + i//2), min(255, self.color[1] + i//3), min(255, self.color[2] + i//4))
            pygame.draw.circle(body_surf, (c[0], c[1], c[2], alpha), (size, size), i)

        eye_offset_x = math.cos(self.angle) * size//4
        eye_offset_y = math.sin(self.angle) * size//4

        pygame.draw.circle(body_surf, (255, 255, 255), (int(size*0.65), int(size*0.35)), size//5)
        pygame.draw.circle(body_surf, (255, 255, 255), (int(size*1.35), int(size*0.35)), size//5)
        pygame.draw.circle(body_surf, (0, 0, 0), (int(size*0.65 + eye_offset_x/2), int(size*0.38 + eye_offset_y/2)), size//8)
        pygame.draw.circle(body_surf, (0, 0, 0), (int(size*1.35 + eye_offset_x/2), int(size*0.38 + eye_offset_y/2)), size//8)

        surf.blit(body_surf, (x - size, y - size))

        bar_width = size * 2
        bar_height = 5
        health_percent = self.health / self.max_health
        pygame.draw.rect(surf, (40, 40, 40), (x - size, y - size - 8, bar_width, bar_height), border_radius=2)
        pygame.draw.rect(surf, (255, 80, 80), (x - size, y - size - 8, bar_width * health_percent, bar_height), border_radius=2)

    @property
    def rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


# ═══════════════════════════════════════════════════════════════════
# BOSS
# ═══════════════════════════════════════════════════════════════════

class Boss(Enemy):
    def __init__(self, x, y, wave):
        super().__init__(x, y, 60 + wave * 5)
        self.is_boss = True
        self.wave = wave
        self.max_health = int(self.size * 8)
        self.health = self.max_health
        self.xp_value = 300 + wave * 50
        self.coin_value = 100 + wave * 20
        self.speed = 1.5
        self.color = (100, 30, 150)
        self.attack_cooldown = 0
        self.attack_pattern = 0
        self.projectiles = []

    def update(self, player_x, player_y):
        super().update(player_x, player_y)

        if self.attack_cooldown <= 0:
            self.attack_pattern = (self.attack_pattern + 1) % 3
            self.shoot_pattern(player_x, player_y)
            self.attack_cooldown = 90
        else:
            self.attack_cooldown -= 1

        for p in self.projectiles[:]:
            p.update()
            if not p.is_alive:
                self.projectiles.remove(p)

    def shoot_pattern(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)

        if self.attack_pattern == 0:
            for i in range(-2, 3):
                bullet = Bullet(self.x, self.y, angle + i * 0.15, self.damage, speed=8, size=8, color=(200, 50, 200))
                self.projectiles.append(bullet)
        elif self.attack_pattern == 1:
            for i in range(8):
                spiral_angle = angle + (i * math.pi * 2 / 8) + self.attack_cooldown * 0.1
                bullet = Bullet(self.x, self.y, spiral_angle, self.damage // 2, speed=6, size=6, color=(200, 100, 200))
                self.projectiles.append(bullet)
        else:
            for i in range(3):
                bullet = Bullet(self.x, self.y, angle + random.uniform(-0.3, 0.3), self.damage * 1.5, speed=10, size=10, color=(255, 100, 255))
                self.projectiles.append(bullet)

    def draw(self, surf):
        super().draw(surf)

        for p in self.projectiles:
            p.draw(surf)

        font = pygame.font.Font(None, 28)
        boss_name = font.render(f"⚠️ BOSS - Wave {self.wave} ⚠️", True, (255, 215, 0))
        x, y = int(self.x), int(self.y)
        surf.blit(boss_name, (x - boss_name.get_width()//2, y - self.size - 35))

        bar_w = LARGURA - 200
        bar_h = 20
        health_percent = self.health / self.max_health
        pygame.draw.rect(surf, (40, 40, 40), (100, 30, bar_w, bar_h), border_radius=10)
        pygame.draw.rect(surf, (255, 80, 80), (100, 30, bar_w * health_percent, bar_h), border_radius=10)

        health_text = font.render(f"{int(self.health)}/{int(self.max_health)}", True, (240, 240, 240))
        surf.blit(health_text, (LARGURA//2 - health_text.get_width()//2, 32))


# ═══════════════════════════════════════════════════════════════════
# CARNE (DROP)
# ═══════════════════════════════════════════════════════════════════

class MeatDrop:
    def __init__(self, x, y, xp_value, coin_value):
        self.x = x
        self.y = y
        self.xp_value = xp_value
        self.coin_value = coin_value
        self.size = 8 + min(15, xp_value // 10)
        self.float_offset = random.uniform(0, math.pi * 2)
        self.life = 300

    def update(self):
        self.life -= 1

    def draw(self, surf, tick):
        if self.life < 60 and (tick // 6) % 2 == 0:
            return

        float_y = self.y + math.sin(tick * 0.05 + self.float_offset) * 3
        x, y = int(self.x), int(float_y)

        pygame.draw.ellipse(surf, (0, 0, 0, 60), (x - self.size, y + self.size//2, self.size*2, self.size//2))

        meat_surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(meat_surf, (180, 50, 40), (0, self.size//2, self.size*2, self.size))
        pygame.draw.ellipse(meat_surf, (140, 30, 20), (self.size//2, self.size//2, self.size, self.size//2))

        surf.blit(meat_surf, (x - self.size, y - self.size))

        font = pygame.font.Font(None, 12)
        xp_text = font.render(f"+{self.xp_value} XP", True, (100, 255, 100))
        coin_text = font.render(f"+{self.coin_value}💰", True, (255, 215, 0))
        surf.blit(xp_text, (x - xp_text.get_width()//2, y - self.size - 10))
        surf.blit(coin_text, (x - coin_text.get_width()//2, y + self.size + 2))

    @property
    def is_alive(self):
        return self.life > 0

    @property
    def rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


# ═══════════════════════════════════════════════════════════════════
# JOGADOR
# ═══════════════════════════════════════════════════════════════════

class Player:
    def __init__(self):
        self.x = LARGURA // 2
        self.y = ALTURA // 2
        self.size = 18
        self.health = 100
        self.max_health = 100
        self.base_speed = 4.5
        self.speed = self.base_speed
        self.damage = 20
        self.fire_rate = 8
        self.fire_timer = 0
        self.bullets = []

        # Dash
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_velocity = 0
        self.dash_angle = 0
        self.dash_cooldown_max = 40

        # Parry
        self.parry_timer = 0
        self.parry_cooldown = 0
        self.parry_duration = 8

        # Upgrades
        self.vampirism = False
        self.double_shot = False
        self.explosive = False
        self.ricochet = False
        self.fast_shoot = False
        self.pierce = False
        self.shield = 0
        self.is_crab = False

        self.defense_mult = 1.0
        self.regen_rate = 0
        self.regen_timer = 0
        self.xp_mult = 1.0
        self.coin_mult = 1.0
        self.bullet_speed_mult = 1.0
        self.bullet_size_mult = 1.0
        self.collect_mult = 1.0

        self.has_rage = False
        self.has_freeze = False
        self.has_chain = False
        self.level_upgrades = []

        self.rage_timer = 0
        self.rage_damage_mult = 1.0

        self.level = 1
        self.xp = 0
        self.xp_to_next = 60
        self.coins = 0
        self.invincible_timer = 0
        self.animation_phase = 0

        self.combo = 0
        self.combo_timer = 0
        self.max_combo = 0

        self.alive = True
        self.boss_upgrades = []

        self.stats = {
            "kills": 0,
            "boss_kills": 0,
            "deaths": 0,
            "coins_collected": 0,
            "damage_dealt": 0,
            "damage_taken": 0
        }

    def update(self, keys, mouse_pos, mouse_buttons):
        if not self.alive:
            return

        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        # Movimento
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

        # Dash
        if keys[pygame.K_LSHIFT] and self.dash_cooldown == 0 and self.dash_duration == 0:
            self.dash_duration = 12
            self.dash_cooldown = self.dash_cooldown_max
            self.invincible_timer = 15
            dash_power = 18 * (1 + (self.speed - self.base_speed) / self.base_speed)
            self.dash_velocity = dash_power
            self.dash_angle = math.atan2(dy, dx) if (dx != 0 or dy != 0) else 0

        if self.dash_duration > 0:
            self.x += math.cos(self.dash_angle) * self.dash_velocity
            self.y += math.sin(self.dash_angle) * self.dash_velocity
            self.dash_duration -= 1
            if self.dash_duration == 0:
                self.dash_velocity = 0
        else:
            self.x += dx * self.speed
            self.y += dy * self.speed

        # Parry
        if mouse_buttons[2] and self.parry_cooldown == 0 and self.parry_timer == 0:
            self.parry_timer = self.parry_duration
            self.parry_cooldown = 30
            self.invincible_timer = self.parry_duration

        if self.parry_timer > 0:
            self.parry_timer -= 1
        if self.parry_cooldown > 0:
            self.parry_cooldown -= 1

        # Limites
        margin = self.size + 20
        self.x = max(margin, min(LARGURA - margin, self.x))
        self.y = max(margin + 40, min(ALTURA - margin - 40, self.y))

        # Atirar
        if mouse_buttons[0] and self.fire_timer <= 0:
            fire_delay = self.fire_rate
            if self.fast_shoot:
                fire_delay = self.fire_rate // 2

            mx, my = mouse_pos
            angle = math.atan2(my - self.y, mx - self.x)

            bullet_speed = 15 * self.bullet_speed_mult
            bullet_size = int(6 * self.bullet_size_mult)
            damage = self.damage * self.rage_damage_mult

            if self.double_shot:
                self.bullets.append(Bullet(self.x, self.y, angle + 0.1, damage, speed=bullet_speed, size=bullet_size))
                self.bullets.append(Bullet(self.x, self.y, angle - 0.1, damage, speed=bullet_speed, size=bullet_size))
            else:
                self.bullets.append(Bullet(self.x, self.y, angle, damage, speed=bullet_speed, size=bullet_size))

            self.fire_timer = fire_delay

        if self.fire_timer > 0:
            self.fire_timer -= 1

        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.is_alive:
                self.bullets.remove(bullet)

        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        if self.regen_rate > 0:
            self.regen_timer += 1
            if self.regen_timer >= 60:
                self.regen_timer = 0
                self.health = min(self.max_health, self.health + self.regen_rate)

        if self.rage_timer > 0:
            self.rage_timer -= 1
            if self.rage_timer <= 0:
                self.rage_damage_mult = 1.0

        self.animation_phase += 0.1

    def apply_level_upgrade(self, upgrade):
        self.level_upgrades.append(upgrade)

        if "dano" in upgrade:
            self.damage = int(self.damage * upgrade["dano"])
        if "speed" in upgrade:
            self.speed = self.base_speed * upgrade["speed"]
        if "max_hp" in upgrade:
            self.max_health += upgrade["max_hp"]
            self.health += upgrade["max_hp"]
            self.health = min(self.health, self.max_health)
        if "defense" in upgrade:
            self.defense_mult *= upgrade["defense"]
        if "regen" in upgrade:
            self.regen_rate += upgrade["regen"]
        if "fire_rate" in upgrade:
            self.fire_rate = int(self.fire_rate * upgrade["fire_rate"])
            self.fire_rate = max(3, self.fire_rate)
        if "xp_bonus" in upgrade:
            self.xp_mult *= upgrade["xp_bonus"]
        if "coin_bonus" in upgrade:
            self.coin_mult *= upgrade["coin_bonus"]
        if "bullet_speed" in upgrade:
            self.bullet_speed_mult *= upgrade["bullet_speed"]
        if "bullet_size" in upgrade:
            self.bullet_size_mult *= upgrade["bullet_size"]
        if "collect_radius" in upgrade:
            self.collect_mult *= upgrade["collect_radius"]
        if "dash_cooldown" in upgrade:
            self.dash_cooldown_max = int(40 * upgrade["dash_cooldown"])
        if upgrade.get("rage"):
            self.has_rage = True
        if upgrade.get("freeze"):
            self.has_freeze = True
        if upgrade.get("chain"):
            self.has_chain = True

    def gain_xp(self, amount):
        self.xp += int(amount * self.xp_mult)
        if self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.xp_to_next = int(self.xp_to_next * 1.3)
            self.level += 1
            return True
        return False

    def gain_coins(self, amount):
        coins_gained = int(amount * self.coin_mult)
        self.coins += coins_gained
        self.stats["coins_collected"] += coins_gained
        return coins_gained

    def add_combo(self):
        self.combo += 1
        self.combo_timer = 120
        if self.combo > self.max_combo:
            self.max_combo = self.combo

    def take_damage(self, damage):
        if self.invincible_timer > 0 or self.parry_timer > 0:
            return False

        if self.has_rage and damage > 0:
            self.rage_timer = 600
            self.rage_damage_mult = 1.3

        if self.shield > 0:
            absorbed = min(self.shield, damage)
            self.shield -= absorbed
            damage -= absorbed
            if damage <= 0:
                self.invincible_timer = 20
                return False

        damage = int(damage * self.defense_mult)
        self.health -= damage
        self.stats["damage_taken"] += damage
        self.invincible_timer = 40
        self.combo = 0

        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.stats["deaths"] += 1
        return True

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def add_boss_upgrade(self, upgrade):
        self.boss_upgrades.append(upgrade)
        efeito = upgrade["efeito"]

        if efeito == "vampirism":
            self.vampirism = True
        elif efeito == "double_shot":
            self.double_shot = True
        elif efeito == "explosive":
            self.explosive = True
        elif efeito == "ricochet":
            self.ricochet = True
        elif efeito == "fast_shoot":
            self.fast_shoot = True
        elif efeito == "pierce":
            self.pierce = True
        elif efeito == "shield":
            self.shield = 50
        elif efeito == "crab":
            self.is_crab = True
            self.damage = int(self.damage * 1.5)
            self.speed *= 1.2
            self.max_health += 50
            self.health += 50

    def draw(self, surf):
        if not self.alive:
            return

        if self.invincible_timer > 0 and (self.invincible_timer // 3) % 2 == 0:
            return

        x, y = int(self.x), int(self.y)
        size = self.size
        color = (210, 70, 40) if self.is_crab else (70, 150, 230)

        # Efeito de parry
        if self.parry_timer > 0:
            parry_size = size + 20
            parry_surf = pygame.Surface((parry_size*2, parry_size*2), pygame.SRCALPHA)
            alpha = 150 - int(math.sin(self.animation_phase * 20) * 50)
            pygame.draw.circle(parry_surf, (80, 200, 255, alpha), (parry_size, parry_size), parry_size)
            surf.blit(parry_surf, (x - parry_size, y - parry_size))

        # Trail do dash
        if self.dash_duration > 0:
            for i in range(1, 5):
                trail_x = x - int(math.cos(self.dash_angle) * i * 15)
                trail_y = y - int(math.sin(self.dash_angle) * i * 15)
                s = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(s, (100, 200, 255, 150), (size//2, size//2), size//2)
                surf.blit(s, (trail_x - size//2, trail_y - size//2))

        if self.shield > 0:
            shield_radius = size + 8
            shield_surf = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            alpha = 100 + int(math.sin(self.animation_phase * 10) * 30)
            pygame.draw.circle(shield_surf, (100, 150, 255, alpha), (shield_radius, shield_radius), shield_radius, 3)
            surf.blit(shield_surf, (x - shield_radius, y - shield_radius))

        if self.rage_timer > 0:
            rage_size = size + 12
            rage_surf = pygame.Surface((rage_size*2, rage_size*2), pygame.SRCALPHA)
            alpha = 80 + int(math.sin(self.animation_phase * 20) * 40)
            pygame.draw.circle(rage_surf, (255, 50, 50, alpha), (rage_size, rage_size), rage_size)
            surf.blit(rage_surf, (x - rage_size, y - rage_size))

        pygame.draw.ellipse(surf, (0, 0, 0, 80), (x - size, y + size//2, size*2, size//2))

        body_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)

        for i in range(size, 0, -2):
            alpha = int(200 * (1 - i / size))
            c = (min(255, color[0] + i//2), min(255, color[1] + i//3), min(255, color[2] + i//2))
            pygame.draw.circle(body_surf, (c[0], c[1], c[2], alpha), (size, size), i)

        mx, my = pygame.mouse.get_pos()
        dx = mx - x
        dy = my - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist

        eye_offset_x = dx * size//4
        eye_offset_y = dy * size//4

        pygame.draw.circle(body_surf, (255, 255, 255), (int(size*0.65), int(size*0.35)), size//5)
        pygame.draw.circle(body_surf, (255, 255, 255), (int(size*1.35), int(size*0.35)), size//5)
        pygame.draw.circle(body_surf, (0, 0, 0), (int(size*0.65 + eye_offset_x), int(size*0.38 + eye_offset_y)), size//8)
        pygame.draw.circle(body_surf, (0, 0, 0), (int(size*1.35 + eye_offset_x), int(size*0.38 + eye_offset_y)), size//8)

        weapon_angle = math.atan2(my - y, mx - x)
        weapon_x = size + math.cos(weapon_angle) * size
        weapon_y = size + math.sin(weapon_angle) * size
        pygame.draw.line(body_surf, (100, 100, 150), (size, size), (weapon_x, weapon_y), 4)
        pygame.draw.circle(body_surf, (150, 150, 200), (int(weapon_x), int(weapon_y)), 4)

        if self.is_crab:
            pygame.draw.polygon(body_surf, (200, 80, 50), [(size, size//4), (size - 10, size//4 - 15), (size + 10, size//4 - 15)])

        surf.blit(body_surf, (x - size, y - size))

        if self.shield > 0:
            shield_percent = self.shield / 50
            bar_w = size * 2
            pygame.draw.rect(surf, (40, 40, 40), (x - size, y - size - 20, bar_w, 4), border_radius=2)
            pygame.draw.rect(surf, (100, 150, 255), (x - size, y - size - 20, bar_w * shield_percent, 4), border_radius=2)

        bar_width = size * 2
        health_percent = self.health / self.max_health
        pygame.draw.rect(surf, (40, 40, 40), (x - size, y - size - 10, bar_width, 6), border_radius=3)
        pygame.draw.rect(surf, (255, 80, 80), (x - size, y - size - 10, bar_width * health_percent, 6), border_radius=3)

        xp_percent = self.xp / self.xp_to_next
        pygame.draw.rect(surf, (40, 40, 40), (x - size, y - size - 17, bar_width, 4), border_radius=2)
        pygame.draw.rect(surf, (100, 255, 100), (x - size, y - size - 17, bar_width * xp_percent, 4), border_radius=2)

        font = pygame.font.Font(None, 18)
        level_text = font.render(str(self.level), True, (255, 215, 0))
        surf.blit(level_text, (x + size - 15, y - size - 20))

        if self.combo > 0:
            combo_text = font.render(f"COMBO x{self.combo}", True, (255, 215, 0))
            surf.blit(combo_text, (x - combo_text.get_width()//2, y - size - 35))

        # Indicador de parry cooldown
        if self.parry_cooldown > 0:
            cd_percent = self.parry_cooldown / 30
            cd_x = x - size - 5
            cd_y = y
            pygame.draw.arc(surf, (80, 80, 80), (cd_x, cd_y, 15, 15), 0, math.pi * 2, 2)
            pygame.draw.arc(surf, (80, 200, 255), (cd_x, cd_y, 15, 15), 0, math.pi * 2 * (1 - cd_percent), 2)

    @property
    def rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

    @property
    def collect_radius(self):
        return self.size + 20 * self.collect_mult


# ═══════════════════════════════════════════════════════════════════
# TELAS
# ═══════════════════════════════════════════════════════════════════

def level_upgrade_screen(screen, clock):
    font_title = pygame.font.Font(None, 48)
    font_name = pygame.font.Font(None, 28)
    font_desc = pygame.font.Font(None, 20)
    font_small = pygame.font.Font(None, 16)

    def get_weighted_upgrades():
        pool = []
        for up in LEVEL_UPGRADES:
            weight = {1: 10, 2: 4, 3: 1}[up.get("rar", 1)]
            pool.extend([up] * weight)
        return random.sample(pool, min(3, len(pool)))

    options = get_weighted_upgrades()
    selected = None
    hover_index = -1
    tick = 0

    card_w, card_h = 280, 240
    gap = 30
    total_w = card_w * 3 + gap * 2
    start_x = (LARGURA - total_w) // 2
    start_y = (ALTURA - card_h) // 2

    while selected is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected = 0
                elif event.key == pygame.K_2:
                    selected = 1
                elif event.key == pygame.K_3:
                    selected = 2
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i in range(3):
                    cx = start_x + i * (card_w + gap)
                    if cx <= mx <= cx + card_w and start_y <= my <= start_y + card_h:
                        selected = i

        mx, my = pygame.mouse.get_pos()
        hover_index = -1
        for i in range(3):
            cx = start_x + i * (card_w + gap)
            if cx <= mx <= cx + card_w and start_y <= my <= start_y + card_h:
                hover_index = i

        tick += 1

        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(180 + int(math.sin(tick * 0.05) * 20))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_y = start_y - 70 + math.sin(tick * 0.05) * 3
        title = font_title.render("✨ NIVEL UP! ESCOLHA SEU UPGRADE ✨", True, (255, 215, 0))
        screen.blit(title, (LARGURA//2 - title.get_width()//2, title_y))

        for i, upgrade in enumerate(options):
            cx = start_x + i * (card_w + gap)
            cy = start_y - (10 if i == hover_index else 0)

            rar = upgrade.get("rar", 1)
            if rar == 3:
                bg_color = (80, 40, 100)
                border_color = (255, 215, 0)
            elif rar == 2:
                bg_color = (60, 50, 90)
                border_color = (100, 150, 255)
            else:
                bg_color = (50, 55, 70)
                border_color = (150, 150, 150)

            pygame.draw.rect(screen, bg_color, (cx, cy, card_w, card_h), border_radius=12)
            pygame.draw.rect(screen, border_color, (cx, cy, card_w, card_h), 3, border_radius=12)

            icon = font_title.render(upgrade["icone"], True, (255, 255, 255))
            screen.blit(icon, (cx + card_w//2 - icon.get_width()//2, cy + 25))

            name = font_name.render(upgrade["nome"], True, border_color)
            screen.blit(name, (cx + card_w//2 - name.get_width()//2, cy + 80))

            pygame.draw.line(screen, border_color, (cx + 20, cy + 105), (cx + card_w - 20, cy + 105), 1)

            desc = font_desc.render(upgrade["desc"], True, (200, 200, 200))
            screen.blit(desc, (cx + card_w//2 - desc.get_width()//2, cy + 120))

            num_text = font_name.render(str(i+1), True, (100, 100, 120))
            screen.blit(num_text, (cx + 12, cy + 10))

        tip = font_small.render("Pressione 1, 2, 3 ou clique para escolher", True, (120, 120, 120))
        screen.blit(tip, (LARGURA//2 - tip.get_width()//2, start_y + card_h + 20))

        pygame.display.flip()
        clock.tick(60)

    return options[selected]


def boss_upgrade_screen(screen, clock):
    font_title = pygame.font.Font(None, 48)
    font_name = pygame.font.Font(None, 32)
    font_desc = pygame.font.Font(None, 24)

    options = random.sample(BOSS_UPGRADES, min(3, len(BOSS_UPGRADES)))
    selected = None
    hover_index = -1

    card_w, card_h = 300, 200
    gap = 40
    total_w = card_w * 3 + gap * 2
    start_x = (LARGURA - total_w) // 2
    start_y = (ALTURA - card_h) // 2

    while selected is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected = 0
                elif event.key == pygame.K_2:
                    selected = 1
                elif event.key == pygame.K_3:
                    selected = 2
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i in range(3):
                    cx = start_x + i * (card_w + gap)
                    if cx <= mx <= cx + card_w and start_y <= my <= start_y + card_h:
                        selected = i

        mx, my = pygame.mouse.get_pos()
        hover_index = -1
        for i in range(3):
            cx = start_x + i * (card_w + gap)
            if cx <= mx <= cx + card_w and start_y <= my <= start_y + card_h:
                hover_index = i

        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = font_title.render("✨ UPGRADE ÉPICO DO BOSS! ✨", True, (255, 215, 0))
        screen.blit(title, (LARGURA//2 - title.get_width()//2, start_y - 60))

        for i, upgrade in enumerate(options):
            cx = start_x + i * (card_w + gap)
            cy = start_y - (10 if i == hover_index else 0)

            pygame.draw.rect(screen, (40, 30, 60), (cx, cy, card_w, card_h), border_radius=12)
            pygame.draw.rect(screen, (255, 215, 0), (cx, cy, card_w, card_h), 3, border_radius=12)

            icon = font_title.render(upgrade["nome"][0], True, (255, 215, 0))
            screen.blit(icon, (cx + 20, cy + 20))

            name = font_name.render(upgrade["nome"], True, (255, 215, 0))
            screen.blit(name, (cx + card_w//2 - name.get_width()//2, cy + 30))

            desc = font_desc.render(upgrade["desc"], True, (200, 200, 200))
            screen.blit(desc, (cx + card_w//2 - desc.get_width()//2, cy + 80))

            num = font_title.render(str(i+1), True, (100, 100, 100))
            screen.blit(num, (cx + card_w - 30, cy + 10))

        pygame.display.flip()
        clock.tick(60)

    return options[selected]


def shop_screen(screen, clock, player):
    font_title = pygame.font.Font(None, 48)
    font_name = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 16)

    upgrades = [
        {"nome": "❤️ Vida +20", "desc": "Aumenta vida máxima", "custo": 100, "level": 0, "max": 5,
         "efeito": lambda p: setattr(p, 'max_health', p.max_health + 20) or setattr(p, 'health', p.health + 20)},
        {"nome": "⚔️ Dano +10%", "desc": "Aumenta dano", "custo": 150, "level": 0, "max": 5,
         "efeito": lambda p: setattr(p, 'damage', int(p.damage * 1.1))},
        {"nome": "🏃 Velocidade +10%", "desc": "Aumenta velocidade", "custo": 120, "level": 0, "max": 5,
         "efeito": lambda p: setattr(p, 'speed', p.speed * 1.1) or setattr(p, 'base_speed', p.base_speed * 1.1)},
        {"nome": "💰 Moedas +20%", "desc": "Aumenta ganho de moedas", "custo": 180, "level": 0, "max": 3,
         "efeito": lambda p: setattr(p, 'coin_mult', p.coin_mult * 1.2)},
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, up in enumerate(upgrades):
                    x = 100 + (i % 2) * 350
                    y = 200 + (i // 2) * 120
                    if x <= mx <= x + 300 and y <= my <= y + 80:
                        if up["level"] < up["max"] and player.coins >= up["custo"]:
                            player.coins -= up["custo"]
                            up["level"] += 1
                            up["efeito"](player)
                            up["custo"] = int(up["custo"] * 1.5)

        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = font_title.render("🛒 LOJA DE UPGRADES PERMANENTES", True, (255, 215, 0))
        screen.blit(title, (LARGURA//2 - title.get_width()//2, 50))

        coins_text = font_name.render(f"💰 MOEDAS: {player.coins}", True, (255, 215, 0))
        screen.blit(coins_text, (LARGURA//2 - coins_text.get_width()//2, 120))

        for i, up in enumerate(upgrades):
            x = 150 + (i % 2) * 400
            y = 200 + (i // 2) * 100

            can_buy = up["level"] < up["max"] and player.coins >= up["custo"]
            bg_color = (50, 70, 90) if can_buy else (40, 40, 50)
            border_color = (255, 215, 0) if can_buy else (100, 100, 100)

            pygame.draw.rect(screen, bg_color, (x, y, 380, 80), border_radius=10)
            pygame.draw.rect(screen, border_color, (x, y, 380, 80), 2, border_radius=10)

            name = font_name.render(up["nome"], True, (255, 215, 0))
            screen.blit(name, (x + 15, y + 10))

            desc = font_small.render(up["desc"], True, (200, 200, 200))
            screen.blit(desc, (x + 15, y + 40))

            level_text = font_small.render(f"Nv:{up['level']}/{up['max']}", True, (150, 150, 150))
            screen.blit(level_text, (x + 300, y + 15))

            cost_text = font_small.render(f"{up['custo']}💰", True, (255, 215, 0) if can_buy else (150, 100, 100))
            screen.blit(cost_text, (x + 300, y + 45))

        tip = font_small.render("Clique nos upgrades para comprar | ESC para sair", True, (120, 120, 120))
        screen.blit(tip, (LARGURA//2 - tip.get_width()//2, ALTURA - 40))

        pygame.display.flip()
        clock.tick(60)


def stats_screen(screen, clock, player):
    font_title = pygame.font.Font(None, 48)
    font_name = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = font_title.render("📊 ESTATÍSTICAS DA PARTIDA", True, (255, 215, 0))
        screen.blit(title, (LARGURA//2 - title.get_width()//2, 50))

        y = 150
        stats = [
            f"🎯 Nível: {player.level}",
            f"💀 Inimigos mortos: {player.stats['kills']}",
            f"👑 Bosses mortos: {player.stats['boss_kills']}",
            f"💰 Moedas: {player.coins}",
            f"✨ Maior Combo: {player.max_combo}",
            f"💪 Upgrades de nível: {len(player.level_upgrades)}",
            f"👑 Upgrades de boss: {len(player.boss_upgrades)}",
        ]

        for stat in stats:
            text = font_name.render(stat, True, (200, 200, 200))
            screen.blit(text, (LARGURA//2 - text.get_width()//2, y))
            y += 40

        tip = font_small.render("Pressione ESC para voltar", True, (120, 120, 120))
        screen.blit(tip, (LARGURA//2 - tip.get_width()//2, ALTURA - 50))

        pygame.display.flip()
        clock.tick(60)


def draw_minimap(surf, player, enemies, meat_drops):
    minimap_size = 150
    minimap_x = LARGURA - minimap_size - 10
    minimap_y = ALTURA - minimap_size - 10

    minimap_surf = pygame.Surface((minimap_size, minimap_size))
    minimap_surf.set_alpha(200)
    minimap_surf.fill((20, 20, 30))
    pygame.draw.rect(minimap_surf, (255, 215, 0), (0, 0, minimap_size, minimap_size), 2)

    def world_to_minimap(x, y):
        return int((x / LARGURA) * minimap_size), int((y / ALTURA) * minimap_size)

    for meat in meat_drops:
        mx, my = world_to_minimap(meat.x, meat.y)
        pygame.draw.circle(minimap_surf, (255, 215, 0), (mx, my), 2)

    for enemy in enemies:
        mx, my = world_to_minimap(enemy.x, enemy.y)
        if hasattr(enemy, 'is_boss') and enemy.is_boss:
            pygame.draw.circle(minimap_surf, (255, 50, 50), (mx, my), 5)
        else:
            pygame.draw.circle(minimap_surf, (255, 80, 80), (mx, my), 2)

    mx, my = world_to_minimap(player.x, player.y)
    pygame.draw.circle(minimap_surf, (70, 150, 230), (mx, my), 4)
    pygame.draw.circle(minimap_surf, (255, 215, 0), (mx, my), 4, 1)

    surf.blit(minimap_surf, (minimap_x, minimap_y))


# ═══════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Everything is Crab - Simplified Edition 🦀")
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(True)

    player = Player()
    enemies = []
    meat_drops = []
    particles = []
    lightning_effects = []
    parry_effects = []
    enemy_bullets = []

    wave = 1
    enemies_to_spawn = 10
    boss_spawned = False

    # Spawn inicial
    for _ in range(enemies_to_spawn):
        x = random.randint(50, LARGURA - 50)
        y = random.randint(80, ALTURA - 80)
        size = random.randint(15, 30)
        enemies.append(Enemy(x, y, size))

    # Fundo
    background = pygame.Surface((LARGURA, ALTURA))
    for y in range(ALTURA):
        t = y / ALTURA
        color = (int(15 * (1 - t) + 10 * t),
                 int(20 * (1 - t) + 12 * t),
                 int(25 * (1 - t) + 18 * t))
        pygame.draw.line(background, color, (0, y), (LARGURA, y))

    stars = [(random.randint(0, LARGURA), random.randint(0, ALTURA//2), random.randint(100, 255)) for _ in range(100)]

    fonts = {
        'large': pygame.font.Font(None, 48),
        'medium': pygame.font.Font(None, 32),
        'small': pygame.font.Font(None, 20),
        'tiny': pygame.font.Font(None, 14)
    }

    running = True
    start_time = pygame.time.get_ticks()
    tick = 0
    show_shop = False
    show_stats = False

    while running:
        delta = clock.tick(FPS)
        current_time = (pygame.time.get_ticks() - start_time) / 1000
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_TAB:
                    show_shop = not show_shop
                if event.key == pygame.K_q:
                    show_stats = not show_stats

        if show_shop:
            shop_screen(screen, clock, player)
            show_shop = False
            continue

        if show_stats:
            stats_screen(screen, clock, player)
            show_stats = False
            continue

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        player.update(keys, mouse_pos, mouse_buttons)

        # Atualizar inimigos
        for enemy in enemies[:]:
            enemy.update(player.x, player.y)

            if player.rect.colliderect(enemy.rect):
                player.take_damage(enemy.damage)

            for bullet in player.bullets[:]:
                if bullet.rect.colliderect(enemy.rect):
                    has_freeze = player.has_freeze
                    if enemy.take_damage(bullet.damage, has_freeze):
                        player.stats["kills"] += 1
                        player.stats["damage_dealt"] += bullet.damage
                        player.add_combo()

                        meat_drops.append(MeatDrop(enemy.x, enemy.y, enemy.xp_value, enemy.coin_value))

                        for _ in range(15):
                            angle = random.uniform(0, math.pi * 2)
                            speed = random.uniform(2, 5)
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            particles.append(Particle(enemy.x, enemy.y, enemy.color, (vx, vy)))

                        enemies.remove(enemy)

                        if player.vampirism:
                            player.heal(bullet.damage // 4)

                        if player.has_chain:
                            closest = None
                            min_dist = 150
                            for other in enemies:
                                dist = math.hypot(other.x - enemy.x, other.y - enemy.y)
                                if 0 < dist < min_dist:
                                    min_dist = dist
                                    closest = other
                            if closest:
                                closest.take_damage(bullet.damage // 2, has_freeze)
                                lightning_effects.append(LightningEffect(enemy.x, enemy.y, closest.x, closest.y))
                    else:
                        if player.ricochet:
                            if bullet.x < 0 or bullet.x > LARGURA or bullet.y < 0 or bullet.y > ALTURA:
                                bullet.angle = math.atan2(-math.sin(bullet.angle), -math.cos(bullet.angle))

                    if not player.pierce:
                        player.bullets.remove(bullet)
                        break

        # Parry
        if player.parry_timer > 0:
            parry_effects.append(ParryEffect(player.x, player.y))
            for bullet in enemy_bullets[:]:
                if math.hypot(bullet.x - player.x, bullet.y - player.y) < player.size + 20:
                    angle = math.atan2(bullet.y - player.y, bullet.x - player.x)
                    player.bullets.append(Bullet(player.x, player.y, angle, bullet.damage * 2, speed=15, size=8, color=(80, 200, 255)))
                    enemy_bullets.remove(bullet)

        for bullet in enemy_bullets[:]:
            bullet.update()
            if bullet.rect.colliderect(player.rect):
                player.take_damage(bullet.damage)
                enemy_bullets.remove(bullet)
            elif not bullet.is_alive:
                enemy_bullets.remove(bullet)

        for bullet in player.bullets[:]:
            bullet.update()
            if not bullet.is_alive:
                player.bullets.remove(bullet)

        for p in particles[:]:
            p.update()
            if not p.is_alive:
                particles.remove(p)

        for l in lightning_effects[:]:
            l.update()
            if not l.is_alive:
                lightning_effects.remove(l)

        for p in parry_effects[:]:
            p.update()
            if not p.is_alive:
                parry_effects.remove(p)

        for meat in meat_drops[:]:
            meat.update()
            if player.rect.colliderect(meat.rect):
                if player.gain_xp(meat.xp_value):
                    upgrade = level_upgrade_screen(screen, clock)
                    player.apply_level_upgrade(upgrade)
                player.gain_coins(meat.coin_value)
                meat_drops.remove(meat)
            elif not meat.is_alive:
                meat_drops.remove(meat)

        # Waves
        if len(enemies) == 0 and not boss_spawned:
            if wave % 10 == 0:
                boss_spawned = True
                x = random.randint(100, LARGURA - 100)
                y = random.randint(100, ALTURA - 100)
                enemies.append(Boss(x, y, wave))
            else:
                wave += 1
                enemies_to_spawn = min(25, 10 + wave // 3)
                for _ in range(enemies_to_spawn):
                    x = random.randint(50, LARGURA - 50)
                    y = random.randint(80, ALTURA - 80)
                    size = random.randint(15, 25 + wave // 10)
                    enemies.append(Enemy(x, y, size))

        if boss_spawned and len([e for e in enemies if hasattr(e, 'is_boss') and e.is_boss]) == 0:
            upgrade = boss_upgrade_screen(screen, clock)
            player.add_boss_upgrade(upgrade)
            player.stats["boss_kills"] += 1
            boss_spawned = False
            wave += 1
            meat_drops.append(MeatDrop(player.x, player.y, 200, 150))

        # Game over
        if not player.alive or current_time >= DURACAO_RUN:
            screen.fill((0, 0, 0))
            if current_time >= DURACAO_RUN:
                text = fonts['large'].render("🏆 VICTORY! 🏆", True, (255, 215, 0))
            else:
                text = fonts['large'].render("💀 GAME OVER 💀", True, (255, 80, 80))
            screen.blit(text, (LARGURA//2 - text.get_width()//2, ALTURA//2 - 150))

            y_offset = ALTURA//2 - 50
            stats_lines = [
                f"Wave: {wave} | Nível: {player.level}",
                f"💀 Inimigos: {player.stats['kills']} | 👑 Bosses: {player.stats['boss_kills']}",
                f"💰 Moedas: {player.coins} | ✨ Combo max: {player.max_combo}",
            ]

            for line in stats_lines:
                text = fonts['medium'].render(line, True, (255, 215, 0))
                screen.blit(text, (LARGURA//2 - text.get_width()//2, y_offset))
                y_offset += 40

            text = fonts['tiny'].render("ESC para sair | TAB para loja", True, (150, 150, 150))
            screen.blit(text, (LARGURA//2 - text.get_width()//2, ALTURA - 50))

            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            waiting = False
                            running = False
                        if event.key == pygame.K_TAB:
                            shop_screen(screen, clock, player)
                clock.tick(30)
            continue

        # Desenhar
        screen.blit(background, (0, 0))

        for sx, sy, brightness in stars:
            pygame.draw.circle(screen, (brightness, brightness, brightness), (sx, sy), 1)

        for meat in meat_drops:
            meat.draw(screen, tick)

        for enemy in enemies:
            enemy.draw(screen)

        for bullet in enemy_bullets:
            bullet.draw(screen)

        for bullet in player.bullets:
            bullet.draw(screen)

        for p in particles:
            p.draw(screen)

        for l in lightning_effects:
            l.draw(screen)

        for p in parry_effects:
            p.draw(screen)

        player.draw(screen)

        draw_minimap(screen, player, enemies, meat_drops)

        # HUD
        time_left = max(0, DURACAO_RUN - current_time)
        minutes = int(time_left) // 60
        seconds = int(time_left) % 60
        timer_text = fonts['medium'].render(f"⏱ {minutes:02d}:{seconds:02d}", True, (255, 215, 0))
        screen.blit(timer_text, (LARGURA - timer_text.get_width() - 10, 10))

        wave_text = fonts['medium'].render(f"🌊 Wave {wave}", True, (100, 255, 100))
        screen.blit(wave_text, (10, 10))

        coins_text = fonts['small'].render(f"💰 {player.coins}", True, (255, 215, 0))
        screen.blit(coins_text, (10, 45))

        combo_text = fonts['small'].render(f"✨ Combo x{player.combo}", True, (100, 255, 100) if player.combo > 0 else (100, 100, 100))
        screen.blit(combo_text, (10, 65))

        enemies_left = len(enemies)
        enemy_text = fonts['small'].render(f"👾 Inimigos: {enemies_left}", True, (150, 150, 150))
        screen.blit(enemy_text, (10, 85))

        parry_text = fonts['tiny'].render("PARRY", True, (80, 200, 255) if player.parry_cooldown == 0 else (100, 100, 100))
        screen.blit(parry_text, (10, 110))

        tip = "WASD → Mover | Mouse → Mirar | Clique Esquerdo → Atirar | Clique Direito → PARRY | Shift → Dash"
        tip_text = fonts['tiny'].render(tip, True, (100, 100, 100))
        screen.blit(tip_text, (LARGURA//2 - tip_text.get_width()//2, ALTURA - 15))

        mx, my = mouse_pos
        pygame.draw.circle(screen, (255, 255, 255), (mx, my), 8, 2)
        pygame.draw.line(screen, (255, 255, 255), (mx - 15, my), (mx - 5, my), 2)
        pygame.draw.line(screen, (255, 255, 255), (mx + 5, my), (mx + 15, my), 2)
        pygame.draw.line(screen, (255, 255, 255), (mx, my - 15), (mx, my - 5), 2)
        pygame.draw.line(screen, (255, 255, 255), (mx, my + 5), (mx, my + 15), 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()