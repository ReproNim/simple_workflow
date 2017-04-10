#/usr/bin/env python

import json
import os
from glob import glob
import pandas as pd
import numpy as np

if __name__ == "__main__":
    from argparse import ArgumentParser, RawTextHelpFormatter
    defstr = ' (default %(default)s)'
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("--ignoremissing", dest="nanignore", action="store_true",
                        default=False,
                        help="Ignore missing subjects when comparing")
    args = parser.parse_args()

    expected_files = sorted(glob('expected_output/*/segstats.json'))

    if len(expected_files) < 24:
        raise ValueError('Expected 24 files, but only %d files exist' % len(expected_files))

    output_files = sorted(glob('output/*/segstats.json'))
    if len(output_files) == 0:
        raise ValueError('Output has no files')

    if len(output_files) != len(expected_files):
        print('Mismatch in number of expected (%d) and actual (%d) output files' % (len(expected_files),
                                                                                    len(output_files)))

    outputmap = {0: 'voxels', 1: 'volume'}

    df = pd.DataFrame()
    for filename in expected_files:
        with open(filename, 'rt') as fp:
            in_dict = json.load(fp)
            subject = filename.split(os.path.sep)[1]
            in_dict_mod = {}
            for k, v in in_dict.items():
                if isinstance(v, list):
                    for idx, value in enumerate(v):
                        in_dict_mod["%s_%s" % (k, outputmap[idx])] = value
                else:
                    in_dict_mod[k] = v
            df[subject] = pd.Series(in_dict_mod)
    df = df.T

    df_out = pd.DataFrame()
    for filename in output_files:
        with open(filename, 'rt') as fp:
            in_dict = json.load(fp)
            subject = filename.split(os.path.sep)[1]
            in_dict_mod = {}
            for k, v in in_dict.items():
                if isinstance(v, list):
                    for idx, value in enumerate(v):
                        in_dict_mod["%s_%s" % (k, outputmap[idx])] = value
                else:
                    in_dict_mod[k] = v
            df_out[subject] = pd.Series(in_dict_mod)
    df_out = df_out.T

    df.to_csv('output/ExpectedOutput.csv')
    df_out.to_csv('output/ActualOutput.csv')

    df_diff = df - df_out

    if args.nanignore:
        df_diff = df_diff.dropna()
    df_diff.to_csv('output/Difference.csv')

    if np.allclose(df_diff, 0):
        print('Outputs MATCH')
    else:
        print('Outputs are not close enough. Printing difference')
        print(df_diff)

    import rdflib as rl
    query = """
    PREFIX nipype: <http://nipy.org/nipype/terms/>  
    PREFIX prov: <http://www.w3.org/ns/prov#>
    
    SELECT DISTINCT ?platform ?fslversion
    { ?a a prov:Activity;
         nipype:platform ?platform;
         nipype:version ?fslversion .
         FILTER (?fslversion != 'Unknown')
    }  
    """
    prov_files = sorted(glob('expected_output/workflow_prov*.trig'))

    g = rl.ConjunctiveGraph()
    g.parse(prov_files[0], format='trig')
    res = g.query(query)
    print("Original platform: {}".format(str(res.bindings[0]['platform'])))
    print("Original FSL version: {}".format(str(res.bindings[0]['fslversion'])))

    prov_files = sorted(glob('output/workflow_prov*.trig'))

    g = rl.ConjunctiveGraph()
    g.parse(prov_files[-1], format='trig')
    res = g.query(query)
    for val in res.bindings:
        print("Current platform: {}".format(str(val['platform'])))
        print("Current FSL version: {}".format(str(val['fslversion'])))
