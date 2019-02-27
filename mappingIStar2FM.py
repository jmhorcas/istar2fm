#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to map i* (istar) models to feature models.
"""

import argparse
import parsers.pistarParser as pistarParser
import istarModel
import featureModel

def clean_str(s):
    s = s.replace('-', ' ')
    s = s.replace('.', ' ')
    s = s.title()
    s = s.replace(' ', '')
    return s

def add_exclusive_constraints(fm, names):
    for n in names:
        constraint = n + ' implies not ('
        for n2 in names:
            if n != n2:
                constraint += n2 + ' or '
        constraint = constraint[:-4] + ')'
        fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)

def add_intentional_element(istar, fm, ie, ie_type, parent_feature, variability_type, lower=0, upper=-1):
    processed = []
    id = clean_str(ie.id)
    feature = fm.get_feature(id)
    if feature is not None:     # si la feature ya existía la elimino y la vuelvo a crear para actualizar su información adecuadamente (padre y tipo de variabilidad)
        feature.delete()

    feature = fm.add_feature(id, clean_str(ie.name), parent_feature, variability_type, lower, upper)
    processed.append(ie)
    if isinstance(ie, istar.istar_metamodel.get_class('Goal')) or isinstance(ie, istar.istar_metamodel.get_class('Task')):
        if ie.refines is not None:
            if isinstance(ie.refines, istar.istar_metamodel.get_class('ORRefinement')):
                or_group = []
                hasConstraints = False
                for child in ie.refines.to:
                    if isinstance(child, istar.istar_metamodel.get_class(ie_type)):
                        or_group.append(child)
                    else:
                        hasConstraints = True

                if not hasConstraints:
                    for or_ie in or_group:
                        processed += add_intentional_element(istar, fm, or_ie, ie_type, feature, 'alternative', 1, 1)
                else:
                    for or_ie in or_group:
                        processed += add_intentional_element(istar, fm, or_ie, ie_type, feature, 'optional')

                    constraint = clean_str(ie.name) + ' implies ('
                    for child in ie.refines.to:
                        constraint += clean_str(child.name) + ' or '
                    constraint = constraint[:-4] + ')'
                    fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)
                    add_exclusive_constraints(fm, [clean_str(e.name) for e in ie.refines.to])
            elif isinstance(ie.refines, istar.istar_metamodel.get_class('ANDRefinement')):
                and_group = []
                ie_constraints = []
                for child in ie.refines.to:
                    if isinstance(child, istar.istar_metamodel.get_class(ie_type)):
                        and_group.append(child)
                    else:
                        ie_constraints.append(child)

                for and_ie in and_group:
                    processed += add_intentional_element(istar, fm, and_ie, ie_type, feature, 'mandatory')
                if len(ie_constraints) > 0:
                    constraint = clean_str(ie.name) + ' implies ('
                    for child in ie_constraints:
                        constraint += clean_str(child.name) + ' and '
                    constraint = constraint[:-4] + ')'
                    fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)
    return processed

def add_intentional_elements(istar, fm, elements, elements_type, root_feature, variability_type):
    processed = []
    for e in elements:
        if e not in processed:
            processed += add_intentional_element(istar, fm, e, elements_type, root_feature, variability_type)
    return processed

def add_cognitive_model(istarModel, fm, actor, name, root_feature):
    goalsF = fm.add_feature(name+'Goals', name+'Goals', root_feature, 'mandatory')
    plansF = fm.add_feature(name+'Plans', name+'Plans', root_feature, 'optional')
    contextF = fm.add_feature(name+'Context', name+'Context', root_feature, 'optional')
    qualityattributesF = fm.add_feature(name+'QAs', name+'QAs', root_feature, 'optional')

    goals = add_intentional_elements(istarModel, fm, istarModel.get_goals(actor), 'Goal', goalsF, 'mandatory')
    tasks = add_intentional_elements(istarModel, fm, istarModel.get_tasks(actor), 'Task', plansF, 'optional')
    resources = add_intentional_elements(istarModel, fm, istarModel.get_resources(actor), 'Resource', contextF, 'optional')
    qualities = add_intentional_elements(istarModel, fm, istarModel.get_qualities(actor), 'Quality', qualityattributesF, 'optional')

    for r in resources:
        for t in r.neededBy:
            constraint = clean_str(t.name) + " implies " + clean_str(r.name)
            fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)

    for ie in goals+tasks+resources+qualities:
        for c in ie.contribution:
            if str(c.type) in ['Make', 'Help']:
                qa = c.contributesTo
                constraint = clean_str(qa.name) + " implies " + clean_str(ie.name)
                fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)

    # Qualification is optional for the user, in other case it would create dead features
    # for qa in qualities:
    #     for ie in qa.qualifies:
    #         constraint = clean_str(ie.name) + " implies " + clean(qa.name)
    #         fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)
    #     for r in qa.qualifiesResource:
    #         constraint = clean_str(r.name) + " implies " + clean(qa.name)
    #         fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)

    print("-----------------")
    print("Name: " + actor.name)
    print("Type: " + str(type(actor)))
    print("#Goals: " + str(len(goals)))
    print("#Tasks: " + str(len(tasks)))
    print("#Resources: " + str(len(resources)))
    print("#QAs: " + str(len(qualities)))
    print("-----------------")

def add_roles(istarModel, fm, root_feature):
    for r in istarModel.get_roles():
        name = clean_str(r.name)
        id = clean_str(r.id)
        f = fm.add_clonable_feature(id, name, parent=root_feature, variability_type='or')
        add_cognitive_model(istarModel, fm, r, name, f)

def add_actors_only(istarModel, fm, root_feature):
    actors = set(istarModel.get_actors())
    roles = set(istarModel.get_roles())
    agents = set(istarModel.get_agents())
    actors -= roles
    actors -= agents

    for a in actors:
        name = clean_str(a.name)
        id = clean_str(a.id)
        f = fm.add_feature(id, name, parent=root_feature, variability_type='or')
        add_cognitive_model(istarModel, fm, a, name, f)

def add_agents(istarModel, fm, root_feature):
    for a in istarModel.get_agents():
        name = clean_str(a.name)
        id = clean_str(a.id)
        f = fm.add_feature(id, name, parent=root_feature, variability_type='or')
        add_cognitive_model(istarModel, fm, a, name, f)

def generate_feature_model(istarModel):
    fm = featureModel.FeatureModel()
    root = fm.add_feature(id='MyFeatureRoot', name='MyFeatureRoot', variability_type='mandatory')
    add_roles(istarModel, fm, root)
    add_actors_only(istarModel, fm, root)
    #add_agents(istarModel, fm, root)   # Esto es para las configuraciones

    return fm

def mapping(filename):
    print(filename)
    p = pistarParser.PiStarParser(filename)
    p.parse()
    xmi_file = p.generate_xmi_model()

    m = istarModel.IStarModel()
    m.load_model(xmi_file)

    fm = generate_feature_model(m)
    fm.save_model(filename[:-4] + "-FM.xmi")


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
