'''
This module is intended to duplicate the 'main()' function found in other
languages such as C++ and Java.  In order to run an experiment, this module
should be passes to your interpreter.  In the interest of speed and consistency
we suggest that PyPy 1.8.0 with GCC 4.6.2 be used to run this code, although
Python 2.7 should be able to handle it correctly.

To see a full description of this modules command line arguments, run
````pypy main.py -h````.

Provided with this code should be the folders ``experiments``, ``problems``,
and ``variants``, which contain configuration information require to recreate
the experiments performed in the Linkage Tree Genetic Algorithms: Variants and
Analysis publication.  For example, the following command uses the general
experiment setup on the Deceptive Trap problem with 50 dimensions and a trap
size of 5.  The LTGA variant ``original+`` is used, and the verbose flag is set
to increase the output given.  Since no population size is specified, it will
automatically call bisection to find the minimum population size.

``pypy main.py experiments/general.cfg problems/DeceptiveTrap_50_5.cfg
variants/originalplus.cfg -v``

For any support questions email brianwgoldman@acm.org or dtauritz@acm.org.
'''
import argparse
import sys
import random
import Experiments
import Util
from HHCRSP import HHCRSP

description = 'Linkage Tree Genetic Algorithms: Variants and Analysis code'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('configs', metavar='Configuration Files',
                    type=str, nargs='+',
                    help='One or more json formatted files containing' +
                        ' configuration information')

parser.add_argument('-i', dest='id', type=int,
                    help='problem Id')

parser.add_argument('-c', dest='output_config', type=str,
                    help='Outputs a single configuration file containing' +
                    ' the entire configuration used in this run')

parser.add_argument('-v', dest='verbose', action='store_true',
                    help='Include this flag to increase periodic output')

parser.add_argument('-o', dest='output_results', type=str,
                    help='Specify a file to output the results of this run.')

if __name__ == '__main__':
    args = parser.parse_args()
    args.configs.append('experiments/general.cfg')
    args.configs.append('variants/hhcrsp.cfg')
    config = Util.loadConfigurations(args.configs)

    config['problemId'] = args.verbose
    config['verbose'] = args.verbose
    random.seed(config['seed'])

    config['hhcrsp'] = HHCRSP(config)
    try:
        rawResults = Experiments.fullRun(config)
        combinedResults = Experiments.combineResults(rawResults)

        print combinedResults
    except KeyError as e:
        print 'You must include a configuration value for', e.args[0]

    if args.output_results != None:
        Util.saveList(args.output_results, [combinedResults] + rawResults)
    if args.output_config != None:
        Util.saveConfiguration(args.output_config, config)
