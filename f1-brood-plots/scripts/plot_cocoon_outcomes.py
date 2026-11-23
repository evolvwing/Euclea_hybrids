import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typography import plot_font
from scipy.stats import chisquare
import pandas as pd
plt.rcParams.update({'font.family':plot_font,'font.size':6,'text.color':'#292D31','axes.labelcolor':'#292D31','xtick.color':'#363B40','ytick.color':'#363B40','mathtext.fontset':'custom','mathtext.rm':plot_font,'mathtext.it':f'{plot_font}:italic'})
w,h=290,180
fig=plt.figure(figsize=(w/72,h/72));ax=fig.add_axes([.108,.32,.88,.685]);ax.set_ylim(0,100);ax.set_yticks([0,20,40,60,80]);ax.set_ylabel('Cocoons (N)',fontsize=8,labelpad=3)
# Reserve legend and letter above the axis by using the original top/bottom coordinates.
ax.set_position([.108,.27,.88,.60])
for side in ['top','right']:ax.spines[side].set_visible(False)
for side in ['left','bottom']:ax.spines[side].set_color('#71777D');ax.spines[side].set_linewidth(.6)
ax.tick_params(length=2,width=.6,labelsize=6)
blue='#4E7994';ochre='#B28B57';ticks=[];labs=[];cursor=0
groups = []
sib_label = '$\\it{E.\\ incisa}$\nsib-crosses'
for row in pd.read_csv('data/survival.csv').itertuples():
 label = sib_label if row.group == 'incisa_sib' else row.group
 groups.append((label, [row.dead_larvae_unsexed, row.dead_pupae_M, row.dead_pupae_F],
                [row.adult_ND_M, row.adult_D_M], [row.adult_ND_F, row.adult_D_F]))

for row in pd.read_csv('data/parental_adult_counts.csv').itertuples():
 species = row.group.removesuffix(' parental').replace(' ', r'\ ')
 label = f'$\\it{{{species}}}$\nparental\n({row.year})'
 male = [row.male, 0] if row.diapause == 'N' else [0, row.male]
 female = [row.female, 0] if row.diapause == 'N' else [0, row.female]
 groups.append((label, None, male, female))
for label,dead,m,f in groups:
 start=cursor
 if dead is not None:
  bottom=0
  for n,c in zip(dead,['#CCCCCC','#808080','#333333']):ax.bar(cursor,n,bottom=bottom,width=.72,color=c,edgecolor='white',linewidth=.25);bottom+=n
  ax.text(cursor,bottom+1.5,str(bottom),ha='center',fontsize=5.5);ticks.append(cursor);labs.append('†');cursor+=1
 mx=cursor
 for arr,sex in [(m,'M'),(f,'F')]:
  bottom=0
  for n,c in zip(arr,[ochre,blue]):ax.bar(cursor,n,bottom=bottom,width=.72,color=c,edgecolor='white',linewidth=.25);bottom+=n
  ax.text(cursor,bottom+1.5,str(bottom),ha='center',fontsize=5.5);ticks.append(cursor);labs.append(sex);cursor+=1
 counts=[sum(m),sum(f)];test=chisquare(counts);mark='***'if test.pvalue<.001 else '**'if test.pvalue<.01 else '*'if test.pvalue<.05 else 'ns';yy=max(counts)+12
 ax.plot([mx,mx,mx+1,mx+1],[yy-2,yy,yy,yy-2],color='#55595D',lw=.6);ax.text(mx+.5,yy+1,mark,ha='center',fontsize=6,weight='bold')
 end=cursor-1;ax.plot([start-.4,end+.4],[-.055]*2,transform=ax.get_xaxis_transform(),clip_on=False,c='#B8BDC2',lw=.5);ax.text((start+end)/2,-.085,label,transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=5.4,linespacing=1.0)
 cursor+=.8
ax.set_xlim(-.7,cursor-.7);ax.set_xticks(ticks,labs);ax.tick_params(axis='x',length=0,pad=2)
fig.text(.005,.995,'C',fontsize=12,weight='bold',va='top')
from matplotlib.patches import Rectangle
for x,y,c,t in [(.25,.96,ochre,'Non-diapaused'),(.25,.86,blue,'Diapaused'),(.59,.96,'#CCCCCC','Dead larvae (unsexed)'),(.59,.86,'#808080','Dead M'),(.79,.86,'#333333','Dead F')]:
 fig.add_artist(Rectangle((x,y-.04),.028,.035,transform=fig.transFigure,color=c,lw=0));fig.text(x+.04,y,t,fontsize=6.5,va='top')
fig.savefig('outputs/panel_C_parental.png',dpi=450)
plt.rcParams['pdf.fonttype']=42
fig.savefig('outputs/panel_C_parental.pdf')
