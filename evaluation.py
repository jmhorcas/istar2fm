#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to measure the performance of the iStar algorithms.

"""

import istarGenerator
import istar2fm
import evolveAgent
import timeit
import statistics
import csv
import os

N_TIMES = 2
STATS_FILENAME_ALG1 = 'statistics-ALG1.csv'
STATS_FILENAME_ALG2 = 'statistics-ALG2.csv'
STATS_FILENAME_ALG3 = 'statistics-ALG3.csv'


ISTAR_FILENAME = 'istarModel-GENERATED.xmi'
AGENT_MODEL_FILENAME = 'agentModel-GENERATED.xmi'
ISTAR_FILENAME_EVOLVED = 'istarModel-GENERATED-EVOLVED.xmi'
AGENT_MODEL_FILENAME_EVOLVED = 'agentModel-GENERATED-EVOLVED.xmi'
HEADERS = ['iStar size', 'Runs', 'Mean Time (s)', 'Std', 'Median  Time (s)']
#RANGE = [10**x for x in range(0,7)] # [1, 10, 100, 1000, 10000,...]
RANGE = [1, 10, 100, 1000, 5000, 10000, 50000, 100000, 1000000]

def execution_time(stmt, ntimes):
    """Measure the execution time (in seconds) of a function stmt executing it ntimes"""
    return timeit.repeat(stmt=stmt, repeat=ntimes, number=1, globals=globals())

def generate_istar_model(size, filename):
    istarGenerator.generate_istarModel_of_size(size, filename)

def generate_agent_model(size, istarFilename, agentFilename):
    models = istarGenerator.generate_agentModel_of_size(size, istarFilename, agentFilename)

def generate_evolved_istar_model(size, istarFilename, agentFilename):
    agentmodel = generate_agent_model(size, istarFilename, agentFilename)
    agentmodel = istarGenerator.random_evolution(agentFilename) # Modifica intentional elements en el istar model (quita y pone ie) para luego pasarle el algoritmo 3.
    return agentmodel

def get_row(size, runs, time):
    return [size, runs, statistics.mean(time), statistics.stdev(time), statistics.median(time)]

def write_statistics(stats, filename):
    with open(filename, 'a+') as file:
        writer = csv.writer(file)
        writer.writerow(stats)

def mapping_evaluation():
    os.remove(STATS_FILENAME_ALG1)
    write_statistics(HEADERS)
    for i in RANGE:
        print("Generating i* model of size: " + str(i))
        generate_istar_model(i, ISTAR_FILENAME)
        print("Mapping i* model of size: " + str(i))
        time = execution_time("istar2fm.istar2fm(ISTAR_FILENAME)", N_TIMES)
        row = get_row(i, N_TIMES, time)
        write_statistics(row, STATS_FILENAME_ALG1)

def agent_evaluation():
    os.remove(STATS_FILENAME_ALG1)
    write_statistics(HEADERS)
    for i in RANGE:
        print("Generating i* model of size: " + str(i))
        generate_agent_model(i, ISTAR_FILENAME, AGENT_MODEL_FILENAME)
        print("Mapping i* agent model of size: " + str(i))
        time = execution_time("istar2fm.agent2configFM(AGENT_MODEL_FILENAME)", N_TIMES)
        row = get_row(i, N_TIMES, time)
        write_statistics(row, STATS_FILENAME_ALG2)


def evolve_agent_evaluation():
    os.remove(STATS_FILENAME_ALG1)
    write_statistics(HEADERS)
    for i in RANGE:
        print("Generating i* model of size: " + str(i))
        generate_evolved_istar_model(i, ISTAR_FILENAME_EVOLVED, AGENT_MODEL_FILENAME_EVOLVED)
        print("Evolving agent model of size: " + str(i))
        time = execution_time("istar2fm.agent2configFM(AGENT_MODEL_FILENAME_EVOLVED)", N_TIMES)
        row = get_row(i, N_TIMES, time)
        write_statistics(row, STATS_FILENAME_ALG3)


if __name__ == "__main__":
    mapping_evaluation()
    agent_evaluation()
    evolve_agent_evaluation()
