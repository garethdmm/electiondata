"""
Various useful functions for inspecting the 2019 Canadian Federal Election results.
"""

import matplotlib
import pandas as pd
import matplotlib.pyplot as plt


PROVINCE_ID_PREFIXES = {
    10: 'Newfoundland',
    11: 'PEI',
    12: 'Nova Scotia',
    13: 'New Brunswick',
    24: 'Quebec',
    35: 'Ontario',
    46: 'Manitoba',
    47: 'Saskatchewan',
    48: 'Alberta',
    59: 'BC',
    60: 'Yukon',
    61: 'NWT',
    62: 'Nunavut',
}


def create_ridings_data(raw_data):
    """
    Convert the elections candidate data (which is given by candidate) into a format
    that is indexed by riding.
    """

    columns = [
        'distnum',
        'distname',
        'bloc_share',
        'cpc_share',
        'gpc_share',
        'lpc_share',
        'ndp_share',
        'ind_share',
        'bloc_margin',
        'cpc_margin',
        'gpc_margin',
        'lpc_margin',
        'ndp_margin',
        'ind_margin',
        'winner',
        'winnershare',
        'province',
    ]

    ridings_df = pd.DataFrame(columns=columns)

    riding_ids = raw_data.distnum.unique().tolist()
  
    for rid in riding_ids:
        local_results = raw_data[raw_data.distnum == rid]
        distnum = rid
        distname = local_results.iloc[0].distname

        province = province_for_district_number(distnum)

        windex = local_results.voteshare.idxmax()
        winner = local_results.loc[windex].party
        winnershare = local_results.loc[windex].voteshare

        bloc_share = get_party_result_for_riding(distnum, 'Bloc', raw_data, local_results)
        cpc_share = get_party_result_for_riding(distnum, 'CPC', raw_data, local_results)
        gpc_share = get_party_result_for_riding(distnum, 'GPC', raw_data, local_results)
        lpc_share = get_party_result_for_riding(distnum, 'LPC', raw_data, local_results)
        ndp_share = get_party_result_for_riding(distnum, 'NDP', raw_data, local_results)
        ind_share = get_party_result_for_riding(distnum, 'IND', raw_data, local_results)

        local_row_data = {
            'distnum': rid,
            'distname': distname,
            'bloc_share': bloc_share,
            'cpc_share': cpc_share,
            'gpc_share': gpc_share,
            'lpc_share': lpc_share,
            'ndp_share': ndp_share,
            'ind_share': ind_share,
            'bloc_margin': bloc_share - winnershare,
            'cpc_margin': cpc_share - winnershare,
            'gpc_margin': gpc_share - winnershare,
            'lpc_margin': lpc_share - winnershare,
            'ndp_margin': ndp_share - winnershare,
            'ind_margin': ind_share - winnershare,
            'winner': winner,
            'winnershare': winnershare,
            'province': province,
        }

        ridings_df = ridings_df.append(local_row_data, ignore_index=True)

    return ridings_df


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


def get_party_result_for_riding(distnum, party, data, riding_results=None):
    if riding_results is None:
        riding_results = data[data.distnum == distnum]

    if party not in riding_results.party.values:
        return 0.0

    party_result = riding_results[riding_results.party == party]

    return party_result['voteshare'].tolist()[0]

 
def results_for_district(distnum, data):
    return data[data['distnum'] == distnum]


def plot_district(distnum, data):
    results = results_for_district(distnum, data)
    results.plot.bar(x='party', y='voteshare')
    plt.show()


def province_for_district_number(district_number):
    prefix = int(district_number / 1000)
  
    return PROVINCE_ID_PREFIXES[prefix]


# Main.
raw_data = pd.read_csv('data/latest.csv')
ridings_data = create_ridings_data(raw_data)

