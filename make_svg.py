# -*- coding: utf-8 -*-
"""
Regenerates dark_mode.svg and light_mode.svg (systemctl-style profile card).

Edit the CONTENT block below, then run:  python make_svg.py

Lines are aligned on a monospace grid by space padding, so edit the text here
rather than the SVG by hand. Element ids (age_data, account_age, repo_data,
contrib_data, star_data, commit_data, follower_data, loc_data, loc_add,
loc_del) are what today.py rewrites on every run -- keep them.
"""
import io
import os

CH = 9.588          # Consolas advance width @16px with size-adjust:109%
LH = 20             # line height
PAD = 15            # padding around the text block
HERE = os.path.dirname(os.path.abspath(__file__))

FONT_FACE = """@font-face {
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}"""


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Line:
    """One rendered line: a list of (class, text, id) segments."""

    def __init__(self):
        self.segs = []
        self.n = 0
        self.ocls = None

    def add(self, text, cls=None, eid=None):
        self.segs.append((cls, text, eid))
        self.n += len(text)
        return self

    def pad_to(self, width):
        if self.n < width:
            self.add(' ' * (width - self.n))
        return self

    def render(self, x, y):
        out = ['<tspan x="%d" y="%d"%s>' % (x, y, ' class="%s"' % self.ocls if self.ocls else '')]
        for cls, text, eid in self.segs:
            if cls is None and eid is None:
                out.append(esc(text))
            else:
                a = ''
                if cls:
                    a += ' class="%s"' % cls
                if eid:
                    a += ' id="%s"' % eid
                out.append('<tspan%s>%s</tspan>' % (a, esc(text)))
        out.append('</tspan>')
        return ''.join(out)


def L(*parts):
    """L('plain', ('text', 'cls'), ('text', 'cls', 'id')) -> Line"""
    ln = Line()
    for p in parts:
        if isinstance(p, str):
            ln.add(p)
        else:
            ln.add(p[0], p[1] if len(p) > 1 else None, p[2] if len(p) > 2 else None)
    return ln


def field(label, eid, value, reserve, lcls='b', vcls='w'):
    """label: <dot leader> value -- the leader absorbs today.py's re-justification.

    `reserve` must be today.py's justify_format length + 2 for that id.
    """
    core = label.rstrip()
    tail = ' ' * (len(label) - len(core))
    pad = reserve - len(value)
    return [(core, lcls), (':' + tail,),
            (' ' + '.' * max(0, pad - 2) + ' ', 'd', eid + '_dots'), (value, vcls, eid)]


