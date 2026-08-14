"""Builds the Macro Exposure field manual as a PDF.

Written as a how-to, not a reference: what to set, in what order, for the kinds
of shots this kit actually takes. The arithmetic is in an appendix at the back
for anyone who wants it, and nowhere else.

Kept in the repo so the manual can be regenerated when the app changes.
"""
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image)

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
                          fontSize=12, leading=16, textColor=MUTED, spaceAfter=16)
S['h1'] = ParagraphStyle('h1', parent=ss['Heading1'], fontName='Helvetica-Bold',
                         fontSize=15.5, leading=19, textColor=ACCENT,
                         spaceBefore=13, spaceAfter=5)
S['kick'] = ParagraphStyle('kick', parent=ss['Normal'], fontName='Helvetica-Oblique',
                           fontSize=10, leading=14, textColor=MUTED, spaceAfter=9)
S['h2'] = ParagraphStyle('h2', parent=ss['Heading2'], fontName='Helvetica-Bold',
                         fontSize=11.5, leading=15, textColor=INK,
                         spaceBefore=10, spaceAfter=4)
S['p'] = ParagraphStyle('p', parent=ss['Normal'], fontName='Helvetica',
                        fontSize=9.8, leading=13.9, textColor=INK, spaceAfter=6)
S['li'] = ParagraphStyle('li', parent=S['p'], leftIndent=14, bulletIndent=3, spaceAfter=4)
S['step'] = ParagraphStyle('step', parent=S['p'], leftIndent=20, bulletIndent=3,
                           spaceAfter=6, leading=14.2)
S['note'] = ParagraphStyle('note', parent=S['p'], fontSize=9.3, leading=13.4,
                           textColor=WARN, leftIndent=9, rightIndent=9,
                           spaceBefore=5, spaceAfter=9)
S['big'] = ParagraphStyle('big', parent=S['p'], fontSize=10.6, leading=15,
                          leftIndent=9, rightIndent=9, spaceBefore=6, spaceAfter=6)
S['cap'] = ParagraphStyle('cap', parent=S['p'], fontSize=8.6, leading=12, textColor=MUTED)

story = []
A = story.append


def P(t, s='p'):
    A(Paragraph(t, S[s]))


def bullets(items, style='li', bullet='•'):
    for t in items:
        A(Paragraph(t, S[style], bulletText=bullet))


def steps(items):
    for i, t in enumerate(items, 1):
        A(Paragraph(t, S['step'], bulletText='%d.' % i))


def _box(t, style, bg, edge):
    A(Table([[Paragraph(t, S[style])]], colWidths=[6.5 * inch],
            style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg),
                              ('BOX', (0, 0), (-1, -1), 0.6, edge),
                              ('LEFTPADDING', (0, 0), (-1, -1), 0),
                              ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                              ('TOPPADDING', (0, 0), (-1, -1), 3),
                              ('BOTTOMPADDING', (0, 0), (-1, -1), 3)])))


def note(t):
    _box(t, 'note', colors.HexColor('#fdf6e8'), colors.HexColor('#e0c68b'))


def key(t):
    _box(t, 'big', colors.HexColor('#eef5f1'), colors.HexColor('#a9c9ba'))


