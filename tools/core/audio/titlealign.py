import json,subprocess,sys,align
o=json.load(open('titleoffsets.json'))
T={'manha': 'A Manhã da Rita', 'sabado': 'O Sábado da Rita', 'domingo': 'O Domingo da Rita', 'jantar': 'O Jantar da Rita', 'passeio': 'O Passeio da Rita', 'pico': 'A Madrugada da Rita', 'seixal': 'A Ana Volta ao Norte', 'casa': 'A Rita Procura Casa', 'garajau': 'O Mergulho no Garajau', 'novacasa': 'A Casa Nova', 'corridas': 'O Dia das Corridas', 'carro': 'O Carro da Rita', 'veleiro': 'O Veleiro', 'voo': 'O Voo da Rita', 'festa': 'A Festa da Casa Nova', 'golfe': 'Com os Pés no Chão', 'presente': 'O Presente'}
src=sys.argv[1];out={}
for k,(s,e) in o.items():
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss',str(s),'-to',str(e),'-i',src,'/tmp/tseg.wav'],check=True)
    ws=T[k].split();tw=align.align('/tmp/tseg.wav',ws)
    out[k]=[[int((s+a)*1000),int((s+b)*1000)] for a,b in tw];print(k,out[k],flush=True)
json.dump(out,open('titlewords.json','w'))
