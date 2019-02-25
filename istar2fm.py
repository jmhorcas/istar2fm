#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to map i* (istar) models to feature models.
"""

import argparse
import parsers.pistarParser as pistarParser
import istarModel

def execution_time(stmt, ntimes):
    """Measure the execution time of a function stmt executing it ntimes"""
    import timeit
    t = timeit.Timer(stmt=stmt, globals=globals())
    res = t.repeat(repeat=ntimes, number=1)
    return res

def execution_time_ms(stmt, ntimes):
    """Show statistics of execution time of a function stmt executing it ntimes"""
    import statistics
    res = execution_time(stmt, ntimes)
    print("Code: " + stmt)
    print("Mean: " + str(statistics.mean(res) * 1e+3))
    print("Standard deviation: " + str(statistics.stdev(res) * 1e+3))
    print("Median: " + str(statistics.median(res) * 1e+3))


def mapping(filename):
    p = pistarParser.PiStarParser(filename)
    p.parse()
    p.generate_xmi_model()
    m = istarModel.IStarModel()
    m.load_model(filename[:-4] + ".xmi")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Generate a feature model from a i* (istar) model."""
    )

    parser.add_argument('-f', '--file', required=True, help='i* (istar) model file',  dest='filename')
    args = parser.parse_args()
    filename = args.filename

    #execution_time_ms("mapping(filename)", 10)
    #execution_time("mapping(filename)", 1)
    mapping(filename)
