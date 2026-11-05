"""Generate the actual Vultr Agent Rush judges' deck from shipped BlastLab screenshots.

All screenshots come from the working app. All metrics and caveats come from
verified Vultr traces. No synthetic product screenshots or fabricated users.
"""
from pathlib import Path
from pptx import Presentation
from PIL import Image
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import MSO_AUTO_SIZE

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'submission'
OUT.mkdir(exist_ok=True)
SCREEN=ROOT/'docs'/'screenshots'
r=Presentation()
r.slide_width=Inches(13.333)
r.slide_height=Inches(7.5)
W=13.333;H=7.5
INK='101619';PANEL='182420';PANEL2='23362B';LINE='476552'
WHITE='F0F2EC';MUTED='B1C2B5';GREEN='ACF0D4';ORANGE='FF754A';DARK='24302C'
URL='https://blastlab.45-77-138-147.sslip.io/app'

def C(hex):return RGBColor.from_string(hex)
def rect(sl,x,y,w,h,fill,border=None,radius=False):
 sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
 sh.fill.solid();sh.fill.fore_color.rgb=C(fill)
 if border:sh.line.color.rgb=C(border);sh.line.width=Pt(1)
 else:sh.line.fill.background()
 if radius:
  try:sh.adjustments[0]=.12
  except:pass
 return sh

