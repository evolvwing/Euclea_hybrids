from plot_shared import blue, colors, groups, hybrids, letters, ochre, pos, raw, style, violin, xmax, xmin

import matplotlib.pyplot as plt
import numpy as np

fig=plt.figure(figsize=(7.5,230/72),facecolor='white')
labels=['F1-1','F1-2','F1-3','F1\npooled','$\\it{E.\\ incisa}$\nsib-crosses','$\\it{E.\\ incisa}$\nparental\n(2024)','$\\it{E.\\ delphinii}$\npooled']
for col,sex in enumerate(['M','F']):
 left=.065+col*.5;width=.42
 fig.text([.015,.504][col],.99,'EF'[col],fontsize=12,weight='bold',va='top')
 ax=fig.add_axes([left,27/230,width,119.4/230]);style(ax);ax.set_xlim(xmin,xmax);ax.set_ylim(7,14.2);ax.set_yticks(range(7,15));ax.set_ylabel(('Male' if col==0 else 'Female')+' forewing length (mm)',labelpad=3,fontsize=8)
 ax.axvline(2.675,c='#D4D8DC',lw=.6,zorder=0)
 sx=left+(2.675-xmin)/(xmax-xmin)*width
 fig.add_artist(plt.Line2D([sx,sx],[27/230,214/230],transform=fig.transFigure,c='#D4D8DC',lw=.6,zorder=0))
 fig.text(left-.041,198/230,'Males' if col==0 else 'Females',rotation=90,ha='center',va='center',fontsize=8)
 ticks=[];ticklabels=[]
 for i,(g,x) in enumerate(zip(groups,pos)):
  sel=raw.group.isin(hybrids) if i==3 else raw.group.eq(g)
  allrows=raw[sel & raw.sex.eq(sex)];rows=allrows[allrows.wing_status.eq('measured')]
  nd=int(allrows.diapaused.eq('N').sum());d=int(allrows.diapaused.eq('Y').sum())
  cx=left+(x-xmin)/(xmax-xmin)*width;diam=30.24
  donut=fig.add_axes([cx-diam/540/2,(198-diam/2)/230,diam/540,diam/230])
  wedges,_=donut.pie([d,nd],colors=[blue,ochre],startangle=90,counterclock=False,wedgeprops={'width':.48,'edgecolor':'white','linewidth':.35})
  for w,n in zip(wedges,[d,nd]):
   if n:
    ang=np.deg2rad((w.theta1+w.theta2)/2);donut.text(.8*np.cos(ang),.8*np.sin(ang),str(n),ha='center',va='center',color='white',fontsize=5.5,weight='bold')
  perc=100*d/(nd+d);lab=f'{perc:.1f}' if d and nd else f'{perc:.0f}'
  donut.text(0,.12,lab,ha='center',va='center',fontsize=5.8,weight='bold');donut.text(0,-.20,'%',ha='center',va='center',fontsize=3.48,weight='bold');donut.set_xlim(-1.03,1.03);donut.set_ylim(-1.03,1.03);donut.axis('off')
  fig.add_artist(plt.Line2D([cx-.021,cx+.021],[176/230]*2,transform=fig.transFigure,c='#B8BDC2',lw=.6))
  fig.text(cx,172/230,labels[i],ha='center',va='top',fontsize=6.1,linespacing=1.1)
  for state,off in [('Y',-.22),('N',.22)]:
   v=rows.loc[rows.diapaused.eq(state),'forewing_mm'].to_numpy();xx=x+off;ticks.append(xx);ticklabels.append('D' if state=='Y' else 'ND')
   ax.text(xx,-.115,str(len(v)),transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=6.5)
   if len(v):
    violin(ax,v,xx,colors[state],.22,.17,False,i+100*col)
    if(i,state)in letters[sex]:ax.text(xx,v.max()+.22,letters[sex][i,state],ha='center',va='bottom',fontsize=9,weight='bold')
 ax.text(-.067,-.115,'N =',transform=ax.transAxes,ha='left',va='top',fontsize=6.5)
 ax.set_xticks(ticks,ticklabels);ax.tick_params(axis='x',length=0,pad=5,labelsize=6.5)
 for j,l in enumerate(ax.get_xticklabels()):l.set_color(blue if j%2==0 else ochre);l.set_weight('bold')
fig.savefig('outputs/vector_ef.pdf')