def build(name, cols, lines, css, bg, fg, anim='', overlay='', radius=12):
    w = int(round(cols * CH)) + PAD * 2
    h = PAD + 17 + (len(lines) - 1) * LH + PAD + 4
    out = ["<?xml version='1.0' encoding='UTF-8'?>",
           '<svg xmlns="http://www.w3.org/2000/svg" '
           'font-family="ConsolasFallback,Consolas,monospace" '
           'width="%dpx" height="%dpx" font-size="16px">' % (w, h),
           '<style>', FONT_FACE, 'text, tspan {white-space: pre;}', css, anim, '</style>',
           '<rect width="%dpx" height="%dpx" fill="%s" rx="%d"/>' % (w, h, bg, radius),
           '<text x="%d" y="%d" fill="%s">' % (PAD, PAD + 17, fg)]
    y = PAD + 17
    for ln in lines:
        if ln is not None:
            out.append(ln.render(PAD, y))
        y += LH
    out.append('</text>')
    if overlay:
        out.append(overlay)
    out.append('</svg>')
    path = os.path.join(HERE, name)
    io.open(path, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('%-16s %dx%d' % (name, w, h))


# ============================================================ CONTENT =======
USER, ORG, ROLE = 'nowte', 'nowtes', 'part time developer'
STATUS = 'my work centers on simplifying complexity and delivering efficient outcomes.'
FOUNDED = '2024-05-24'                       # nowtes founding date, matches today.py
LANGUAGES = 'Rust, Go, JavaScript'
HOBBIES = 'cybersecurity, artificial intelligence, backend systems'
TREE = [('1337', 'cargo run --release --bin recon'),
        (' 911', 'go run ./cmd/api'),
        (' 502', 'node inference-server.js'),
        (' 256', 'python3 today.py --profile'),
        (' 128', 'nowtes-cli setup --profile')]

CMD = ' $ systemctl status %s.service --no-pager' % USER


def sd(label):
    return [('%11s' % label, 'b'), (': ', 'd')]


def jrnl(t, unit, rest):
    return [('Aug 25 %s github ' % t, 'd'), (unit, 'm'), (': ', 'd')] + rest


S = [L((CMD, 'w')), None]
S.append(L(('● ', 'dot'), ('%s.service' % USER, 'b'), (' - ', 'd'),
           (ROLE, 'w'), (' @ ', 'd'), (ORG, 'w')))
S.append(L(*(sd('Loaded') + [('loaded ', 'w'),
             ('(/etc/systemd/system/%s.service; ' % USER, 'd'),
             ('enabled', 'w'), ('; preset: enabled)', 'd')])))
S.append(L(*(sd('Active') + [('active (running)', 'b'), (' since %s; ' % FOUNDED, 'd'),
             ('1 year, 3 months, 1 day', 'w', 'age_data'), (' ago', 'd')])))
S.append(L(*(sd('Docs') + [('man:%s(1)' % USER, 'm')])))
S.append(L('             ', ('https://github.com/%s' % USER, 'm')))
S.append(L(*(sd('Main PID') + [('1337', 'w'), (' (%s)' % USER, 'd')])))
S.append(L(*(sd('Status') + [('"%s"' % STATUS, 'w')])))
S.append(L(*(sd('Tasks') + [('95', 'w', 'repo_data'), (' repos ', 'd'), ('(limit: ', 'd'),
             ('133', 'w', 'contrib_data'), (' contributed)', 'd')])))
S.append(L(*(sd('Memory') + [('446,276', 'w', 'loc_data'), (' lines ', 'd'), ('(peak: ', 'd'),
             ('523,178', 'w', 'loc_add'), (', freed: ', 'd'),
             ('76,902', 'm', 'loc_del'), (')', 'd')])))
S.append(L(*(sd('CPU') + [('5y 9m 22d', 'w', 'account_age'), (' on GitHub', 'd')])))
S.append(L(*(sd('CGroup') + [('/system.slice/%s.service' % USER, 'd')])))
for i, (pid, cmd) in enumerate(TREE):
    br = '└─' if i == len(TREE) - 1 else '├─'
    S.append(L('             ', (br, 'd'), (pid, 'm'), (' ',), (cmd, 'w')))
S.append(None)

J0 = len(S)                                  # first journal line, for the tail animation
S.append(L(*jrnl('04:12:07', 'systemd[1]', [('Started ', 'd'), (ROLE, 'w'), ('.', 'd')])))
S.append(L(*jrnl('04:12:07', '%s[1337]' % USER, field('stars', 'star_data', '342', 16))))
S.append(L(*jrnl('04:12:08', '%s[1337]' % USER, field('commits', 'commit_data', '2,116', 24))))
S.append(L(*jrnl('04:12:08', '%s[1337]' % USER, field('followers', 'follower_data', '196', 12))))
S.append(L(*jrnl('04:12:09', '%s[1337]' % USER, [('languages: ', 'b'), (LANGUAGES, 'w')])))
S.append(L(*jrnl('04:12:09', '%s[1337]' % USER, [('hobbies: ', 'b'), (HOBBIES, 'w')])))
S.append(L(*jrnl('04:12:10', 'systemd[1]', [('Reached target ', 'd'), ('Ship It', 'b'), ('.', 'd')])))
S.append(None)
S.append(L((' $ ', 'd')).add('█', 'cur'))

COLS = max(ln.n for ln in S if ln is not None)

# ---------------------------------------------------------- ANIMATION ------
# Every rule uses `backwards` fill and a visible base state, so a renderer that
# ignores CSS animation still shows the finished card instead of a blank box.
TYPE_DUR, BODY_T0, BODY_STEP, JRNL_T0, JRNL_STEP = 1.0, 1.10, 0.045, 1.90, 0.13
anim = ['@keyframes fx{from{opacity:0}to{opacity:1}}',
        '@keyframes bl{0%,49%{opacity:1}50%,100%{opacity:0}}',
        '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}',
        '@keyframes type{from{transform:translateX(0)}}',
        '.cur{animation:bl 1.06s steps(1) infinite;}',
        '.dot{font-weight:bold;animation:pulse 2.4s ease-in-out infinite;}']
for i, ln in enumerate(S):
    if ln is None or i == 0:
        continue
    t = (BODY_T0 + (i - 2) * BODY_STEP) if i < J0 else (JRNL_T0 + (i - J0) * JRNL_STEP)
    ln.ocls = 'l%d' % i
    anim.append('.l%d{animation:fx .2s ease-out %.2fs backwards;}' % (i, t))

TW = int(round(len(CMD) * CH))               # cover slides right to "type" the command
anim.append('.typer{transform:translateX(%dpx);animation:type %.2fs steps(%d) backwards;}'
            % (TW, TYPE_DUR, len(CMD)))
ANIM = '\n'.join(anim)

# ------------------------------------------------------------- THEMES ------
THEMES = {
    'dark_mode.svg':  dict(bg='#0a0a0a', fg='#c8c8c8', d='#585858', b='#ffffff',
                           w='#f2f2f2', m='#8a8a8a', hi='#ffffff'),
    'light_mode.svg': dict(bg='#ffffff', fg='#3a3a3a', d='#a8a8a8', b='#000000',
                           w='#1a1a1a', m='#6e6e6e', hi='#000000'),
}

if __name__ == '__main__':
    for fname, t in THEMES.items():
        css = ('.d{fill:%(d)s;}\n.b{fill:%(b)s;font-weight:bold;}\n.w{fill:%(w)s;}\n'
               '.m{fill:%(m)s;}\n.cur,.dot{fill:%(hi)s;}' % t)
        overlay = ('<rect class="typer" x="%d" y="%d" width="%d" height="22" fill="%s"/>'
                   % (PAD, PAD + 2, TW, t['bg']))
        build(fname, COLS, S, css, t['bg'], t['fg'], anim=ANIM, overlay=overlay)
