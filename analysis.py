"""
Various useful functions for inspecting the 2019 Canadian Federal Election results.
"""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

import data_operations


def alternate_reality(ridings_data):
    """
    Create a new dataset from  our usual ridings data in which all NDP and GPC votes
    go to a new party called the GDP.
    """
    gdp_share = ridings_data['ndp_share'] + ridings_data['gpc_share']
    
    alt_ridings = ridings_data.drop([
        'gpc_share',
        'ndp_share',
        'bloc_margin',  # Some winnershares are change so we also recalculate margins.
        'cpc_margin',
        'gpc_margin',
        'lpc_margin',
        'ndp_margin',
        'ind_margin',
        'winner',
        'winnershare',
    ], axis=1)
    
    alt_ridings['gdp_share'] = gdp_share

    new_share_columns = [
        'bloc_share',
        'cpc_share',
        'gdp_share',
        'lpc_share',
        'ind_share',
    ]

    winner = alt_ridings[new_share_columns]\
        .idxmax(axis=1)\
        .apply(lambda x: x.replace('_share', '').upper())

    winnershare = alt_ridings[new_share_columns].max(axis=1)

    alt_ridings['winner'] = winner
    alt_ridings['winnershare'] = winnershare

    alt_ridings['bloc_margin'] = alt_ridings['bloc_share'] - winnershare
    alt_ridings['cpc_margin'] = alt_ridings['cpc_share'] - winnershare
    alt_ridings['gdp_margin'] = alt_ridings['gdp_share'] - winnershare
    alt_ridings['lpc_margin'] = alt_ridings['lpc_share'] - winnershare
    alt_ridings['ind_margin'] = alt_ridings['ind_share'] - winnershare

    return alt_ridings


def near_misses_for_party(party, ridings_data):
    """
    Show the ridings for a given party where they lost by less than 10%, sorted by
    the loss margin.
    """
    margin_key = '%s_margin' % party.lower()

    return ridings_data[['distname', margin_key, 'winner']]\
        [ridings_data[margin_key] < 0]\
        [ridings_data[margin_key] > -10.0]\
        .sort_values(by=margin_key)

 
def results_for_district(distnum, data):
    return data[data['distnum'] == distnum]


def plot_district(distnum, data):
    results = results_for_district(distnum, data)
    results.plot.bar(x='party', y='voteshare')
    plt.show()


def do_join(df43, df42):
    return df43.set_index('distnum').join(
        df42.set_index('distnum'),
        how='left',
        lsuffix='43',
        rsuffix='42',
    )

def get_list_of_swings(joined_data):
    parties = ['bloc', 'cpc', 'gpc', 'lpc', 'ndp']
    columns = ['distname', 'party', 'province', 'swing']

    swings = pd.DataFrame(columns=columns)

    swings.distname - joined_data.distname43

    for party in parties:
        party_swings = pd.DataFrame(columns=columns)

        party_swings.distname = joined_data.distname43.copy()
        party_swings.province = joined_data.province43.copy()

        party_key_43 = '%s_share43' % party.lower()
        party_key_42 = '%s_share42' % party.lower()
        party_swings.swing = joined_data[party_key_43] - joined_data[party_key_42]

        party_swings.party = party

        swings = pd.concat([swings, party_swings])

    return swings


def get_swing_data(party, joined_data):
    parties = ['bloc', 'cpc', 'gpc', 'lpc', 'ndp']
    columns = ['distname'] + parties
    swing_data = pd.DataFrame(columns=columns)

    swing_data['distname'] = joined_data['distname43']

    for party in parties:
        party_key_43 = '%s_share43' % party.lower()
        party_key_42 = '%s_share42' % party.lower()

        swing_data[party] = joined_data[party_key_43] - joined_data[party_key_42]

    return swing_data


df42 = data_operations.load_2015_ridings_data()
df43 = data_operations.load_2019_ridings_data()

