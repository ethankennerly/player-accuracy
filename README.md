# TODO: How can basketball field goals and baseball hits be compared?

In general, I find it interesting to compare game systems by player performance metrics.

For example:

Are players more consistent at field goals or batting?

I conveniently found game logs with accuracy metrics for basketball and baseball.

Accuracy is confounded by difficulty.  Making a field goal is influenced by the performance of the defensive players.  Hitting a baseball is influenced by the performance of the pitcher.

Basketball player game log

* FGA: Field goals attempted.
* FGM: Field goals made.

This was in CSV format.  Example:

<http://www.basketball-reference.com/players/c/curryst01/gamelog/2016/>

Baseball player game log

* AB: Times at bat.
* H: Hits.

This was in CSV format.  Example:

<http://www.baseball-reference.com/players/gl.cgi?id=fernajo02&t=b&year=>

## Candidate metrics of accuracy

* Accuracy:  Number correct / number of tries
* Inaccuracy:  Number of tries / number correct
* Errors:  Number of tries - number correct

### Normalizing different number of attempts

Some players have more field goal attempts than a corresponding player at bat.

The greater number of attempts tends to decrease sample standard deviation.

A similar number of attempts would make them comparable.

Or it can be recognized that the game with fewer attempts has greater deviation.

### Normalizing between distributions

How to compare dispersion between different game systems?

* Percentiles among game players' latest session
* Quartile coefficient of dispersion
* Z-score among game players' latest session

Percentiles converts different distributions and normalizes outliers.

For distributions with a long tail, percentiles compresses values toward the center.

Percentiles could be over all game sessions or stratified by game players.

For simplicity here, I will calculate percentiles from all game sessions.

Then dispersion of percentiles.

Quartile dispersion ignores outliers and half of the sample.

### Not coefficient of variation

Coefficient of variation is fragile to distributions.  To quote Wikipedia:

> A more robust possibility is the quartile coefficient of dispersion, i.e. interquartile range {\displaystyle {(Q_{3}-Q_{1})/2}} {\displaystyle {(Q_{3}-Q_{1})/2}} divided by the average of the quartiles (the midhinge), {\displaystyle {(Q_{1}+Q_{3})/2}} {\displaystyle {(Q_{1}+Q_{3})/2}}.
> ...
> Examples of misuse[edit]
> To see why the coefficient of variation should not be applied to interval level data, compare the same set of temperatures in Celsius and Fahrenheit:
>
> Celsius: [0, 10, 20, 30, 40]
> 
> Fahrenheit: [32, 50, 68, 86, 104]
>
> The sample standard deviations are 15.81 and 28.46 respectively. The CV of the first set is 15.81/20 = 0.79. For the second set (which are the same temperatures) it is 28.46/68 = 0.42.
>
> If, for example, the data sets are temperature readings from two different sensors (a Celsius sensor and a Fahrenheit sensor) and you want to know which sensor is better by picking the one with the least variance then you will be misled if you use CV. The problem here is that neither sensor is better in this case, because the data sets are direct conversions of each other, but the CV of each data set is different: 0.79 versus 0.42.

<https://en.wikipedia.org/wiki/Coefficient_of_variation>
<https://en.wikipedia.org/wiki/Statistical_dispersion>
<https://en.wikipedia.org/wiki/Quartile_coefficient_of_dispersion>


### Reading tables

Using Pandas.

    $ pip install pandas

Script is in `player_accuracy.py`

```python
    >>> from player_accuracy import *

```

In games of 1988-1989 season, Kareem Abdul-Jabbar.

    >>> abdul = read_csv('abdulka01_gamelog_1989.csv')

<http://www.basketball-reference.com/players/a/abdulka01/gamelog/1989>

In the first three games, 

    >>> abdul3 = abdul[0:3]

he attempted these field goals:

    >>> abdul3['FGA']
    0    10
    1     7
    2     8
    Name: FGA, dtype: int64

He made these field goals:

    >>> abdul3['FG']
    0    3
    1    5
    2    3
    Name: FG, dtype: int64

I applied candidate metrics of accuracy.

    >>> abdul_accuracy = extract_accuracy(abdul3, 'FGA', 'FG')
    >>> abdul_accuracy
       attempts  corrects  accuracy  errors  inaccuracy
    0        10         3  0.300000       7    3.333333
    1         7         5  0.714286       2    1.400000
    2         8         3  0.375000       5    2.666667

To normalize, I extended percentiles from all accuracies.

    >>> abdul_pct = abdul_accuracy.rank(pct = True)
    >>> abdul_pct
       attempts  corrects  accuracy    errors  inaccuracy
    0  1.000000       0.5  0.333333  1.000000    1.000000
    1  0.333333       1.0  1.000000  0.333333    0.333333
    2  0.666667       0.5  0.666667  0.666667    0.666667

Standard deviations of the percentiles:

    >>> abdul_pct.std()
    attempts      0.333333
    corrects      0.288675
    accuracy      0.333333
    errors        0.333333
    inaccuracy    0.333333
    dtype: float64

Upper and lower quartiles:

    >>> abdul_pct.quantile([0.25, 0.75])
          attempts  corrects  accuracy    errors  inaccuracy
    0.25  0.500000      0.50  0.500000  0.500000    0.500000
    0.75  0.833333      0.75  0.833333  0.833333    0.833333

Quartile coefficient of dispersion as (Q3-Q1)/(Q3+Q1)

    >>> quantile_dispersion(abdul_pct)
    attempts      0.25
    corrects      0.20
    accuracy      0.25
    errors        0.25
    inaccuracy    0.25
    dtype: float64

Summarized dispersion:

    >>> disperse(abdul_accuracy)
                    mean  quartile       std
    attempts    0.666667      0.25  0.333333
    corrects    0.666667      0.20  0.288675
    accuracy    0.666667      0.25  0.333333
    errors      0.666667      0.25  0.333333
    inaccuracy  0.666667      0.25  0.333333

