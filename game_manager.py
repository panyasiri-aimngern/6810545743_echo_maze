import pygame
import time
import threading
from constants import *
from map import Map
from player import Player
from ghost import Ghost
from mission import Mission
from ui import Panel, Button, TextInput, draw_rounded_rect
import stats as ST


class GameManager:
    GRACE_TOTAL = 3.0

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self._init_fonts()
        self._init_state()
        self._init_sounds()
        self._load_bg()
        self._build_menu()
        self._play_bgm('menu')

    def _init_fonts(self):
        import os
        custom = os.path.join(os.path.dirname(__file__), 'assets', 'font.ttf')
        def mf(size, bold=False):
            if os.path.exists(custom):
                try: return pygame.font.Font(custom, size)
                except Exception: pass
            return pygame.font.SysFont('monospace', size, bold=bold)
        def mf_thai(size, bold=False):
            """Font with Thai support — ลองหา path จริงของ font บน Windows ก่อน"""
            import os, sys
            win_fonts = os.environ.get('WINDIR', r'C:\Windows')
            candidates_path = [
                os.path.join(win_fonts, 'Fonts', 'tahoma.ttf'),
                os.path.join(win_fonts, 'Fonts', 'tahomabd.ttf'),
                os.path.join(win_fonts, 'Fonts', 'leelawad.ttf'),
                os.path.join(win_fonts, 'Fonts', 'leelawui.ttf'),
            ]
            for path in candidates_path:
                if os.path.exists(path):
                    try:
                        f = pygame.font.Font(path, size)
                        surf = f.render('ทดสอบ', True, (0,0,0))
                        if surf.get_width() > 10:
                            return f
                    except Exception:
                        pass
            for name in ['tahoma','leelawadee','leelawadeeuI','thsarabunnew','freesans','dejavusans']:
                try:
                    f = pygame.font.SysFont(name, size, bold=bold)
                    surf = f.render('ทดสอบ', True, (0,0,0))
                    if surf.get_width() > 10:
                        return f
                except Exception:
                    pass
            return mf(size, bold)
        self.ft   = mf(24, bold=True)
        self.fb   = mf(16)
        self.fbt  = mf(15, bold=True)
        self.fh   = mf(14, bold=True)
        self.fbig = mf(36, bold=True)
        self.fsm  = mf(13)
        self.fthai = mf_thai(18)
        self.fonts = {'title': self.ft, 'body': self.fb, 'btn': self.fbt, 'small': self.fsm, 'thai': self.fthai}

    #Background
    def _load_bg(self):
        """Load background image — ค้นหาใน assets/ และ root folder."""
        import os
        self._bg_image = None
        self._bg_frames = []
        base = os.path.dirname(__file__)
        assets = os.path.join(base, 'assets')
        i = 0
        while True:
            for folder in [assets, base]:
                p = os.path.join(folder, f'bg_{i:03d}.png')
                if os.path.exists(p):
                    try: self._bg_frames.append(pygame.image.load(p).convert())
                    except Exception: pass
            if not any(os.path.exists(os.path.join(f, f'bg_{i:03d}.png'))
                       for f in [assets, base]):
                break
            i += 1
        self._bg_frame_idx   = 0.0
        self._bg_frame_speed = 12
        for name in ['background.png', 'background.jpg', 'bg.png', 'bg.jpg']:
            for folder in [assets, base]:
                path = os.path.join(folder, name)
                if os.path.exists(path):
                    try:
                        self._bg_image = pygame.image.load(path).convert()
                        break
                    except Exception: pass
            if self._bg_image:
                break

    #Sound
    def _init_sounds(self):
        """โหลดเสียงทั้งหมด — mixer 8 channels, grace ใช้ channel 0 เฉพาะ"""
        import os
        self._snd_on = True
        self._sounds = {}         
        self._bgm_paths = {}     
        self._cur_bgm   = None    
        self._grace_ticks_done = set()  
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(8)
            sounds_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
            for key, fname in [
                ('checkpoint',  'sfx_checkpoint.wav'),
                ('goal',        'sfx_goal.wav'),
                ('stage_clear', 'sfx_stage_clear.wav'),
                ('fail',        'sfx_fail.wav'),
                ('break_wall',  'sfx_break_wall.wav'),
                ('grace',       'sfx_grace.wav'),
            ]:
                path = os.path.join(sounds_dir, fname)
                if os.path.exists(path):
                    try:
                        self._sounds[key] = pygame.mixer.Sound(path)
                    except Exception:
                        pass
            for key, fname in [('menu','bgm_menu.wav'), ('game','bgm_game.wav')]:
                path = os.path.join(sounds_dir, fname)
                if os.path.exists(path):
                    self._bgm_paths[key] = path
        except Exception:
            self._snd_on = False

    def _sfx(self, key):
        if not self._snd_on: return
        s = self._sounds.get(key)
        if not s: return
        if key == 'grace':
            ch = pygame.mixer.Channel(0)
            ch.stop()
            ch.play(s)
        else:
            s.play()

    #compat alias
    def _play_sfx(self, key): self._sfx(key)

    def _play_bgm(self, key):
        if not self._snd_on: return
        if self._cur_bgm == key: return
        path = self._bgm_paths.get(key, '')
        if not path: return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1)
            self._cur_bgm = key
        except Exception:
            pass

    def _stop_bgm(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self._cur_bgm = None

    def _toggle_sound(self):
        self._snd_on = not self._snd_on
        if self._snd_on:
            self._cur_bgm = None
            bgm = 'game' if self.screen_state == 'playing' else 'menu'
            self._play_bgm(bgm)
        else:
            self._stop_bgm()
            try: pygame.mixer.stop()
            except Exception: pass

    #State
    def _init_state(self):
        sw, sh     = self.screen.get_size()
        self.panel = Panel(sw, sh, self.fonts)

        self.screen_state = 'menu'
        self.player_name  = ''
        self.unlocked     = 1

        self.stage = 1
        self.round = 1
        self.maze:   Map    | None = None
        self.player: Player | None = None
        self.ghosts: list[Ghost]   = []
        self.mission: Mission | None = None
        self.records: dict = {}

        self.timer_start  = 0.0
        self.stage_time   = 0.0
        self.stage_steps  = 0
        self.ghost_hits   = 0
        self.retries      = 0
        self.grace        = 0.0
        self.goal_open    = False

        self._items: list = []

        self._buttons:    list[Button]    = []
        self._inputs:     list[TextInput] = []

        self._leaderboard_tab  = 0
        self._stats_player     = ''
        self._scroll_y         = 0
        self._lb_tab_rects:    list = []
        self._lb_player_rects: list = []
        self._stage_btn_rects: list = []

    def _sw(self): return self.screen.get_width()
    def _sh(self): return self.screen.get_height()

    def _elapsed(self): return time.perf_counter() - self.timer_start
    def _fmt_time(self, s):
        return f'{int(s//60):02d}:{int(s%60):02d}'
    def _calc_score(self):
        return max(0, 10000 - int(self.stage_time * 10))

    #Panel builders
    def _set_items(self, items):
        self._items   = items
        self._buttons = []
        self._inputs  = []
        for it in items:
            if it['type'] == 'buttons':
                self._buttons.extend(it['btns'])
            elif it['type'] == 'input':
                self._inputs.append(it['widget'])
        self.panel.layout(items)

    def _build_menu(self):
        self.screen_state = 'menu'
        if hasattr(self, '_snd_on'): self._play_bgm('menu')
        self._set_items([
            {'type':'title',   'text':'EcHo MaZe'},
            {'type':'body',    'lines':['Your past movements become ghost enemies.']},
            {'type':'space',   'h':6},
            {'type':'buttons', 'btns':[
                Button('Play'),
                Button('Leaderboard', 'sec'),
                Button('Stats', 'sec'),
                Button('How to Play', 'sec'),
            ]},
        ])

    def _build_name_screen(self):
        self.screen_state = 'name'
        self._name_input  = TextInput('Your name...')
        self._name_input.use_thai = True 
        self._set_items([
            {'type':'title',   'text':'Enter Your Name'},
            {'type':'space',   'h':6},
            {'type':'input',   'widget': self._name_input, 'font':'thai'},
            {'type':'body',    'lines':['Press Enter to continue'],
             'color': (100,100,140)},
        ])

    def _build_stage_select(self):
        self.screen_state     = 'select'
        self._stage_btn_rects = []
        back = Button('Back', 'sec')
        self._buttons = [back]
        self._inputs  = []
        self._items   = []   

    def _build_leaderboard(self):
        self.screen_state     = 'leaderboard'
        self._leaderboard_tab = 0
        back = Button('Back', 'sec')
        self._buttons = [back]
        self._inputs  = []
        self._items   = []
        self._lb_player_rects = []
        self._lb_tab_rects    = []
        sw, sh = self._sw(), self._sh()
        self._compute_lb_layout(sw, sh)

    def _build_stats_choice(self):
        self.screen_state = 'stats_choice'
        self._set_items([
            {'type':'title',   'text':'Statistics'},
            {'type':'body',    'lines':['What would you like to view?']},
            {'type':'space',   'h':6},
            {'type':'buttons', 'btns':[
                Button('Data Analysis Report'),
                Button('Player Stats (by name)'),
                Button('Back', 'sec'),
            ]},
        ])

    def _build_pause(self):
        self.screen_state = 'paused'
        self._set_items([
            {'type':'title',   'text':'Paused'},
            {'type':'space',   'h':6},
            {'type':'buttons', 'btns':[
                Button('Resume'),
                Button('Stage Select', 'sec'),
                Button('Retry Stage', 'danger'),
                Button('Main Menu', 'sec'),
            ]},
        ])

    def _build_confirm_retry(self):
        self.screen_state = 'confirm_retry'
        self._set_items([
            {'type':'title',   'text':'Retry Stage?'},
            {'type':'body',    'lines':['All ghost recordings will be erased.']},
            {'type':'space',   'h':6},
            {'type':'buttons', 'btns':[
                Button('Confirm — Erase Ghosts', 'danger'),
                Button('Cancel', 'sec'),
            ]},
        ])

    def _build_game_over(self):
        self.screen_state = 'gameover'
        self._play_sfx('fail')
        self._stop_bgm()
        score = self._calc_score()
        ST.save_record({
            'player': self.player_name, 'stage': self.stage, 'round': self.round,
            'survival_time': round(self._elapsed(), 2),
            'steps': self.player.steps if self.player else 0,
            'items': len(self.mission.collected) if self.mission else 0,
            'ghost_hits': self.ghost_hits, 'retries': self.retries,
            'score': score, 'total_score': '', 'stage_total_hits': '',
            'completed': False, 'is_stage_clear': False,
        })
        self._set_items([
            {'type':'title',   'text':'Game Over'},
            {'type':'body',    'lines':[f'Caught by a ghost!  Round {self.round}/3']},
            {'type':'space',   'h':6},
            {'type':'buttons', 'btns':[
                Button('Restart Round'),
                Button('Retry Stage', 'danger'),
                Button('Main Menu', 'sec'),
            ]},
        ])

    def _build_stage_clear(self, total_score, prev_cumulative):
        self.screen_state = 'clear'
        new_total  = int(prev_cumulative + total_score)
        fb, fbig, fsm = self.fb, self.fbig, self.fsm
        stage_time = self.stage_time
        fmt = self._fmt_time

        def draw_score(surf, px, pw, cx, y):
            g = fb.render(f'{int(prev_cumulative):,}  +{int(total_score):,}', True, C_GRAY)
            surf.blit(g, g.get_rect(centerx=cx, top=y))
            b = fbig.render(f'{new_total:,}', True, C_ACCENT)
            surf.blit(b, b.get_rect(centerx=cx, top=y+22))
            t = fsm.render(f'Time: {fmt(stage_time)}', True, C_DIM)
            surf.blit(t, t.get_rect(centerx=cx, top=y+64))

        ns = self.stage + 1
        self._set_items([
            {'type':'title',   'text':'Stage Clear!'},
            {'type':'extra',   'fn': draw_score, 'height': 84},
            {'type':'buttons', 'btns':[
                Button(f'Next Stage ({ns})') if ns in MAPS else Button('Play Again'),
                Button('Stage Select', 'sec'),
                Button('Main Menu', 'sec'),
            ]},
        ])

    def _build_ready(self):
        has_ghosts = bool(self.ghosts)
        body = ([f'{self.round-1} ghost{"s" if self.round>2 else ""} will replay your path.',
                 'You have 3 seconds before they move.']
                if has_ghosts else ['No ghosts — movement will be recorded.'])
        self.screen_state = 'ready'
        self._set_items([
            {'type':'title',   'text':f'Round {self.round}/3'},
            {'type':'body',    'lines': body},
            {'type':'space',   'h':8},
            {'type':'body',    'lines':['Controls:',
                                        'WASD / Arrow keys — move',
                                        'Space + direction — break wall',
                                        'ESC — pause'],
             'color': (120, 120, 160)},
            {'type':'space',   'h':6},
            {'type':'buttons', 'btns':[Button('Ready!')]},
        ])

    def _build_player_stats_input(self):
        self.screen_state  = 'player_stats_input'
        self._pstats_input = TextInput('Enter player name...')
        self._pstats_input.use_thai = True
        self._set_items([
            {'type':'title',   'text':'Player Stats'},
            {'type':'space',   'h':6},
            {'type':'input',   'widget': self._pstats_input, 'font':'thai'},
            {'type':'buttons', 'btns':[
                Button('View Stats'),
                Button('Back', 'sec'),
            ]},
        ])

    #Stage+Round flow
    def start_stage(self, stage: int):
        self.stage = stage; self.round = 1
        self.records = {}; self.retries = 0
        self.stage_time = 0.0; self.stage_steps = 0; self.ghost_hits = 0
        self._start_round()

    def _start_round(self):
        self.maze    = Map(self.stage)
        self.player  = Player(*self.maze.start)
        self.mission = Mission(self.maze.checkpoints)
        self.goal_open   = False
        self.timer_start = time.perf_counter()
        self.ghosts = [Ghost(self.records[r], r-1)
                       for r in range(1, self.round) if r in self.records]
        self.grace = self.GRACE_TOTAL if self.ghosts else 0.0
        self._grace_ticks_done = set()
        self._build_ready()

    def _finish_round(self):
        self.stage_time  += self._elapsed()
        self.stage_steps += self.player.steps
        self.records[self.round] = list(self.player.path)
        self._stop_bgm()         
        self._sfx('goal')        
        ST.save_record({
            'player': self.player_name, 'stage': self.stage, 'round': self.round,
            'survival_time': round(self._elapsed(), 2), 'steps': self.player.steps,
            'items': len(self.mission.collected), 'ghost_hits': self.ghost_hits,
            'retries': self.retries, 'score': self._calc_score(),
            'total_score':'', 'stage_total_hits':'', 'completed': True, 'is_stage_clear': False,
        })
        if self.round >= 3:
            total_score = self._calc_score()
            ns = self.stage + 1
            if ns in MAPS and ns > self.unlocked:
                self.unlocked = ns
                (ST.DATA_FILE.parent / f'unlock_{self.player_name}.txt').write_text(str(ns))
            prev = ST.get_player_total_score(self.player_name)
            ST.save_record({
                'player': self.player_name, 'stage': self.stage, 'round': 3,
                'survival_time': round(self.stage_time, 2), 'steps': self.stage_steps,
                'items': len(self.mission.collected), 'ghost_hits': self.ghost_hits,
                'retries': self.retries, 'score': total_score,
                'total_score': total_score, 'stage_total_hits': self.ghost_hits,
                'completed': True, 'is_stage_clear': True,
            })
            self._play_sfx('stage_clear')
            self._build_stage_clear(total_score, prev)
        else:
            self.round += 1
            self._start_round()

    #Input
    def handle_event(self, event):
        self.panel.update_size(self._sw(), self._sh())

        # QUIT / RESIZE
        if event.type in (pygame.QUIT, pygame.VIDEORESIZE):
            return

        # Mute button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, '_mute_rect') and self._mute_rect.collidepoint(event.pos):
                self._toggle_sound()
                return

        if self.screen_state == 'playing':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._build_pause()
                elif event.key == pygame.K_SPACE:
                    keys = pygame.key.get_pressed()
                    if self.player.try_break(keys, self.maze):
                        self._play_sfx('break_wall')
            return

        # Scroll
        if event.type == pygame.MOUSEWHEEL:
            if self.screen_state in ('game_stats', 'player_stats'):
                self._scroll_y = max(0, self._scroll_y - event.y * 20)

        # Stage select stage
        if self.screen_state == 'select':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for r, stage, unlocked in self._stage_btn_rects:
                    if unlocked and r.collidepoint(event.pos):
                        self.start_stage(stage)
                        return

        if self.screen_state == 'leaderboard':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(self._lb_tab_rects):
                    if r.collidepoint(event.pos):
                        self._leaderboard_tab = i
                        return
                    
                for rr, player in self._lb_player_rects:
                    if rr.collidepoint(event.pos):
                        self._stats_player = player
                        self.screen_state  = 'player_stats'
                        self._scroll_y     = 0
                        self._buttons      = [Button('Back', 'sec')]
                        self._inputs       = []
                        return

        # Text inputs
        for inp in self._inputs:
            if inp.handle_event(event):   # Enter pressed
                self._on_input_confirm(inp)
                return

        # Buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self._buttons):
                if btn.rect.collidepoint(event.pos):
                    self._on_btn(i)
                    return

        # hover update
        if event.type == pygame.MOUSEMOTION:
            for btn in self._buttons:
                btn.hovered = btn.rect.collidepoint(event.pos)

    def _on_input_confirm(self, inp):
        s = self.screen_state
        if s == 'name':
            name = inp.text.strip()
            if not name: return
            self.player_name = name
            uf = ST.DATA_FILE.parent / f'unlock_{name}.txt'
            try:   self.unlocked = int(uf.read_text()) if uf.exists() else 1
            except: self.unlocked = 1
            self._build_stage_select()
        elif s == 'player_stats_input':
            name = inp.text.strip()
            if not name: return
            records = [r for r in ST.get_records() if r['player'] == name]
            if not records:
                self._pstats_input.text = ''
                self._set_items([
                    {'type':'title',   'text':'Player Stats'},
                    {'type':'body',    'lines':[f'No records found for "{name}".', 'Please check the name and try again.'],
                     'color': (255, 100, 100)},
                    {'type':'space',   'h':4},
                    {'type':'input',   'widget': self._pstats_input, 'font':'thai'},
                    {'type':'buttons', 'btns':[
                        Button('View Stats'),
                        Button('Back', 'sec'),
                    ]},
                ])
                return
            self._stats_player = name
            self.screen_state  = 'player_stats'
            self._scroll_y     = 0
            self._buttons = [Button('Back', 'sec')]
            self._inputs  = []

    def _on_btn(self, idx):
        s = self.screen_state
        if s == 'menu':
            [self._build_name_screen,
             self._build_leaderboard,
             self._build_stats_choice,
             self._launch_tutorial][idx]()

        elif s == 'ready':
            self.screen_state = 'playing'
            self.timer_start  = time.perf_counter()
            self._buttons = []; self._inputs = []
            if self.grace > 0:
                self._stop_bgm()         
                self._sfx('grace')      
            else:
                self._play_bgm('game')   

        elif s == 'paused':
            [self._resume,
             self._build_stage_select,
             self._build_confirm_retry,
             self._build_menu][idx]()

        elif s == 'confirm_retry':
            if idx == 0:
                self.retries += 1; self.start_stage(self.stage)
            else:
                self._build_game_over()

        elif s == 'gameover':
            [self._start_round,
             self._build_confirm_retry,
             self._build_menu][idx]()

        elif s == 'clear':
            ns = self.stage + 1
            [(lambda: self.start_stage(ns)) if ns in MAPS else (lambda: self.start_stage(1)),
             self._build_stage_select,
             self._build_menu][idx]()

        elif s == 'stats_choice':
            [self._launch_graphs,
             self._build_player_stats_input,
             self._build_menu][idx]()

        elif s == 'player_stats':
            self._build_stats_choice()

        elif s == 'player_stats_input':
            if idx == 0:
                self._on_input_confirm(self._pstats_input)
            else:
                self._build_stats_choice()

        elif s == 'leaderboard':
            self._build_menu()

        elif s == 'select':
            self._build_menu()

    def _resume(self):
        self.screen_state = 'playing'
        self.timer_start  = time.perf_counter()
        self._buttons = []; self._inputs = []
        if self.grace <= 0:
            self._play_bgm('game')



    def _launch_graphs(self):
        from data_window import open_data_window
        threading.Thread(target=open_data_window, daemon=True).start()

    def _launch_tutorial(self):
        from tutorial import open_tutorial
        threading.Thread(target=open_tutorial, daemon=True).start()

    # Update
    def update(self):
        if self.screen_state != 'playing': return
        dt = 1 / FPS
        if self.grace > 0:
            prev_grace = self.grace
            self.grace = max(0.0, self.grace - dt)
            if prev_grace > 0 and self.grace <= 0:
                self._play_bgm('game')

        keys = pygame.key.get_pressed()
        landed = self.player.update(self._elapsed())
        if not self.player.moving:
            if   keys[pygame.K_UP]    or keys[pygame.K_w]: self.player.try_move(0,-1,self.maze,self._elapsed())
            elif keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.player.try_move(0, 1,self.maze,self._elapsed())
            elif keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.player.try_move(-1,0,self.maze,self._elapsed())
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player.try_move( 1,0,self.maze,self._elapsed())

        if landed:
            self._on_land(*landed)
            if self.screen_state != 'playing': return

        if self.grace <= 0:
            for g in self.ghosts:
                g.update()
                if g.check_collision(self.player):
                    self.ghost_hits += 1
                    self._build_game_over(); return

    def _on_land(self, x, y):
        if self.mission.collect(x, y):
            self._play_sfx('checkpoint')
        if self.mission.is_complete: self.goal_open = True
        if self.grace <= 0:
            for g in self.ghosts:
                if g.check_collision(self.player):
                    self.ghost_hits += 1
                    self._build_game_over(); return
        if self.goal_open and (x,y) == self.maze.goal:
            self._finish_round()

    # Draw
    def draw(self):
        sw, sh = self._sw(), self._sh()
        self.screen.fill(C_BG)

        if self.screen_state == 'playing':
            hud_h     = max(36, int(sh * HUD_RATIO))
            mission_h = max(26, int(sh * MISSION_RATIO))
            offset_y  = hud_h + mission_h
            maze_h    = sh - offset_y
            tile_w    = sw // COLS
            tile_h    = maze_h // ROWS
            tile      = max(1, min(tile_w, tile_h))
            maze_pw   = tile * COLS
            maze_ph   = tile * ROWS
            mx = (sw - maze_pw) // 2
            my = offset_y + (maze_h - maze_ph) // 2

            if self.maze:
                collected = self.mission.collected if self.mission else set()
                self.maze.draw_scaled(self.screen, mx, my, tile, self.goal_open, collected)
                for g in self.ghosts: g.draw_scaled(self.screen, mx, my, tile)
                if self.player: self.player.draw_scaled(self.screen, mx, my, tile)
                if self.grace > 0:
                    self._draw_grace(mx, my, maze_pw, maze_ph)
                if self.round > 1 and self.grace <= 0:
                    rt = self.fsm.render(f'Round {self.round}/3', True, (180,180,180))
                    self.screen.blit(rt, (sw - rt.get_width() - 8, sh - rt.get_height() - 8))

            self._draw_hud(sw, hud_h)
            self._draw_mission_bar(sw, hud_h, mission_h)

        else:
            img = None
            if hasattr(self, '_bg_frames') and self._bg_frames:
                self._bg_frame_idx = (self._bg_frame_idx + self._bg_frame_speed / FPS) % len(self._bg_frames)
                img = self._bg_frames[int(self._bg_frame_idx)]
            elif hasattr(self, '_bg_image') and self._bg_image:
                img = self._bg_image
            if img:
                if getattr(self, '_bg_cache_sz', None) != (sw, sh):
                    self._bg_cache = pygame.transform.scale(img, (sw, sh)).convert()
                    self._bg_cache_sz = (sw, sh)
                self.screen.blit(self._bg_cache, (0, 0))
                dark = pygame.Surface((sw, sh))
                dark.fill((0, 0, 0))
                dark.set_alpha(80)
                self.screen.blit(dark, (0, 0))

        self._mute_rect = pygame.Rect(0, 0, 0, 0)

        self._draw_overlay(sw, sh)

        if self.screen_state != 'playing':
            enabled  = getattr(self, '_snd_on', True)
            lbl      = 'SOUND ON' if enabled else 'SOUND OFF'
            col      = C_ACCENT if enabled else C_DIM
            mt       = self.fsm.render(lbl, True, col)
            btn_w    = mt.get_width() + 18
            btn_h    = 28
            bx       = sw - btn_w - 10
            by       = 10
            self._mute_rect = pygame.Rect(bx, by, btn_w, btn_h)
            s = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            pygame.draw.rect(s, (18, 18, 48, 230), (0, 0, btn_w, btn_h), border_radius=6)
            pygame.draw.rect(s, (*col, 220),        (0, 0, btn_w, btn_h), 1, border_radius=6)
            self.screen.blit(s, (bx, by))
            self.screen.blit(mt, mt.get_rect(center=self._mute_rect.center))

        pygame.display.flip()

    def _draw_hud(self, sw, hud_h):
        pygame.draw.rect(self.screen, C_HUD_BG, (0, 0, sw, hud_h))
        pygame.draw.line(self.screen, C_HUD_BORDER, (0, hud_h), (sw, hud_h))
        cy = hud_h // 2
        p = self.fthai.render(f'Player: {self.player_name or "—"}', True, C_GRAY)
        self.screen.blit(p, (12, cy - p.get_height()//2))
        s = self.ft.render(f'Stage {self.stage}  ·  Round {self.round}/3', True, C_CYAN)
        self.screen.blit(s, s.get_rect(centerx=sw//2, centery=cy))
        el = self._elapsed() if self.screen_state == 'playing' else 0
        t = self.fb.render(self._fmt_time(el), True, C_WHITE)
        self.screen.blit(t, (sw - t.get_width() - 12, cy - t.get_height()//2))

    def _draw_mission_bar(self, sw, hud_h, mission_h):
        y = hud_h
        pygame.draw.rect(self.screen, (14,14,36), (0, y, sw, mission_h))
        pygame.draw.line(self.screen, (26,26,58), (0, y+mission_h), (sw, y+mission_h))
        cy = y + mission_h//2
        if self.mission:
            col2, tot = self.mission.count
            cp_col  = C_ACCENT if col2 == tot else C_CHECKPOINT
            status_col = C_ACCENT if self.goal_open else (180, 180, 220)
            status  = 'Reach the goal!' if self.goal_open else 'Collect all checkpoints'
            cp_txt  = self.fb.render(f'CP: {col2}/{tot}', True, cp_col)
            sep_txt = self.fb.render('  ·  ', True, (80,80,100))
            st_txt  = self.fb.render(status, True, status_col)
            x = 14
            self.screen.blit(cp_txt,  (x, cy - cp_txt.get_height()//2)); x += cp_txt.get_width()
            self.screen.blit(sep_txt, (x, cy - sep_txt.get_height()//2)); x += sep_txt.get_width()
            self.screen.blit(st_txt,  (x, cy - st_txt.get_height()//2))
        hint = self.fsm.render('WASD/Arrows  ·  Space=break  ·  ESC=pause', True, (70,70,100))
        self.screen.blit(hint, (sw - hint.get_width() - 12, cy - hint.get_height()//2))

    def _draw_grace(self, mx, my, mw, mh):
        ov = pygame.Surface((mw, mh), pygame.SRCALPHA)
        ov.fill((0,0,0,110)); self.screen.blit(ov, (mx, my))
        cx = mx+mw//2; cy = my+mh//2
        n = self.fbig.render(str(int(self.grace)+1), True, C_GRACE_NUM)
        self.screen.blit(n, n.get_rect(centerx=cx, centery=cy+8))
        s = self.fb.render('ghosts start in...', True, (255,220,0))
        self.screen.blit(s, s.get_rect(centerx=cx, centery=cy-34))
        m = self.fsm.render('move now!', True, C_WHITE)
        self.screen.blit(m, m.get_rect(centerx=cx, centery=cy+50))

    # Overlay
    def _draw_overlay(self, sw, sh):
        s = self.screen_state
        if s == 'playing': return
        self.panel.update_size(sw, sh)

        if s == 'select':
            self._draw_stage_select(sw, sh)
        elif s == 'leaderboard':
            self._draw_leaderboard(sw, sh)
        elif s == 'player_stats':
            self._draw_player_stats(sw, sh)
        else:
            if self._items:
                self.panel.layout(self._items)
                self.panel.draw(self.screen, self._items)

    # Stage Select
    def _draw_stage_select(self, sw, sh):
        bg = pygame.Surface((sw, sh), pygame.SRCALPHA)
        bg.fill((0,0,0,200)); self.screen.blit(bg,(0,0))
        pw = min(380, sw-40); ph = 220
        px = (sw-pw)//2; py = (sh-ph)//2
        draw_rounded_rect(self.screen, C_PANEL_BG, (px,py,pw,ph), 12)
        pygame.draw.rect(self.screen, C_PANEL_EDGE,(px,py,pw,ph),2,border_radius=12)
        t = self.ft.render('Select Stage', True, C_CYAN)
        self.screen.blit(t, t.get_rect(centerx=px+pw//2, top=py+16))

        btn_sz = min(52, (pw-80)//5)
        gap    = 8
        total_w = 5*btn_sz + 4*gap
        sx = px + (pw-total_w)//2; sy = py+62
        self._stage_btn_rects = []
        for i, stage in enumerate(range(1,6)):
            unlocked = stage <= self.unlocked
            bx = sx + i*(btn_sz+gap)
            r  = pygame.Rect(bx, sy, btn_sz, btn_sz)
            self._stage_btn_rects.append((r, stage, unlocked))
            col = C_CYAN if unlocked else C_DIM
            draw_rounded_rect(self.screen,(13,13,34),r,8)
            pygame.draw.rect(self.screen,col,r,2,border_radius=8)
            lbl = self.ft.render(str(stage) if unlocked else '?', True, col)
            self.screen.blit(lbl, lbl.get_rect(center=r.center))

        back = self._buttons[0] if self._buttons else Button('Back','sec')
        back.set_rect(px+20, py+ph-52, pw-40)
        back.draw(self.screen, self.fbt)
        self._buttons = [back]

    # Leaderboard
    def _compute_lb_layout(self, sw, sh):
        """Compute leaderboard rects without drawing — safe to call before draw."""
        pw = min(380, sw-40); ph = min(340, sh-40)
        px = (sw-pw)//2;      py = (sh-ph)//2
        tw = (pw-44)//2
        # tab rects
        self._lb_tab_rects = [
            pygame.Rect(px+20+i*(tw+6), py+50, tw, 28) for i in range(2)
        ]
        # player row rects
        data = ST.leaderboard_score() if self._leaderboard_tab==0 else ST.leaderboard_hits()
        self._lb_player_rects = []
        y = py+88; row_h = 34
        for i,(player,val) in enumerate(data):
            self._lb_player_rects.append((pygame.Rect(px+10, y, pw-20, row_h), player))
            y += row_h + 2
        # back button
        if self._buttons:
            self._buttons[0].set_rect(px+20, py+ph-50, pw-40)

    def _draw_leaderboard(self, sw, sh):
        self._compute_lb_layout(sw, sh)

        bg = pygame.Surface((sw, sh), pygame.SRCALPHA)
        bg.fill((0,0,0,200)); self.screen.blit(bg,(0,0))
        pw = min(380, sw-40); ph = min(340, sh-40)
        px = (sw-pw)//2; py = (sh-ph)//2
        draw_rounded_rect(self.screen,C_PANEL_BG,(px,py,pw,ph),12)
        pygame.draw.rect(self.screen,C_PANEL_EDGE,(px,py,pw,ph),2,border_radius=12)
        t = self.ft.render('Leaderboard', True, C_CYAN)
        self.screen.blit(t, t.get_rect(centerx=px+pw//2, top=py+14))

        tw = (pw-44)//2
        for i, (tr, lbl) in enumerate(zip(self._lb_tab_rects, ['Top Score','Total Hits'])):
            active = i == self._leaderboard_tab
            pygame.draw.rect(self.screen,C_CYAN if active else C_DIM,tr,2,border_radius=5)
            lt = self.fsm.render(lbl, True, C_CYAN if active else C_DIM)
            self.screen.blit(lt, lt.get_rect(center=tr.center))

        y = py+88
        data = ST.leaderboard_score() if self._leaderboard_tab==0 else ST.leaderboard_hits()
        medals = ['1st','2nd','3rd','4th','5th']
        if not data:
            no = self.fb.render('No records yet!', True, C_DIM)
            self.screen.blit(no, no.get_rect(centerx=px+pw//2, top=y+16))
        else:
            medal_colors = [(255,215,0),(192,192,192),(205,127,50),(170,170,170),(170,170,170)]
            for i,((rr,player),(_,val)) in enumerate(zip(self._lb_player_rects, data)):
                row_h = 34
                row_bg = (40,35,10) if i==0 else (32,32,34) if i==1 else (34,28,20) if i==2 else (20,20,40)
                draw_rounded_rect(self.screen, row_bg, rr, 4)
                if i < 3:
                    pygame.draw.rect(self.screen, medal_colors[i], rr, 1, border_radius=4)
                mc = medal_colors[i]
                suffix = '  · stats' if i < 3 else ''
                name_surf = self.fthai.render(f'{medals[i]} {player}{suffix}', True, mc)
                self.screen.blit(name_surf, (px+16, rr.y + (row_h-name_surf.get_height())//2))
                vf = f'{int(val):,}' if self._leaderboard_tab==0 else f'{int(val)} hits'
                vt = self.fb.render(vf, True, mc)
                self.screen.blit(vt, (px+pw-16-vt.get_width(), rr.y + (row_h-vt.get_height())//2))

        back = self._buttons[0] if self._buttons else Button('Back','sec')
        back.set_rect(px+20, py+ph-50, pw-40)
        back.draw(self.screen, self.fbt)
        self._buttons = [back]

    # Game Stats
    def _section_title(self, text, px, pw, y):
        t = self.fsm.render(text.upper(), True, C_CYAN)
        self.screen.blit(t, (px+10, y))
        pygame.draw.line(self.screen, (26,26,58), (px+10, y+14), (px+pw-10, y+14))
        return y + 20

    # Player Stats
    def _draw_player_stats(self, sw, sh):
        records=[r for r in ST.get_records() if r['player']==self._stats_player]
        bg=pygame.Surface((sw,sh),pygame.SRCALPHA)
        bg.fill((0,0,0,200)); self.screen.blit(bg,(0,0))
        pw=min(440,sw-32); ph=sh-60
        px=(sw-pw)//2; py=30
        draw_rounded_rect(self.screen,C_PANEL_BG,(px,py,pw,ph),12)
        pygame.draw.rect(self.screen,C_PANEL_EDGE,(px,py,pw,ph),2,border_radius=12)
        title=self.fthai.render(f"{self._stats_player}'s Stats",True,C_CYAN)
        self.screen.blit(title,title.get_rect(centerx=px+pw//2,top=py+12))

        clip=pygame.Rect(px+2,py+42,pw-4,ph-90)
        self.screen.set_clip(clip)
        y=py+48-self._scroll_y

        if not records:
            m=self.fb.render(f'No records for "{self._stats_player}"',True,C_DIM)
            self.screen.blit(m,m.get_rect(centerx=px+pw//2,top=y+20))
        else:
            total=len(records); comp=[r for r in records if r['completed']]
            ts=ST.get_player_total_score(self._stats_player)
            avg_t=sum(r['survival_time'] for r in records)/total
            th=ST.get_player_total_hits(self._stats_player)
            tsteps=sum(r['steps'] for r in records)
            y=self._section_title('Overview',px,pw,y)
            for fi,(lb,val) in enumerate([('Rounds Played',str(total)),
                ('Completed',f'{len(comp)} ({round(len(comp)/total*100)}%)'),
                ('Total Score',f'{int(ts):,}'),('Avg Round Time',f'{avg_t:.1f}s'),
                ('Total Ghost Hits',str(th)),('Total Steps',str(tsteps))]):
                draw_rounded_rect(self.screen,(26,26,58) if fi%2==0 else (20,20,40),(px+8,y-1,pw-16,17),3)
                lt=self.fsm.render(lb,True,C_GRAY); vt=self.fsm.render(val,True,C_CYAN)
                self.screen.blit(lt,(px+14,y)); self.screen.blit(vt,(px+pw-14-vt.get_width(),y)); y+=18
            y+=6
            y=self._section_title('Stage Clear Rate',px,pw,y)
            for stage in range(1,6):
                attempts=[r for r in records if r['stage']==stage and r['round']==1]
                clears  =[r for r in records if r['stage']==stage and r['is_stage_clear']]
                if not attempts: continue
                pct=round(len(clears)/len(attempts)*100)
                sr=attempts
                lb=self.fsm.render(f'Stage {stage}',True,C_DIM); self.screen.blit(lb,(px+10,y))
                bx2=px+68; bw2=pw-100
                pygame.draw.rect(self.screen,(13,13,34),(bx2,y+1,bw2,11),border_radius=4)
                if pct: pygame.draw.rect(self.screen,C_CYAN,(bx2,y+1,int(bw2*pct/100),11),border_radius=4)
                pt=self.fsm.render(f'{pct}%',True,C_CYAN); self.screen.blit(pt,(bx2+bw2+4,y)); y+=18

        self.screen.set_clip(None)
        back = self._buttons[0] if self._buttons else Button('Back','sec')
        back.set_rect(px+20, py+ph-46, pw-40)
        back.draw(self.screen, self.fbt)
        self._buttons = [back]

    # Main loop
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE)
                    self.panel.update_size(event.w, event.h)
                    self._bg_cache_sz = None
                else:
                    self.handle_event(event)
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
