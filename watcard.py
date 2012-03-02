#!/usr/bin/env python
"""Basic library for fetching and processing Watcard data.
http://account.watcard.uwaterloo.ca
"""

import urllib
import datetime

import BeautifulSoup
import tablib


## Watcard balances
## "Known" balances renamed to be clearer
balances = {
    '1': 'mealplan',        # originally 'VILLAGE MEAL'
    '2': 'BEST BUY MEAL',
    '3': 'FOOD PLAN',
    '4': 'flex',            # originally 'FLEXIBLE'
    '5': 'FLEXIBLE',
    '6': 'FLEXIBLE',
    '7': 'TRANSFER MP',
    '8': 'DONS VILLAGE',
    '9': 'DONS NON VILLAGE',
    'A': 'EXTRA',
    'B': 'DEPT CHARGE',
    'C': 'OVERDRAFT',
}


#################
# Error Classes #
#################

class WatcardError(Exception):
    def __init__(self, issue):
        self.issue = issue

    def __str__(self):
        return repr(self.issue)


class AuthError(WatcardError):
    """Userid and PIN are invalid."""
    pass


##############
# Main class #
##############

class Watcard(object):
    """An object representing a single person's Watcard account.

    The object stores authentication information, transactions and account
    balances. The provided methods are the intended interface for working
    with Watcards.

    Attributes:
        userid: An integer Waterloo ID number.
        pin: An integer PIN for the Watcard.
        mealplan: A float balance of the meal plan account.
        flex: A Float balance of flex dollars.
    """

    def __init__(self, userid, pin):
        self.userid = userid  # Waterloo student number
        self.pin = pin        # Watcard PIN
        self.update()

    def __repr__(self):
        return '<Watcard %r>' % self.userid

    def update(self):
        """Updates transaction and balance information."""
        self.balances = get_balances(self.userid, self.pin)
        self.trans = get_transactions(self.userid, self.pin)
        self.mealplan = self.balances[0][1]
        self.flex = self.balances[3][1]

    def transactions(self, account=None, start=None, end=None):
        """Create a dataset containing transactions meeting certain criteria.

        Args:
            account: String representing a Watcard sub-account.
            start: Datetime object representing earliest date to include
                in transaction table.
            end: Datetime object representing latest time to include.

        Returns:
            A tablib Dataset with the headers:
            "Datetime", "Amount", "Account", "Terminal"
        """
        if not account and not start and not end:
            return self.trans
        if start is None:
            start = datetime.datetime(1, 1, 1)
        if end is None:
            end = datetime.datetime.now()
        if not account:
            trans = filter(lambda x: start < x[0] <= end, self.trans)
        else:
            trans = filter(lambda x: start < x[0] <= end and x[2] == account,
                self.trans)
        headers = ["Datetime", "Amount", "Account", "Terminal"]
        return tablib.Dataset(*trans, headers=headers)

    def balance_history(self, account, start=None, end=None, coalesce=1):
        """Create a dataset containing the balance history of an account.

        Args:
            account: String representing a Watcard sub-account.
            start: Datetime object representing earliest date to include.
            end: Datetime object representing latest date to include.
            coalesce: Integer representing the number of days to coalesce.

        Returns:
            A tablib Dataset with the headers:
            "Date", "Balance"
        """
        trans = self.transactions(account, start, end)
        if account == "mealplan":
            balance = self.mealplan
        elif account == "flex":
            balance = self.flex
        headers = ('Date', 'Balance')
        history = []
        if end is None:
            end = datetime.date.today()
        date = end
        coalesce_sum = 0
        for transaction in trans:
            while transaction[0].date() < date:
                history.append((date, balance - coalesce_sum))
                date = date - datetime.timedelta(coalesce)
            if transaction[0].date() == date:
                coalesce_sum += transaction[1]
        return tablib.Dataset(*history, headers=headers)

    def mean(self, days, account=None):
        """Calculate the mean daily expenditure for the given number of days.

        Args:
            days: Integer representing the number of days to include in mean.
            account: Optional string representing sub-account to calculate
                mean for.

        Returns:
            A float representing the mean daily expenditure for the given
            period of days.
        """
        start = datetime.datetime.now() - datetime.timedelta(days)
        amounts = self.transactions(account=account, start=start)['Amount']
        amounts = filter(lambda x: x < 0, amounts)  # ignore deposits
        return float(sum(amounts)) / days

    def punchcard(self, account=None):
        """Produce a list of transactions per day of the week and time.

        Args:
            account: Optional string representing a Waterloo sub-account.
        """
        trans = self.transactions(account)
        headers = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday")
        data = []
        for hour in range(0, 24):
            data.append([])
            for day in range(0, 7):
                data[hour].append(0)
        for transaction in trans:
            data[transaction[0].hour][transaction[0].weekday()] += 1
        return tablib.Dataset(*data, headers=headers)


###########################
# Supplementary Functions #
###########################