def table(rows, widths, align=()):
    cell = ParagraphStyle('cell', parent=S['p'], fontSize=9, leading=12.3, spaceAfter=0)
    head = ParagraphStyle('head', parent=cell, fontName='Helvetica-Bold', textColor=colors.white)
    data = [[Paragraph(c, head) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(c, cell) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [('BACKGROUND', (0, 0), (-1, 0), ACCENT),
          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('GRID', (0, 0), (-1, -1), 0.4, RULE),
          ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
          ('TOPPADDING', (0, 0), (-1, -1), 4.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5)]
    for i in range(2, len(data), 2):
        st.append(('BACKGROUND', (0, i), (-1, i), BAND))
    for c in align:
        st.append(('ALIGN', (c, 0), (c, -1), 'CENTER'))
    t.setStyle(TableStyle(st))
    A(t)


def chrome(canvas, doc):
    canvas.saveState()
    w, h = LETTER
    if doc.page > 1:
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(1 * inch, h - 0.62 * inch, 'MACRO EXPOSURE — HOW TO USE IT')
        canvas.drawRightString(w - 1 * inch, h - 0.62 * inch, 'Canon EOS R5 · Laowa macro set')
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(1 * inch, h - 0.72 * inch, w - 1 * inch, h - 0.72 * inch)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(w / 2, 0.55 * inch, str(doc.page))
    canvas.restoreState()


# ================================================================ cover
A(Spacer(1, 0.35 * inch))
_ic = Image(ICON, width=1.05 * inch, height=1.05 * inch)
_ic.hAlign = 'LEFT'
A(_ic)
A(Spacer(1, 0.24 * inch))
P('Macro Exposure', 'title')
P('How to use it &mdash; Canon EOS R5 with the Laowa macro set', 'sub')

P('You are in front of a subject. This tells you what to set, in what order, and '
  'what to do with what the app says back.')

P('The whole app exists because of one problem. When you focus close, your lens loses '
  'light &mdash; a lot of it, and more the closer you get. Your camera hides this from you: the '
  'ring still says f/2.8 while the sensor is getting f/7. Everything that goes wrong in macro '
  'follows from that gap. Photos come out dark. Depth of field vanishes. Flash power is a '
  'guess. Stacks come out soft no matter how carefully you focus.')

P('The app closes the gap. You tell it which lens, how close you are, and where the ring is '
  'set. It tells you what the sensor is really getting &mdash; and from that, how much will be '
  'in focus, how far to move the rail, and how much flash you need.')

A(Spacer(1, 0.1 * inch))
key('<b>If you read nothing else:</b><br/>'
    '<b>1.</b> The number in big type on the Shoot tab is your <i>real</i> aperture. Ignore the '
    'ring for every decision except where to physically set it.<br/>'
    '<b>2.</b> Depth of field on the Stack tab is how much of your subject will be sharp. '
    'If it is smaller than your subject, you are stacking or you are accepting soft.<br/>'
    '<b>3.</b> Get one flash exposure right, save it as your baseline, and the app corrects '
    'the power for you every time you change anything after that.')

A(Spacer(1, 0.12 * inch))
P('Open it at <b>executivedezign.github.io/valley-view-trails/macro/</b>, then Share &rsaquo; '
  'Add to Home Screen. It works with no signal and remembers your settings.', 'cap')

# ================================================================ step 1
A(PageBreak())
P('First: how close am I?', 'h1')
P('Everything in the app starts with magnification, and nobody can eyeball that. '
  'Here is the trick &mdash; magnification is just how wide your frame is.', 'kick')

P('Your sensor is 36 mm across. At 1x the frame is 36 mm wide. At 2x it is 18 mm. So look at '
  'your subject and ask how wide a strip of the world you are covering.')

table([['Set the app to', 'Frame is this wide', 'Which means'],
       ['0.5x', '72 mm', 'A small frog, a hawk moth, a whole large butterfly'],
       ['1x', '36 mm', 'A big beetle or dragonfly filling the frame'],
       ['1.5x', '24 mm', 'A honeybee with room around it'],
       ['2x', '18 mm', 'A honeybee filling the frame; a large beetle'],
       ['2.5x', '14 mm', 'A bumblebee head-on; a big hoverfly'],
       ['5x', '7 mm', 'A housefly filling the frame; a ladybird with room'],
       ['10x', '3.6 mm', 'An ant filling the frame; a large aphid'],
       ['20x', '1.8 mm', 'An aphid filling the frame; a springtail'],
       ['35x', '1 mm', 'A mite; part of a compound eye'],
       ['50x', '0.7 mm', 'Pollen grains; individual eye facets']],
      [1.2 * inch, 1.35 * inch, 3.95 * inch], align=(0, 1))

A(Spacer(1, 0.08 * inch))
P('Do not agonise over it. Being off by a tenth changes nothing that matters. If the fly fills '
  'your frame, you are at 5x &mdash; type 5 and move on.')

P('Which lens for which subject', 'h2')
table([['Subject', 'Lens', 'Why'],
       ['Anything alive and jumpy', '180mm APO',
        'Nearly 6 inches of working distance at 1.5x. You can get the shot without '
        'casting a shadow on it or spooking it.'],
       ['Live insects, general work', '100mm APO',
        'The only lens that meters and autoexposes. Easiest of the set, and 2&frac12; inches '
        'of room at 1:1.'],
       ['Very small, on a rail', '25mm Ultra',
        '2.5x to 5x. Nothing living will hold still for this &mdash; assume tripod and stack.'],
       ['Habitat with the subject in it', '15mm Shift',
        'Subject plus its whole surroundings. But 5 mm of working distance means your '
        'lens is nearly touching it.'],
       ['Into a hole, or underwater', '24mm Probe',
        'The only one that goes places. Very dark &mdash; see its own page.'],
       ['Dead or preserved specimens', 'Aurogon',
        '10x and up. Lab work, motorised rail, nothing alive.']],
      [1.65 * inch, 1.1 * inch, 3.75 * inch])

# ================================================================ step 2
A(PageBreak())
P('Second: where do I set the aperture ring?', 'h1')
P('This is the question the app really answers. Here is the short version so you do not '
  'have to work it out in the field.', 'kick')

P('Stopping down normally buys you depth of field. In macro it also multiplies the light loss '
  'and blurs the whole frame by diffraction &mdash; so past a point, stopping down makes the '
  'picture <i>worse</i> while feeling like it should help. Where that point sits depends on how '
  'close you are, which is why there is no single answer.')

P('Two honest choices, depending on what you are doing:')

table([['Lens and magnification', 'One frame, handheld', 'Stacking on a rail'],
       ['15mm Shift at 1:1', 'f/11', 'f/5.6'],
       ['24mm Probe at 2:1', 'f/14 &mdash; no choice', 'f/14 &mdash; no choice'],
       ['25mm Ultra at 2.5x', 'f/6.3', 'f/3.2'],
       ['25mm Ultra at 5x', 'f/3.5', 'f/2.8'],
       ['100mm APO at 1:1', 'f/13', 'f/6.3'],
       ['100mm APO at 2:1', 'f/9', 'f/4.5'],
       ['180mm APO at 1.5x', 'f/9', 'f/4.5'],
       ['Aurogon, any', 'NA 0.5', 'NA 0.5']],
      [2.3 * inch, 2.1 * inch, 2.1 * inch], align=(1, 2))

A(Spacer(1, 0.08 * inch))
P('<b>Handheld column:</b> you get one frame, so you need every scrap of depth and you accept '
  'the softening that comes with it. A slightly soft photo with the whole insect in it beats a '
  'crisp one with only an antenna sharp.')
P('<b>Stacking column:</b> you are taking fifty frames anyway, so each one should be as sharp as '
  'it can be. Depth comes from the stack, not the aperture. Open up, take more slices.')

note('<b>The probe is a special case.</b> f/14 is as wide as it opens, and at 2:1 that behaves '
     'like f/42. There is no decision to make &mdash; you are always wide open, always diffracted, '
     'always short of light. Plan for ISO 3200 and a light on it.')

P('If you are between magnifications, or on a lens and magnification not in the table, the app '
  'does it live: set the lens, magnification and aperture, and watch the big number. Keep it '
  'near <b>f/11</b> for stacking, and up to about <b>f/22</b> for a single handheld frame.')

# ================================================================ recipe: live insect
A(PageBreak())
P('Live insect, handheld, with flash', 'h1')
P('The bread-and-butter shot. 100mm or 180mm, twin flash, something that will not wait.', 'kick')

P('Set the camera once', 'h2')
bullets(['Mode <b>M</b>. Shutter <b>1/200</b>. ISO <b>400</b>.',
         'Flash on <b>manual</b> power, not TTL. Diffuser on.',
         'Electronic first curtain. MF peaking on. IS on (enter the focal length by hand '
         'on everything except the 100mm).'])
P('The shutter speed is not doing what you think. At 1/200 with flash in the dark, the flash '
  'burst is so brief that <i>it</i> is your real shutter &mdash; it freezes the insect and your '
  'own shake. That is why handheld at 2x is possible at all. Do not go faster than 1/200 '
  'looking for sharpness; you will just get a black band.')

P('Then, once', 'h2')
steps(['Frame your subject and read the width off the table on page 2. Type that '
       'magnification into the app.',
       'Set the ring where the table on page 3 says &mdash; f/13 for a 1:1 shot on the 100mm.',
       'Take a frame. Look at it. Adjust flash power until the exposure is right. '
       'Start around <b>1/32</b> and work from there.',
       'Open the <b>Flash</b> tab, set <b>Power then</b> to the power that worked, and press '
       '<b>Save current as baseline</b>.'])

key('That baseline is the whole point. From now on, when you move to 2x or change the '
    'aperture, glance at <b>Power now</b> and it tells you what to set the flash to. No test '
    'frames, no chimping, no working it out while the insect leaves.')

P('While you shoot', 'h2')
bullets(['<b>Changed magnification or aperture?</b> Check Power now. Usually it is a stop or so.',
         '<b>Want to know what will be sharp?</b> Stack tab, top number. At 1:1 and f/13 you '
         'have about 1.4 mm of depth &mdash; enough for an eye and not much else, so focus '
         'on the eye and let the rest go.',
         '<b>Nothing is sharp at all?</b> You are probably closer than you think. Depth of '
         'field falls off a cliff past 1:1.'])

note('<b>Twin flash arm position matters as much as power.</b> The app cannot see where your '
     'heads are pointed. If you move them significantly closer or further from the subject, '
     'your baseline is stale &mdash; take one test frame and save it again.')

# ================================================================ recipe: stacking
A(PageBreak())
P('Stacking on a rail', 'h1')
P('Anything that will hold still. This is where the app saves you the most work.', 'kick')

P('Set up', 'h2')
bullets(['Rail clamped to something heavy. <b>IBIS off</b> &mdash; on a rail it drifts the frame '
         'between slices and ruins the stack.',
         'Electronic first curtain, or fully electronic on the Aurogon. 2-second timer or a '
         'remote. Do not touch the camera.',
         'Aperture from the <b>stacking</b> column on page 3. Wider than feels right. Trust it.'])

P('Work out the slices', 'h2')
steps(['Set the lens and magnification in the app as usual.',
       'Guess how deep your subject is, front to back, in millimetres. A ladybird is about '
       '4 mm. A bee, maybe 8 mm through the thorax. Round up.',
       'Open the <b>Stack</b> tab and type that into <b>Subject depth</b>.',
       'It gives you a <b>rail step</b> and a <b>frame count</b>. Advance the rail by that '
       'step, that many times.'])

P('Print or pixel level?', 'h2')
P('The toggle changes the answer by about three times, so it is worth understanding once.')
bullets(['<b>Print</b> &mdash; you want a good photograph. Fewer frames, sharp at any normal '
         'viewing size.',
         '<b>Pixel level</b> &mdash; you want it critically sharp at 100% on screen, the way '
         'people pixel-peep macro. Three times the frames.'])
P('For a 3 mm subject at 5x, that is 108 frames against 356. Both are legitimate; just decide '
  'which one you are doing before you start, rather than discovering it afterwards.')

P('If the numbers look impossible', 'h2')
table([['Problem', 'What to do'],
       ['Hundreds of frames', 'Switch to the print standard, or stop down a little and accept '
                              'the softening. Both roughly halve the count.'],
       ['Step is a few microns',
        'Beyond a manual rail. Either drop to a lower magnification or use a motorised '
        'controller. On the Aurogon this is normal.'],
       ['Stack has visible bands',
        'Your slices did not overlap enough. Raise the overlap from 30% to 40% and redo it.']],
      [1.9 * inch, 4.6 * inch])

note('None of the Laowa lenses support the R5&rsquo;s in-camera focus bracketing &mdash; there '
     'is no focus motor for the camera to drive. The rail is the only way, which is exactly '
     'why the step number is worth having.')

# ================================================================ recipe: dark lenses
A(PageBreak())
P('The probe, and other dark situations', 'h1')
P('When there simply is not enough light and no aperture will fix it.', 'kick')

P('The 24mm probe at 2:1 behaves like f/42. That is roughly four stops darker than the ring '
  'suggests, and there is no wider setting. The 25mm at 5x is nearly as bad, at f/17 with the '
  'ring wide open.')

P('What that means in practice:')
bullets(['<b>Supplemental light is not optional.</b> The LED ring on the probe, or twin flash. '
          'Open shade with no light source will not get there.',
         '<b>ISO 3200 is a normal working value</b> on these, not a failure. Your R5 handles it.',
         '<b>Set the ring wide open and leave it.</b> There is nothing to gain by stopping down '
          'when you are already at f/42 effective.',
         '<b>Watch your own shadow.</b> At 20 mm working distance the lens blocks the light it '
          'needs. This is why the probe has a ring light built into the front.'])

P('Aurogon: 10x and beyond', 'h2')
bullets(['<b>NA 0.5 &mdash; widest &mdash; always.</b> It is your main light-gathering control, and '
         'stopping down costs resolution you cannot get back.',
         '<b>Fully electronic shutter, IBIS off, remote release.</b> At these magnifications a '
         'footstep across the room shows up.',
         '<b>Stacking is not optional.</b> At 20x you have about 3 microns of depth. Nothing is '
         'ever in focus in a single frame.',
         '<b>10x works outdoors on a tripod. 20x needs still air. 35x and 50x are indoor work '
         'on dead specimens</b> &mdash; do not fight this.'])

P('Continuous light instead of flash', 'h2')
P('With the Lume Cubes or the RM03 panels, select <b>Continuous LED</b> on the Flash tab and the '
  'power maths switches off &mdash; there is nothing to calculate, because your camera meter '
  'reads continuous light correctly.')
P('What does not go away is the light loss. At f/17 or f/42 effective, those panels are working '
  'hard, and you will be into exposures long enough to need the tripod. That is fine for a '
  'specimen and hopeless for anything alive.')

# ================================================================ troubleshooting
A(PageBreak())
P('When something looks wrong', 'h1')
P('Symptom first, since that is how you meet the problem.', 'kick')

table([['What you are seeing', 'What it is', 'Fix'],
       ['Photos are far too dark',
        'The light loss. You are shooting at several stops less than the ring says.',
        'Check the big number on Shoot. Add light, raise ISO, or get closer with the flash.'],
       ['Black band across the frame',
        'You went past flash sync.',
        '1/200 or slower. 1/250 only with electronic first curtain. Flash never fires on '
        'the fully electronic shutter.'],
       ['Almost nothing is in focus',
        'Depth of field is thinner than your subject.',
        'Stack tab tells you how thin. Either stack it, or back off to a lower '
        'magnification where there is more depth.'],
       ['Soft everywhere, even stacked',
        'Diffraction. You stopped down too far.',
        'Open up to the stacking column on page 3 and take more slices instead.'],
       ['Handheld shots are smeared',
        'Shutter, or the subject moving.',
        'Use flash and let the burst freeze it. Shutter speed alone will not save you '
        'at magnification.'],
       ['Flash exposure keeps drifting',
        'Your baseline is stale.',
        'Save a fresh one whenever you move the heads or change lenses.'],
       ['Frame drifts between stack slices',
        'IBIS is on.',
        'Turn it off whenever the camera is on a rail.'],
       ['No aperture recorded in the file',
        'Five of six lenses have no electrical contacts.',
        'Expected. Nothing to fix &mdash; note it yourself if it matters.'],
       ['Camera will not fire at all',
        'It thinks no lens is attached.',
        'Custom Functions &rsaquo; Release shutter without lens &rsaquo; Enable. '
        'Needed on every lens except the 100mm.']],
      [1.65 * inch, 1.85 * inch, 3.0 * inch])

P('What the app&rsquo;s warnings are telling you', 'h1')
table([['If the app says', 'Do this'],
       ['Not diffraction limited', 'Nothing. You have room to stop down further if you want depth.'],
       ['Softening at 100%, invisible in a print',
        'Carry on. This is the normal working state for macro and prints fine.'],
       ['Diffraction visible in print',
        'Only accept this on a single handheld frame where you need the depth. '
        'If you are stacking, open up.'],
       ['Past your ISO ceiling', 'Add light or open up before you raise ISO further.'],
       ['Slower than the handheld floor',
        'Either get on a tripod, or use flash and let the flash freeze it.']],
      [2.35 * inch, 4.15 * inch])


# ================================================================ appendix
A(PageBreak())
P('Appendix: the arithmetic', 'h1')
P('Only if you want it. Nothing here is needed to use the app.', 'kick')

P('<b>Effective aperture.</b> N<sub>eff</sub> = N &times; (1 + m/P), where N is the marked '
  'f-number, m is magnification, and P is pupil magnification &mdash; 1 for a symmetric lens, '
  '1.29 for the 100mm APO, fitted to the losses Laowa publishes for it (1.7 stops at 1:1, 2.7 '
  'at 2x). Light lost in stops is 2 &times; log<sub>2</sub>(1 + m/P).')

P('<b>Aurogon.</b> Specified by numerical aperture, so the working f-number is '
  '(1 + m) / (2 &times; NA).')

P('<b>Depth of field.</b> 2 &times; N<sub>eff</sub> &times; c / m<super>2</super>, with c the '
  'circle of confusion &mdash; 0.030 mm for print, 0.009 mm at pixel level on 45 MP. Note the m '
  'squared: double the magnification and depth of field quarters.')

P('<b>Rail step.</b> Depth of field less the overlap. Frames = depth &divide; step, plus one.')

P('<b>Diffraction.</b> The Airy disk is 2.44 &times; &lambda; &times; N<sub>eff</sub> across, at '
  '&lambda; = 550 nm, compared against the R5&rsquo;s 4.39 &micro;m pixels for the first '
  'threshold and the print circle of confusion for the second.')

P('<b>Flash power.</b> &Delta;stops = 2 &times; log<sub>2</sub>(N<sub>now</sub>/N<sub>base</sub>) '
  '&minus; log<sub>2</sub>(ISO<sub>now</sub>/ISO<sub>base</sub>). Shutter speed is absent because '
  'below sync the whole flash lands in the frame regardless &mdash; shutter controls ambient only.')

P('<b>Handheld floor.</b> 1 / (focal length &times; (1 + m)). Magnification amplifies your shake '
  'along with the subject.')

A(Spacer(1, 0.2 * inch))
P('Canon EOS R5: 45 MP full frame, 4.39 &micro;m pixels, flash sync 1/200 mechanical and 1/250 '
  'with electronic first curtain, 30 s to 1/8000, ISO 100&ndash;51200. Lens figures are from the '
  'owner&rsquo;s Laowa and R5 settings reference.', 'cap')

doc = SimpleDocTemplate(OUT, pagesize=LETTER,
                        leftMargin=1 * inch, rightMargin=1 * inch,
                        topMargin=0.95 * inch, bottomMargin=0.85 * inch,
                        title='Macro Exposure — How to use it',
                        subject='Canon EOS R5 with the Laowa macro set')
doc.build(story, onFirstPage=chrome, onLaterPages=chrome)
print('wrote', OUT)
