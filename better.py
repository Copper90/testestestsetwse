import pygame, sys, math, random

class TextInput:
    def __init__(self, x, y, w, h, val, mn, mx):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(val)
        self.active, self.mn, self.mx, self.val = False, mn, mx, val

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            if not self.active: self.submit()
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.active = False
                self.submit()
            elif event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif event.unicode in "0123456789.": self.text += event.unicode

    def submit(self):
        try: self.val = max(self.mn, min(float(self.text), self.mx))
        except: self.val = self.mn
        self.text = str(self.val)

    def set_val(self, nv):
        self.val = max(self.mn, min(nv, self.mx))
        if not self.active: self.text = f"{self.val:.2f}".rstrip('0').rstrip('.')

    def draw(self, surf, font):
        bg = (52, 73, 94) if self.active else (44, 62, 80)
        pygame.draw.rect(surf, bg, self.rect, border_radius=4)
        pygame.draw.rect(surf, (127, 140, 141), self.rect, 1, border_radius=4)
        txt = font.render(self.text + ("|" if self.active else ""), True, (236, 240, 241))
        surf.blit(txt, (self.rect.x + 6, self.rect.y + (self.rect.h - txt.get_height()) // 2))

class Slider:
    def __init__(self, x, y, w, mn, mx, val):
        self.rect = pygame.Rect(x, y, w, 6)
        self.mn, self.mx, self.val, self.r, self.drag = mn, mx, val, 8, False
        self.set_val(val)

    def update(self, event):
        mx, my = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if math.hypot(mx - self.hx, my - (self.rect.y + 3)) <= self.r + 4: self.drag = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: self.drag = False
        if self.drag:
            self.hx = max(self.rect.left, min(mx, self.rect.right))
            self.val = self.mn + ((self.hx - self.rect.left) / self.rect.width) * (self.mx - self.mn)

    def set_val(self, nv):
        self.val = max(self.mn, min(nv, self.mx))
        self.hx = self.rect.left + int(((self.val - self.mn) / (self.mx - self.mn)) * self.rect.width)

    def draw(self, surf):
        pygame.draw.rect(surf, (44, 62, 80), self.rect, border_radius=3)
        pygame.draw.circle(surf, (241, 196, 15), (self.hx, self.rect.y + 3), self.r)

class Switch:
    def __init__(self, x, y, w=44, h=22, state=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_on, self.r = state, h // 2

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.is_on = not self.is_on

    def draw(self, surf):
        bg = (39, 174, 96) if self.is_on else (44, 62, 80)
        pygame.draw.rect(surf, bg, self.rect, border_radius=self.r)
        kx = self.rect.right - self.r if self.is_on else self.rect.left + self.r
        pygame.draw.circle(surf, (236, 240, 241), (kx, self.rect.centery), self.r - 2)

class Speedometer:
    def __init__(self, x, y, mx=15.0):
        self.x, self.y, self.mx, self.r = x, y, mx, 45

    def draw(self, surf, spd, font):
        pygame.draw.arc(surf, (44, 62, 80), (self.x, self.y, self.r * 2, self.r * 2), math.pi, 0, 6)
        pct = min(1.0, spd / self.mx)
        ang = math.pi - (pct * math.pi)
        if pct > 0.01:
            c = (int(52 + pct * 179), int(152 - pct * 26), int(219 - pct * 173))
            pygame.draw.arc(surf, c, (self.x, self.y, self.r * 2, self.r * 2), ang, math.pi, 6)
        cx, cy = self.x + self.r, self.y + self.r
        nx, ny = cx + int(math.cos(ang) * -(self.r - 8)), cy + int(math.sin(ang) * -(self.r - 8))
        pygame.draw.line(surf, (236, 240, 241), (cx, cy), (nx, ny), 3)
        txt = font.render(f"{spd:.1f} u/f", True, (189, 195, 199))
        surf.blit(txt, (cx - txt.get_width() // 2, cy + 12))

class Player:
    def __init__(self, x, y, r, c):
        self.x, self.y, self.r, self.c = float(x), float(y), r, c
        self.vx, self.vy, self.spd = 0.0, 0.0, 0.0

    def move(self, keys, tspd, acc, rate, obs, w, h):
        tx = (pygame.K_d in keys) - (pygame.K_a in keys)
        ty = (pygame.K_s in keys) - (pygame.K_w in keys)
        if tx != 0 or ty != 0:
            leng = math.hypot(tx, ty)
            tx, ty = (tx / leng) * tspd, (ty / leng) * tspd
        if acc:
            self.vx += (tx - self.vx) * rate
            self.vy += (ty - self.vy) * rate
            if tx == 0 and abs(self.vx) < 0.05: self.vx = 0.0
            if ty == 0 and abs(self.vy) < 0.05: self.vy = 0.0
        else: self.vx, self.vy = tx, ty
        self.spd = math.hypot(self.vx, self.vy)
        steps = max(1, int(math.ceil(self.spd / 2.0)))
        sx, sy = self.vx / steps, self.vy / steps
        for _ in range(steps):
            self.x = max(self.r, min(self.x + sx, w - self.r))
            self.y = max(self.r, min(self.y + sy, h - self.r))
            obs.collide(self)

    def draw(self, surf):
        pygame.draw.circle(surf, self.c, (int(self.x), int(self.y)), self.r)

class ObstacleManager:
    def __init__(self, c):
        self.c = c
        self.rects = [
            pygame.Rect(325, 250, 50, 300), pygame.Rect(200, 375, 300, 50),
            pygame.Rect(120, 150, 80, 40), pygame.Rect(500, 150, 80, 40),
            pygame.Rect(120, 650, 80, 40), pygame.Rect(500, 650, 80, 40)
        ]
        self.circles = [(160, 290, 30), (540, 290, 30), (160, 530, 30), (540, 530, 30)]

    def collide(self, p):
        for w in self.rects:
            cx, cy = max(w.left, min(p.x, w.right)), max(w.top, min(p.y, w.bottom))
            dx, dy = p.x - cx, p.y - cy
            d = math.hypot(dx, dy)
            if d < p.r:
                if d == 0: p.x, p.y = p.x + random.choice([1, -1]), p.y + random.choice([1, -1])
                else: p.x, p.y = p.x + (dx / d) * (p.r - d), p.y + (dy / d) * (p.r - d)
        for ccx, ccy, ccr in self.circles:
            dx, dy = p.x - ccx, p.y - ccy
            d, md = math.hypot(dx, dy), p.r + ccr
            if d < md:
                if d == 0: p.x, p.y = p.x + random.choice([1, -1]), p.y + random.choice([1, -1])
                else: p.x, p.y = p.x + (dx / d) * (md - d), p.y + (dy / d) * (md - d)

    def draw(self, surf):
        for w in self.rects: pygame.draw.rect(surf, self.c, w, border_radius=6)
        for ccx, ccy, ccr in self.circles: pygame.draw.circle(surf, self.c, (ccx, ccy), ccr)

width, height = 700, 900
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
clock = pygame.time.Clock()
fnt, sfnt = pygame.font.SysFont("Arial", 16, True), pygame.font.SysFont("Arial", 12, False)

keys = set()
player = Player(450.0, 750.0, 12, (241, 196, 15))
osw = Switch(40, 45, state=True)
s_sld = Slider(40, 115, 140, 1.0, 15.0, 5.0)
s_inp = TextInput(195, 106, 50, 22, 5.0, 1.0, 15.0)
asw = Switch(40, 175)
a_sld = Slider(40, 235, 140, 0.01, 0.3, 0.1)
a_inp = TextInput(195, 226, 50, 22, 0.1, 0.01, 0.3)
gauge = Speedometer(40, 295)
r_btn = pygame.Rect(40, 410, 205, 30)
obs = ObstacleManager((142, 68, 173))
lbls = ["Menu Overlay", "Speed Limit", "Acceleration", "Acceleration Rate", "Velocity Gauge"]

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()
        
        osw.update(e)
        if osw.is_on:
            s_inp.update(e)
            a_inp.update(e)
            asw.update(e)
            
            if s_inp.active: 
                s_sld.set_val(s_inp.val)
            elif a_inp.active: 
                a_sld.set_val(a_inp.val)
            else:
                if e.type == pygame.KEYDOWN and e.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d): 
                    keys.add(e.key)
                elif e.type == pygame.KEYUP and e.key in keys: 
                    keys.remove(e.key)
                    
            if not s_inp.active and not a_inp.active:
                s_sld.update(e)
                s_inp.set_val(s_sld.val)
                a_sld.update(e)
                a_inp.set_val(a_sld.val)
                
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and r_btn.collidepoint(e.pos):
                s_sld.set_val(5.0); s_inp.set_val(5.0); asw.is_on = False; a_sld.set_val(0.1); a_inp.set_val(0.1)
        else:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d): 
                keys.add(e.key)
            elif e.type == pygame.KEYUP and e.key in keys: 
                keys.remove(e.key)

    player.move(keys, s_sld.val, asw.is_on, a_sld.val, obs, width, height)
    screen.fill((26, 36, 43))
    obs.draw(screen)
    player.draw(screen)
        
    screen.blit(fnt.render(lbls[0], True, (149, 165, 166)), (40, 20))
    osw.draw(screen)
        
    if osw.is_on:
        positions = [85, 150, 210, 270]
        for i, y in enumerate(positions):
            screen.blit(fnt.render(lbls[i+1], True, (149, 165, 166)), (40, y))
        s_sld.draw(screen); s_inp.draw(screen, sfnt)
        asw.draw(screen); a_sld.draw(screen); a_inp.draw(screen, sfnt)
        gauge.draw(screen, player.spd, sfnt)
        pygame.draw.rect(screen, (192, 57, 43), r_btn, border_radius=6)
        btxt = fnt.render("Reset Values", True, (236, 240, 241))
        screen.blit(btxt, (r_btn.centerx - btxt.get_width()//2, r_btn.centery - btxt.get_height()//2))

    pygame.display.flip()
    clock.tick(60)
