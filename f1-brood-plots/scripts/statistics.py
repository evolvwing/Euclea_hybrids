"""Audit analyses. These recompute tests; they do not invent historical provenance."""
from pathlib import Path
import os,itertools,json
import numpy as np,pandas as pd
from scipy import stats
os.chdir(Path(__file__).resolve().parents[1]);Path('results').mkdir(exist_ok=True)
summary=[];pairs=[];omnibus=[]
def compare(name,groups):
 for k,v in groups.items():
  summary.append(dict(analysis=name,group=k,n=len(v),mean=np.mean(v),sd=np.std(v,ddof=1),se=stats.sem(v)))
 k=len(groups);ns=np.array([len(v)for v in groups.values()]);means=np.array([np.mean(v)for v in groups.values()]);variances=np.array([np.var(v,ddof=1)for v in groups.values()]);w=ns/variances;mu=np.sum(w*means)/sum(w);term=np.sum((1-w/sum(w))**2/(ns-1));F=np.sum(w*(means-mu)**2)/(k-1)/(1+2*(k-2)*term/(k*k-1));df2=(k*k-1)/(3*term)
 omnibus.append(dict(analysis=name,test='Welch ANOVA',statistic=F,df1=k-1,df2=df2,p=stats.f.sf(F,k-1,df2)))
 for (a,x),(b,y) in itertools.combinations(groups.items(),2):
  vx=np.var(x,ddof=1)/len(x);vy=np.var(y,ddof=1)/len(y);df=(vx+vy)**2/(vx*vx/(len(x)-1)+vy*vy/(len(y)-1));t=abs(np.mean(x)-np.mean(y))/np.sqrt(vx+vy)
  pairs.append(dict(analysis=name,group1=a,group2=b,t_abs=t,df=df,p_Welch=2*stats.t.sf(t,df),p_Games_Howell=stats.studentized_range.sf(t*np.sqrt(2),k,df)))
e=pd.read_csv('data/eggs.csv');compare('B_eggs',{k:g.eggs_total.to_numpy() for k,g in e.groupby('group',sort=False)})
d=pd.read_csv('data/development.csv');compare('D_development',{k:g.days_hatch_to_cocoon.to_numpy()for k,g in d.groupby('group',sort=False)})
s=pd.read_csv('data/survival.csv');out=[]
for _,r in s.iterrows():
 m=r.adult_ND_M+r.adult_D_M;f=r.adult_ND_F+r.adult_D_F;test=stats.chisquare([m,f]);out.append(dict(group=r.group,male=m,female=f,chi2=test.statistic,df=1,p=test.pvalue,label='***' if test.pvalue<.001 else '**' if test.pvalue<.01 else '*' if test.pvalue<.05 else 'ns'))
pd.DataFrame(out).to_csv('results/C_sex_ratio_tests.csv',index=False)
r=pd.read_csv('data/individuals.tsv',sep='\t').dropna(how='all');r=r[r.sex.isin(['M','F'])].copy();r['group']=r.group.replace({'E. delphinii, Ipswich clutch':'E. delphinii','E. delphinii, wild from DMV area':'E. delphinii'})
measured=r[r.wing_status.eq('measured')];letters={'M':['b','a','a','ab'],'F':['c','ab','ab','a','bc']};checks=[];donuts=[]
for sex in ['M','F']:
 z=measured[measured.sex.eq(sex)];hy=z[z.group.isin(['F1-1','F1-2','F1-3'])];groups={}
 for state in ['Y','N']:
  v=hy[hy.diapaused.eq(state)].forewing_mm.to_numpy()
  if len(v):groups['F1 pooled '+state]=v
 for g,state in [('Inbred E. incisa','N'),('Parental E. incisa (2024 brood)','Y'),('E. delphinii','Y')]:groups[g+' '+state]=z[z.group.eq(g)&z.diapaused.eq(state)].forewing_mm.to_numpy()
 name='EF_forewing_'+sex;compare(name,groups);cld=dict(zip(groups,letters[sex]))
 for p in [x for x in pairs if x['analysis']==name]:checks.append(dict(**p,letter1=cld[p['group1']],letter2=cld[p['group2']],compatible=(bool(set(cld[p['group1']])&set(cld[p['group2']]))==(p['p_Games_Howell']>=.05))))
 for g in ['F1-1','F1-2','F1-3','F1 pooled','Inbred E. incisa','Parental E. incisa (2024 brood)','E. delphinii']:
  z=r[r.sex.eq(sex)&(r.group.isin(['F1-1','F1-2','F1-3']) if g=='F1 pooled' else r.group.eq(g))];D=int(z.diapaused.eq('Y').sum());ND=int(z.diapaused.eq('N').sum());donuts.append(dict(sex=sex,group=g,D=D,ND=ND,percent_D=100*D/(D+ND)))
pd.DataFrame(summary).to_csv('results/descriptive_statistics.csv',index=False);pd.DataFrame(pairs).to_csv('results/pairwise_tests.csv',index=False);pd.DataFrame(omnibus).to_csv('results/Welch_ANOVA.csv',index=False);pd.DataFrame(checks).to_csv('results/CLD_audit.csv',index=False);pd.DataFrame(donuts).to_csv('results/diapause_counts.csv',index=False)
print('Historical letter comparisons compatible with recomputed Games–Howell:',sum(c['compatible']for c in checks),'/',len(checks))

parental=pd.read_csv('data/parental_adult_counts.csv')
parental_results=[]
for row in parental.itertuples():
 test=stats.chisquare([row.male,row.female])
 parental_results.append(dict(group=row.group,male=row.male,female=row.female,chi2=test.statistic,df=1,p=test.pvalue,label='ns' if test.pvalue>=.05 else '*'))
pd.DataFrame(parental_results).to_csv('results/C_parental_sex_ratio_tests.csv',index=False)
