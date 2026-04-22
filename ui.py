import pygame
from constants import *

PAD = 24
GAP = 10


def draw_rounded_rect(surf, color, rect, radius=8, alpha=None):
    r = (int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
    if alpha is not None:
        s = pygame.Surface((r[2], r[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color[:3], alpha), (0, 0, r[2], r[3]), border_radius=radius)
        surf.blit(s, (r[0], r[1]))
    else:
        pygame.draw.rect(surf, color, r, border_radius=radius)


class Button:
    H = 42
    def __init__(self, label, style='primary'):
        self.label   = label
        self.style   = style
        self.rect    = pygame.Rect(0, 0, 1, self.H)
        self.hovered = False

    def _colors(self):
        if self.style == 'danger': return C_BTN_DANGER, C_BTN_DANGER
        if self.style == 'sec':    return C_BTN_SEC,    C_BTN_SEC
        return C_BTN_BORDER, C_BTN_TEXT

    def set_rect(self, x, y, w):
        self.rect = pygame.Rect(int(x), int(y), int(w), self.H)

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))

    def draw(self, surf, font):
        bc, tc = self._colors()
        if self.hovered:
            draw_rounded_rect(surf, bc, self.rect, 8, alpha=35)
        pygame.draw.rect(surf, bc, self.rect, 2, border_radius=8)
        txt = font.render(self.label, True, tc)
        surf.blit(txt, txt.get_rect(center=self.rect.center))


class TextInput:
    H = 44
    def __init__(self, placeholder='', max_len=16):
        self.rect        = pygame.Rect(0, 0, 1, self.H)
        self.text        = ''
        self.placeholder = placeholder
        self.max_len     = max_len
        self.active      = True

    def set_rect(self, x, y, w):
        self.rect = pygame.Rect(int(x), int(y), int(w), self.H)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return bool(self.text.strip())
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_len and event.unicode.isprintable():
                self.text += event.unicode
        return False

    def draw(self, surf, font):
        border = C_CYAN if self.active else C_PANEL_EDGE
        # bg
        draw_rounded_rect(surf, (20, 20, 50), self.rect, 8)
        pygame.draw.rect(surf, border, self.rect, 2, border_radius=8)
        display = self.text or self.placeholder
        color   = C_WHITE if self.text else (100, 100, 130)
        txt = font.render(display, True, color)
        surf.blit(txt, txt.get_rect(center=self.rect.center))
        if self.active and self.text:
            tx = self.rect.centerx - font.size(display)[0]//2 + font.size(self.text)[0] + 2
            ty = self.rect.centery - font.get_height()//2
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                pygame.draw.line(surf, C_CYAN,
                                 (tx, ty+2), (tx, ty+font.get_height()-2), 2)


class Panel:
    def __init__(self, sw, sh, fonts: dict):
        self.sw = sw
        self.sh = sh
        self.f  = fonts

    def update_size(self, sw, sh):
        self.sw = sw
        self.sh = sh

    def _pw(self):
        return max(320, min(480, int(self.sw * 0.60)))

    def _measure(self, items):
        h = 0
        for it in items:
            t = it['type']
            if t == 'title':
                h += self.f['title'].get_linesize() + GAP + 4
            elif t == 'body':
                h += self.f['body'].get_linesize() * len(it.get('lines', [''])) + GAP
            elif t == 'input':
                h += TextInput.H + GAP
            elif t == 'buttons':
                h += len(it['btns']) * (Button.H + GAP)
            elif t == 'extra':
                h += it['height'] + GAP
            elif t == 'space':
                h += it.get('h', GAP)
        return h

    def layout(self, items: list):
        pw = self._pw()
        ch = self._measure(items)
        ph = min(ch + PAD * 2 + 8, self.sh - 20)
        px = (self.sw - pw) // 2
        py = max(10, (self.sh - ph) // 2)
        bx = px + PAD
        bw = pw - PAD * 2
        y  = py + PAD

        for it in items:
            t = it['type']
            if t == 'title':
                y += self.f['title'].get_linesize() + GAP + 4
            elif t == 'body':
                y += self.f['body'].get_linesize() * len(it.get('lines', [''])) + GAP
            elif t == 'input':
                it['widget'].set_rect(bx, y, bw)
                y += TextInput.H + GAP
            elif t == 'buttons':
                for btn in it['btns']:
                    btn.set_rect(bx, y, bw)
                    y += Button.H + GAP
            elif t == 'extra':
                y += it['height'] + GAP
            elif t == 'space':
                y += it.get('h', GAP)

    def draw(self, surf, items: list):
        pw = self._pw()
        ch = self._measure(items)
        ph = min(ch + PAD * 2 + 8, self.sh - 20)
        px = (self.sw - pw) // 2
        py = max(10, (self.sh - ph) // 2)

        bg = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 210))
        surf.blit(bg, (0, 0))

        glow = pygame.Surface((pw + 8, ph + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*C_PANEL_EDGE, 40), (0, 0, pw+8, ph+8), border_radius=16)
        surf.blit(glow, (px-4, py-4))

        draw_rounded_rect(surf, C_PANEL_BG, (px, py, pw, ph), 14)
        pygame.draw.rect(surf, C_PANEL_EDGE, (px, py, pw, ph), 2, border_radius=14)

        cx = px + pw // 2
        bx = px + PAD
        bw = pw - PAD * 2
        y  = py + PAD

        for it in items:
            t = it['type']

            if t == 'title':
                txt = self.f['title'].render(it['text'], True, C_CYAN)
                surf.blit(txt, txt.get_rect(centerx=cx, top=y))
                tw = txt.get_width()
                pygame.draw.line(surf, (*C_PANEL_EDGE, 120),
                                 (cx - tw//2, y + txt.get_height() + 2),
                                 (cx + tw//2, y + txt.get_height() + 2), 1)
                y += self.f['title'].get_linesize() + GAP + 4

            elif t == 'body':
                col = it.get('color', C_GRAY)
                for line in it.get('lines', []):
                    if line:
                        txt = self.f['body'].render(line, True, col)
                        surf.blit(txt, txt.get_rect(centerx=cx, top=y))
                    y += self.f['body'].get_linesize()
                y += GAP

            elif t == 'input':
                font_key = it.get('font', 'body')
                input_font = self.f.get(font_key, self.f['body'])
                it['widget'].draw(surf, input_font)
                y += TextInput.H + GAP

            elif t == 'buttons':
                for btn in it['btns']:
                    btn.draw(surf, self.f['btn'])
                    y += Button.H + GAP

            elif t == 'extra':
                it['fn'](surf, px, pw, cx, y)
                y += it['height'] + GAP

            elif t == 'space':
                y += it.get('h', GAP)
