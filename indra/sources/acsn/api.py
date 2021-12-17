__all__ = ['process_from_web', 'process_df']

import os
import csv
import pandas
import requests
from .processor import AcsnProcessor

ACSN_URL = 'https://acsn.curie.fr/ACSN2/downloads/'
ACSN_RELATIONS_URL = ACSN_URL + \
                     'ACSN2_binary_relations_between_proteins_with_PMID.txt'
ACSN_CORRESPONDENCE_URL = ACSN_URL + 'ACSN2_HUGO_Correspondence.gmt'


def process_from_web():
    relations_df = pandas.read_csv(ACSN_RELATIONS_URL, sep='\t')
    correspondence_dict = _transform_gmt(
        requests.get(ACSN_CORRESPONDENCE_URL).text.split('\n'))
    return process_df(relations_df, correspondence_dict)


def process_files(relations_path: str, correspondence_path: str):
    relations_df = pandas.read_csv(relations_path)
    with open(correspondence_path, 'r') as fh:
        correspondence_dict = _transform_gmt(fh)
    return process_df(relations_df, correspondence_df)


def process_df(relations_df, correspondence_dict):
    ap = AcsnProcessor(relations_df, correspondence_dict)
    ap.extract_statements()
    return ap


def _transform_gmt(gmt):
    # Convert the GMT file into a dictionary
    acsn_hgnc_dict = {}
    for line in gmt:
        parts = line.strip().split('\t')
        acsn_hgnc_dict[parts[0]] = parts[2:]
    return acsn_hgnc_dict


