"""EcHo MaZe — Data Analysis Window"""
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import stats as ST

DARK='#0a0a19'; PANEL='#12122e'; CYAN='#00e0ff'; GREEN='#00ff88'
GOLD='#ffd700'; ORANGE='#ff9900'; PURPLE='#c040ff'; RED='#ff4466'
GRAY='#888888'; WHITE='#ffffff'; GRID='#1a1a3a'

VIEWS = [
    'Summary Statistics Table',
    'Bar Chart — Avg Survival Time / Stage',
    'Line Graph — Avg Steps / Round',
    'Boxplot — Ghost Collisions / Round & Stage',
    'Scatter Plot — Steps vs Score',
    'Bar Chart — Stage Clear Rate / Stage',
]

def _style_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=GRAY, labelsize=9)
    for sp in ax.spines.values(): sp.set_color(GRID)
    if xlabel: ax.set_xlabel(xlabel, fontsize=10, color=GRAY, fontfamily='monospace')
    if ylabel: ax.set_ylabel(ylabel, fontsize=10, color=GRAY, fontfamily='monospace')
    if title:  ax.set_title(title, color=CYAN, fontsize=11, pad=10, fontfamily='monospace')
    ax.grid(color=GRID, linewidth=0.5, alpha=0.7, zorder=0)

def _no_data(ax):
    ax.set_facecolor(PANEL); ax.axis('off')
    ax.text(0.5, 0.5, 'No data yet — play a game first!',
            ha='center', va='center', color=GRAY,
            fontsize=11, fontfamily='monospace', transform=ax.transAxes)

def draw_summary(fig):
    records = ST.get_records()
    ax = fig.add_subplot(111); ax.set_facecolor(PANEL); ax.axis('off')
    ax.set_title('Summary Statistics — All Players', color=CYAN,
                 fontsize=12, fontfamily='monospace', pad=12)
    if not records: _no_data(ax); return
    features = [('survival_time','Survival Time (s)'), ('steps','Steps'),
                ('items','Items Collected'), ('ghost_hits','Ghost Collisions'),
                ('score','Score')]
    col_labels = ['Feature','Mean','Median','Min','Max','SD','N']
    rows = []
    for key, label in features:
        vals = [r[key] for r in records if isinstance(r[key], (int, float))]
        s = ST.summary_stats(vals)
        rows.append([label, f"{s['mean']:.2f}", f"{s['median']:.2f}",
                     f"{s['min']:.2f}", f"{s['max']:.2f}",
                     f"{s['sd']:.2f}", str(s['n'])] if s
                    else [label, '—', '—', '—', '—', '—', '0'])
    tbl = ax.table(cellText=rows, colLabels=col_labels, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1, 2.0)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_facecolor('#1a1a3a' if row % 2 == 0 else PANEL)
        cell.set_edgecolor(GRID)
        if row == 0:
            cell.set_facecolor('#0d0d30')
            cell.set_text_props(color=GRAY, fontfamily='monospace', fontweight='bold')
        else:
            cell.set_text_props(color=CYAN if col > 0 else WHITE, fontfamily='monospace')

def draw_bar_survival(fig):
    records = ST.get_records(); ax = fig.add_subplot(111)
    if not records: _no_data(ax); return
    stages = list(range(1, 6)); avgs = []; counts = []
    for s in stages:
        sr = [r for r in records if r['stage'] == s and r['completed']]
        avgs.append(sum(r['survival_time'] for r in sr) / len(sr) if sr else 0)
        counts.append(len(sr))
    bars = ax.bar(stages, avgs, color=[CYAN if v > 0 else GRID for v in avgs],
                  alpha=0.85, width=0.55, zorder=3, edgecolor='#005566', linewidth=1.2)
    mx = max(avgs) if any(avgs) else 1
    for bar, val, n in zip(bars, avgs, counts):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, val + mx*0.02, f'{val:.1f}s',
                    ha='center', va='bottom', color=WHITE,
                    fontsize=9, fontfamily='monospace', fontweight='bold')
            ax.text(bar.get_x() + bar.get_width()/2, val/2, f'n={n}',
                    ha='center', va='center', color='#003344',
                    fontsize=8, fontfamily='monospace')
    ax.set_xticks(stages); ax.set_xticklabels([f'Stage {s}' for s in stages])
    _style_ax(ax, 'Avg Survival Time per Stage', xlabel='Stage', ylabel='Avg Survival Time (s)')

