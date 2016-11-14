# How can basketball field goals and baseball hits be compared?

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

### Reading tables

Using Pandas.

    $ pip install pandas

Script is in `player_accuracy.py`

```python
    >>> from player_accuracy import *

```

In games of 1988-1989 season, Kareem Abdul-Jabbar.

    >>> abdul = read_csv('abdulka01_gamelog_1989.csv')
    >>> abdul['group'] = 'abdul'

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

    >>> abdul3_accuracy = extract_accuracy(abdul3, 'FGA', 'FG')
    >>> abdul3_accuracy
       attempts  corrects  accuracy  errors  inaccuracy
    0        10         3  0.300000       7    3.333333
    1         7         5  0.714286       2    1.400000
    2         8         3  0.375000       5    2.666667

To normalize, I extended percentiles from all accuracies.

    >>> abdul3_pct = abdul3_accuracy.rank(pct = True)
    >>> abdul3_pct
       attempts  corrects  accuracy    errors  inaccuracy
    0  1.000000       0.5  0.333333  1.000000    1.000000
    1  0.333333       1.0  1.000000  0.333333    0.333333
    2  0.666667       0.5  0.666667  0.666667    0.666667

Standard deviations of the percentiles:

    >>> abdul3_pct.std()
    attempts      0.333333
    corrects      0.288675
    accuracy      0.333333
    errors        0.333333
    inaccuracy    0.333333
    dtype: float64

Upper and lower quartiles:

    >>> abdul3_pct.quantile([0.25, 0.75])
          attempts  corrects  accuracy    errors  inaccuracy
    0.25  0.500000      0.50  0.500000  0.500000    0.500000
    0.75  0.833333      0.75  0.833333  0.833333    0.833333

Quartile coefficient of dispersion as (Q3-Q1)/(Q3+Q1)

    >>> quantile_dispersion(abdul3_pct)
    attempts      0.25
    corrects      0.20
    accuracy      0.25
    errors        0.25
    inaccuracy    0.25
    dtype: float64

Summarized dispersion:

    >>> disperse(abdul3_accuracy)
                    mean  quartile       std
    attempts    0.666667      0.25  0.333333
    corrects    0.666667      0.20  0.288675
    accuracy    0.666667      0.25  0.333333
    errors      0.666667      0.25  0.333333
    inaccuracy  0.666667      0.25  0.333333

    >>> abdul_accuracy = extract_accuracy(abdul, 'FGA', 'FG')
    >>> disperse(abdul_accuracy)
                    mean  quartile       std
    attempts    0.506757  0.400000  0.288544
    corrects    0.506757  0.397849  0.287097
    accuracy    0.506757  0.502609  0.290275
    errors      0.506757  0.483444  0.287823
    inaccuracy  0.506757  0.462400  0.290275

The standard deviation is a reasonable measure of dispersion of accuracy.


## Comparing two basketball players

I loaded two players' files.  Example: Steph Curry from 2016.

    >>> curry = read_csv('curryst01_gamelog_2016.csv')
    >>> curry['group'] = 'curry'
    >>> curry3 = curry[0:3]

<http://www.basketball-reference.com/players/c/curryst01/gamelog/2016/>

Coerced type to numeric.
<http://stackoverflow.com/questions/15891038/pandas-change-data-type-of-columns>

    >>> couple3 = pandas.concat([abdul3, curry3])
    >>> couple3_accuracy = extract_accuracy(couple3, 'FGA', 'FG', 'group')
    >>> couples = couple3_accuracy.groupby('group')
    >>> couples.std()
           attempts  corrects  accuracy    errors  inaccuracy
    group                                                    
    abdul  1.527525  1.154701  0.220746  2.516611    0.982061
    curry  6.658328  4.041452  0.046505  3.055050    0.138290

From multiple CSVs:

    >>> basketball = concat_csvs(['abdulka01_gamelog_1989.csv',
    ...     'curryst01_gamelog_2016.csv'], 'group')
    >>> basketball.to_csv('test_basketball.tsv', index=False, sep='\t')

From single TSV:

    >>> basketball = read_table('test_basketball.tsv')
    >>> basketball_accuracy = extract_accuracy(basketball, 'FGA', 'FG', 'group')
    >>> basketball_couples = basketball_accuracy.groupby('group')
    >>> basketball_couples.std()
                                attempts  corrects  accuracy    errors  inaccuracy
    group                                                                         
    abdulka01_gamelog_1989.csv  3.311122  1.962297  0.175021  2.433263    1.033569
    curryst01_gamelog_2016.csv  4.787669  3.471776  0.111805  3.094424    0.565446

Baseball:

    >>> baseball = concat_csvs([
    ...     'arroybr01_gamelog_batting_2014.csv',
    ...     'fernajo02_gamelog_batting_2016.csv'],
    ...     'group')
    >>> baseball_accuracy = extract_accuracy(baseball, 'AB', 'H', 'group')
    >>> baseball_couples = baseball_accuracy.groupby('group')
    >>> baseball_couples.std()
                                        attempts  corrects  accuracy    errors  \
    group                                                                        
    arroybr01_gamelog_batting_2014.csv  6.354788  1.527525  0.247978  4.951431   
    fernajo02_gamelog_batting_2016.csv  9.337013  2.425237  0.392872  7.051360   
    <BLANKLINE>
                                        inaccuracy  
    group                                           
    arroybr01_gamelog_batting_2014.csv         NaN  
    fernajo02_gamelog_batting_2016.csv         NaN  

    >>> baseball_couples.std().median()
    attempts      7.845900
    corrects      1.976381
    accuracy      0.320425
    errors        6.001395
    inaccuracy         NaN
    dtype: float64

