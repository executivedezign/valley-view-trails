"""Builds the Macro Exposure field manual as a PDF.

Kept in the repo so the manual can be regenerated whenever the app changes,
rather than drifting out of date as a hand-made document would.
"""
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image, KeepTogether)

OUT = '/home/user/valley-view-trails/macro/Macro-Exposure-Manual.pdf'
ICON = '/home/user/valley-view-trails/macro/icon-512.png'

INK = colors.HexColor('#1b2220')
MUTED = colors.HexColor('#5d6b66')
ACCENT = colors.HexColor('#1f6b52')
RULE = colors.HexColor('#cfd8d4')
BAND = colors.HexColor('#eef3f1')
WARN = colors.HexColor('#8a5a10')

ss = getSampleStyleSheet()
S = {}
S['title'] = ParagraphStyle('title', parent=ss['Title'], fontName='Helvetica-Bold',
                            fontSize=26, leading=30, textColor=INK, alignment=TA_LEFT,
                            spaceAfter=4)
S['sub'] = ParagraphStyle('sub', parent=ss['Normal'], fontName='Helvetica',
                          fontSize=12, leading=16, textColor=MUTED, spaceAfter=18)
S['h1'] = ParagraphStyle('h1', parent=ss['Heading1'], fontName='Helvetica-Bold',
                         fontSize=15, leading=19, textColor=ACCENT,
                         spaceBefore=13, spaceAfter=6)
S['h2'] = ParagraphStyle('h2', parent=ss['Heading2'], fontName='Helvetica-Bold',
                         fontSize=11.5, leading=15, textColor=INK,
                         spaceBefore=9, spaceAfter=4)
S['p'] = ParagraphStyle('p', parent=ss['Normal'], fontName='Helvetica',
                        fontSize=9.8, leading=13.8, textColor=INK, spaceAfter=6)
S['li'] = ParagraphStyle('li', parent=S['p'], leftIndent=13, bulletIndent=3, spaceAfter=4)
S['note'] = ParagraphStyle('note', parent=S['p'], fontSize=9.3, leading=13.4,
                           textColor=WARN, leftIndent=9, rightIndent=9,
                           spaceBefore=5, spaceAfter=9, borderPadding=7)
S['form'] = ParagraphStyle('form', parent=S['p'], fontName='Courier-Bold', fontSize=10.5,
                           leading=15, textColor=ACCENT, leftIndent=10,
                           spaceBefore=3, spaceAfter=8)
S['cap'] = ParagraphStyle('cap', parent=S['p'], fontSize=8.6, leading=12, textColor=MUTED)


def P(t, s='p'):
    return Paragraph(t, S[s])


def bullets(items):
    """Appends straight into the story, since a list of flowables cannot be
    handed to list.append in one go."""
    for t in items:
        story.append(Paragraph(t, S['li'], bulletText='\u2022'))


def note(t):
    return Table([[Paragraph(t, S['note'])]], colWidths=[6.5 * inch],
                 style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fdf6e8')),
                                   ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#e0c68b')),
                                   ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                   ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                   ('TOPPADDING', (0, 0), (-1, -1), 2),
                                   ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))


