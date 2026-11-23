import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typography import plot_font
from matplotlib.colors import to_rgb
from scipy.stats import norm
plt.rcParams.update({'font.family':plot_font,'font.size':8,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'text.color':'#292D31','axes.labelcolor':'#292D31','xtick.color':'#363B40','ytick.color':'#363B40','mathtext.fontset':'custom','mathtext.rm':plot_font,'mathtext.it':f'{plot_font}:italic','mathtext.bf':f'{plot_font}:bold','pdf.fonttype':42})
blue='#4E7994';ochre='#B28B57';green='#648B76';magenta='#A16B8D';olive='#8D9C65';colors={'Y':blue,'N':ochre}
def style(ax):
 for s in ['top','right']:ax.spines[s].set_visible(False)
 for s in ['left','bottom']:ax.spines[s].set_color('#71777D');ax.spines[s].set_linewidth(.65)
 ax.tick_params(length=3,width=.65)
def violin(ax,v,pos,c,bw,width,horizontal=False,seed=1):
 v=np.asarray(v);t=np.linspace(v.min(),v.max(),256);d=norm.pdf((t[:,None]-v)/bw).mean(axis=1);d=d/d.max()*width
 fill=tuple(.16*np.array(to_rgb(c))+.84);j=np.random.default_rng(seed).uniform(-width*.42,width*.42,len(v))
 if horizontal:
  ax.fill_between(t,pos-d,pos+d,color=fill,linewidth=0)
  ax.plot(t,pos-d,c=c,lw=1.2);ax.plot(t,pos+d,c=c,lw=1.2)
  for k in [0,-1]:ax.plot([t[k]]*2,[pos-d[k],pos+d[k]],c=c,lw=1.2)
  ax.scatter(v,pos+j,s=9,c=c,alpha=.29,linewidths=0,zorder=4)
 else:
  ax.fill_betweenx(t,pos-d,pos+d,color=fill,linewidth=0)
  ax.plot(pos-d,t,c=c,lw=1.2);ax.plot(pos+d,t,c=c,lw=1.2)
  for k in [0,-1]:ax.plot([pos-d[k],pos+d[k]],[t[k]]*2,c=c,lw=1.2)
  ax.scatter(pos+j,v,s=7,c=c,alpha=.29,linewidths=0,zorder=4)
# Original forewing data and all sexed individuals for donuts.
raw=pd.read_csv('data/individuals.tsv',sep='\t').dropna(how='all')
raw=raw[raw.sex.isin(['M','F'])].copy()
raw['group']=raw.group.replace({'E. delphinii, Ipswich clutch':'E. delphinii','E. delphinii, wild from DMV area':'E. delphinii'})
hybrids=['F1-1','F1-2','F1-3'];groups=hybrids+['F1 pooled','Inbred E. incisa','Parental E. incisa (2024 brood)','E. delphinii']
labels=['F1-1','F1-2','F1-3','F1\npooled','$\\it{E.\\ incisa}$\ninbred','$\\it{E.\\ incisa}$\nparental\n(2024)','$\\it{E.\\ delphinii}$\npooled']
letters={'M':{(3,'N'):'b',(4,'N'):'a',(5,'Y'):'a',(6,'Y'):'ab'},'F':{(3,'Y'):'c',(3,'N'):'ab',(4,'N'):'ab',(5,'Y'):'a',(6,'Y'):'bc'}}
pos=np.arange(7,dtype=float);pos[3:]+=.35
xmin,xmax=-.55,6.9
