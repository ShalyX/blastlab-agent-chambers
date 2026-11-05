"""Generate a LabLab cover from an actual Web Chamber screenshot, not a mockup."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
ROOT=Path(__file__).resolve().parents[1]
SCREEN=ROOT/'docs/screenshots/library-desktop.png'
OUT=ROOT/'submission/BlastLab-Cover.png'
W,H=1600,900
background=Image.new('RGB',(W,H),(14,21,22))
d=ImageDraw.Draw(background)
for i in range(0,W,60):
 d.line((i,0,i,H),fill=(30,44,40),width=1)
for j in range(0,H,60):
 d.line((0,j,W,j),fill=(30,44,40),width=1)
d.rectangle((0,0,13,H),fill=(255,117,74))
with Image.open(SCREEN).convert('RGB') as shot:
 # Crop the actual viewport, preserving ratio and no invented elements.
 shot=shot.crop((250,65,1430,min(900,shot.height)))
 shot.thumbnail((850,725),Image.Resampling.LANCZOS)
 background.paste(shot,(W-shot.width-50,105))
d=ImageDraw.Draw(background)
d.rectangle((W-840,100,W-46,830),outline=(99,143,119),width=3)
fontdir=Path(r'C:/Windows/Fonts')
def font(name,size,fall='arial.ttf'):
 try:return ImageFont.truetype(str(fontdir/name),size)
 except:return ImageFont.truetype(str(fontdir/fall),size)
fmono=font('consola.ttf',21)
fbold=font('arialbd.ttf',90)
fbold2=font('arialbd.ttf',62)
fsub=font('arial.ttf',29)
d.text((74,89),'BLAST / LAB   •   VULTR AGENT RUSH',font=fmono,fill=(172,240,212))
d.rectangle((72,165,146,176),fill=(255,117,74))
d.text((73,220),'CRASH-TEST',font=fbold,fill=(239,244,238))
d.text((73,320),'THE BLAST',font=fbold2,fill=(255,117,74))
d.text((73,400),'RADIUS.',font=fbold2,fill=(255,117,74))
d.text((75,526),'A real Chamber-based testing facility',font=fsub,fill=(234,239,231))
d.text((75,570),'for browser agents facing hostile pages.',font=fsub,fill=(189,211,194))
d.rectangle((74,699,613,768),fill=(33,66,48),outline=(92,145,105),width=2)
d.text((101,719),'VULTR  /  GLM-5.3  /  DOCKER',font=fmono,fill=(172,240,212))
d.text((75,815),'ONE OPERATIONAL WEB CHAMBER  •  VERIFIED EXECUTION',font=font('consola.ttf',15),fill=(167,193,173))
OUT.parent.mkdir(exist_ok=True)
background.save(OUT,optimize=True)
print('COVER_READY',OUT,OUT.stat().st_size)
