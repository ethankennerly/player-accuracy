"""
TODO
Compare player accuracy dispersion between
basketball field goals and baseball hits.
More info in README.md
"""

from pandas import DataFrame, read_csv, read_table, to_numeric
import pandas

from player_accuracy_config import configs
from StringIO import StringIO


def extract_accuracy(gamelog, attempt_name, correct_name, group_name = None):
    accuracy = DataFrame()
    accuracy['attempts'] = gamelog[attempt_name]
    accuracy['corrects'] = gamelog[correct_name]
    accuracy = accuracy.apply(lambda x: to_numeric(x, errors='coerce'))
    if group_name:
        accuracy[group_name] = gamelog[group_name]
    accuracy['accuracy'] = accuracy['corrects'] / accuracy['attempts']
    accuracy['errors'] = accuracy['attempts'] - accuracy['corrects']
    accuracy['inaccuracy'] = accuracy['attempts'] / accuracy['corrects']
    return accuracy


def quantile_dispersion(frame, quantiles=[0.25, 0.75]):
    quantiled = frame.quantile(quantiles).transpose()
    lower = quantiles[0]
    upper = quantiles[-1]
    dispersion = (quantiled[upper] - quantiled[lower]
        ) / (quantiled[upper] + quantiled[lower])
    return dispersion


def disperse(accuracy):
    pct = accuracy.rank(pct = True)
    dispersion = DataFrame()
    dispersion['mean'] = pct.mean()
    dispersion['quartile'] = quantile_dispersion(pct)
    dispersion['std'] = pct.std()
    return dispersion


def percentile_groups(accuracy, group_name):
    pct = accuracy.rank(pct = True)
    pct[group_name] = accuracy[group_name]
    groups = pct.groupby(group_name)
    return groups


def concat_csvs(paths, group_name):
    frames = []
    for path in paths:
        frame = read_csv(path)
        frame[group_name] = path
        frames.append(frame)
    everybody = pandas.concat(frames)
    return everybody


def std_median(groups, names):
    frame = DataFrame()
    for group, name in zip(groups, names):
        median = group.std().median()
        frame[name] = median
    frame = frame.transpose()
    return frame


def compare_tsv(key, configs):
    config = configs[key]
    compares = []
    paths = []
    for path, attempt_name, correct_name, group_name in config:
        table = read_table(path)
        paths.append(path)
        accuracy = extract_accuracy(table, attempt_name, correct_name, group_name)
        groups = percentile_groups(accuracy, group_name)
        compares.append(groups)
    std_medians = std_median(compares, paths)
    std_medians = std_medians.round(3)
    in_string = StringIO()
    std_medians.to_csv(in_string, index_label = group_name, sep='\t')
    return in_string.getvalue()


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', action='store_true', help='Run tests in README.md')
    parser.add_argument('config_key', help='Configuration key in player_accuracy_config.py', default='test')
    args = parser.parse_args()
    if args.test:
        from doctest import testfile
        testfile('README.md')
    elif args.config_key:
        print(compare_tsv(args.config_key, configs))