def draw_line_steps(fig):
    records = ST.get_records(); ax = fig.add_subplot(111)
    if not records: _no_data(ax); return
    rounds = [1, 2, 3]; avg_steps = []; std_steps = []; counts = []
    for rnd in rounds:
        rr = [r for r in records if r['round'] == rnd]
        if rr:
            vals = [r['steps'] for r in rr]
            avg_steps.append(np.mean(vals)); std_steps.append(np.std(vals))
            counts.append(len(vals))
        else:
            avg_steps.append(None); std_steps.append(0); counts.append(0)
    xp = [r for r, v in zip(rounds, avg_steps) if v is not None]
    yp = [v for v in avg_steps if v is not None]
    sp = [s for s, v in zip(std_steps, avg_steps) if v is not None]
    if len(xp) > 1:
        ax.fill_between(xp, [y-s for y, s in zip(yp, sp)],
                        [y+s for y, s in zip(yp, sp)],
                        alpha=0.15, color=CYAN, label='±1 SD')
        ax.fill_between(xp, yp, alpha=0.10, color=CYAN)
    ax.plot(xp, yp, color=CYAN, linewidth=2.5, marker='o', markersize=9,
            markerfacecolor=GREEN, markeredgecolor=CYAN, zorder=4, label='Avg Steps')
    mx = max(yp) if yp else 1
    for x, y, n in zip(xp, yp, counts):
        ax.text(x, y + mx*0.05, f'{y:.1f}\n(n={n})',
                ha='center', va='bottom', color=WHITE,
                fontsize=8, fontfamily='monospace')
    ax.set_xticks(rounds); ax.set_xticklabels([f'Round {r}' for r in rounds])
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=WHITE, fontsize=9)
    _style_ax(ax, 'Avg Steps over Rounds', xlabel='Round', ylabel='Avg Steps')

def _make_boxplot(ax, box_data, box_labels, title):
    box_fc = ['#0d2040', '#0d2830', '#1a1030', '#1a0d30', '#0d1a30']
    box_ec = ['#0088dd', '#00aacc', '#6644cc', '#aa44cc', '#2266cc']
    bp = ax.boxplot(
        box_data, tick_labels=box_labels, patch_artist=True,
        medianprops=dict(color=CYAN, linewidth=2.5),
        whiskerprops=dict(color='#5588aa', linewidth=1.8, linestyle='--'),
        capprops=dict(color='#5588aa', linewidth=2),
        flierprops=dict(marker='D', markerfacecolor=ORANGE, markeredgecolor=RED,
                        markersize=6, alpha=0.85, linestyle='none'),
        meanprops=dict(marker='s', markerfacecolor=GREEN,
                       markeredgecolor=GREEN, markersize=6),
        showmeans=True, zorder=3,
    )
    for patch, fc, ec in zip(bp['boxes'],
                              box_fc[:len(box_data)],
                              box_ec[:len(box_data)]):
        patch.set_facecolor(fc); patch.set_edgecolor(ec); patch.set_linewidth(2)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax * 1.25)
    _style_ax(ax, title, ylabel='Ghost Hits')
    return bp


