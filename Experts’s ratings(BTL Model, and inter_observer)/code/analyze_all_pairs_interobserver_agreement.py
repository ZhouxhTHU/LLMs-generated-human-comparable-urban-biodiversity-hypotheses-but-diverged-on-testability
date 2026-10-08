# -*- coding: utf-8 -*-
"""All-source repeated-pair reliability, with paired dimension comparisons.

Run: python analyze.py
Requires numpy, pandas, openpyxl. Plotting additionally uses matplotlib in
this runtime or an existing Python on PATH. All outputs stay beside this file.
"""
from pathlib import Path
import hashlib
import itertools
import json
import os
import sys
import subprocess
import shutil
import importlib.util
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
SOURCE=PROJECT/'Experts\u2019s ratings(DescriptionAnalysis)'/'All_Comparison_Results.xlsx'
MANUSCRIPT_MATERIALS=ROOT.parent/'manuscript_materials'
INTERNAL_REPORTS=ROOT.parent/'internal_reports'/'all_pairs_agreement'
DIMS=['Novelty','Significance','Testability']
SEED=20260921
B=10000


def alpha(c):
    """Nominal coincidence alpha; omit units with <2 ratings, never impute."""
    c=np.asarray(c,dtype=float)
    c=c[c.sum(axis=1)>=2]
    n=c.sum(axis=1)
    N=n.sum()
    if N<2:
        return np.nan
    do=((n*n-(c*c).sum(axis=1))/(n-1)).sum()/N
    marg=c.sum(axis=0)
    de=(N*N-(marg*marg).sum())/(N*(N-1))
    return 1-do/de if de>0 else np.nan


def independent_alpha(units):
    coincidence=np.zeros((3,3))
    for values in units:
        for i,j in itertools.permutations(range(len(values)),2):
            coincidence[values[i],values[j]]+=1/(len(values)-1)
    N=coincidence.sum()
    marg=coincidence.sum(axis=0)
    return 1-((N-np.trace(coincidence))/N)/((N*N-(marg*marg).sum())/(N*(N-1)))


def save(df,name):
    df.to_csv(ROOT/name,index=False,encoding='utf-8-sig',na_rep='NA')


def table(df):
    return '\n'.join(['| '+' | '.join(df.columns)+' |','| '+' | '.join(['---']*len(df.columns))+' |']+['| '+' | '.join(map(str,row))+' |' for row in df.itertuples(index=False,name=None)])


def plot():
    os.environ['MPLCONFIGDIR']=str(ROOT/'.matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    d=pd.read_csv(ROOT/'01_reliability_summary.csv').set_index('Dimension').loc[DIMS]
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans','Liberation Sans'],
                         'font.size':9.5,'axes.titlesize':10,'axes.labelsize':10,
                         'xtick.labelsize':9,'ytick.labelsize':10,'pdf.fonttype':42,
                         'ps.fonttype':42,'axes.unicode_minus':False,
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(4.8,3.1))
    v=d.Exact_agreement_percent.values
    err=np.vstack([v-d.Agreement_CI_lower_percent.values,d.Agreement_CI_upper_percent.values-v])
    ax.set_axisbelow(True)
    ax.grid(axis='y',color='0.92',linewidth=.6)
    for i,(y,color) in enumerate(zip((2,1,0),['#0072B2','#E69F00','#CC79A7'])):
        ax.errorbar(v[i],y,xerr=err[:,i:i+1],fmt='o',markersize=5.8,
                    markerfacecolor=color,markeredgecolor='white',markeredgewidth=.8,
                    ecolor=color,elinewidth=1.7,capsize=3,capthick=1.1,zorder=3)
    ax.set_xlim(0,60)
    ax.set_xticks([0,20,40,60])
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=100,decimals=0))
    ax.set_ylim(-.55,2.55)
    ax.set_yticks([2,1,0],labels=DIMS)
    ax.set_xlabel('Exact agreement',labelpad=6)
    ax.set_title('Inter-observer agreement',loc='left',fontsize=10,fontweight='semibold',pad=10)
    ax.tick_params(axis='both',length=3,width=.8,color='0.25',pad=4)
    ax.spines['left'].set_linewidth(.8)
    ax.spines['bottom'].set_linewidth(.8)
    fig.subplots_adjust(left=.24,right=.97,bottom=.22,top=.78)
    for ext in ['png','pdf']:
        fig.savefig(ROOT/f'03_agreement_by_dimension.{ext}',dpi=600,facecolor='white')
    plt.close(fig)


