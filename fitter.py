import csv, json, os
import numpy as np

def load_samples(path):
    vals = []
    with open(path, 'r', encoding='utf-8') as f:
        r = csv.reader(f)
        for row in r:
            if not row: continue
            try:
                vals.append(float(row[0]))
            except:
                continue
    return np.array(vals)

def fit_normal(samples):
    mu = float(np.mean(samples))
    sigma = float(np.std(samples, ddof=0))
    return {'dist':'normal','mu':mu,'sigma':sigma}

def save_model_json(model, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(model, f, indent=2)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', help='input CSV with one numeric column of samples')
    parser.add_argument('--out', help='output JSON model path', default='model.json')
    args = parser.parse_args()
    s = load_samples(args.csv)
    if s.size == 0:
        print('No samples')
    else:
        m = fit_normal(s)
        save_model_json(m, args.out)
        print('Saved model to', args.out)
