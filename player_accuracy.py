"""
Compare player accuracy dispersion between diverse game rules.
More info in README.md
"""

from pandas import DataFrame, read_csv, read_table, to_numeric
import pandas

from player_accuracy_config import configs
from StringIO import StringIO
from random import random
from os.path import exists


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
        frame[name] = group.std().median()
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
        groups = accuracy.groupby(group_name)
        compares.append(groups)
    std_medians = std_median(compares, paths)
    std_medians = std_medians.round(3)
    in_string = StringIO()
    std_medians.to_csv(in_string, index_label = group_name, sep='\t')
    return in_string.getvalue()


def random_csvs(accuracy_ranges, players_sessions, 
        attempt_name = 'attempts', correct_name = 'corrects', group_name = 'group'):
    paths = []
    for low, high in accuracy_ranges:
        for player_count in players_sessions:
            attempts = []
            corrects = []
            player_ids = []
            for player_id in range(player_count):
                for session_count in range(player_count):
                    correct_count = 0
                    attempt_count = 0
                    accuracy = random() * (high - low) + low
                    for attempt in range(player_count):
                        attempt_count += 1
                        if random() < accuracy:
                            correct_count += 1
                    player_ids.append(player_id)
                    attempts.append(attempt_count)
                    corrects.append(correct_count)
            sessions = DataFrame()
            sessions[group_name] = player_ids
            sessions[attempt_name] = attempts
            sessions[correct_name] = corrects
            path = 'test_random_%s_%s_%s_%s.tsv' % (
                low, high, player_count, player_count)
            paths.append(path)
            if not exists(path):
                sessions.to_csv(path, index=False, sep='\t')
    return paths


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