def main():
    MANUSCRIPT_MATERIALS.mkdir(parents=True,exist_ok=True)
    INTERNAL_REPORTS.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    raw=pd.read_excel(SOURCE,dtype=str,keep_default_na=False)
    required=['Expert_ID','Hypothesis_A_ID','Hypothesis_B_ID','Dimension','Result']
    assert set(required).issubset(raw.columns)
    assert not (raw[required].isna()|raw[required].eq('')).any().any()
    assert not raw.duplicated().any()
    assert set(raw.Dimension)==set(DIMS)
    assert (raw.Result.eq(raw.Hypothesis_A_ID)|raw.Result.eq(raw.Hypothesis_B_ID)|raw.Result.eq('Tie')).all()
    assert raw.Hypothesis_A_ID.ne(raw.Hypothesis_B_ID).all()
    assert raw.Hypothesis_A_ID.str.fullmatch(r'(HUM|LLM)_\d+').all()
    assert raw.Hypothesis_B_ID.str.fullmatch(r'(HUM|LLM)_\d+').all()
    d=raw.copy()
    d.insert(0,'Source_Row',np.arange(2,len(d)+2))
    ordered=[sorted([a,b]) for a,b in zip(d.Hypothesis_A_ID,d.Hypothesis_B_ID)]
    d['Hypothesis_1']=[x[0] for x in ordered]
    d['Hypothesis_2']=[x[1] for x in ordered]
    d['Pair_ID']=['__'.join(x) for x in ordered]
    d['Pair_type']=['-'.join([x[0].split('_')[0],x[1].split('_')[0]]) for x in ordered]
    assert not d.duplicated(['Expert_ID','Dimension','Pair_ID']).any()
    # Within-pair fixed identity, independent of presented A/B and source label.
    d['Choice']=np.select([d.Result.eq(d.Hypothesis_1),d.Result.eq(d.Hypothesis_2),d.Result.eq('Tie')],[0,1,2],default=-1)
    assert d.Choice.ge(0).all()
    n=d.groupby(['Dimension','Pair_ID']).Expert_ID.transform('nunique')
    rep=d[n>=2].copy()
    rep['Standardized_Result']=rep.Choice.map({0:'HYPOTHESIS_1',1:'HYPOTHESIS_2',2:'TIE'})
    save(rep,'07_repeated_judgments.csv')
    pairs=sorted(rep.Pair_ID.unique())
    # Paired inference requires identical items AND expert assignment by dimension.
    assignments=[set(zip(g.Pair_ID,g.Expert_ID)) for _,g in rep.groupby('Dimension')]
    assert all(x==assignments[0] for x in assignments)
    counts=np.stack([pd.crosstab(rep[rep.Dimension.eq(dim)].Pair_ID,rep[rep.Dimension.eq(dim)].Choice).reindex(index=pairs,columns=[0,1,2],fill_value=0).values for dim in DIMS],axis=1)
    sizes=counts.sum(axis=2)
    assert (sizes[:,0,None]==sizes).all()
    agree=(counts*(counts-1)/2).sum(axis=2)
    denom=sizes*(sizes-1)/2
    # Known analytic examples and independent ordered-expert enumeration.
    assert np.isclose(alpha([[2,0,0],[0,2,0]]),1)
    assert np.isclose(alpha([[1,1,0],[1,1,0]]),-.5)
    assert np.isclose(alpha([[2,0,0],[1,2,0],[0,0,1],[0,2,0]]),.5)
    for i,dim in enumerate(DIMS):
        units=[g.Choice.tolist() for _,g in rep[rep.Dimension.eq(dim)].groupby('Pair_ID')]
        assert np.isclose(alpha(counts[:,i]),independent_alpha(units))
        combos=[a==b for u in units for a,b in itertools.combinations(u,2)]
        assert sum(combos)==agree[:,i].sum() and len(combos)==denom[:,i].sum()
    rng=np.random.default_rng(SEED)
    draws=np.empty((B,3))
    alpha_draws=np.empty((B,3))
    # Same sampled Pair_ID indices in all three dimensions preserve pairing.
    for start in range(0,B,250):
        idx=rng.integers(0,len(pairs),size=(min(250,B-start),len(pairs)))
        draws[start:start+len(idx)]=agree[idx].sum(axis=1)/denom[idx].sum(axis=1)
        cc=counts[idx]
        nn=cc.sum(axis=3)
        N=nn.sum(axis=1)
        marg=cc.sum(axis=1)
        do=((nn*nn-(cc*cc).sum(axis=3))/(nn-1)).sum(axis=1)/N
        de=(N*N-(marg*marg).sum(axis=2))/(N*(N-1))
        alpha_draws[start:start+len(idx)]=1-do/de
    assert np.isfinite(draws).all() and np.isfinite(alpha_draws).all()
    summaries=[]
    for i,dim in enumerate(DIMS):
        sub=rep[rep.Dimension.eq(dim)]
        lo,hi=np.quantile(draws[:,i],[.025,.975])*100
        al,ah=np.quantile(alpha_draws[:,i],[.025,.975])
        summaries.append(dict(Dimension=dim,Total_unique_pairs=d[d.Dimension.eq(dim)].Pair_ID.nunique(),Repeated_pairs=len(pairs),Judgments=len(sub),Experts=sub.Expert_ID.nunique(),HUM_HUM_pairs=sub[sub.Pair_type.eq('HUM-HUM')].Pair_ID.nunique(),HUM_LLM_pairs=sub[sub.Pair_type.eq('HUM-LLM')].Pair_ID.nunique(),LLM_LLM_pairs=sub[sub.Pair_type.eq('LLM-LLM')].Pair_ID.nunique(),Agreement_numerator=int(agree[:,i].sum()),Comparison_denominator=int(denom[:,i].sum()),Exact_agreement_percent=100*agree[:,i].sum()/denom[:,i].sum(),Agreement_CI_lower_percent=lo,Agreement_CI_upper_percent=hi,Nominal_alpha=alpha(counts[:,i]),Alpha_CI_lower=al,Alpha_CI_upper=ah))
    summary=pd.DataFrame(summaries)
    save(summary,'01_reliability_summary.csv')
    comparisons=[]
    for i,j in itertools.combinations(range(3),2):
        delta=(draws[:,i]-draws[:,j])*100
        lo,hi=np.quantile(delta,[.025,.975])
        # 98.333% per-comparison percentile intervals: nominal Bonferroni
        # familywise 95% coverage for three contrasts, subject to bootstrap validity.
        blo,bhi=np.quantile(delta,[.05/(2*3),1-.05/(2*3)])
        comparisons.append(dict(Contrast=DIMS[i]+' minus '+DIMS[j],Difference_percentage_points=summary.Exact_agreement_percent[i]-summary.Exact_agreement_percent[j],CI95_lower=lo,CI95_upper=hi,Bonferroni_CI_lower=blo,Bonferroni_CI_upper=bhi,Adjusted_interval_excludes_zero=bool(blo>0 or bhi<0)))
    diff=pd.DataFrame(comparisons)
    save(diff,'02_dimension_differences.csv')
    details=[]
    types=rep.set_index('Pair_ID').Pair_type.to_dict()
    for u,pair in enumerate(pairs):
        for i,dim in enumerate(DIMS):
            details.append(dict(Pair_ID=pair,Pair_type=types[pair],Dimension=dim,N_experts=int(sizes[u,i]),Hypothesis_1_count=int(counts[u,i,0]),Hypothesis_2_count=int(counts[u,i,1]),Tie_count=int(counts[u,i,2]),Agreement_numerator=int(agree[u,i]),Comparison_denominator=int(denom[u,i])))
    save(pd.DataFrame(details),'06_pair_summary.csv')
    printable=pd.DataFrame([{'维度':r.Dimension,'一致判断 / 专家组合':f'{r.Agreement_numerator}/{r.Comparison_denominator}','完全一致率（95% CI）':f'{r.Exact_agreement_percent:.1f}% ({r.Agreement_CI_lower_percent:.1f}–{r.Agreement_CI_upper_percent:.1f})','名义 alpha（95% CI）':f'{r.Nominal_alpha:.3f} ({r.Alpha_CI_lower:.3f}–{r.Alpha_CI_upper:.3f})'} for r in summary.itertuples()])
    contrast_table=pd.DataFrame([{'差值方向':r.Contrast,'差值（百分点）':f'{r.Difference_percentage_points:.2f}','95% CI':f'[{r.CI95_lower:.2f}, {r.CI95_upper:.2f}]','三次比较校正后区间':f'[{r.Bonferroni_CI_lower:.2f}, {r.Bonferroni_CI_upper:.2f}]','校正区间排除 0':str(r.Adjusted_interval_excludes_zero)} for r in diff.itertuples()])
    supported=diff[diff.Adjusted_interval_excludes_zero]
    if len(supported):
        inference='After adjustment for three comparisons, the interval excluded zero for '+ '; '.join(f'{r.Contrast} ({r.Difference_percentage_points:.2f} percentage points, adjusted CI {r.Bonferroni_CI_lower:.2f} to {r.Bonferroni_CI_upper:.2f})' for r in supported.itertuples())+'.'
    else:
        inference='All three multiplicity-adjusted intervals for between-dimension differences included zero, so the observed ordering did not provide clear evidence of differences under this analysis.'
    methods='We assessed inter-observer agreement separately for novelty, significance and testability using all hypothesis pairs rated by at least two experts, including human–human, human–LLM and LLM–LLM comparisons. We merged reversed presentation orders using sorted hypothesis identifiers and coded judgments as selection of the first or second canonical hypothesis, or a tie. Exact agreement was the proportion of matching judgments across all within-pair expert combinations. Nominal Krippendorff’s alpha was also calculated. We used 10,000 paired hypothesis-pair bootstrap resamples to estimate confidence intervals and between-dimension differences in exact agreement, with Bonferroni-adjusted intervals for the three comparisons.'
    results=f'Each dimension included {len(pairs)} repeated pairs and {len(rep)//3} judgments from {rep.Expert_ID.nunique()} experts. Exact agreement for novelty, significance and testability was '+', '.join(f'{v:.1f}%' for v in summary.Exact_agreement_percent)+', respectively; corresponding nominal alpha values were '+', '.join(f'{v:.3f}' for v in summary.Nominal_alpha)+'. '+inference+' These estimates describe agreement on repeated pairs, not the balance of aggregate preferences for human- versus LLM-generated hypotheses.'
    caption='Figure. Inter-observer agreement across evaluation dimensions. Points show exact agreement across all within-pair expert combinations for repeated hypothesis pairs, including human–human, human–LLM and LLM–LLM comparisons. Horizontal error bars are pointwise 95% percentile confidence intervals from 10,000 paired hypothesis-pair bootstrap resamples. Between-dimension differences are evaluated directly using paired bootstrap contrasts and multiplicity-adjusted intervals, rather than by comparing the overlap of these error bars.'
    (MANUSCRIPT_MATERIALS/'all_pairs_agreement_manuscript_text.md').write_text('# Methods\n\n'+methods+'\n\n# Results\n\n'+results+'\n\n# Figure caption\n\n'+caption+'\n',encoding='utf-8')
    report=f'''# 全来源假设对：精简专家一致性分析

## 目的与范围

回答两个问题：不同专家评价同一假设对时有多一致？Novelty、Significance、Testability 的一致性是否存在明确差异？纳入 HUM–HUM、HUM–LLM、LLM–LLM，不筛选来源。保留 Tie，不再添加去 Tie、分来源系数和大量 pairwise kappa 分析。

原始数据共 {len(raw)} 行。各维度有 {int(summary.Total_unique_pairs.iloc[0])} 个唯一假设对，其中 {len(pairs)} 个至少由 2 位专家评价，共 {int(summary.Judgments.iloc[0])} 条判断，涉及 {int(summary.Experts.iloc[0])} 位专家。重复对构成为 HUM–HUM {int(summary.HUM_HUM_pairs.iloc[0])}、HUM–LLM {int(summary.HUM_LLM_pairs.iloc[0])}、LLM–LLM {int(summary.LLM_LLM_pairs.iloc[0])}。未发现缺失、重复评分、非法 Result 或自我比较。不同 A/B 顺序已按相同两个 ID 合并。

## 一致性统计

主指标为完全一致率：同一假设对的专家组合中，选择同一假设或都选 Tie 的比例。每个维度共 {int(denom[:,0].sum())} 个专家组合比较；人数较多的 pair 贡献更多组合。alpha 作为机会校正的辅助指标。

{table(printable)}

## 维度间差异

三个维度具有完全相同的 pair 集合和专家分配。以假设对为单位，同一次抽样在三个维度使用相同的 pair 索引，重复 {B:,} 次，随机种子 {SEED}。下表比较完全一致率，正值表示前一维度更高；不以三个独立样本处理，也不根据两条单独 CI 是否重叠判断差异。除常规 95% CI 外，三次比较使用各自 98.333% percentile CI 作 Bonferroni 校正，对应名义上总体 95% 覆盖率。

{table(contrast_table)}

{inference}

## 写作边界

- 该结果支持讨论“同一假设对的专家一致性”，不再专门回答 Human 对 LLM 的偏好。
- 未排除任何来源类型，但 repeated subset 仍以跨来源对为主（{int(summary.HUM_LLM_pairs.iloc[0])}/{len(pairs)}）。不能据此断言三个来源类型各自都有相同可靠性。
- CI 条件于当前专家面板；pair 间共享专家或单个假设的依赖未被完全建模，因此属于当前面板的探索性维度比较，不能直接推广为专家总体的正式推断。
- alpha 用排序后的假设 1／假设 2／Tie 三分类计算，缺失评分不补齐。其机会基线受固定 ID 排序编码影响，因此以不依赖类别边际基线的完全一致率作为主结果；不要把 alpha 当成不受编码影响的绝对质量评级。
- “没有明确差异”不等于证明各维度相等。本分析没有做等效性检验。

## 文件与复现

首先看 `01_reliability_summary.csv` 和 `02_dimension_differences.csv`；论文文字和图注见 `04_manuscript_text.md`，图片见 `03_agreement_by_dimension.pdf/png`。`06_pair_summary.csv`、`07_repeated_judgments.csv` 供核查。唯一分析脚本为 `analyze.py`，执行 `python analyze.py` 即可重算；依赖 numpy、pandas、openpyxl，绘图另需 matplotlib。原始数据只读，旧分析和精选包未改动。

alpha 公式沿用 [Krippendorff 的名义 coincidence 定义](https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff%27s%20Alpha-Reliability.pdf)，并以手算例子及实际数据的显式有序专家组合枚举交叉验证。所有分子分母也用实际专家组合逐项核对。
'''
    (INTERNAL_REPORTS/'all_pairs_agreement_report.md').write_text(report,encoding='utf-8')
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==h
    (INTERNAL_REPORTS/'run_info.json').write_text(json.dumps({'input':str(SOURCE),'sha256':h,'input_unchanged':True,'seed':SEED,'bootstrap_resamples':B,'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'validation':'no missing, duplicates, invalid results or self-comparisons; paired item/expert assignments verified; alpha independently cross-checked','primary_estimand':'expert-combination-weighted exact agreement','contrasts':'paired pair-cluster bootstrap of exact agreement; 3 contrasts with Bonferroni percentile intervals'},ensure_ascii=False,indent=2),encoding='utf-8')
    py=sys.executable if importlib.util.find_spec('matplotlib') else shutil.which('python')
    plot_note='No plotting runtime available.'
    if py:
        done=subprocess.run([py,str(Path(__file__).resolve()),'--plot-only'],capture_output=True,text=True)
        plot_note='Figure generated.' if done.returncode==0 else done.stderr
    log=summary.to_string(index=False)+'\n\n'+diff.to_string(index=False)+'\n\n'+plot_note+'\n\n'+inference
    (INTERNAL_REPORTS/'analysis.log').write_text(log,encoding='utf-8')
    print(log)
    print('\nFiles:\n'+'\n'.join(str(f) for f in sorted(ROOT.glob('*')) if f.is_file()))


if __name__=='__main__':
    plot() if '--plot-only' in sys.argv else main()
