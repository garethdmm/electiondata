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


def get_swings_heatmap_data(joined):
    changes = joined[joined.winner42 != joined.winner43]

    parties = ['Bloc', 'CPC', 'GPC', 'LPC', 'NDP']

    df = pd.DataFrame()

    for p1 in parties:
        z = {x: 0 for x in parties}

        for p2 in parties:
            if p1 == p2:
                z[p2] == 0
            else:
                wins = changes[changes.winner42 == p1][changes.winner43 == p2]
                print(wins)
                z[p2] = wins.shape[0]

        df[p1] = pd.Series(z)

    return df


def plot_swings_heatmap(joined):
    df = get_swings_heatmap_data(joined)

    plt.ion()

    ax = sns.heatmap(df, cbar=False, cmap='Blues', annot=True)

    ax.invert_yaxis()
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.xaxis.tick_top()
    ax.figure.subplots_adjust(bottom = 0.5)

    plt.suptitle('Seat handovers by winning party (top) and losing party (left)')

    return ax


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


def plot_alternate_reality_weak(df43, new_fig=True):
    """
    This version shows the 43rd house, changes, and 43rd alternate house in the weak
    unified-left conjecture (left win where GPC + NDP > previous winner)..
    """
    alt = alternate_reality(df43)

    house = df43.winner.value_counts()
    althouse = alt.winner.value_counts()

    gdp_old = house['NDP'] + house['GPC']

    new_parties = ['Bloc', 'CPC', 'GDP', 'LPC', 'IND']

    house = house.reindex(new_parties, fill_value=0)
    house['GDP'] = gdp_old

    althouse = althouse.reindex(new_parties, fill_value=0)

    changes = althouse - house

    colours = [PARTY_COLOURS[party] for party in changes.index]

    if new_fig is True:
        plt.figure(figsize=(15,4.5))

    plt.ion()

    plt.subplot(131)
    plt.pie(
        house.values,
        labels=['%s %s' % (party, house[party]) for party in house.index],
        colors=[PARTY_COLOURS[party] for party in house.index],
        textprops={'fontsize': 'large'},
    )

    plt.subplot(132)
    plt.barh(
        changes.index,
        changes.values,
        color=colours,
    )
    plt.axvline(x=0, color='tab:grey')
    plt.xlim(-20,20)
    plt.xticks((-20, -10, 0, 10, 20))

    plt.subplot(133)
    plt.pie(
        althouse.values,
        labels=['%s %s' % (party, althouse[party]) for party in althouse.index],
        colors=[PARTY_COLOURS[party] for party in althouse.index],
        textprops={'fontsize': 'large'},
    )

    plt.suptitle('43rd House of Commons, Seat Changes with a Unified Left, and resulting alternate House of Commons', fontsize='x-large')


def plot_alternate_reality_strong(df43, new_fig=True):
    """
    This version shows the 43rd house, changes, and 43rd alternate house in the strong
    unified-left conjecture (all ridings within a 10% margin of left victory become
    wins).
    """
    alt = alternate_reality(df43)

    alt.winner = alt.apply(
        lambda x: 'GDP' if x.gdp_margin > -10 and x.gdp_margin < 0 else x.winner,
        axis=1,
    )

    house = df43.winner.value_counts()
    althouse = alt.winner.value_counts()

    gdp_old = house['NDP'] + house['GPC']

    new_parties = ['Bloc', 'CPC', 'GDP', 'LPC', 'IND']

    house = house.reindex(new_parties, fill_value=0)
    house['GDP'] = gdp_old

    althouse = althouse.reindex(new_parties, fill_value=0)

    changes = althouse - house

    colours = [PARTY_COLOURS[party] for party in changes.index]

    if new_fig is True:
        plt.figure(figsize=(15,4.5))

    plt.ion()

    plt.subplot(131)
    plt.pie(
        house.values,
        labels=['%s %s' % (party, house[party]) for party in house.index],
        colors=[PARTY_COLOURS[party] for party in house.index],
        textprops={'fontsize': 'large'},
    )

    plt.subplot(132)
    plt.barh(
        changes.index,
        changes.values,
        color=colours,
    )
    plt.axvline(x=0, color='tab:grey')
    plt.xlim(-40,40)
    plt.xticks((-40, -20, 0, 20, 40))

    plt.subplot(133)
    plt.pie(
        althouse.values,
        labels=['%s %s' % (party, althouse[party]) for party in althouse.index],
        colors=[PARTY_COLOURS[party] for party in althouse.index],
        textprops={'fontsize': 'large'},
    )

    plt.suptitle('43rd House of Commons, Seat Changes with a Unified Left and 5% Swing, and resulting alternate House')

    plt.show()


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
joined_data = data_operations.get_2019_2015_joined_data(df42, df43)

