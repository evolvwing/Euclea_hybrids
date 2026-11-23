import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typography import plot_font
from matplotlib.colors import to_rgb
from scipy.stats import norm, ttest_ind
plt.rcParams.update({'font.family':plot_font,'font.size':7,'axes.labelsize':8,'text.color':'#292D31','axes.labelcolor':'#292D31','xtick.color':'#363B40','ytick.color':'#363B40','mathtext.fontset':'custom','mathtext.rm':plot_font,'mathtext.it':f'{plot_font}:italic'})
fig=plt.figure(figsize=(7.5,2.5),facecolor='white')
axes=[fig.add_axes([x,.27,w,.60]) for x,w in [(.075,.126),(.80,.1848)]]
for a in axes:
 for s in ['top','right']:a.spines[s].set_visible(False)
 for s in ['left','bottom']:a.spines[s].set_color('#71777D');a.spines[s].set_linewidth(.6)
 a.tick_params(length=2,width=.6,pad=3)
for x,l in zip([.008,.745],'BD'):fig.text(x,.98,l,fontsize=12,weight='bold',va='top')
# B: total egg counts, mean and SE, individual cross counts.
a=axes[0]
egg_table = pd.read_csv('data/eggs.csv')
egg_groups = [egg_table.query('group == @g').eggs_total.to_numpy() for g in ['F1', 'incisa_sib']]
for i,(v,c) in enumerate(zip(egg_groups,['#A16B8D','#648B76'])):
 a.bar(i,v.mean(),width=.58,facecolor=tuple(.22*np.array(to_rgb(c))+.78),edgecolor=c,lw=1.2)
 a.errorbar(i,v.mean(),yerr=v.std(ddof=1)/np.sqrt(len(v)),fmt='none',ecolor=c,elinewidth=1.2,capsize=3)
 a.scatter(i+np.random.default_rng(i).uniform(-.15,.15,len(v)),v,s=15,c=c,alpha=.4,linewidths=0,zorder=4)
 a.text(i,-.04,['F1\ncrosses','$\\it{E.\\ incisa}$\nsib-crosses'][i],transform=a.get_xaxis_transform(),ha='center',va='top',fontsize=6,linespacing=1.15)
for i,n in enumerate(map(len, egg_groups)):a.text(i,-.235,f'N = {n}',transform=a.get_xaxis_transform(),ha='center',va='top',fontsize=6)
a.set_xlim(-.65,1.65);a.set_ylim(0,470);a.set_yticks([0,100,200,300,400]);a.set_xticks([]);a.set_ylabel('Total eggs',labelpad=4)
a.plot([0,0,1,1],[420,432,432,420],color='#55595D',lw=.6)
p = ttest_ind(*egg_groups, equal_var=False).pvalue
mark = '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else 'ns'
a.text(.5,437,mark,ha='center',va='bottom',fontsize=9,weight='bold')
# D: duration distributions, same data and smoothing as previous figure.
a=axes[1];duration_table=pd.read_csv('data/development.csv');data={k:g.days_hatch_to_cocoon.tolist() for k,g in duration_table.groupby('group',sort=False)}
for i,(k,c) in enumerate(zip(['F1','incisa_sib','incisa_2024'],['#A16B8D','#648B76','#8D9C65'])):
 v=np.array(data[k]);t=np.linspace(v.min(),v.max(),256);density=norm.pdf((t[:,None]-v)/.8).mean(axis=1);hw=density/density.max()*(.29/1.1)
 a.fill_betweenx(t,i-hw,i+hw,color=tuple(.16*np.array(to_rgb(c))+.84),linewidth=0)
 a.plot(i-hw,t,c=c,lw=1.2);a.plot(i+hw,t,c=c,lw=1.2)
 for j in [0,-1]:a.plot([i-hw[j],i+hw[j]],[t[j]]*2,c=c,lw=1.2)
 a.scatter(i+np.random.default_rng(i).uniform(-.12/1.1,.12/1.1,len(v)),v,s=9,c=c,alpha=.29,linewidths=0,zorder=4)
 a.text(i,v.max()+.65,['a','b','c'][i],ha='center',va='bottom',fontsize=9,weight='bold')
 a.text(i,-.04,['F1\ncrosses','$\\it{E.\\ incisa}$\nsib-crosses','$\\it{E.\\ incisa}$\nparental\n(2024)'][i],transform=a.get_xaxis_transform(),ha='center',va='top',fontsize=6,linespacing=1.15)
for i,n in enumerate(len(data[k]) for k in ['F1', 'incisa_sib', 'incisa_2024']):a.text(i,1.085,f'N = {n}',transform=a.get_xaxis_transform(),ha='center',va='top',fontsize=6)
a.set_xlim(-.55,2.55);a.set_ylim(30,57);a.set_yticks([30,35,40,45,50,55]);a.set_xticks([]);a.set_ylabel('Egg hatch to cocoon (days)',labelpad=3)

fig.savefig('outputs/panels_bd.pdf')