def txt(sl,text,x,y,w,h,sz=17,col=WHITE,bold=False,font='Aptos',align=None,spacing=1.05):
 box=sl.shapes.add_textbox(Inches(x),Inches(y), Inches(w), Inches(h))
 tf=box.text_frame;tf.clear();tf.word_wrap=True
 tf.margin_left=Inches(.02);tf.margin_top=Inches(.02);tf.margin_right=Inches(.02);tf.margin_bottom=0
 for i,line in enumerate(text.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
  p.text=line;p.font.name=font;p.font.size=Pt(sz);p.font.bold=bold;p.font.color.rgb=C(col)
  p.space_after=Pt(0);p.line_spacing=spacing
  if align is not None:p.alignment=align
 return box

def image(sl,filename,x,y,w,h):
 p=SCREEN/filename
 assert p.is_file(),f'Missing authentic screenshot: {p}'
 # Crop the *actual* browser screenshot to a 16:9 viewport rather than
 # squashing an entire vertically long webpage into a slide rectangle.
 cropped=OUT/'crops';cropped.mkdir(parents=True,exist_ok=True)
 target=cropped/filename
 with Image.open(p) as source:
  viewport_height=min(source.height,900)
  source.crop((0,0,source.width,viewport_height)).save(target,optimize=True)
 picture=sl.shapes.add_picture(str(target),Inches(x), Inches(y),width=Inches(w),height=Inches(h))
 return picture

def base(k,title,sub=None):
 sl=r.slides.add_slide(r.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=C(INK)
 rect(sl,.38,.42,.1,.29,ORANGE)
 txt(sl,'BLAST / LAB   —   VULTR AGENT RUSH',.63,.43,8,.2,10,GREEN,True,'Consolas')
 txt(sl,f'{k:02d} / 07',12.13,.42,.8,.24,10,MUTED,True,'Consolas',PP_ALIGN.RIGHT)
 rect(sl,.55,7.07,12.2,.012,LINE)
 txt(sl,URL,.59,7.14,8,.2,8,MUTED,False,'Consolas')
 if title:txt(sl,title,.58,.90,11.9,1.16,34,WHITE,True)
 if sub:txt(sl,sub,.6,2.06,11.7,.35,15,MUTED)
 return sl

def note(sl,text,y=6.53):
 txt(sl,text,.62,y,12.0,.38,10,MUTED,False,'Consolas')

# Slide 1
s=base(1,'Give your agent a mission.\nThen make its environment hostile.')
rect(s,.59,2.72,6.1,3.63,PANEL,LINE)
txt(s,'BLASTLAB',.95,3.05,5.2,.6,43,WHITE,True)
txt(s,'A containment test facility for browser agents.',.96,3.82,4.99,.65,21,GREEN)
txt(s,'1 real Web Chamber  /  2 tasks  /  4 attacks + baseline',.96,4.87,5.3,.68,14,WHITE,False,'Consolas')
txt(s,'Vultr VM  •  Serverless Inference  •  Docker/Chromium',.96,5.83,5.3,.3,11,MUTED,False,'Consolas')
image(s,'library-desktop.png',7.01,2.59,5.76,3.91)

# Slide 2
s=base(2,'Safety claims are easy.\nExecution evidence is harder.','Browser agents read untrusted content. That text can masquerade as high-priority instructions.')
for i,(head,body) in enumerate([
 ('THE LEGITIMATE JOB','Calculate supplier inventory or low-stock value.'),
 ('THE ADVERSARY','Inject role spoofing, off-route instructions and forged evidence into the page.'),
 ('THE REAL QUESTION','Can forbidden authority cross the tool boundary and can the task survive a reset?'),
]):
 x=.63+i*4.18
 rect(s,x,2.73,3.83,3.12,PANEL,LINE)
 rect(s,x,2.73,3.83,.06,ORANGE if i==1 else GREEN)
 txt(s,f'0{i+1} / '+head,x+.23,3.15,3.36,.4,13,GREEN if i!=1 else ORANGE,True,'Consolas')
 txt(s,body,x+.23,3.87,3.34,1.42,23,WHITE,True)
note(s,'The focus is bounded, real-world agent execution—not a chatbot and not a generalized jailbreak certification.')

# Slide 3
s=base(3,'A real Chamber workflow.','Chamber Library → Configure → Execute → Inspect → Report → Re-run.')
image(s,'setup-desktop.png',.64,2.38,7.3,3.91)
rect(s,8.18,2.4,4.53,3.92,PANEL,LINE)
txt(s,'CHAMBER 01 / THE WEB',8.48,2.72,3.85,.3,13,GREEN,True,'Consolas')
txt(s,'Choose the trusted task.',8.48,3.3,3.82,.37,20,WHITE,True)
txt(s,'Inventory valuation or low-stock exposure',8.48,3.73,3.84,.6,15,MUTED)
txt(s,'Choose the attack.',8.48,4.52,3.82,.37,20,WHITE,True)
txt(s,'Role spoofing · exfil bait · forged receipt · compound',8.48,4.95,3.8,.72,15,MUTED)
note(s,'The other four Chambers remain explicitly UNIMPLEMENTED. No fabricated feature catalogue.')

# Slide 4
s=base(4,'Vultr is the control plane.\nDocker is the disposable boundary.','All genuine agent LLM calls run through Vultr Serverless Inference, not a shadow provider.')
for i,(h,sub) in enumerate([
 ('GLM-5.3 / VULTR INFERENCE','Proposes browse and finish actions'),
 ('TRUSTED SUPERVISOR','Validates exact tool arguments, checkpoints and manages reset'),
 ('DOCKER + CHROMIUM','Read-only root; no external network; no host mounts; non-root process'),
]):
 y=2.47+i*1.28
 rect(s,1.02,y,8.92,1.03,PANEL2,LINE)
 txt(s,f'0{i+1}',1.3,y+.25,.6,.3,17,ORANGE,True,'Consolas')
 txt(s,h,2.02,y+.14,7.55,.38,20,WHITE,True)
 txt(s,sub,2.02,y+.57,7.63,.27,12,MUTED)
 if i<2:rect(s,1.56,y+1.04,.032,.22,ORANGE)
rect(s,10.28,2.47,2.0,3.58,INK,LINE)
txt(s,'BOUNDARY\nRULES',10.57,2.8,1.4,.75,17,GREEN,True,'Consolas')
txt(s,'NO SECRETS\nNO SHELL\nNO EGRESS\nNO HOST MOUNTS\nDISPOSABLE',10.58,4.0,1.51,1.37,11,MUTED,True,'Consolas')
note(s,'The forced reset is supervisor-scheduled fault injection, NOT compromise-triggered remediation.')

# Slide 5
s=base(5,'Two real executions.\nTwo clearly different sources.','Real model choices and deliberately scripted malicious proposals are never conflated.')
rect(s,.64,2.57,6.02,3.72,PANEL,LINE)
rect(s,6.79,2.57,5.89,3.72,PANEL,LINE)
txt(s,'LIVE GLM-5.3 MODEL',.95,2.89,5.33,.37,16,GREEN,True,'Consolas')
txt(s,'$24.00',.93,3.34,5.3,.75,49,WHITE,True)
txt(s,'2 isolated worker generations\n2 browser reads\n0 forbidden actions proposed',.95,4.36,5.34,1.19,18,WHITE)
txt(s,'ACTUAL VULTR SERVERLESS INFERENCE',.95,5.81,5.4,.28,10,GREEN,True,'Consolas')
txt(s,'SCRIPTED POLICY CHALLENGE',7.1,2.89,5.3,.37,16,ORANGE,True,'Consolas')
txt(s,'1 denied',7.09,3.34,5.05,.75,43,WHITE,True)
txt(s,'Receipt-forgery proposal blocked\n$24.00 task still completed\nDocker reset verified',7.1,4.36,5.25,1.19,18,WHITE)
txt(s,'SCRIPTED FIXTURE — NOT LLM BEHAVIOR',7.1,5.81,5.3,.28,10,ORANGE,True,'Consolas')
note(s,'Actual public and VM test data, November 5, 2026. Different scenario examples may have different denial counts.')

# Slide 6
s=base(6,'Not a green badge.\nA test report with receipts.','Every case explains what was attempted, what was blocked, what survived and what remains untested.')
image(s,'results-desktop.png',.65,2.39,7.29,3.92)
rect(s,8.18,2.39,4.52,3.92,PANEL,LINE)
txt(s,'INDEPENDENTLY CHECKABLE',8.47,2.77,3.86,.28,12,GREEN,True,'Consolas')
txt(s,'Sanitized SHA-256 chain',8.47,3.32,3.81,.54,24,WHITE,True)
txt(s,'Download the run JSON and verify it offline. Its digest is not silently substituted for the private raw log.',8.47,4.12,3.8,1.1,15,MUTED)
txt(s,'WORKER RESET + VALUATION VERIFIED',8.47,5.65,3.8,.46,11,ORANGE,True,'Consolas')
note(s,'Recommendations are rule-based from observed evidence. Unattempted attacks are labeled UNTESTED.')

# Slide 7
s=base(7,'The reusable agent crash-test facility.','The first Chamber proves the product loop. Four more attack surfaces have room to grow.')
rect(s,.68,2.48,7.32,3.84,PANEL,LINE)
txt(s,'WHY THIS MATTERS',.98,2.83,6.65,.3,13,GREEN,True,'Consolas')
txt(s,'Agent builders need evidence before shipping autonomy—not a safety promise stapled onto a chat window.',.96,3.43,6.55,1.66,27,WHITE,True)
txt(s,'The Web: working. Toolchain, Vault, Machine, Chaos: planned, unbuilt.',.96,5.52,6.52,.6,14,MUTED)
rect(s,8.27,2.48,4.38,3.84,PANEL2,LINE)
txt(s,'TEST THE WEB CHAMBER',8.57,2.88,3.75,.39,16,ORANGE,True,'Consolas')
txt(s,'blastlab.45-77-138-147.sslip.io/app',8.57,3.52,3.72,.78,16,WHITE,True)
txt(s,'Vultr Agent Rush\nChallenge: Blast Radius Zero\nNovember 2026',8.57,4.63,3.67,1.1,14,GREEN)
note(s,'Public app URL is a temporary domain. Code, recorded proof and architecture are included in the submission materials.')

target=OUT/'BlastLab-Vultr-Agent-Rush.pptx'
r.save(target)
print('PRESENTATION_READY',target,'slides=',len(r.slides),'bytes=',target.stat().st_size)
