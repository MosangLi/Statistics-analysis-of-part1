"""MPHY0044 Part 1: offline reaction time analysis (desktop Python).
Install numpy, pandas, matplotlib, scipy before running.
Edit FILES and COLUMNS to match the actual exported CSV files.
One row per trial, RT in milliseconds; blank RT for no response.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from itertools import combinations

BASE = Path(__file__).resolve().parent
OUT = BASE / 'analysis_results'
FILES = {'Simple': 'simple_data.csv',
         'Recognition': 'recognition_data.csv',
         'Choice': 'choice_data.csv'}
# Change the values below to match your CSV column names.
COLUMNS = {
    'Simple': {'rt': 'RT_ms'},
    'Recognition': {'rt': 'RT_ms', 'result': 'Result'},
    'Choice': {'rt': 'RT_ms', 'correct': 'Correct'},
}
# Recognition Result must contain TP, TN, FP or FN.
# Choice Correct must be 1/0, True/False or Correct/Incorrect.


def load_data(name):
    df = pd.read_csv(BASE / FILES[name])
    cols = COLUMNS[name]
    rt = pd.to_numeric(df[cols['rt']], errors='coerce')
    valid = np.isfinite(rt) & (rt > 0)
    performance = {'Experiment': name, 'Trials': len(df)}
    if name == 'Recognition':
        result = df[cols['result']].astype(str).str.strip().str.upper()
        if not result.isin(['TP', 'TN', 'FP', 'FN']).all():
            raise ValueError('Recognition Result must contain TP/TN/FP/FN.')
        tp, tn, fp, fn = (int((result == x).sum()) for x in ['TP','TN','FP','FN'])
        performance.update(TP=tp, TN=tn, FP=fp, FN=fn,
                           Accuracy_pct=rate(tp+tn, len(df)),
                           FPR_pct=rate(fp, fp+tn), FNR_pct=rate(fn, fn+tp))
        valid &= result.eq('TP')
    elif name == 'Choice':
        correct = df[cols['correct']].astype(str).str.strip().str.lower()
        yes = correct.isin(['1','1.0','true','correct'])
        no = correct.isin(['0','0.0','false','incorrect'])
        if not (yes | no).all():
            raise ValueError('Choice Correct must contain recognised binary labels.')
        performance.update(Correct=int(yes.sum()), Incorrect=int(no.sum()),
                           Accuracy_pct=rate(yes.sum(), len(df)))
        valid &= yes
    values = rt[valid].to_numpy(dtype=float)
    performance['RT_trials_included'] = len(values)
    performance['RT_trials_excluded'] = len(df)-len(values)
    return values, performance


def rate(n, d):
    return 100*n/d if d else np.nan


def describe(name, x):
    n = len(x)
    return {'Experiment': name, 'N': n, 'Mean_ms': np.mean(x),
            'Median_ms': np.median(x),
            'SD_ms': np.std(x, ddof=1) if n > 1 else np.nan,
            'SEM_ms': stats.sem(x) if n > 1 else np.nan,
            'P10_ms': np.percentile(x, 10), 'P90_ms': np.percentile(x, 90)}


def save_plot(name):
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    OUT.mkdir(exist_ok=True)
    data, summaries, performance = {}, [], []
    for name in FILES:
        if not (BASE / FILES[name]).exists():
            print('Missing file:', FILES[name])
            continue
        x, p = load_data(name)
        performance.append(p)
        if not len(x):
            print('No valid RTs:', name)
            continue
        data[name] = x
        summaries.append(describe(name, x))
    if performance:
        p = pd.DataFrame(performance)
        p.to_csv(OUT / 'performance.csv', index=False)
        print(p.to_string(index=False))
        if 'Accuracy_pct' in p:
            a = p.dropna(subset=['Accuracy_pct'])
            if len(a):
                plt.figure(figsize=(6,4))
                plt.bar(a.Experiment, a.Accuracy_pct)
                plt.ylim(0,100)
                plt.ylabel('Accuracy (%)')
                save_plot('accuracy.png')
    if not data:
        print('No valid reaction time data available.')
        return
    s = pd.DataFrame(summaries)
    s.to_csv(OUT / 'reaction_time_statistics.csv', index=False)
    print(s.to_string(index=False))
    bins = np.histogram_bin_edges(np.concatenate(list(data.values())), bins='auto')
    for name, x in data.items():
        plt.figure(figsize=(7,4))
        plt.hist(x, bins=bins, weights=np.ones(len(x))/len(x), edgecolor='black')
        plt.axvline(np.mean(x), linestyle='--', label='Mean')
        plt.xlabel('Reaction time (ms)')
        plt.ylabel('Proportion of valid trials')
        plt.title(name + ' reaction time')
        plt.legend()
        save_plot(name.lower() + '_histogram.png')
    plt.figure(figsize=(7,5))
    plt.boxplot(list(data.values()))
    plt.xticks(range(1,len(data)+1), list(data))
    plt.ylabel('Reaction time (ms)')
    save_plot('comparative_boxplot.png')
    # Exploratory trial-level comparisons only: repeated trials from one
    # participant are not independent participant-level observations.
    tests = []
    for a,b in combinations(data,2):
        x,y = data[a],data[b]
        if min(len(x),len(y)) < 2:
            continue
        t,p = stats.ttest_ind(x,y,equal_var=False)
        tests.append({'Group_A':a,'Group_B':b,'Mean_difference_ms':np.mean(x)-np.mean(y),
                      'Welch_t':t,'p_raw':p})
    if tests:
        t = pd.DataFrame(tests)
        t['p_Bonferroni'] = (t.p_raw * 3).clip(upper=1)
        t.to_csv(OUT / 'exploratory_trial_tests.csv',index=False)
        print(t.to_string(index=False))
        print('CAUTION: trial-level tests assume independent trials; no population inference.')
    print('Results saved in', OUT)


if __name__ == '__main__':
    main()
