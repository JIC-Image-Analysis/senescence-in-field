"""Parse and explore canopy level data"""

import datetime

import pandas as pd

import click


def parse_scores_file_with_cleaning(ground_scores_file):
    senescence_scores_xls = pd.ExcelFile(ground_scores_file)
    senescence_scores = senescence_scores_xls.parse()

    base_datetime = datetime.datetime(2017, 6, 28)

    def clean_item(item):
        if type(item) == datetime.datetime:
            return item
        else:
            return base_datetime

    cleaned = map(clean_item, senescence_scores['Leaf Senescence Date'])

    def find_days_since_base(item):
        return (item - base_datetime).days

    days_since_base = map(find_days_since_base, cleaned)

    for d in days_since_base:
        print(d)


def parse_scores_file_2(ground_scores_file):
    senescence_scores_xls = pd.ExcelFile(ground_scores_file)
    senescence_scores = senescence_scores_xls.parse()

    # property_of_interest = 'Leaf Senescence Date'
    property_of_interest = 'Peduncle Senescence Date'
    property_of_interest = 'Heading Date'

    valid_only = [item
                  for item in senescence_scores[property_of_interest]
                  if type(item) == datetime.datetime]

    base_datetime = min(valid_only)

    def find_days_since_base(item):
        return (item - base_datetime).days

    days_since_base = map(find_days_since_base, valid_only)

    # for d in days_since_base:
    #     print(d)

    print("{}, {}".format("date", "count"))
    for d in range(30):
        date = base_datetime + datetime.timedelta(d)
        print("{}, {}".format(date, days_since_base.count(d)))

    # print("Date Time")
    # for d in days_since_base:
    #     print(base_datetime + datetime.timedelta(d))


def median(list_of_values):

    mid_point = int(len(list_of_values) / 2)

    return sorted(list_of_values)[mid_point]


def generate_senescence_scores(ground_scores_file):
    senescence_scores_xls = pd.ExcelFile(ground_scores_file)
    senescence_scores = senescence_scores_xls.parse()

    # property_of_interest = 'Leaf Senescence Date'
    # # property_of_interest = 'Peduncle Senescence Date'

    # properties = ['Leaf Senescence Date', 'Peduncle Senescence Date']

    both_scores = zip(
        senescence_scores['Leaf Senescence Date'],
        senescence_scores['Peduncle Senescence Date']
    )

    valid_only = []
    for ls, ps in both_scores:
        if type(ls) == datetime.datetime and type(ps) == datetime.datetime:
            valid_only.append((ls, ps))

    all_ls, all_ps = zip(*valid_only)

    median_ls = median(all_ls)
    median_ps = median(all_ps)

    print("LS,PS")
    for ls, ps in valid_only:
        ls_delta = (ls - median_ls).days
        ps_delta = (ps - median_ps).days
        print("{},{}".format(ls_delta, ps_delta))

    # valid_only = [item
    #               for item in senescence_scores[property_of_interest]
    #               if type(item) == datetime.datetime]

    # base_datetime = min(valid_only)

    # print(median(valid_only))


@click.command()
@click.argument('canopy_fpath')
def main(canopy_fpath):

    # parse_scores_file_2(canopy_fpath)
    generate_senescence_scores(canopy_fpath)


if __name__ == '__main__':
    main()