def punchcard_url(table):
    """Produces a url to a punchcard image. Inspired by Github.

    Args:
        table: A tablib Dataset. 7x24 cells, representing each hour of each
            day of the week. Produced by Watcard.punchcard()

    Returns:
        A string representing the url of a visual punchcard.
    """
    base = "" + \
        "https://chart.googleapis.com/chart?chs=800x300&chds=-1,24,-1,7,0," + \
        "%s&chf=bg,s,efefef&chd=t:0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16" + \
        ",17,18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" + \
        ",18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18" + \
        ",19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19" + \
        ",20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20" + \
        ",21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21" + \
        ",22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22" + \
        ",23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23" + \
        "|0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1," + \
        "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2" + \
        ",2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4," + \
        "4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,5,5,5,5,5,5,5,5,5,5" + \
        ",5,5,5,5,5,5,5,5,5,5,5,5,5,5,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6," + \
        "6,6,6,6,6,6,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7|%s,0," + \
        "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0&chxt=x,y&chm=o,3333" + \
        "33,1,1.0,25.0&chxl=0:||12am|1|2|3|4|5|6|7|8|9|10|11|12pm|1|2|3|4|" + \
        "5|6|7|8|9|10|11||1:||Mon|Tue|Wed|Thr|Fri|Sat|Sun|&cht=s"
    s = []
    for header in table.headers:
        for hour in table[header]:
            s.append(hour)
    seq = ",".join(map(str, s))
    return base % (max(s), seq)


def homebank_csv(userid, pin, account):
    """Writes a transaction csv compatible with homebank.

    Args:
        userid (str): Your waterloo userid.
        pin (str): Your watcard PIN.
        account (str): Watcard sub-account to write out balances for.

    Returns a string ready to be written to file.
    """
    ret = "date; paymode; info; payee; description; amount; category\n"
    table = get_transactions(userid, pin)
    for row in table:
        if balance == row[2]:
            date = datetime.datetime.strftime(row[0], "%d-%m-%y")
            ret += "%s;6;;;%s;%s;%s\n" % (date, row[3], row[1], row[2])


def get_transactions(userid, pin):
    """Gets a all watcard transactions.

    Returns a tablib Dataset with the headers:
    "Datetime", "Amount", "Account", "Terminal"
    """
    headers = ["Datetime", "Amount", "Account", "Terminal"]
    table_id = "oneweb_financial_history_table"
    raw = get_raw_html(userid, pin, "transactions")
    return parse_table(raw, table_id, process_transactions, headers)


def get_balances(userid, pin):
    """Gets balances for all watcard accounts.

    Returns a tablib Dataset with the headers:
    "Account", "Amount"
    """
    headers = ["Account", "Amount"]
    table_id = "oneweb_balance_information_table"
    raw = get_raw_html(userid, pin, "balances")
    return parse_table(raw, table_id, process_balances, headers)


def get_raw_html(userid, pin, dataset):
    """Get the raw html for the the speceficied dataset page."""
    if dataset == "transactions":
        data = urllib.urlencode({
            'acnt_1': userid,
            'acnt_2': pin,
            'DBDATE': '01/01/0001',
            'DEDATE': '01/01/2111',
            'PASS': 'PASS',
            'STATUS': 'HIST',
        })
    elif dataset == "balances":
        data = urllib.urlencode({
            'acnt_1': userid,
            'acnt_2': pin,
            'FINDATAREP': "ON",
            'STATUS': 'STATUS',
        })
    url = 'https://account.watcard.uwaterloo.ca/watgopher661.asp'
    resp = urllib.urlopen(url, data)
    resp = resp.read()
    if "The Account or PIN code is incorrect!" in resp:
        raise AuthError("The Account or PIN code is incorrect!")
    return resp


def parse_table(rawhtml, tableid, row_process_func, headers):
    """Parses a table out of raw html.

    Args:
        rawhtml: A string containing the raw html from the Watcard site.
        tableid: A string containing the id of the table to parse.
        row_process_func: A function used to process html row into a python
            list.
        headers: A list of headers for the output Dataset.

    Returns:
        A tablib Dataset. Headers depend on input.
    """
    table = tablib.Dataset(headers=headers)
    htmltable = BeautifulSoup.BeautifulSoup(rawhtml)('table', {'id': tableid})
    for row in htmltable[0].findAll('tr')[2:]:
        row = [col.renderContents() for col in row.findAll('td')]
        rowlist = row_process_func(row)
        if rowlist:
            table.append(rowlist)
    return table


def process_transactions(row):
    """Processes a transaction row."""
    datefmt = "%m/%d/%Y %H:%M:%S"
    date = datetime.datetime.strptime(row[0] + " " + row[1], datefmt)
    return [date, float(row[2]), balances[row[3]], row[6]]


def process_balances(row):
    """Process an balances row."""
    if row[0].rstrip() not in balances:
        return None
    return [row[2].rstrip(), float(row[5])]