def _draw_stats_table(ax, stats_per, labels):
    ax.set_facecolor('#0d0d25')
    ax.axis('off')
    col_labels = ['', 'Mean', 'Median', 'Min', 'Max', 'SD', 'N']
    rows = []
    for s, lbl in zip(stats_per, labels):
        rows.append([lbl,
            f"{s['mean']:.2f}", f"{s['median']:.1f}",
            str(s['min']), str(s['max']),
            f"{s['sd']:.2f}", str(s['n'])])
    tbl = ax.table(cellText=rows, colLabels=col_labels,
                   loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    tbl.scale(1, 1.2)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(GRID)
        if row == 0:
            cell.set_facecolor('#0d0d30')
            cell.set_text_props(color=GRAY, fontfamily='monospace', fontweight='bold')
        elif col == 0:
            cell.set_facecolor('#1a1a3a')
            cell.set_text_props(color=WHITE, fontfamily='monospace')
        else:
            cell.set_facecolor('#12122e' if row % 2 == 0 else '#1a1a3a')
            cell.set_text_props(color=CYAN, fontfamily='monospace')


def draw_boxplot(fig):
    records = ST.get_records()
    if not records:
        ax = fig.add_subplot(111); _no_data(ax); return

    # เตรียมข้อมูล per Round
    rnd_data = []; rnd_labels = []; rnd_stats = []
    for rnd in [1, 2, 3]:
        vals = [r['ghost_hits'] for r in records if r['round'] == rnd]
        if vals:
            rnd_data.append(vals)
            rnd_labels.append(f'Round {rnd}')
            rnd_stats.append({
                'mean': np.mean(vals), 'median': np.median(vals),
                'min': int(np.min(vals)), 'max': int(np.max(vals)),
                'sd': np.std(vals), 'n': len(vals),
            })

    # เตรียมข้อมูล per Stage
    stg_data = []; stg_labels = []; stg_stats = []
    for stg in range(1, 6):
        vals = [r['ghost_hits'] for r in records if r['stage'] == stg]
        if vals:
            stg_data.append(vals)
            stg_labels.append(f'Stage {stg}')
            stg_stats.append({
                'mean': np.mean(vals), 'median': np.median(vals),
                'min': int(np.min(vals)), 'max': int(np.max(vals)),
                'sd': np.std(vals), 'n': len(vals),
            })

    if not rnd_data and not stg_data:
        ax = fig.add_subplot(111); _no_data(ax); return

    gs = fig.add_gridspec(2, 2, height_ratios=[3.2, 1], hspace=0.28, wspace=0.22)
    ax_rnd  = fig.add_subplot(gs[0, 0])
    ax_rtbl = fig.add_subplot(gs[1, 0])
    ax_stg  = fig.add_subplot(gs[0, 1])
    ax_stbl = fig.add_subplot(gs[1, 1])

    fig.subplots_adjust(left=0.06, right=0.97, top=0.88, bottom=0.08)

    if rnd_data:
        _make_boxplot(ax_rnd, rnd_data, rnd_labels, 'Ghost Collisions per Round')
        _draw_stats_table(ax_rtbl, rnd_stats, rnd_labels)
    else:
        _no_data(ax_rnd); ax_rtbl.axis('off')

    if stg_data:
        _make_boxplot(ax_stg, stg_data, stg_labels, 'Ghost Collisions per Stage')
        _draw_stats_table(ax_stbl, stg_stats, stg_labels)
    else:
        _no_data(ax_stg); ax_stbl.axis('off')

def draw_scatter(fig):
    records = ST.get_records(); ax = fig.add_subplot(111)
    if not records: _no_data(ax); return
    pts = [(r['steps'], r['score'], r['stage']) for r in records
           if r['steps'] > 0 and r['score'] > 0]
    if not pts: _no_data(ax); return
    for stage, color in zip(range(1, 6), [CYAN, GREEN, GOLD, ORANGE, PURPLE]):
        sp = [(x, y) for x, y, s in pts if s == stage]
        if sp:
            xs, ys = zip(*sp)
            ax.scatter(xs, ys, color=color, alpha=0.75, s=45, zorder=3,
                       label=f'Stage {stage}', edgecolors='none')
    all_x = [x for x, y, s in pts]; all_y = [y for x, y, s in pts]
    if len(all_x) > 2:
        z = np.polyfit(all_x, all_y, 1); p = np.poly1d(z)
        xl = np.linspace(min(all_x), max(all_x), 100)
        ax.plot(xl, p(xl), color=WHITE, linewidth=1.5,
                linestyle='--', alpha=0.5, label='Trend (all)')
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=WHITE, fontsize=9, ncol=2)
    _style_ax(ax, 'Steps vs Score (colored by Stage)', xlabel='Steps', ylabel='Score')

