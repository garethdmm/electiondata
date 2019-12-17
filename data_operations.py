# -*- coding: utf-8 -*-
"""
Various functions for cleaning up the data given to us by Elections Canada.
"""

import pandas as pd

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
        distname = local_results.iloc[0].distname # distname
        province = local_results.iloc[0].province # province

        windex = local_results.voteshare.idxmax() # voteshare
        winner = local_results.loc[windex].party # party
        winnershare = local_results.loc[windex].voteshare # voteshare

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


def get_party_result_for_riding(distnum, party, data, riding_results=None):
    if riding_results is None:
        riding_results = data[data.distnum == distnum]

    if party not in riding_results.party.values:
        return 0.0

    party_result = riding_results[riding_results.party == party]

    return max(party_result['voteshare'].tolist()) # voteshare


def province_for_district_number(district_number):
    prefix = int(district_number / 1000)
  
    return PROVINCE_ID_PREFIXES[prefix]


def prune_2015_data(raw_data):
    """
    The data that elections canada gives us for 2015 is unweidly. This conforms it to
    an easier schema.
    """
    formatted_data = raw_data.drop(columns=[
        'Majority/Majorité',
        'Candidate Occupation/Profession du candidat',
        'Majority Percentage/Pourcentage de majorité',
        'Candidate Residence/Résidence du candidat',
    ])

    formatted_data.rename(columns={
        u'Electoral District Name/Nom de circonscription': 'distname',
        'Electoral District Number/Numéro de circonscription': 'distnum',
        u'Province': 'province',
        u'Percentage of Votes Obtained /Pourcentage des votes obtenus': 'voteshare',
        u'Candidate/Candidat': 'candidate',
        u'Votes Obtained/Votes obtenus': 'numvotes',
    }, inplace=True)

    # Extract the party from the columns.
    formatted_data['party'] = formatted_data['candidate'].apply(
        lambda candidate: extract_party_from_candidate_field(candidate),
    )

    # 2015 data comes with the province but we take it from the district code for
    # congruency with 2019.
    formatted_data['province'] = formatted_data['distnum'].apply(
        lambda x: province_for_district_number(x),
    )

    # Re-order the columns.
    formatted_data = formatted_data[[
        'distnum',
        'distname',
        'candidate',
        'party',
        'numvotes',
        'voteshare',
        'province',
    ]]

    return formatted_data


def extract_party_from_candidate_field(candidate):
    party = ''

    if 'Bloc Québécois/Bloc Québécois' in candidate:
        party = 'Bloc'
    elif 'Conservative/Conservateur' in candidate:
        party = 'CPC'
    elif 'Green Party/Parti Vert' in candidate:
        party = 'GPC'
    elif 'Liberal/Libéral' in candidate:
        party = 'LPC'
    elif 'NDP-New Democratic Party' in candidate:
        party = 'NDP'
    else:
        party = 'IND'

    return party


def prune_2019_data(raw_data):
    """
    This conforms the raw data received from Elections Canada to a more readily-usable
    format.
    """

    formatted_data = raw_data.rename(columns={
        'Electoral district number - Numéro de la circonscription': 'distnum',
        'Type of results*': 'resulttype',
        'Electoral district name': 'distname',
        'Political affiliation': 'party',
        'Votes obtained - Votes obtenus': 'numvotes',
        '% Votes obtained - Votes obtenus %': 'voteshare',
        'Given name - Prénom': 'firstname',
        'Surname - Nom de famille': 'lastname',
    })

    formatted_data = formatted_data[formatted_data['resulttype'] == 'validated']

    formatted_data['candidate'] = '%s %s' % (
        formatted_data['firstname'],
        formatted_data['lastname'],
    )

    formatted_data = formatted_data.drop(columns=[
        'Total number of ballots cast - Nombre total de votes déposés',
        'Rejected ballots - Bulletins rejetés***',
        'Type de résultats**',
        'Nom de la circonscription',
        'Appartenance politique',
        'resulttype',
        'firstname',
        'lastname',
        'Middle name(s) - Autre(s) prénom(s)',
    ])

    formatted_data['party'] = formatted_data['party'].apply(
        lambda x: format_party_name(x),
    )

    formatted_data.distnum = formatted_data.distnum.astype('int')

    formatted_data['province'] = formatted_data['distnum'].apply(
        lambda x: province_for_district_number(x),
    )

    # Re-order the columns.
    formatted_data = formatted_data[[
        'distnum',
        'distname',
        'candidate',
        'party',
        'numvotes',
        'voteshare',
        'province',
    ]]

    return formatted_data


def format_party_name(party_name):
    party = ''

    if party_name == 'Bloc Québécois':
        party = 'Bloc'
    elif party_name == 'Conservative':
        party = 'CPC'
    elif party_name == 'Green Party':
        party = 'GPC'
    elif party_name == 'Liberal':
        party = 'LPC'
    elif party_name == 'NDP-New Democratic Party':
        party = 'NDP'
    else:
        party = 'IND'
    
    return party 


def load_2015_ridings_data(recalculate=False):
    if recalculate is True:
        candidate_data = prune_2015_data(pd.read_csv(
            'data/elections_canada_2015_data.csv',
            header=0,
        ))

        ridings_data = create_ridings_data(candidate_data)

        return ridings_data
    else:
        return pd.read_csv('data/parsed_ridings_data_2015.csv')


def load_2019_ridings_data(recalculate=False):
    if recalculate is True:
        candidate_data = prune_2019_data(pd.read_csv(
            'data/elections_canada_2019_data.csv',
            header=1,
        ))

        ridings_data = create_ridings_data(candidate_data)

        return ridings_data
    else:
        return pd.read_csv('data/parsed_ridings_data_2019.csv')


def get_2019_2015_joined_data(df43, df42):
    return df43.set_index('distnum').join(
        df42.set_index('distnum'),
        how='left',
        lsuffix='43',
        rsuffix='42',
    )


