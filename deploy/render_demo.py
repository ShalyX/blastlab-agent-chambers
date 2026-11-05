from __future__ import annotations
import json, subprocess, wave
from pathlib import Path

root=Path(__file__).resolve().parents[1]
raw=max((root/'web'/'submission-captures').glob('*.webm'),key=lambda p:p.stat().st_mtime)
audio_dir=root/'submission'/'audio'
lines=json.loads((audio_dir/'script.json').read_text(encoding='utf-8-sig'))
wavs=sorted(audio_dir.glob('voice-*.wav'))
assert len(wavs)==len(lines)==14

parts=[]; ends=0; slots=[]
for i,(wav,line) in enumerate(zip(wavs,lines)):
    with wave.open(str(wav),'rb') as f: duration=f.getnframes()/f.getframerate()
    start=max(0.0,float(line['At'])-3.8,ends+0.13) if i else 0.0
    ends=start+duration/1.15
    slots.append({'line':i+1,'start':round(start,3),'end':round(ends,3),'text':line['Line']})
    parts.append(f'[{i}:a]asetpts=PTS-STARTPTS,atempo=1.15,adelay={int(start*1000)}:all=1[a{i}]')
mix=''.join(f'[a{i}]' for i in range(len(wavs)))
filter_audio=';'.join(parts+[mix+f'amix=inputs={len(wavs)}:duration=longest:dropout_transition=0:normalize=0,volume=0.94,alimiter=limit=0.92,aresample=48000[a]'])
narration=audio_dir/'final-narration.wav'
args=['ffmpeg','-hide_banner','-nostdin','-y','-loglevel','error']
for wav in wavs:args+=['-i',str(wav)]
args+=['-filter_complex',filter_audio,'-map','[a]','-ac','2','-ar','48000','-c:a','pcm_s16le',str(narration)]
print('MIXING_NARRATION')
subprocess.run(args,check=True)
duration=80
output=root/'submission'/'BlastLab-Agent-Rush.mp4'
cmd=[
  'ffmpeg','-hide_banner','-nostdin','-y','-loglevel','error',
  '-ss','5.8','-i',str(raw),'-i',str(narration),
  '-filter_complex',
  '[0:v]scale=1728:1080:flags=lanczos,pad=1920:1080:96:0:color=#101619,fps=30,tpad=stop_mode=clone:stop_duration=4,format=yuv420p[v]',
  '-map','[v]','-map','1:a',
  '-c:v','libx264','-preset','veryfast','-crf','20',
  '-c:a','aac','-b:a','160k',
  '-af','loudnorm=I=-16:TP=-1.5:LRA=11',
  '-movflags','+faststart','-t',str(duration),
  '-metadata','title=BlastLab | Agent Rush | Web Chamber',
  '-metadata','comment=Actual Vultr Docker Web Chamber walkthrough; scripted policy test clearly labeled',
  str(output),
]
print('ENCODING_MP4')
subprocess.run(cmd,check=True)
out=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(output)],text=True)
print('DEMO_FINAL',output)
print(out)
(audio_dir/'timing.json').write_text(json.dumps(slots,indent=2)+'\n')
