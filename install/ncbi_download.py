#!/usr/bin/env python3

"""
Retrieves the proteins identified by IDS (as fasta files)
from https://www.ncbi.nlm.nih.gov/protein/
"""

import os
from settings import DATA_DIR, USER_EMAIL
from Bio import SeqIO
from Bio import Entrez


# Proteins to be downloaded.
# Values are NCBI Reference Sequence codes.
IDS = ['NC_000852', 'NC_007346', 'NC_008724', 'NC_009899',
       'NC_014637', 'NC_020104', 'NC_023423', 'NC_023640',
       'NC_023719', 'NC_027867']


def fetch(id, format='fasta'):
    """
    :param id: NCBI Reference Sequence id
    :param format: either 'fasta' or 'gb'
    """
    fname = os.path.join(DATA_DIR, f'{id}.{format}')
    if not os.path.isfile(fname):
        with Entrez.efetch(db="nuccore", id=id, rettype=format, retmode="text") as conn:
            with open(fname, 'w') as fp:
                fp.write(conn.read())
                print(f'Saved {fname}')

def main():
    Entrez.email = EMAIL
    for id in IDS:
        f = fetch(id)
        

if __name__ == '__main__':
    main()
