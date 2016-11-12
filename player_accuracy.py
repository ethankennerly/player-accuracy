"""
TODO
Compare player accuracy dispersion between
basketball field goals and baseball hits.
More info in README.md
"""

from pandas import DataFrame, read_csv, to_numeric
import pandas


def extract_accuracy(gamelog, attempt_name, correct_name, group_name = None):
    accuracy = DataFrame()
    accuracy['attempts'] = gamelog[attempt_name]
    accuracy['corrects'] = gamelog[correct_name]
    accuracy = accuracy.apply(lambda x: to_numeric(x, errors='coerce'))
    if group_name:
        accuracy['group'] = gamelog[group_name]
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


if '__main__' == __name__:
    from doctest import testfile
    testfile('README.md')
