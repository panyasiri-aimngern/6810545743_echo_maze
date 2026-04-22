"""EcHo MaZe — Tutorial Window"""
import tkinter as tk
from PIL import Image, ImageTk
import pygame
import io

DARK   = '#0a0a19'
PANEL  = '#12122e'
CYAN   = '#00e0ff'
GREEN  = '#00ff88'
GOLD   = '#ffd700'
PURPLE = '#c040ff'
GRAY   = '#888888'
WHITE  = '#ffffff'
GRID   = '#1a1a3a'
EDGE   = '#5a3aaa'
DIM    = '#444466'

C_FLOOR       = (12,  12,  32)
C_WALL        = (24,  16,  64)
C_WALL_INNER  = (34,  21,  96)
C_PLAYER      = (0,  212, 255)
C_GHOST1      = (192, 64, 255)
C_GHOST2      = (255, 60, 80)
C_CHECKPOINT  = (255, 224,  0)
C_GOAL_OPEN   = (0,  255, 136)
C_WHITE       = (255, 255, 255)
C_GOAL_CLOSED = (26,  51,  40)


def _surf_to_tk(surf: pygame.Surface) -> ImageTk.PhotoImage:
    raw  = pygame.image.tostring(surf, 'RGB')
    img  = Image.frombytes('RGB', surf.get_size(), raw)
    return ImageTk.PhotoImage(img)