def draw_clear_rate(fig):
    records = ST.get_records(); ax = fig.add_subplot(111)
    if not records: _no_data(ax); return
    stages = list(range(1, 6)); pcts = []; att_n = []; clr_n = []
    for s in stages:
        att = [r for r in records if r['stage'] == s and r['round'] == 1]
        clr = [r for r in records if r['stage'] == s and r['is_stage_clear']]
        pct = round(len(clr) / len(att) * 100) if att else 0
        pcts.append(pct); att_n.append(len(att)); clr_n.append(len(clr))
    ax.barh(stages, pcts,
            color=[GREEN if p == 100 else CYAN if p >= 50 else RED for p in pcts],
            alpha=0.85, height=0.5, zorder=3, edgecolor='#003322', linewidth=1)
    for s, pct, na, nc in zip(stages, pcts, att_n, clr_n):
        ax.text(pct + 1, s, f'  {pct}%  ({nc}/{na} attempts)',
                va='center', color=WHITE, fontsize=9, fontfamily='monospace')
    ax.set_yticks(stages); ax.set_yticklabels([f'Stage {s}' for s in stages])
    ax.set_xlim(0, 130)
    ax.axvline(x=50,  color=GRAY,  linewidth=1, linestyle=':', alpha=0.5)
    ax.axvline(x=100, color=GREEN, linewidth=1, linestyle=':', alpha=0.5)
    legend_items = [
        mpatches.Patch(facecolor=GREEN, label='100% — Perfect'),
        mpatches.Patch(facecolor=CYAN,  label='50–99%'),
        mpatches.Patch(facecolor=RED,   label='< 50%'),
    ]
    ax.legend(handles=legend_items, facecolor=PANEL, edgecolor=GRID,
              labelcolor=WHITE, fontsize=9, loc='lower right')
    _style_ax(ax, 'Stage Clear Rate — % of Stages Cleared', xlabel='Clear Rate (%)')


RENDERERS = {
    VIEWS[0]: draw_summary,
    VIEWS[1]: draw_bar_survival,
    VIEWS[2]: draw_line_steps,
    VIEWS[3]: draw_boxplot,
    VIEWS[4]: draw_scatter,
    VIEWS[5]: draw_clear_rate,
}

