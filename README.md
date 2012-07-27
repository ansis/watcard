Watcard
=======

A Python module for working with transaction and balance data from University of Waterloo's Watcard. *To access your Watcard's transaction data you must have your student ID and your Watcard PIN. To create/reset your PIN visit [http://www.watcard.uwaterloo.ca/account.html](http://www.watcard.uwaterloo.ca/account.html)*

## Installation

To install watcard:

    $ pip install watcard

## Dependencies

- BeautifulSoup
- Tablib

## Basic Usage ##

Create a new Watcard:

    >>> import watcard
    >>> w = watcard.Watcard(userid, pin)

Access mealplan and flex balances:

    >>> w.mealplan
    523.14
    >>> w.flex
    65.23

Access transaction records. Optionally filter by account and date. Since tablib 
Datasets are returned, exporting to JSON, YAML, CSV, HTML, and Excel is easy.

    >>> t = w.transactions()
    >>> print t.csv
    Datetime,Amount,Account,Terminal
    2012-02-11 20:27:55,-3.19,mealplan,(00033)WAT-FS-V1-C-RIGHT
    2012-02-11 12:07:52,-2.05,mealplan,(00043)WAT-FS-REV-LEFT  
    2012-02-11 12:06:15,-1.0,flex,(00608)REV LAUNDRY (DRYE
    2012-02-11 12:06:02,-1.0,flex,(00608)REV LAUNDRY (DRYE
    ...

Access and filter balance history, which contains the balance at each date.
Default interval between dates is a day.

    >>> bh = w.balance_history("mealplan")
    >>> print bh.csv
    Date,Balance
    2012-02-24,381.48
    2012-02-23,394.29
    ...
    >>> w.balance_history("mealplan", start=datetime(...))
    >>> w.balance_history("mealplan, coalesce="day")

Calculate the mean daily expenditure for the given period of days.

    >>> w.mean(14)
    12.15
    >>> w.mean(14, account="mealplan")
    10.35
    >>> w.mean(14, account="flex")
    1.80

Get information on the number of transactions per day of the week and hour.

    >>> p = w.punchcard(account="mealplan")
    >>> print p.csv
    Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday
    1,0,1,0,1,2,2
    0,0,2,0,0,1,2
    ... (one row per hour)

Visualize punchard data:

    >>> watcard.punchcard_url(w.punchcard())
    'https://chart.googleapis.com/...'

![Punchcard visualization example](https://github.com/ansis/watcard/raw/master/punchcard_example.png)

## Documentation
While no separate documentation exists, docstrings within the code are thorough. If you have any questions, ask.
