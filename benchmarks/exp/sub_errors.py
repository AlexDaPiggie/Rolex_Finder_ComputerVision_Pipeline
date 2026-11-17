import json, numpy as np, torch
from pathlib import Path
from src.training.clip_head import *
names=[n for n,_ in sorted(json.loads(Path("data/processed/class_mapping.json").read_text()).items(), key=lambda kv: kv[1])]
tr=np.load("features_out/train.npz"); real=np.load("features_out/real.npz")
ex=set(json.loads(Path("benchmarks/real_exclude.json").read_text()))
keep=np.array([f.replace("\\","/") not in ex for f in real["files"]])
lab=real["labels"][keep]; emb=real["emb"][keep].astype("float32")
xtr,ytr=tr["feats"].astype("float32"),tr["labels"]
groups=creator_groups(real["files"][keep])
S,D=names.index("submariner"),names.index("sea_dweller")
unique=sorted(set(groups)); np.random.default_rng(0).shuffle(unique)
fold=np.array([{g:i%5 for i,g in enumerate(unique)}[g] for g in groups])
def run(pair_w, pair_scale, epochs=60):
    base=np.zeros(len(lab),int); pair=np.zeros(len(lab),int)
    for k in range(5):
        trn,tst=fold!=k,fold==k
        x,y=with_real(xtr,ytr,emb[trn],lab[trn],10)
        head,sc=train_head(x,y,len(names),0.1,epochs=epochs)
        p=predict(head,sc,emb[tst][:,3]); pred=p.argmax(1); base[tst]=pred
        if pair_w:
            m=np.isin(y,[S,D]); px,py=x[m],(y[m]==D).astype("int64")
            xs=np.concatenate([emb[trn][:,v] for v in (0,1,3)]); ys=np.concatenate([lab[trn]]*3); mm=np.isin(ys,[S,D])
            px=np.concatenate([px]+[xs[mm]]*pair_w); py=np.concatenate([py]+[(ys[mm]==D).astype("int64")]*pair_w)
            ph,ps=train_head(px,py,2,0.1,epochs=epochs,scale=pair_scale)
            q=predict(ph,ps,emb[tst][:,3]).argmax(1)
            pred=np.where(np.isin(pred,[S,D]),np.where(q==1,D,S),pred)
        pair[tst]=pred
    out=pair if pair_w else base
    return (out==lab).mean(), (out[lab==S]==S).mean(), (out[lab==D]==D).mean(), (lab==S).sum(), (lab==D).sum()

files=real["files"][keep]
pred=np.zeros(len(lab),int)
for k in range(5):
    trn,tst=fold!=k,fold==k
    x,y=with_real(xtr,ytr,emb[trn],lab[trn],10)
    head,sc=train_head(x,y,len(names),0.1,epochs=60)
    pred[tst]=predict(head,sc,emb[tst][:,3]).argmax(1)
from PIL import Image, ImageDraw
bad=[(f,names[l],names[p]) for f,l,p in zip(files,lab,pred) if l in (S,D) and p!=l]
print(len(bad))
t=220;cols=6;rows=(len(bad)+cols-1)//cols
sh=Image.new("RGB",(cols*t,rows*(t+14)),"white");d=ImageDraw.Draw(sh)
for i,(f,l,p) in enumerate(bad):
    im=Image.open("data/realworld_all/"+f.replace("\\","/")).convert("RGB");im.thumbnail((t,t))
    x,y=(i%cols)*t,(i//cols)*(t+14);sh.paste(im,(x,y+14));d.text((x+2,y),f"{l[:5]}->{p[:6]}",fill="red")
sh.save("benchmarks/exp/sub_sd_errors.jpg",quality=80)