def open_data_window():
    root = tk.Tk()
    root.title('EcHo MaZe — Data Analysis')
    root.configure(bg=DARK)
    root.geometry('960x640')
    root.minsize(720, 500)

    header = tk.Frame(root, bg=PANEL, pady=10)
    header.pack(fill='x')
    tk.Label(header, text='EcHo MaZe  —  Data Analysis',
             bg=PANEL, fg=CYAN,
             font=('Courier New', 14, 'bold')).pack(side='left', padx=16)

    ctrl = tk.Frame(root, bg=DARK, pady=8)
    ctrl.pack(fill='x', padx=14)
    tk.Label(ctrl, text='View:', bg=DARK, fg=GRAY,
             font=('Courier New', 10)).pack(side='left', padx=(0, 6))

    selected = tk.StringVar(value=VIEWS[0])
    style = ttk.Style(); style.theme_use('clam')
    style.configure('Dark.TCombobox',
                    fieldbackground=PANEL, background=PANEL, foreground=CYAN,
                    selectbackground=PANEL, selectforeground=CYAN, arrowcolor=CYAN,
                    bordercolor=GRID, lightcolor=GRID, darkcolor=GRID,
                    font=('Courier New', 10))
    style.map('Dark.TCombobox',
              fieldbackground=[('readonly', PANEL)],
              foreground=[('readonly', CYAN)])

    combo = ttk.Combobox(ctrl, textvariable=selected, values=VIEWS,
                         state='readonly', style='Dark.TCombobox',
                         font=('Courier New', 10), width=48)
    combo.pack(side='left')

    refresh_btn = tk.Button(ctrl, text='↻  Refresh', bg=PANEL, fg=GREEN,
                            font=('Courier New', 10, 'bold'), bd=0,
                            padx=12, pady=2, activebackground=GRID,
                            activeforeground=GREEN, cursor='hand2', relief='flat')
    refresh_btn.pack(side='left', padx=10)

    # legend inline ชิดขวา — แสดงเฉพาะตอนเลือก Boxplot view
    legend_frame = tk.Frame(ctrl, bg=DARK)
    legend_frame.pack(side='right', padx=(0, 10))

    _LEGEND_ITEMS = [
        ('▬', CYAN,      'Median'),
        ('■', GREEN,     'Mean'),
        ('◆', ORANGE,    'Outlier'),
        ('□', '#0088dd', 'IQR Box'),
    ]
    legend_labels = []
    for sym, col, txt in _LEGEND_ITEMS:
        lbl = tk.Label(legend_frame, text=f'{sym} {txt}',
                       bg=DARK, fg=col, font=('Courier New', 9))
        legend_labels.append(lbl)

    def _update_legend_visibility(*_):
        is_boxplot = 'Boxplot' in selected.get()
        for lbl in legend_labels:
            if is_boxplot:
                lbl.pack(side='left', padx=5)
            else:
                lbl.pack_forget()

    selected.trace_add('write', _update_legend_visibility)
    _update_legend_visibility()

    fig = plt.Figure(facecolor=DARK, tight_layout=True)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().configure(bg=DARK)
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=14, pady=(0, 4))

    # insight label
    insight_label = tk.Label(
        root, text='', bg=PANEL, fg=CYAN,
        font=('Courier New', 9), anchor='w',
        justify='left', wraplength=900, pady=5, padx=12
    )
    insight_label.pack(fill='x', padx=14, pady=(0, 8))

    def _calc_insight(view: str, records: list) -> str:
        if not records:
            return 'No data yet — play a game to generate statistics.'

        if 'Summary' in view:
            n = len(records)
            players = len({r['player'] for r in records})
            stages_played = len({r['stage'] for r in records})
            avg_hits = sum(r['ghost_hits'] for r in records) / n
            return (f'Total: {n} rounds recorded across {players} player(s) and {stages_played} stage(s).  '
                    f'Avg ghost hits per round: {avg_hits:.2f}')

        elif 'Survival' in view:
            stages = range(1, 6)
            avgs = {}
            for s in stages:
                sr = [r['survival_time'] for r in records if r['stage'] == s and r['completed']]
                if sr: avgs[s] = sum(sr) / len(sr)
            if not avgs:
                return 'No completed rounds yet.'
            best  = max(avgs, key=avgs.get)
            worst = min(avgs, key=avgs.get)
            ratio = avgs[best] / avgs[worst] if avgs[worst] > 0 else 0
            return (f'Stage {best} has the highest avg survival time ({avgs[best]:.1f}s).  '
                    f'Stage {worst} is the fastest ({avgs[worst]:.1f}s). Difference Ratio: {ratio:.1f} x')

        elif 'Steps' in view and 'Score' not in view:
            avgs = {}
            for rnd in [1, 2, 3]:
                rr = [r['steps'] for r in records if r['round'] == rnd]
                if rr: avgs[rnd] = sum(rr) / len(rr)
            if len(avgs) < 2:
                return 'Not enough round data to compare.'
            r1_avg = avgs.get(1, 0)
            r2_avg = avgs.get(2, 0)
            r3_avg = avgs.get(3, 0)
            mn, mx = min(avgs.values()), max(avgs.values())
            change = ((mx - mn) / mn * 100) if mn > 0 else 0
            if r2_avg < r1_avg and r3_avg > r2_avg:
                trend_desc = f'Steps dip at Round 2 ({r2_avg:.1f}) then rise at Round 3 ({r3_avg:.1f})'
            elif r3_avg > r1_avg:
                trend_desc = f'Steps increase from Round 1 ({r1_avg:.1f}) to Round 3 ({r3_avg:.1f})'
            else:
                trend_desc = f'Steps decrease from Round 1 ({r1_avg:.1f}) to Round 3 ({r3_avg:.1f})'
            return (f'{trend_desc}.  '
                    f'Overall range: {change:.1f}% — players adjust movement when ghosts appear.')

        elif 'Boxplot' in view:
            r1 = [r['ghost_hits'] for r in records if r['round'] == 1]
            r3 = [r['ghost_hits'] for r in records if r['round'] == 3]
            s_hits = {s: [r['ghost_hits'] for r in records if r['stage'] == s] for s in range(1, 6)}
            s_hits = {s: v for s, v in s_hits.items() if v}
            parts = []
            if r1 and r3:
                m1, m3 = sum(r1)/len(r1), sum(r3)/len(r3)
                if m1 > 0:
                    parts.append(f'Round 3 avg hits ({m3:.2f}) is {m3/m1:.1f}× higher than Round 1 ({m1:.2f}).')
                else:
                    parts.append(f'Round 1 avg hits = 0 — ghosts only appear from Round 2 onward.  Round 3 avg: {m3:.2f}.')
            if s_hits:
                hardest = max(s_hits, key=lambda s: sum(s_hits[s])/len(s_hits[s]))
                easiest = min(s_hits, key=lambda s: sum(s_hits[s])/len(s_hits[s]))
                h_avg = sum(s_hits[hardest])/len(s_hits[hardest])
                e_avg = sum(s_hits[easiest])/len(s_hits[easiest])
                parts.append(f'Stage {hardest} has most ghost hits on avg ({h_avg:.2f}) — Stage {easiest} is easiest ({e_avg:.2f}).')
            return '  '.join(parts) if parts else 'Not enough data.'

        elif 'Scatter' in view:
            pts = [(r['steps'], r['score']) for r in records if r['steps'] > 0 and r['score'] > 0]
            if len(pts) < 3:
                return 'Not enough data points for correlation analysis.'
            import numpy as np
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            r = np.corrcoef(xs, ys)[0, 1]
            direction = 'negative' if r < 0 else 'positive'
            strength = 'strong' if abs(r) > 0.6 else 'moderate' if abs(r) > 0.3 else 'weak'
            return (f'Correlation (r = {r:.2f}): {strength} {direction} relationship.  '
                    f'{"Fewer steps → higher score — efficient routing pays off." if r < -0.3 else "Step count has little impact on score."}')

        elif 'Clear' in view:
            pcts = {}
            for s in range(1, 6):
                att = [r for r in records if r['stage'] == s and r['round'] == 1]
                clr = [r for r in records if r['stage'] == s and r['is_stage_clear']]
                if att: pcts[s] = len(clr) / len(att) * 100
            if not pcts:
                return 'No stage attempt data yet.'
            best  = max(pcts, key=pcts.get)
            worst = min(pcts, key=pcts.get)
            perfect = [s for s, p in pcts.items() if p == 100]
            parts = [f'Stage {worst} is hardest ({pcts[worst]:.0f}% clear rate).']
            if perfect:
                parts.append(f'Stage(s) {", ".join(map(str, perfect))} cleared perfectly (100%).')
            return '  '.join(parts)

        return ''

    def refresh(*_):
        fig.clear()
        records = ST.get_records()
        renderer = RENDERERS.get(selected.get(), draw_summary)
        renderer(fig)
        canvas.draw()
        insight = _calc_insight(selected.get(), records)
        insight_label.config(text=f'  ▸  {insight}' if insight else '')

    combo.bind('<<ComboboxSelected>>', refresh)
    refresh_btn.config(command=refresh)
    refresh()
    root.mainloop()

if __name__ == '__main__':
    open_data_window()

