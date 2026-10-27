"""Make the light publish copy in dist/:
 - index.html without the big PHOTOS table; each book's pictures go to photos/<storyId>.<hash>.js, loaded when the book is opened;
 - small cover images img/c/<storyId>.<hash>.webp for the library shelf.
usage: split.py -> prints the files to publish and the old ones to retire (as JSON)"""
import hashlib, os, re, json, io
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
D = S + 'dist/'
os.makedirs(D + 'photos', exist_ok=True); os.makedirs(D + 'img/c', exist_ok=True)
h = open(A + 'index.html').read()
i = h.index('const PHOTOS={'); j = h.index('`}};\n', i) + 4
body = h[i + len('const PHOTOS={'):j - 2]            # entries, without the outer braces and ;
ents = re.split(r",\n(?='[a-z]+:\d+':)", body)
groups = {}
for e in ents:
    sid = re.match(r"'([a-z]+):\d+':", e).group(1)
    groups.setdefault(sid, []).append(e.rstrip().rstrip(','))
files = {}; PHF = {}
for sid, es in groups.items():
    js = '__PHB(function(){return {' + ',\n'.join(es) + '}});\n'
    name = f'photos/{sid}.' + hashlib.sha1(js.encode()).hexdigest()[:10] + '.js'
    open(D + name, 'w').write(js); files[name] = D + name; PHF[sid] = name
loader = ("const PHOTOS={},PHF=" + json.dumps(PHF) + ",PHL={};"
          "function __PHB(f){Object.assign(PHOTOS,f())}"
          "function loadBook(id){if(PHL[id])return PHL[id];return PHL[id]=new Promise((res,rej)=>{const s=document.createElement('script');"
          "s.src=PHF[id];s.onload=res;s.onerror=()=>{delete PHL[id];rej()};document.head.appendChild(s)})}")
out = h[:i] + loader + h[j:]
# small covers
m = re.search(r"const COVER_IMG=(\{[^}]*\})", out)
cov = dict(re.findall(r"(\w+):'([^']+)'", m.group(1))); new = {}
for sid, src in cov.items():
    im = Image.open(A + src).convert('RGB'); im.thumbnail((720, 405), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=74, method=6); data = b.getvalue()
    name = f'img/c/{sid}.' + hashlib.sha1(data).hexdigest()[:10] + '.webp'
    open(D + name, 'wb').write(data); files[name] = D + name; new[sid] = name
out = out.replace(m.group(1), '{' + ','.join(f"{k}:'{v}'" for k, v in new.items()) + '}', 1)

# narration: one file per book, pages at offsets; page buttons: one strip per book
import subprocess, numpy as np
ids = re.findall(r"\{id:'(\w+)',title:'[^']*',.*?pages:(\w+)", out)
npages = {}
for bi, (sid, var) in enumerate(ids):
    arr = re.search(r'const ' + var + r'=\[(.*?)\n\];', out, re.S).group(1)
    npages[sid] = len(json.loads('[' + arr + ']'))
PACK = {'narr': {}, 'thumbs': {}}
os.makedirs(D + 'audio/book', exist_ok=True); os.makedirs(D + 'img/t/book', exist_ok=True)
sr = 24000
for bi, (sid, _) in enumerate(ids):
    n = npages[sid]; parts = []; off = []; end = []; t = 0
    for p in range(1, n + 1):
        f = A + f'audio/b{bi+1}p{p}.mp3'
        a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
        off.append(round(t / sr, 4)); parts.append(a); t += len(a); end.append(round(t / sr, 4))
        gap = np.zeros(int(.3 * sr), np.float32); parts.append(gap); t += len(gap)
    pcm = np.concatenate(parts)
    key = hashlib.sha1(pcm.tobytes()).hexdigest()[:10]
    name = f'audio/book/{sid}.{key}.mp3'
    if not os.path.exists(D + name):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-b:a', '48k', D + name], input=pcm.tobytes(), check=True)
    files[name] = D + name; PACK['narr'][sid] = {'src': name, 'off': off, 'end': end}
    ims = [Image.open(A + f'img/t/b{bi+1}p{p}.webp').convert('RGB').resize((192, 108)) for p in range(1, n + 1)]
    strip = Image.new('RGB', (192 * n, 108))
    for k, im in enumerate(ims): strip.paste(im, (192 * k, 0))
    b = io.BytesIO(); strip.save(b, 'WEBP', quality=72, method=6); data = b.getvalue()
    name = f'img/t/book/{sid}.' + hashlib.sha1(data).hexdigest()[:10] + '.webp'
    open(D + name, 'wb').write(data); files[name] = D + name; PACK['thumbs'][sid] = name
assert out.count('const PACK=null;') == 1
out = out.replace('const PACK=null;', 'const PACK=' + json.dumps(PACK, separators=(',', ':')) + ';', 1)
open(D + 'index.html', 'w').write(out)
prev = json.load(open(D + 'state.json')) if os.path.exists(D + 'state.json') else {'files': []}
retire = [f for f in prev.get('files', []) if f not in files]
for f in retire:
    try: os.remove(D + f) if os.path.isfile(D + f) else None
    except FileNotFoundError: pass
json.dump({'files': sorted(files)}, open(D + 'state.json', 'w'))
print(json.dumps({'publish': files, 'retire': retire, 'index_bytes': len(out)}))
