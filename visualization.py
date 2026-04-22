import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from stats import get_records, summary_stats

# Style
DARK_BG   = '#0a0a19'
PANEL_BG  = '#12122e'
CYAN      = '#00e0ff'
GREEN     = '#00ff88'
PURPLE    = '#c040ff'
GRAY      = '#888888'
WHITE     = '#ffffff'
GRID_COL  = '#1a1a3a'


def _apply_style(ax, title=''):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.spines[:].set_color(GRID_COL)
    ax.yaxis.label.set_color(GRAY)
    ax.xaxis.label.set_color(GRAY)
    if title:
        ax.set_title(title, color=CYAN, fontsize=9, pad=6,
                     fontfamily='monospace')
    ax.grid(color=GRID_COL, linewidth=0.5)


def show_data_analysis():
    records = get_records()
    if not records:
        fig, ax = plt.subplots(facecolor=DARK_BG)
        ax.set_facecolor(DARK_BG)
        ax.text(0.5, 0.5, 'No data yet — play a game first!',
                ha='center', va='center', color=GRAY,
                fontfamily='monospace', transform=ax.transAxes)
        ax.axis('off')
    import tempfile, os, subprocess, sys
    tmp = tempfile.mktemp(suffix='.png')
    plt.savefig(tmp, dpi=110, bbox_inches='tight', facecolor=DARK_BG)
    plt.close()
    try:
        if sys.platform == 'win32':
            os.startfile(tmp)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', tmp])
        else:
            subprocess.Popen(['xdg-open', tmp])
    except Exception as e:
        print(f'Cannot open chart: {e}')
        return

    fig = plt.figure(figsize=(14, 9), facecolor=DARK_BG)
    fig.canvas.manager.set_window_title('Echo Maze — Data Analysis Report')
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.4)

    # Summary Stats Table 
    ax_tbl = fig.add_subplot(gs[0, :])
    ax_tbl.set_facecolor(PANEL_BG)
    ax_tbl.axis('off')
    ax_tbl.set_title('Summary Statistics', color=CYAN, fontsize=9, pad=4,
                     fontfamily='monospace', loc='left')

    features = [
        ('survival_time', 'Survival Time (s)'),
        ('steps',         'Steps'),
        ('items',         'Items Collected'),
        ('ghost_hits',    'Ghost Collisions'),
        ('score',         'Score'),
    ]
    col_labels = ['Feature', 'Mean', 'Median', 'Min', 'Max', 'SD', 'N']
    rows_data = []
    for key, label in features:
        vals = [r[key] for r in records if isinstance(r[key], (int, float))]
        s = summary_stats(vals)
        if s:
            rows_data.append([
                label,
                f"{s['mean']:.2f}",
                f"{s['median']:.2f}",
                f"{s['min']:.2f}",
                f"{s['max']:.2f}",
                f"{s['sd']:.2f}",
                str(s['n']),
            ])
        else:
            rows_data.append([label, '—', '—', '—', '—', '—', '0'])

    tbl = ax_tbl.table(
        cellText=rows_data,
        colLabels=col_labels,
        loc='center',
        cellLoc='center',
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_facecolor(PANEL_BG if row % 2 == 0 else '#1a1a3a')
        cell.set_edgecolor(GRID_COL)
        cell.set_text_props(color=CYAN if col > 0 else WHITE,
                            fontfamily='monospace')
        if row == 0:
            cell.set_facecolor('#0d0d30')
            cell.set_text_props(color=GRAY, fontfamily='monospace')
    ax_tbl.set_xlim(0, 1)

    # Bar Chart: Avg survival time per stage
    ax_bar = fig.add_subplot(gs[1, 0])
    stages = list(range(1, 6))
    avgs = []
    for s in stages:
        sr = [r for r in records if r['stage'] == s and r['completed']]
        avgs.append(sum(r['survival_time'] for r in sr) / len(sr) if sr else 0)
    bars = ax_bar.bar(stages, avgs, color=CYAN, alpha=0.8, width=0.6)
    for bar, val in zip(bars, avgs):
        if val:
            ax_bar.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.3,
                        f'{val:.1f}s', ha='center', va='bottom',
                        color=WHITE, fontsize=7, fontfamily='monospace')
    ax_bar.set_xlabel('Stage', fontsize=8)
    ax_bar.set_ylabel('Avg Time (s)', fontsize=8)
    ax_bar.set_xticks(stages)
    _apply_style(ax_bar, 'Avg Survival Time / Stage')

    # Line Graph: Steps over rounds 
    ax_line = fig.add_subplot(gs[1, 1])
    rnd_labels = [1, 2, 3]
    avg_steps = []
    for rnd in rnd_labels:
        rr = [r for r in records if r['round'] == rnd]
        avg_steps.append(sum(r['steps'] for r in rr) / len(rr) if rr else None)
    x_plot = [r for r, v in zip(rnd_labels, avg_steps) if v is not None]
    y_plot = [v for v in avg_steps if v is not None]
    if len(x_plot) > 1:
        ax_line.fill_between(x_plot, y_plot, alpha=0.15, color=CYAN)
    ax_line.plot(x_plot, y_plot, color=CYAN, linewidth=2, marker='o',
                 markersize=5, markerfacecolor=GREEN)
    for xv, yv in zip(x_plot, y_plot):
        ax_line.text(xv, yv + max(y_plot)*0.04 if y_plot else yv,
                     f'{yv:.1f}', ha='center', va='bottom',
                     color=WHITE, fontsize=7, fontfamily='monospace')
    ax_line.set_xlabel('Round', fontsize=8)
    ax_line.set_ylabel('Avg Steps', fontsize=8)
    ax_line.set_xticks(rnd_labels)
    _apply_style(ax_line, 'Steps over Rounds')

    # Boxplot: Ghost collisions per round
    ax_box = fig.add_subplot(gs[1, 2])
    box_data = []
    box_labels = []
    for rnd in [1, 2, 3]:
        vals = [r['ghost_hits'] for r in records if r['round'] == rnd]
        if vals:
            box_data.append(vals)
            box_labels.append(f'R{rnd}')
    if box_data:
        bp = ax_box.boxplot(box_data, labels=box_labels, patch_artist=True,
                            medianprops=dict(color=CYAN, linewidth=2),
                            whiskerprops=dict(color=GRAY),
                            capprops=dict(color=GRAY),
                            flierprops=dict(marker='o', color=PURPLE,
                                            markersize=4, alpha=0.6))
        for patch in bp['boxes']:
            patch.set_facecolor('#0d2040')
            patch.set_edgecolor('#0088dd')
    _apply_style(ax_box, 'Ghost Collisions / Round')
    ax_box.set_ylabel('Hits', fontsize=8)

    # Scatter: Steps vs Score
    ax_sc = fig.add_subplot(gs[2, :2])
    pts = [(r['steps'], r['score']) for r in records
           if r['steps'] > 0 and r['score'] > 0]
    if pts:
        xs, ys = zip(*pts)
        ax_sc.scatter(xs, ys, color=CYAN, alpha=0.65, s=20)
        if len(xs) > 2:
            z = np.polyfit(xs, ys, 1)
            p = np.poly1d(z)
            xl = np.linspace(min(xs), max(xs), 100)
            ax_sc.plot(xl, p(xl), color=GREEN, linewidth=1.2,
                       linestyle='--', alpha=0.7)
    ax_sc.set_xlabel('Steps', fontsize=8)
    ax_sc.set_ylabel('Score', fontsize=8)
    _apply_style(ax_sc, 'Steps vs Score')

    # Completion rate per stage (horizontal bars) 
    ax_comp = fig.add_subplot(gs[2, 2])
    pcts = []
    for s in stages:
        sr = [r for r in records if r['stage'] == s]
        pcts.append(round(len([r for r in sr if r['completed']]) / len(sr) * 100)
                    if sr else 0)
    ax_comp.barh(stages, pcts, color=CYAN, alpha=0.75, height=0.5)
    for s, pct in zip(stages, pcts):
        ax_comp.text(pct + 1, s, f'{pct}%', va='center',
                     color=WHITE, fontsize=7, fontfamily='monospace')
    ax_comp.set_xlabel('Completion %', fontsize=8)
    ax_comp.set_yticks(stages)
    ax_comp.set_yticklabels([f'S{s}' for s in stages])
    ax_comp.set_xlim(0, 115)
    _apply_style(ax_comp, 'Completion Rate / Stage')

    plt.show()