I summarized by median of standard deviations.  For example, here are two basketball players and two baseball players for their games in a season each.

    >>> std_median([basketball_couples, baseball_couples],    ['basketball_couple', 'baseball_couple'])
                       attempts  corrects  accuracy    errors  inaccuracy
    basketball_couple  4.049396  2.717037  0.143413  2.763844    0.799508
    baseball_couple    7.845900  1.976381  0.320425  6.001395         NaN


I entered multiple files into configuration in `player_accuracy_config.py`:

    >>> baseball.to_csv('test_baseball.tsv', index=False, sep='\t')
    >>> configs['test_ball']
    [['test_baseball.tsv', 'AB', 'H', 'group'], ['test_basketball.tsv', 'FGA', 'FG', 'group']]
    >>> print(compare_tsv('test_ball', configs)) #doctest: +NORMALIZE_WHITESPACE
    group	attempts	corrects	accuracy	errors	inaccuracy
    test_baseball.tsv	7.846	1.976	0.32	6.001	
    test_basketball.tsv	4.049	2.717	0.143	2.764	0.8
    <BLANKLINE>

From the command line I called the key to read this.  I could save the output to a file.

    $ python player_accuracy.py test > test_std.tsv

Another example with 3 players' seasons:

    >>> baseball = concat_csvs([
    ...     'arroybr01_gamelog_batting_2014.csv',
    ...     'fernajo02_gamelog_batting_2016.csv',
    ...     'donaljo02_gamelog_batting_2016.csv'],
    ...     'group')
    >>> baseball.to_csv('test_baseball3.tsv', index=False, sep='\t')
    >>> basketball = concat_csvs([
    ...     'abdulka01_gamelog_1989.csv',
    ...     'curryst01_gamelog_2016.csv',
    ...     'jamesle01_gamelog_2016.csv'], 'group')
    >>> basketball.to_csv('test_basketball3.tsv', index=False, sep='\t')
    >>> print(compare_tsv('test_ball3', configs)) #doctest: +NORMALIZE_WHITESPACE
    group	attempts	corrects	accuracy	errors	inaccuracy
    test_baseball3.tsv	9.337	2.425	0.248	7.051	
    test_basketball3.tsv	4.463	2.561	0.124	3.094	0.565

In batting averages per game, the increased deviation is easily explained by the lesser number of times at bat than a basketball player's field goal attempts.



# Comparing to random

What are the differences between these data sets?

* Random attempts by players with fixed accuracy rates: 0.25, 0.5, 0.75.
* Random attempts by players with random accuracy rates.
* Ten game sessions by ten players.
* A hundred game sessions by a hundred players.
* A thousand game sessions by a thousand players.

I simulated simple trials.  For consistent testing, these do not overwrite files if they already exist.

    >>> accuracy_ranges = [[0.25, 0.25], [0.5, 0.5], [0.75, 0.75], [0.0, 1.0]]
    >>> players_sessions = [10, 100]
    >>> from pprint import pprint
    >>> pprint(random_csvs(accuracy_ranges, players_sessions))
    ['test_random_0.25_0.25_10_10.tsv',
     'test_random_0.25_0.25_100_100.tsv',
     'test_random_0.5_0.5_10_10.tsv',
     'test_random_0.5_0.5_100_100.tsv',
     'test_random_0.75_0.75_10_10.tsv',
     'test_random_0.75_0.75_100_100.tsv',
     'test_random_0.0_1.0_10_10.tsv',
     'test_random_0.0_1.0_100_100.tsv']

I expected more dispersion in the set with a random range.  And more dispersion in smaller sample.

    >>> print(compare_tsv('test_random', configs)) #doctest: +NORMALIZE_WHITESPACE
    group	attempts	corrects	accuracy	errors	inaccuracy
    test_random_0.25_0.25_10_10.tsv	0.0	1.329	0.133	1.329	2.892
    test_random_0.25_0.25_100_100.tsv	0.0	4.305	0.043	4.305	0.754
    test_random_0.5_0.5_10_10.tsv	0.0	2.023	0.202	2.023	1.087
    test_random_0.5_0.5_100_100.tsv	0.0	5.005	0.05	5.005	0.208
    test_random_0.75_0.75_10_10.tsv	0.0	1.13	0.113	1.13	0.225
    test_random_0.75_0.75_100_100.tsv	0.0	4.344	0.043	4.344	0.079
    test_random_0.0_1.0_10_10.tsv	0.0	3.287	0.329	3.287	3.189
    test_random_0.0_1.0_100_100.tsv	0.0	29.166	0.292	29.166	11.774
    <BLANKLINE>

Median standard deviation of accuracy (corrects / attempts) the most comparable among these metrics.

The standard deviation diminishes drastically when comparing 10 to 100 sessions with a fixed accuracy rate.  Such as 0.20 to 0.05.  Whereas the random accuracy rate diminishes much less.  Such as 0.33 to 0.29.


### Not dispersion of percentiles

I measured dispersion of percentiles of accuracy. The results were probably equal for the random sets.  

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

