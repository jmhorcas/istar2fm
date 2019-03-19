#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to generate arbitrary i* models..

Usage:
    python istarGenerator.py <actors, roles, agents, goals, tasks, resources, qualities>

Input:
    <actors, roles, agents, goals, tasks, resources, qualities> is a list of integers with the number of elements.

Output:
    <istar-model-GENERATED.xmi> is the i* model generated conformed to the i* 2.0 metamodel.

References:
    i* 2.0 metamodel: https://arxiv.org/abs/1605.07767
"""

import argparse
import json
import istarModel
import random

PERCENTAGE_OF_ELEMENTS = [0.025, 0.05, 0.075, 0.325, 0.4, 0.1, 0.025] # actors, roles, agents, goals, tasks, resources, qualities (taken from the Travel Reinbursement example)
PERCENTAGE_OF_ELEMENTS_ACTOR_ROLE_MODEL = [0.025, 0.125, 0, 0.325, 0.4, 0.1, 0.025]
PERCENTAGE_OF_ELEMENTS_AGENT_MODEL = [0, 0, 0.15, 0.325, 0.4, 0.1, 0.025]

def get_id(string):
    return "_" + string

def add_actors(model, actor_type, n):
    actors = []
    for i in range(1, n+1):
        id = get_id(actor_type + str(i))
        name = actor_type + str(i)
        actors.append(model.add_actor(id, name, actor_type))
    return actors

# def add_intentional_elements(model, actor, ie_type, n):
#     ies = []
#     for i in range(1, n+1):
#         id = get_id(ie_type, i)
#         name = get_name(ie_type, i)
#         ies.append(model.add_intentional_element(id, name, actor, ie_type))
#     return ies

# def ie_for_refinement(model, ies):
#     all_is = set(ies)
#     my_is = set()
#     ie = None
#     while ie == None or my_ies!=all_ies or not isinstance(ie, model.metamodel.get_class('Goal')) and not isinstance(ie, model.metamodel.get_class('Task')):
#         ie = next(random.sample(ies, 1))
#         my_ies.add(ie)
#     if not isinstance(ie, model.metamodel.get_class('Goal')) and not isinstance(ie, model.metamodel.get_class('Task'):
#         return None
#     else:
#         return ie

# def add_refinements(model, actor, ies, refinement_type, n, factor):
#     ies_with_refinements = []
#     for i in range(1, n+1):
#         id = get_id(refinement_type, i)
#         name = get_name(refinement_type, i)
#         ie_target = ie_for_refinement(model, ies)
#         if ie_source not in ies_with_refinements and is_target not in ies_with_refinements:
#             for i in range(1, random.randint(1, factor)+1):
#
#                 ref = ie_for_refinement(model, ies)
#
#         model.add_refinement()
#         ies.append(model.add_intentional_element(id, name, actor, ie_type))
#     return ies


def generate_istarModel_of_size(size, filename):
    integers = [int(round(size*x)) for x in PERCENTAGE_OF_ELEMENTS]
    agents = int(integers[2] / 2)
    integers[0] += agents
    integers[1] += agents
    integers[2] = 0
    return generate_istarModel(integers, filename)

def generate_agentModel_of_size(size, istarFilename, agentFilename):
    istarModel = generate_istarModel_of_size(size, istarFilename)
    integers = [int(round(size*x)) for x in PERCENTAGE_OF_ELEMENTS]
    actors = integers[0] + integers[1]
    integers[2] += actors
    integers[0] = 0
    integers[1] = 0
    print("Agents: " + str(integers[2]))
    return generate_agentModel(istarModel, integers, agentFilename)


def add_intentional_element(model, actor, ie_type, i):
    id = get_id(ie_type + actor.id + str(i))
    name = ie_type + actor.name + str(i)
    model.add_intentional_element(id, name, actor, ie_type)

def generate_istarModel(integers, filename="istarModel-GENERATED.xmi"):
    n_actors, n_roles, n_agents, n_goals, n_tasks, n_resources, n_qualities = integers

    model = istarModel.IStarModel()
    actors = []
    actors += add_actors(model, 'Actor', n_actors)
    actors += add_actors(model, 'Role', n_roles)
    actors += add_actors(model, 'Agent', n_agents)

    ies = []
    if len(actors) > 0:
        for i in range(0,n_goals):
            a = random.sample(actors, 1)[0]
            add_intentional_element(model, a, 'Goal', i)

        for i in range(0,n_tasks):
            a = random.sample(actors, 1)[0]
            add_intentional_element(model, a, 'Task', i)

        for i in range(0,n_resources):
            a = random.sample(actors, 1)[0]
            add_intentional_element(model, a, 'Resource', i)

        for i in range(0,n_qualities):
            a = random.sample(actors, 1)[0]
            add_intentional_element(model, a, 'Quality', i)

    # for a in actors:
    #     ies += add_intentional_elements(model, a, 'Goal', n_goals)
    #     ies += add_intentional_elements(model, a, 'Task', n_tasks)
    #     ies += add_intentional_elements(model, a, 'Resource', n_resources)
    #     ies += add_intentional_elements(model, a, 'Quality', n_qualities)

        #add_refinements(model, actor, ies, 'ANDRefinement', and_refinements, refinements_factor)
        #add_refinements(model, actor, ies, 'ORRefinement', or_refinements, refinements_factor)

    model.save_model(filename)
    return model


def generate_agentModel(istarModel, integers, filename="agentModel-GENERATED.xmi"):
    n_actors, n_roles, n_agents, n_goals, n_tasks, n_resources, n_qualities = integers

    agents = add_actors(istarModel, 'Agent', n_agents)
    if len(agents) > 0:
        roles = istarModel.get_roles()
        if len(roles) > 0:
            for a in agents:
                r = random.sample(roles, 1)[0]
                istarModel.add_participatesIn(a, r)

            for i in range(0,n_goals):
                inserted = False
                while not inserted:
                    r = random.sample(roles, 1)[0]
                    rIEs = istarModel.get_goals(r)
                    if len(rIEs) <= 0:
                        inserted = True
                    else:
                        ie = random.sample(rIEs, 1)[0]
                        a = random.sample(agents, 1)[0]
                        ies = istarModel.get_goals(a)
                        if not any(x for x in ies if x.name == ie.name):
                            istarModel.add_intentional_element(a.id + "_" + ie.id, ie.name, a, 'Goal')
                            inserted = True

            for i in range(0,n_tasks):
                inserted = False
                while not inserted:
                    r = random.sample(roles, 1)[0]
                    rIEs = istarModel.get_tasks(r)
                    if len(rIEs) <= 0:
                        inserted = True
                    else:
                        ie = random.sample(rIEs, 1)[0]
                        a = random.sample(agents, 1)[0]
                        ies = istarModel.get_tasks(a)
                        if not any(x for x in ies if x.name == ie.name):
                            istarModel.add_intentional_element(a.id + "_" + ie.id, ie.name, a, 'Task')
                            inserted = True

            for i in range(0,n_resources):
                inserted = False
                while not inserted:
                    r = random.sample(roles, 1)[0]
                    rIEs = istarModel.get_resources(r)
                    if len(rIEs) <= 0:
                        inserted = True
                    else:
                        ie = random.sample(rIEs, 1)[0]
                        a = random.sample(agents, 1)[0]
                        ies = istarModel.get_resources(a)
                        if not any(x for x in ies if x.name == ie.name):
                            istarModel.add_intentional_element(a.id + "_" + ie.id, ie.name, a, 'Resource')
                            inserted = True

            for i in range(0,n_qualities):
                inserted = False
                while not inserted:
                    r = random.sample(roles, 1)[0]
                    rIEs = istarModel.get_qualities(r)
                    if len(rIEs) <= 0:
                        inserted = True
                    else:
                        ie = random.sample(rIEs, 1)[0]
                        a = random.sample(agents, 1)[0]
                        ies = istarModel.get_qualities(a)
                        if not any(x for x in ies if x.name == ie.name):
                            istarModel.add_intentional_element(a.id + "_" + ie.id, ie.name, a, 'Quality')
                            inserted = True

    istarModel.save_model(filename)
    return istarModel

def random_evolution(istarModel_filename):
    model = istarModel.IStarModel()
    model.load_model(istarModel_filename)
    roles = model.get_roles()
    for r in roles:
        ies = model.get_intentional_elements(r)
        n_modifications = int(len(ies) * 0.10)
        ies_to_remove = random.sample(ies, n_modifications)
        for ie in ies_to_remove:
            model.delete_intentional_element(r, ie)
        for i in range(0,n_modifications):
            model.add_intentional_element(r.id + "_" + str(i) + "_evolved", r.name + "_" + str(i) + "_evolved", r, 'Goal')

    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""It generate a i* model with the numbers of actors and intentional elements indicated."""
    )

    parser.add_argument('integers', metavar='N', type=int, nargs='+', help='numbers of actors (actors, roles, and agents) and intentional elements (goals, tasks, resources, qualities).')
    args = parser.parse_args()
    generate_istarModel(args.integers)
