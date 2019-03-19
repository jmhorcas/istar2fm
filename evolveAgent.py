#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Algorithm to evolve an agent model (i*).

Usage:
    python evolveAgent.py --file <istar-model-evolved.xmi>

Input:
    <istar-model-evolved.xmi> is the i* model evolved.

Output:
    <agent-model-EVOLVED.xmi> is the original agent model (i*) evolved according the evolved i* model.

References:
    i* 2.0 metamodel: https://arxiv.org/abs/1605.07767

"""

import argparse
import istarModel

def evolve_agents(model):
    roles = model.get_roles()
    agents = model.get_agents()

    for a in agents:
        print(str(type(a)) + ": " + a.name)
        for ie in a.wants:
            print(str(type(ie)) + ": " + ie.name)
        print("-------------")


    for a in agents:
        if len(a.participatesIn) > 0:
            role = next((r for r in roles if r.name == a.participatesIn[0].name), None)
            print(a.name + " participatesIn " + role.name)
            role_ies = model.get_intentional_elements(role)
            agent_ies = model.get_intentional_elements(a)
            for ie in agent_ies:
                print(str(type(ie)) + ": " + ie.name)
                if not any(e for e in role_ies if e.name == ie.name):
                    print("delete ie: " + ie.name)
                    model.delete_intentional_element(a, ie)

            for ie in role_ies:
                if not any(e for e in agent_ies if e.name == ie.name):
                    if isinstance(ie, model.metamodel.get_class('Goal')):
                        print("add goal: " + ie.name)
                        model.add_intentional_element(a.id+"_"+ie.id, ie.name, a, 'Goal')
                    elif isinstance(ie, model.metamodel.get_class('Task')):
                        print("add task: " + ie.name)
                        model.add_intentional_element(a.id+"_"+ie.id, ie.name, a, 'Task')
                    elif isinstance(ie, model.metamodel.get_class('Resource')):
                        print("add resource: " + ie.name)
                        model.add_intentional_element(a.id+"_"+ie.id, ie.name, a, 'Resource')
                    elif isinstance(ie, model.metamodel.get_class('Quality')):
                        print("add quality: " + ie.name)
                        model.add_intentional_element(a.id+"_"+ie.id, ie.name, a, 'Quality')
    return model


def calculate_differences(istarModel):
    roles = evolvedModel.get_roles()
    agents = agentModel.get_agents()

    for a in agents:
        print(str(type(a)) + ": " + a.name)
        for ie in a.wants:
            print(str(type(ie)) + ": " + ie.name)
        print("-------------")


    for a in agents:
        if len(a.participatesIn) > 0:
            role = next((r for r in roles if r.name == a.participatesIn[0].name), None)
            print(a.name + " participatesIn " + role.name)
            role_ies = evolvedModel.get_intentional_elements(role)
            agent_ies = agentModel.get_intentional_elements(a)
            for ie in agent_ies:
                print(str(type(ie)) + ": " + ie.name)
                if not any(e for e in role_ies if e.name == ie.name):
                    agentModel.delete_intentional_element(a, ie)

    print("----------")

    print("====================================================")
    for r in roles:
        print(str(type(r)) + ": " + r.name)
        for ie in r.wants:
            print(str(type(ie)) + ": " + ie.name)
        print("-------------")

    for a in agentModel.get_agents():
        print(str(type(a)) + ": " + a.name)
        for ie in a.wants:
            print(str(type(ie)) + ": " + ie.name)
        print("-------------")

    return agentModel


def evolve_model(filename):
    model = istarModel.IStarModel()
    model.load_model(filename)

    model = evolve_agents(model)

    model.save_model(filename[:-4] + "-EVOLVED.xmi")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""It evolves an agent model from an evolved i* model."""
    )

    parser.add_argument('-f', '--file', required=True, help='Evolved i* (istar) model filename',  dest='filename')
    #parser.add_argument('-a', required=True, help='Agent model (i*) filename',  dest='agentModel_filename')
    args = parser.parse_args()
    filename = args.filename

    evolve_model(filename)
