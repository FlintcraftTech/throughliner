import re,sys
def syl(w):
    w=w.lower(); w=re.sub(r'[^a-z]','',w)
    if not w: return 0
    v=re.findall(r'[aeiouy]+',w); n=len(v)
    if w.endswith('e') and not w.endswith('le') and n>1: n-=1
    return max(n,1)
def score(t):
    t=re.sub(r'`[^`]*`','code',t); t=re.sub(r'https?://\S+','link',t); t=re.sub(r'[*#>_\[\]()]','',t)
    sents=[s for s in re.split(r'[.!?]+\s',t) if s.strip()]
    words=[w for w in re.findall(r"[A-Za-z'][A-Za-z'-]*",t)]
    if not words or not sents: return None
    wps=len(words)/len(sents); spw=sum(map(syl,words))/len(words)
    grade=0.39*wps+11.8*spw-15.59; ease=206.835-1.015*wps-84.6*spw
    long=sum(1 for s in sents if len(re.findall(r"[A-Za-z']+",s))>25)
    return f"grade {grade:4.1f}  ease {ease:5.1f}  words/sentence {wps:4.1f}  sentences>25w {long}/{len(sents)}"
for p in sys.argv[1:]:
    txt=open(p,encoding='utf-8').read()
    print(f"{score(txt)}  {p.split('/')[-1]}")