def _make_player(size=48) -> pygame.Surface:
    T = size
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    glow = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*C_PLAYER, 50), (T//2, T//2), T//2)
    s.blit(glow, (0, 0))
    pad = max(3, T//7)
    pygame.draw.rect(s, C_PLAYER, (pad, pad, T-pad*2, T-pad*2), border_radius=max(2, T//7))
    ew = max(2, T//7)
    ep = max(3, T//4)
    pygame.draw.rect(s, C_WHITE, (ep, ep+2, ew, ew))
    pygame.draw.rect(s, C_WHITE, (T-ep-ew, ep+2, ew, ew))
    return s


def _make_checkpoint(size=48) -> pygame.Surface:
    T = size
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    glow = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 220, 0, 60), (T//2, T//2), T//2)
    s.blit(glow, (0, 0))
    r = max(4, T//5)
    pygame.draw.circle(s, C_CHECKPOINT, (T//2, T//2), r)
    pygame.draw.circle(s, C_WHITE, (T//2 - max(1,r//3), T//2 - max(1,r//3)), max(1, r//3))
    return s


def _make_goal(size=48) -> pygame.Surface:
    T = size
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    pad = max(3, T//7)
    pygame.draw.rect(s, C_GOAL_OPEN, (pad, pad, T-pad*2, T-pad*2), border_radius=max(2, T//9))
    pygame.draw.rect(s, (0, 255, 170), (pad-2, pad-2, T-pad*2+4, T-pad*2+4), 2, border_radius=max(2, T//8))
    return s


def _make_ghost(color, size=48) -> pygame.Surface:
    T = size
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    r = max(2, T//2 - max(2, T//7))
    glow = pygame.Surface((T+4, T+4), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, 60), (T//2+2, T//2+2), T//2+2)
    s.blit(glow, (-2, -2))
    pygame.draw.circle(s, (*color, 210), (T//2, T//2), r)
    er = max(2, T//9)
    cx, cy = T//2, T//2
    for ex, ey in [(-max(2,T//7), -max(1,T//10)), (max(2,T//7), -max(1,T//10))]:
        pygame.draw.circle(s, C_WHITE, (cx+ex, cy+ey), er+1)
        pygame.draw.circle(s, (51, 51, 51), (cx+ex+1, cy+ey), max(1, er-1))
    return s


def _make_breakable(size=52) -> pygame.Surface:
    T = size
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    C_WALL      = (24, 16, 64)
    C_BREAK_3   = (58, 24, 0)
    C_BREAK_EDGE= (192, 96, 32)
    C_BREAK_LINE= (255, 128, 48)
    pygame.draw.rect(s, C_WALL,       (0, 0, T, T))
    pygame.draw.rect(s, C_BREAK_3,    (2, 2, T-4, T-4))
    pygame.draw.rect(s, C_BREAK_EDGE, (1, 1, T-2, T-2), 2)
    pygame.draw.line(s, C_BREAK_LINE, (max(2,T//6), max(2,T//7)),   (T//2, T//2), 1)
    pygame.draw.line(s, C_BREAK_LINE, (T//2, T//2), (T-max(2,T//6), T-max(2,T//7)), 1)
    return s


def _surf_to_tk_with_bg(surf: pygame.Surface, bg=(10,10,25)) -> ImageTk.PhotoImage:
    T = surf.get_width()
    H = surf.get_height()
    bg_surf = pygame.Surface((T, H))
    bg_surf.fill(bg)
    bg_surf.blit(surf, (0, 0))
    return _surf_to_tk(bg_surf)


def _pages():
    p  = _make_player(52)
    cp = _make_checkpoint(52)
    gl = _make_goal(52)
    g1 = _make_ghost(C_GHOST1, 52)
    g2 = _make_ghost(C_GHOST2, 52)
    bw = _make_breakable(52)

    return [
        {
            'title': '1 / 7   Objective',
            'sections': [
                {'text': 'Navigate the maze, collect all checkpoints,\nthen reach the goal to complete each round.'},
                {'images': [
                    (p,  'You'),
                    (cp, 'Checkpoint'),
                    (gl, 'Goal'),
                ]},
                {'text': 'The goal only opens after all\ncheckpoints have been collected.'},
            ],
        },
        {
            'title': '2 / 7   The Echo System',
            'sections': [
                {'text': 'Every step you take is recorded.'},
                {'text': 'In later rounds, your past path\nreplays as a ghost enemy.\n\nThe ghost follows your exact movements\nfrom the previous round — dodge yourself!'},
                {'text': '"Echo" — your actions come back to haunt you.'},
            ],
        },
        {
            'title': '3 / 7   Stages & Unlocks',
            'sections': [
                {'text': 'There are 5 stages in total.\nEach stage must be cleared to unlock the next.'},
                {'text': 'Every stage consists of 3 rounds.\nYou must complete all 3 rounds to clear the stage\nand unlock the next one.'},
                {'text': 'Stages get progressively harder\nwith more complex mazes and tighter paths.'},
            ],
        },
        {
            'title': '4 / 7   Rounds',
            'sections': [
                {'text': 'Each stage has 3 rounds:'},
                {'images': [
                    (p,  'Round 1\nNo ghosts'),
                ]},
                {'images': [
                    (g1, 'Round 2\nOne ghost'),
                ]},
                {'images': [
                    (g1, 'Round 3'),
                    (g2, 'Two ghosts'),
                ]},
                {'text': 'When the round ends, you can choose:\n\n  •  Restart Round → Ghost recordings are kept,\n     round replays from the beginning\n\n  •  Retry Stage → Erases all ghost recordings\n     and restarts from Round 1'},
            ],
        },
        {
            'title': '5 / 7   Score & Stats',
            'sections': [
                {'text': 'Score is calculated when you clear a stage:\n\n   Score  =  10,000  -  (time x 10)\n\nFaster clears = higher scores!'},
                {'text': 'Check the Leaderboard to compare scores\nand ghost hits with other players.\nCompete with friends for the top spot!'},
                {'text': 'The Stats menu (Main Menu → Stats) has two main sections:\n\n  •  Data Analysis Report (Game Stats) — overall\n data across all players\n\n  •  Player Stats — search by name to view\n     your own history and performance'},
            ],
        },
        {
            'title': '6 / 7   Controls',
            'sections': [
                {'text': (
                    'MOVE\n'
                    '   W  /  ↑   —   Move Up\n'
                    '   S  /  ↓   —   Move Down\n'
                    '   A  /  ←   —   Move Left\n'
                    '   D  /  →   —   Move Right\n\n'
                    'PAUSE\n'
                    '   ESC   —   Pause / Resume'
                )},
                {'text': 'BREAK WALL\n   Space + Direction (3 times) — break the wall next to you'},
                {'images': [(bw, 'Breakable Wall')]},
                {'text': 'Breakable walls are orange.\nStand next to one and press Space\n+ the direction toward it.'},
            ],
        },
        {
            'title': '7 / 7   Tips',
            'sections': [
                {'text': (
                    '★  Plan your route before moving.\n'
                    '   An efficient path in Round 1\n'
                    '   makes your ghost easier to avoid later.\n\n'
                    '★  Your past self is your biggest obstacle.\n'
                    '   Avoid retracing steps unnecessarily.\n\n'
                    '★  Breakable walls (orange) can open\n'
                    '   new shortcuts — use them wisely.\n\n'
                    '★  During the grace period (3-second countdown),\n'
                    '   ghosts freeze — use that time to reposition.'
                )},
            ],
        },
    ]


# Main window 
def open_tutorial():
    if not pygame.get_init():
        pygame.init()
    try:
        pygame.display.get_surface()
    except Exception:
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    pages = _pages()
    total = len(pages)
    idx   = [0]

    root = tk.Tk()
    root.title('EcHo MaZe — Tutorial')
    root.configure(bg=DARK)
    root.geometry('560x520')
    root.resizable(False, False)

    # Header
    hdr = tk.Frame(root, bg=PANEL, pady=8)
    hdr.pack(fill='x')
    tk.Label(hdr, text='EcHo MaZe  —  How to Play',
             bg=PANEL, fg=CYAN,
             font=('Courier New', 13, 'bold')).pack(side='left', padx=14)

    # Title bar
    title_var = tk.StringVar()
    tk.Label(root, textvariable=title_var, bg=DARK, fg=CYAN,
             font=('Courier New', 12, 'bold'),
             pady=10).pack(fill='x', padx=20)

    content_outer = tk.Frame(root, bg=DARK)
    content_outer.pack(fill='both', expand=True, padx=20, pady=(0, 8))

    canvas_scroll = tk.Canvas(content_outer, bg=DARK, highlightthickness=0)
    scrollbar     = tk.Scrollbar(content_outer, orient='vertical',
                                  command=canvas_scroll.yview)
    canvas_scroll.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    canvas_scroll.pack(side='left', fill='both', expand=True)

    content = tk.Frame(canvas_scroll, bg=DARK)
    content_win = canvas_scroll.create_window((0, 0), window=content, anchor='nw')

    def _on_resize(event):
        canvas_scroll.itemconfig(content_win, width=event.width)
    canvas_scroll.bind('<Configure>', _on_resize)

    def _on_content_resize(event):
        canvas_scroll.configure(scrollregion=canvas_scroll.bbox('all'))
    content.bind('<Configure>', _on_content_resize)

    # mouse wheel
    def _on_wheel(event):
        canvas_scroll.yview_scroll(int(-1*(event.delta/120)), 'units')
    canvas_scroll.bind_all('<MouseWheel>', _on_wheel)

    # Navigation bar
    nav = tk.Frame(root, bg=PANEL, pady=8)
    nav.pack(fill='x', side='bottom')

    btn_prev = tk.Button(nav, text='◀  Back', bg=PANEL, fg=GRAY,
                         font=('Courier New', 10), bd=0, padx=14,
                         activebackground=GRID, activeforeground=WHITE,
                         cursor='hand2', relief='flat')
    btn_prev.pack(side='left', padx=10)

    page_lbl = tk.Label(nav, text='', bg=PANEL, fg=GRAY,
                        font=('Courier New', 10))
    page_lbl.pack(side='left', expand=True)

    btn_next = tk.Button(nav, text='Next  ▶', bg=PANEL, fg=CYAN,
                         font=('Courier New', 10, 'bold'), bd=0, padx=14,
                         activebackground=GRID, activeforeground=CYAN,
                         cursor='hand2', relief='flat')
    btn_next.pack(side='right', padx=10)

    # Render page
    _tk_images = []

    def render_page():
        _tk_images.clear()
        for w in content.winfo_children():
            w.destroy()
        canvas_scroll.yview_moveto(0)

        page = pages[idx[0]]
        title_var.set(page['title'])
        page_lbl.config(text=f'{idx[0]+1} / {total}')

        btn_prev.config(fg=GRAY if idx[0] == 0 else WHITE,
                        cursor='arrow' if idx[0] == 0 else 'hand2')
        is_last = idx[0] == total - 1
        btn_next.config(
            text='Ready to Play!' if is_last else 'Next  ▶',
            fg=GREEN if is_last else CYAN,
            cursor='hand2',
        )

        for sec in page['sections']:
            if 'text' in sec:
                sep = tk.Frame(content, bg=GRID, height=1)
                sep.pack(fill='x', pady=(6, 0), padx=4)

                lbl = tk.Label(content, text=sec['text'],
                               bg=DARK, fg=WHITE,
                               font=('Courier New', 11),
                               justify='left', anchor='w',
                               wraplength=480, pady=8, padx=6)
                lbl.pack(fill='x', padx=4)

            elif 'images' in sec:
                sep = tk.Frame(content, bg=GRID, height=1)
                sep.pack(fill='x', pady=(6, 0), padx=4)

                row = tk.Frame(content, bg=DARK)
                row.pack(pady=10)
                for surf, label in sec['images']:
                    col = tk.Frame(row, bg=DARK)
                    col.pack(side='left', padx=18)
                    tk_img = _surf_to_tk_with_bg(surf)
                    _tk_images.append(tk_img)
                    img_lbl = tk.Label(col, image=tk_img, bg=DARK)
                    img_lbl.pack()
                    for line in label.split('\n'):
                        tk.Label(col, text=line,
                                 bg=DARK, fg=CYAN,
                                 font=('Courier New', 9)).pack()

    def go_prev():
        if idx[0] > 0:
            idx[0] -= 1
            render_page()

    def go_next():
        if idx[0] < total - 1:
            idx[0] += 1
            render_page()
        else:
            root.destroy()  

    btn_prev.config(command=go_prev)
    btn_next.config(command=go_next)

    # keyboard navigation
    root.bind('<Left>',  lambda e: go_prev())
    root.bind('<Right>', lambda e: go_next())
    root.bind('<Escape>', lambda e: root.destroy())

    render_page()
    root.mainloop()


if __name__ == '__main__':
    pygame.init()
    open_tutorial()
