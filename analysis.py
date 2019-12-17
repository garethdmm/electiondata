"""
Various useful functions for inspecting the 2019 Canadian Federal Election results.
"""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

import data_operations


PARTY_COLOURS = {
  'LPC': 'tab:red',
  'CPC': 'tab:blue',
  'GPC': 'tab:green',
  'NDP': 'tab:orange',
  'GDP': 'tab:green',
  'Bloc': 'tab:cyan',
  'BLOC': 'tab:cyan',
  'IND': 'tab:grey',
}


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

    winner = winner.apply(lambda x: 'Bloc' if x == 'BLOC' else x)

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

    return ridings_data[ridings_data[margin_key] < 0]\
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


def domination_visualization(data):
    dominated_ridings = data[data.winnershare > 60]

    byparty = dominated_ridings.winner.value_counts()
    byprov = dominated_ridings.province.value_counts()

    plt.cla()

    plt.subplot(211)
    bars = plt.bar(byparty.index, byparty.values)
    bars[1].set_color('r')
    plt.title('Dominated ridings by Party')

    plt.subplot(212)
    bars = plt.barh(byprov.index, byprov.values)
    plt.title('Dominated ridings by Province')
    plt.show()


def alternate_house_visualization(data):
    althouse = alternate_reality(data)

    house43 = data.winner.value_counts()
    althouse43 = althouse.winner.value_counts()

    plt.cla()

    plt.subplot(211)
    plt.pie(
        house43.values,
        labels=house43.index,
        colors=['r', 'b', 'c', 'orange', 'g', 'b'],
    )
    plt.title('43rd House of Commons')

    plt.subplot(212)
    plt.pie(
        althouse43.values,
        labels=althouse43.index,
        colors=['r', 'b', 'g', 'c'],
    )
    plt.title('43rd House of Commons with Unified Left')

    plt.show()


def althouse_viz_2(df43):
    althouse = alternate_reality(df43)

    house43 = df43.winner.value_counts()
    althouse43 = althouse.winner.value_counts()

    plt.ion()

    plt.subplot(221)
    house_pie_chart(house43)
    plt.subplot(222)
    house_pie_chart(althouse43)
    plt.subplot(223)
    house_bar_chart(house43)
    plt.subplot(224)
    house_bar_chart(althouse43)

    plt.subplot(221)
    plt.title('43rd House of Commons')

    plt.subplot(222)
    plt.title('43rd House with Unified Left')


def house_pie_chart(results):
    colours = [PARTY_COLOURS[party] for party in results.index]

    plt.pie(results.values, labels=results.index, colors=colours)

    plt.show()


def house_bar_chart(results):
    colours = [PARTY_COLOURS[party] for party in results.index]
    plt.bar(results.index, results.values, color=colours)

    plt.ylim(0, 180)

    for i, v in enumerate(results.values):
        plt.text(i - 0.18, v + 10, str(v), color=colours[i])

    plt.show()

df42 = data_operations.load_2015_ridings_data()
df43 = data_operations.load_2019_ridings_data()

