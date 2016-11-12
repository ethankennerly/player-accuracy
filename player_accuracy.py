"""
TODO
Compare player accuracy dispersion between
basketball field goals and baseball hits.
More info in README.md
"""

from pandas import read_csv

def extract_accuracy(gamelog, attempt_name, correct_name):
    accuracy = gamelog[[attempt_name, correct_name]]
    accuracy.columns = ['attempts', 'corrects']
    accuracy['accuracy'] = accuracy['corrects'] / accuracy['attempts']
    accuracy['errors'] = accuracy['attempts'] - accuracy['corrects']
    accuracy['inaccuracy'] = accuracy['attempts'] / accuracy['corrects']
    return accuracy


if '__main__' == __name__:
    from doctest import testfile
    testfile('README.md')