def table(rows, widths, align_right=()):
    cell = ParagraphStyle('cell', parent=S['p'], fontSize=9, leading=12.4, spaceAfter=0)
    head = ParagraphStyle('head', parent=cell, fontName='Helvetica-Bold', textColor=colors.white)
    data = [[Paragraph(c, head) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(c, cell) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [('BACKGROUND', (0, 0), (-1, 0), ACCENT),
          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('GRID', (0, 0), (-1, -1), 0.4, RULE),
          ('LEFTPADDING', (0, 0), (-1, -1), 6),
          ('RIGHTPADDING', (0, 0), (-1, -1), 6),
          ('TOPPADDING', (0, 0), (-1, -1), 5),
          ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]
    for i in range(2, len(data), 2):
        st.append(('BACKGROUND', (0, i), (-1, i), BAND))
    for c in align_right:
        st.append(('ALIGN', (c, 0), (c, -1), 'RIGHT'))
    t.setStyle(TableStyle(st))
    return t


def chrome(canvas, doc):
    canvas.saveState()
    w, h = LETTER
    if doc.page > 1:
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(1 * inch, h - 0.62 * inch, 'MACRO EXPOSURE — FIELD MANUAL')
        canvas.drawRightString(w - 1 * inch, h - 0.62 * inch, 'Canon EOS R5 · Laowa macro set')
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(1 * inch, h - 0.72 * inch, w - 1 * inch, h - 0.72 * inch)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(w / 2, 0.55 * inch, str(doc.page))
    canvas.restoreState()


story = []
A = story.append

# ---------------------------------------------------------------- cover
A(Spacer(1, 0.5 * inch))
_ic = Image(ICON, width=1.15 * inch, height=1.15 * inch)
_ic.hAlign = 'LEFT'
A(_ic)
A(Spacer(1, 0.28 * inch))
A(P('Macro Exposure', 'title'))
A(P('Field manual &middot; Canon EOS R5 with the Laowa macro set', 'sub'))
A(P('This app answers the four questions that manual macro work keeps asking and that '
    'nothing on the camera will tell you: what aperture the sensor is <i>actually</i> seeing, '
    'how thin the plane of focus has become, how far to advance the rail, and how much flash '
    'power the last change just cost you.'))
A(P('It runs entirely on the phone. No network, no GPS, no permissions, no account. Once the '
    'page has loaded it works in a cellar or a swamp with the phone in airplane mode.'))
A(Spacer(1, 0.18 * inch))
A(table([['Where it lives', 'What it needs'],
         ['executivedezign.github.io/valley-view-trails/macro/',
          'Any phone browser. Nothing else.']], [3.6 * inch, 2.9 * inch]))
A(Spacer(1, 0.3 * inch))
A(P('<b>Install it properly.</b> Open the link in Safari, then Share &rsaquo; Add to Home Screen. '
    'That gives you an icon, full screen, and a copy cached on the phone so it opens without '
    'a signal. Settings are remembered between sessions.', 'p'))
A(P('Everything in this manual describes the app as built. The formulas are given in full at '
    'the end, so nothing here has to be taken on trust.', 'cap'))

# ---------------------------------------------------------------- the idea
A(PageBreak())
A(P('The one idea', 'h1'))
A(P('At macro magnifications the number on the aperture ring is close to fiction. Extending a '
    'lens to focus close moves the aperture further from the sensor, and the light spreads out '
    'over that extra distance. What reaches the sensor follows the <b>effective aperture</b>:'))
A(P('N<sub>eff</sub> = N &times; (1 + m/P)', 'form'))
A(P('where <i>N</i> is the marked f-number, <i>m</i> is magnification, and <i>P</i> is the '
    'lens’s pupil magnification. The light lost, in stops, is 2 &times; log<sub>2</sub>(1 + m/P).'))
A(P('Wide open, across your kit:'))
A(table([['Lens', 'Magnification', 'Marked', 'Effective', 'Light lost'],
         ['15mm f/4 Shift', '1:1', 'f/4', 'f/8', '2.0 stops'],
         ['24mm f/14 Probe', '2:1', 'f/14', 'f/42', '3.2 stops'],
         ['25mm Ultra', '2.5x', 'f/2.8', 'f/9.8', '3.6 stops'],
         ['25mm Ultra', '5x', 'f/2.8', 'f/16.8', '5.2 stops'],
         ['100mm f/2.8 APO', '2:1', 'f/2.8', 'f/7.3', '2.7 stops'],
         ['180mm f/4.5 APO', '1.5x', 'f/4.5', 'f/11.2', '2.6 stops'],
         ['Aurogon, NA 0.5', '20x', '—', 'f/21', '—'],
         ['Aurogon, NA 0.5', '50x', '—', 'f/51', '—']],
        [1.75 * inch, 1.25 * inch, 1.1 * inch, 1.15 * inch, 1.25 * inch]))
A(Spacer(1, 0.1 * inch))
A(P('The probe is the clearest case: f/14 is as wide as it opens, and at 2:1 that behaves like '
    'f/42. Four stops darker than the barrel says. This is why open shade on that lens needs '
    'ISO 3200 and it is not the meter being wrong.'))

A(P('What the light loss does and does not mean', 'h2'))
A(P('The R5 meters off the sensor. With a fully manual lens the meter is reading the light that '
    '<i>actually arrived</i>, so the loss is already in what the camera shows you. <b>It is not a '
    'correction to dial in.</b> Adding it again would overexpose by several stops.'))
A(P('It matters for three other things, all of which the app handles:'))
(bullets(['<b>Flash power</b> — manual flash cannot see through the lens, so the correction '
            'is yours to make.',
            '<b>ISO headroom</b> — knowing you are shooting at f/42 explains why ISO is climbing.',
            '<b>Diffraction and depth of field</b> — both follow the effective aperture, '
            'never the marked one.']))

A(P('Why the 100mm is different', 'h2'))
A(P('Most lenses are treated as symmetric, P = 1. The 100mm f/2.8 APO is not, and Laowa publishes '
    'its real losses: 1.7 stops at 1:1 and 2.7 at 2x. Those two figures fix P = 1.29, which '
    'reproduces both to within a twentieth of a stop and predicts everything in between. So that '
    'lens is modelled from measured data rather than theory, and it loses about a third of a stop '
    'less than the naive formula would claim.'))

# ---------------------------------------------------------------- shoot
A(PageBreak())
A(P('The Shoot tab', 'h1'))
A(P('Set three things: lens, magnification, aperture. Everything below updates.'))

A(P('Lens', 'h2'))
A(P('Six buttons. Choosing one loads that lens’s real limits, so the app will not offer you '
    'f/4 on the probe or 3x on the 180mm — and magnification clamps into range if the new lens '
    'cannot reach where you were.'))

A(P('Magnification', 'h2'))
A(P('A slider with a number field beside it. On the Aurogon it becomes four tube buttons, '
    'since that lens only does 10x, 20x, 35x and 50x.'))

A(P('Aperture', 'h2'))
A(P('Stepped in thirds through the range that lens actually has. On the Aurogon it becomes NA '
    'instead — eight detents from 0.5 to 0.15 — because a microscope objective is specified by '
    'numerical aperture. The app converts it with the working f-number, (1 + m) / 2NA.'))

A(P('What you get back', 'h2'))
A(table([['Reading', 'What it tells you'],
         ['Effective aperture', 'The headline figure, in the large type. What the sensor sees.'],
         ['Light lost', 'How many stops separate that from the barrel marking.'],
         ['Working distance', 'Front of lens to subject, at Laowa’s nearest documented '
                              'magnification — the app names which one it used.'],
         ['Airy disk', 'The diffraction blur diameter, in microns, against your 4.4 µm pixels.'],
         ['Scene light', 'The ambient EV at ISO 100 implied by your ISO and shutter.'],
         ['Handheld floor', 'The slowest shutter worth attempting, 1/(focal &times; (1 + m)). '
                            'Shake is magnified along with the subject.']],
        [1.6 * inch, 4.9 * inch]))

A(P('Diffraction', 'h2'))
A(P('Reported in three bands, not as a single threshold, because diffraction is not a cliff — '
    'it costs resolution steadily long before anyone would call a print soft.'))
(bullets(['<b>Not diffraction limited</b> — below about f/6.5 effective.',
            '<b>Softening at 100%, invisible in a print</b> — roughly f/6.5 to f/22.',
            '<b>Visible in print too</b> — past about f/22 effective.']))
A(note('Every lens in your kit is at or past the first threshold <i>wide open</i> at working '
       'magnification. That is not a fault and it is not avoidable. On this kit the question is '
       'never whether you are diffracted, only which compromise you would rather have — which '
       'is exactly the trade the Stack tab lets you price.'))


# ---------------------------------------------------------------- stack
A(PageBreak())
A(P('The Stack tab', 'h1'))
A(P('Depth of field at macro distances does not behave like the depth of field you are used to. '
    'It follows:'))
A(P('DoF = 2 &times; N<sub>eff</sub> &times; c / m<super>2</super>', 'form'))
A(P('Note the <i>m</i> squared. Doubling magnification quarters your depth of field, and no '
    'aperture on any of these lenses can buy that back.'))

A(P('Which circle of confusion', 'h2'))
A(P('The toggle offers two, and the choice is not cosmetic — it changes the answer roughly '
    'threefold.'))
(bullets(['<b>Print, 0.030 mm</b> — the traditional standard. Right if the picture ends up '
            'on a wall or a screen at sensible size.',
            '<b>Pixel level, 0.009 mm</b> — about two pixels on your 45 MP sensor. The honest '
            'figure if you inspect at 100%, and the one to stack by if you want it critically '
            'sharp everywhere.']))

A(P('Rail step and frame count', 'h2'))
A(P('Give it the depth of subject you need covered and it returns the step and the number of '
    'frames. Step is depth of field less the overlap, defaulting to 30%.'))
A(P('The overlap is not padding. Slices that merely touch leave visible banding where the sharp '
    'zones meet, because the edge of a depth of field is a gradual thing rather than a line. '
    'Thirty percent is the usual insurance; tighten it if a stack shows seams.'))

A(P('A worked example', 'h2'))
A(P('25mm Ultra at 5x, wide open at f/2.8, stacking a 3 mm subject:'))
A(table([['', 'Print (0.030 mm)', 'Pixel level (0.009 mm)'],
         ['Effective aperture', 'f/16.8', 'f/16.8'],
         ['Depth of field', '40 µm', '12 µm'],
         ['Rail step at 30%', '28 µm', '8.5 µm'],
         ['Frames for 3 mm', '108', '356']],
        [1.9 * inch, 2.3 * inch, 2.3 * inch], align_right=(1, 2)))
A(Spacer(1, 0.08 * inch))
A(P('Same subject, same settings, three times the work for the stricter standard. That is the '
    'decision the toggle is there to let you make deliberately rather than by accident.'))
A(note('The app warns when the step falls below about 5 µm, which is finer than most manual '
       'rails resolve — on the Aurogon that happens immediately, and at 20x the step is '
       'around 2 µm. That is motorised controller territory, not thumb and micrometer.'))

# ---------------------------------------------------------------- flash
A(PageBreak())
A(P('The Flash tab', 'h1'))
A(P('Five of your six lenses have no electronic contacts. The camera therefore has no aperture to '
    'work from, TTL cannot compute a correct exposure, and you are on manual power whether you '
    'wanted to be or not.'))
A(P('Guide numbers do not rescue you either: they are quoted in metres, and at a 20 mm working '
    'distance the arithmetic has left the range where it means anything.'))

A(P('So the app works from a baseline', 'h2'))
A(P('Get one frame right by eye. Then open the Flash tab, set <b>Power then</b> to the power you '
    'used, and press <b>Save current as baseline</b>. It records the magnification, the effective '
    'aperture and the ISO alongside it.'))
A(P('From that point on, change anything you like. <b>Power now</b> tells you what to set, and by '
    'how many stops the requirement moved:'))
A(P('&Delta;stops = 2 &times; log<sub>2</sub>(N<sub>now</sub> / N<sub>base</sub>) '
    '&minus; log<sub>2</sub>(ISO<sub>now</sub> / ISO<sub>base</sub>)', 'form'))
A(P('Power is displayed the way the Godox units display it — a fraction plus thirds, so '
    '&ldquo;1/4 +1/3&rdquo; is one third of a stop above quarter power.'))

A(P('Example', 'h2'))
A(P('Baseline: 100mm APO at 1:1, marked f/8, ISO 400, MF-12 twin at 1/16. Now you move to 2:1 '
    'and leave everything else alone. Effective aperture goes from f/14.2 to f/20.4 — just '
    'over a stop — so the app calls for 1/8. Nothing else on the camera changed, and nothing '
    'on the camera would have told you.'))

A(P('Shutter speed is deliberately not in that formula', 'h2'))
A(P('This is the part that trips people up, so it is worth being explicit. <b>Shutter speed does '
    'not affect flash exposure.</b> The pop lasts a fraction of a millisecond; below sync speed '
    'the whole of it lands in the frame whether you are at 1/60 or 1/200.'))
A(P('Shutter controls your <i>ambient</i> only. That is a feature: drag it to bring the background '
    'up or shut it down, without touching how the flash renders your subject.'))
A(note('<b>Sync is a hard wall.</b> The R5 syncs at 1/200 with the mechanical shutter and 1/250 '
       'with electronic first curtain, and will not fire flash at all on the fully electronic '
       'shutter. Go past it and a black band crosses the frame. The app refuses to hand you a '
       'setting beyond that rather than letting you find out later.'))

A(P('Continuous light', 'h2'))
A(P('Selecting the LED option turns the power maths off, because there is nothing to calculate — '
    'continuous light meters normally and the shutter is back in play. What the effective aperture '
    'still costs you is output, and at f/17 or f/42 the Lume Cubes and RM03s will be working hard. '
    'Expect long exposures on a rail.'))

# ---------------------------------------------------------------- lens reference
A(PageBreak())
A(P('Lens quick reference', 'h1'))
A(table([['Lens', 'Mag', 'Aperture', 'Working dist.', 'Contacts'],
         ['15mm f/4 Shift', 'to 1:1', 'f/4–f/32', '5 mm at 1:1', 'None'],
         ['24mm f/14 Probe', 'to 2:1', 'f/14–f/40', '20 mm at 2:1', 'None'],
         ['25mm Ultra', '2.5–5x', 'f/2.8–f/16', '40–45 mm', 'None'],
         ['100mm f/2.8 APO', 'to 2:1', 'f/2.8–f/22', '71 mm at 2x', '<b>Full</b>'],
         ['180mm f/4.5 APO', 'to 1.5x', 'f/4.5–f/32', '147 mm at 1.5x', 'None'],
         ['Aurogon', '10–50x', 'NA 0.5–0.15', '20 mm, fixed', 'None']],
        [1.55 * inch, 0.85 * inch, 1.2 * inch, 1.45 * inch, 1.45 * inch]))
A(Spacer(1, 0.12 * inch))
A(P('Working distance is front of lens to subject — the one you can judge. Minimum focus '
    'distance, quoted from the sensor plane, is always longer and less useful in the field. The '
    'app shows both.'))
A(P('The 100mm is the only lens here that meters, autoexposes, records EXIF and can drive TTL. '
    'When something behaves unexpectedly, check which lens you are on first.'))

A(P('Per-lens notes live in the app', 'h2'))
A(P('The bottom of the Shoot tab carries that lens’s handling notes — which ones shadow '
    'the subject, which need the hood removed, where IBIS must be switched off, which need the '
    'focal length entered by hand. They are drawn from your own settings reference so the app and '
    'your notes cannot disagree.'))

A(P('Warnings you may see', 'h1'))
(bullets(['<b>Past your ISO ceiling</b> — above 6400, the limit you set.',
            '<b>Slower than the handheld floor</b> — fine on a rail. Handheld, let the flash '
            'duration be your real shutter.',
            '<b>Aurogon</b> — electronic shutter only, IBIS off, remote release, hands off '
            'the camera entirely.',
            '<b>No electronic contacts</b> — on five of the six lenses nothing about the '
            'exposure reaches EXIF. Write it down if it matters.']))

A(P('Troubleshooting', 'h1'))
A(P('<b>The effective aperture looks alarming.</b> It is meant to. f/42 on the probe is correct, '
    'not a bug — it is the reason that lens needs so much light.'))
A(P('<b>It says I am diffracted wide open.</b> On this kit you usually are. Choose for depth of '
    'field instead and accept the softening; a stacked, slightly diffracted frame beats a sharp '
    'one with nothing in focus.'))
A(P('<b>The frame count is enormous.</b> Switch the circle of confusion to print, or stop down and '
    'take the diffraction. Both are legitimate, and the app shows what each costs.'))
A(P('<b>Flash power says beyond full.</b> You have run out of light. Raise ISO, open up, or move '
    'the heads closer — halving the distance is worth two stops.'))
A(P('<b>Nothing appears in EXIF.</b> Expected on five of six lenses. There are no contacts to '
    'carry it.'))

# ---------------------------------------------------------------- formulas
A(PageBreak())
A(P('The formulas, in full', 'h1'))
A(P('Nothing in the app is hidden. Every number on the screen comes from one of these.'))

A(P('Effective aperture', 'h2'))
A(P('N<sub>eff</sub> = N &times; (1 + m/P)', 'form'))
A(P('P = 1 for a symmetric lens, 1.29 for the 100mm APO, fitted to Laowa’s published losses.'))

A(P('Light lost', 'h2'))
A(P('stops = 2 &times; log<sub>2</sub>(1 + m/P)', 'form'))

A(P('Aurogon working f-number', 'h2'))
A(P('N<sub>eff</sub> = (1 + m) / (2 &times; NA)', 'form'))

A(P('Depth of field', 'h2'))
A(P('DoF = 2 &times; N<sub>eff</sub> &times; c / m<super>2</super>', 'form'))
A(P('c = 0.030 mm for print, 0.009 mm at pixel level on the R5’s 45 MP sensor.'))

A(P('Rail step and frames', 'h2'))
A(P('step = DoF &times; (1 &minus; overlap)<br/>frames = ceiling(depth / step) + 1', 'form'))

A(P('Diffraction', 'h2'))
A(P('Airy diameter = 2.44 &times; &lambda; &times; N<sub>eff</sub>,&nbsp;&nbsp;&lambda; = 550 nm', 'form'))
A(P('Compared against the R5 pixel pitch of 4.39 µm, and against the print circle of '
    'confusion for the second threshold.'))

A(P('Flash power change', 'h2'))
A(P('&Delta;stops = 2 &times; log<sub>2</sub>(N<sub>now</sub>/N<sub>base</sub>) '
    '&minus; log<sub>2</sub>(ISO<sub>now</sub>/ISO<sub>base</sub>)', 'form'))

A(P('Handheld floor', 'h2'))
A(P('shutter = 1 / (focal length &times; (1 + m))', 'form'))

A(P('Scene light', 'h2'))
A(P('EV<sub>100</sub> = log<sub>2</sub>(N<sub>eff</sub><super>2</super> / t) '
    '&minus; log<sub>2</sub>(ISO / 100)', 'form'))

A(Spacer(1, 0.25 * inch))
A(P('Camera figures used throughout: Canon EOS R5, 45 MP full frame, 4.39 µm pixel pitch, '
    'flash sync 1/200 mechanical and 1/250 with electronic first curtain, shutter 30 s to '
    '1/8000, ISO 100–51200. Lens specifications are taken from the owner’s Laowa and R5 '
    'settings reference.', 'cap'))

doc = SimpleDocTemplate(OUT, pagesize=LETTER,
                        leftMargin=1 * inch, rightMargin=1 * inch,
                        topMargin=0.95 * inch, bottomMargin=0.85 * inch,
                        title='Macro Exposure — Field Manual',
                        author='Nature’s Hidden Worlds',
                        subject='Canon EOS R5 with the Laowa macro set')
doc.build(story, onFirstPage=chrome, onLaterPages=chrome)
print('wrote', OUT)
