#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to map i* (istar) models to feature models (FMs).

Usage:
    python istar2fm.py --file <istar-model.xmi>

Input:
    <istar-model.xmi> is the i* model conformed to the i* 2.0 metamodel.

Output:
    <fm-model-FM.xmi> is the FM conformed to its metamodel.
    <fm-model-FMconfig.xmi> is a partial configuration of the FM.

References:
    i* 2.0 metamodel: https://arxiv.org/abs/1605.07767
    Feature Model: https://en.wikipedia.org/wiki/Feature_model
"""

import argparse
import istarModel
import featureModel
import configurationFM

def clean_str(s):
    """Remove special characters from a name o ID."""
    s = s.replace('-', ' ')
    s = s.replace('.', ' ')
    s = s.title()
    s = s.replace(' ', '')
    return s

def clean_id(s):
    """IDs begins with an underscore."""
    return '_' + clean_str(s)

def add_exclusive_constraints(fm, ids):
    """Create exclusive constraints in the feature model.

    Constraints are in First-order logic.
    Exclusive constraints are of these types:
    A -> B & C &..., and
    B -> A & C &..., and
    C -> A & B &..., and so on.

    The ID of the constraint starts with an underscore followed by its formula.

    Note:
        Could this create redundancy constraints?.

    Args:
        fm (FeatureModel): The feature model.
        ids (:obj:`list` of :obj:`str`): List of IDs of the entities involved in the constraints.
    """
    for x in ids:
        constraint = x + ' implies not ('
        for y in ids:
            if x != y:
                constraint += y + ' or '
        constraint = constraint[:-4] + ')'
        fm.add_constraint('_' + constraint, 'First-order logic', constraint)

def add_intentional_element(istar, fm, ie, ie_type, parent_feature, variability_type, lower=0, upper=-1):
    """Create new features in the feature model from an intentional element (goal, task, resource, or quality) and its children.

    The mapping for intentional elements is as follow:
        Each intentional element (goal, task, resource, or quality) is mapped to a unique feature.
        The ID of the feature is the ID of the intentional element preceded with an underscore.
        The name of the feature is the name of the intentional element without special chars like dots, dashes, whitespaces, etc. (see `clean_str` method).
        OR Refinements of intentional elements are mapped to `exclusive or` features where only a feature child can be selected.
        Concretely:
            OR Refinements of intentional elements of the same type are mapped to `alternative` features .
            OR Refinements of intentional elements of different types are mapped to `optional` features plus `exclusive constraints` (see `add_exclusive_constraints` method).
        AND Refinements of intentional elements are mapped to:
            `mandatory` features for those intentional elements of the same type being processed.
            `requires (implies)` constraints (A -> B & C) for those intentional elements with different type.

    Args:
        istar (IStarModel): The i* model.
        fm (FeatureModel): The feature model.
        ie (pyecore.ecore.IntentionalElement): The intentional element to be mapped.
        ie_type (str): Type of the intentional element. It can be: 'Goal', 'Task', 'Resource', or 'Quality'.
        parent_feature (pyecore.ecore.Feature): The parent feature of the new feature to be created.
        variability_type (str): Type of variability of the feature to be created. It can be: 'optional', 'mandatory', 'or', 'alternative'.
        lower (int, optional): Lower bound for group cardinality features (only for 'or', or 'alternative' features).
        upper (int, optional): Upper bound for group cardinality features (only for 'or', or 'alternative' features).

    Returns:
        The list of intentional elements that has been mapped.

    """
    processed = []
    id = clean_id(ie.id)
    feature = fm.get_feature(id)
    if feature is not None:     # si la feature ya existía la elimino y la vuelvo a crear para actualizar su información adecuadamente (padre y tipo de variabilidad)
        feature.delete()

    feature = fm.add_feature(id, clean_str(ie.name), parent_feature, variability_type, lower, upper)
    processed.append(ie)
    if isinstance(ie, istar.metamodel.get_class('Goal')) or isinstance(ie, istar.metamodel.get_class('Task')):
        if ie.refines is not None:
            if isinstance(ie.refines, istar.metamodel.get_class('ORRefinement')):
                or_group = []
                hasConstraints = False
                for child in ie.refines.to:
                    if isinstance(child, istar.metamodel.get_class(ie_type)):
                        or_group.append(child)
                    else:
                        hasConstraints = True

                if not hasConstraints:
                    for or_ie in or_group:
                        processed += add_intentional_element(istar, fm, or_ie, ie_type, feature, 'alternative', 1, 1)
                else:
                    for or_ie in or_group:
                        processed += add_intentional_element(istar, fm, or_ie, ie_type, feature, 'optional')

                    constraint = clean_id(ie.id) + ' implies ('
                    for child in ie.refines.to:
                        constraint += clean_id(child.id) + ' or '
                    constraint = constraint[:-4] + ')'
                    fm.add_constraint('_' + constraint, 'First-order logic', constraint)
                    add_exclusive_constraints(fm, [clean_id(e.id) for e in ie.refines.to])
            elif isinstance(ie.refines, istar.metamodel.get_class('ANDRefinement')):
                and_group = []
                ie_constraints = []
                for child in ie.refines.to:
                    if isinstance(child, istar.metamodel.get_class(ie_type)):
                        and_group.append(child)
                    else:
                        ie_constraints.append(child)

                for and_ie in and_group:
                    processed += add_intentional_element(istar, fm, and_ie, ie_type, feature, 'mandatory')
                if len(ie_constraints) > 0:
                    constraint = clean_id(ie.id) + ' implies ('
                    for child in ie_constraints:
                        constraint += clean_id(child.id) + ' and '
                    constraint = constraint[:-5] + ')'
                    fm.add_constraint('_' + constraint, 'First-order logic', constraint)
    return processed

def add_intentional_elements(istar, fm, elements, elements_type, root_feature, variability_type):
    """Map all the intentional elements that are not previously mapped (processed) for a specific type ('Goal', 'Task', 'Resource', or 'Quality').

    Note:
        Each type of intentional element has its own subtree in the feature model.

    Args:
        istar (IStarModel): The i* model.
        fm (FeatureModel): The feature model.
        elements (:obj:`list` of :obj:`IntentionalElement`): List of intentional elements of a type.
        elements_type (str): Type of the intentional elements. It can be: 'Goal', 'Task', 'Resource', or 'Quality'.
        root_feature (pyecore.ecore.Feature): The parent feature of subtree of the intentional elements.
        variability_type (str): Type of variability of the feature to be created. It can be: 'optional', 'mandatory', 'or', 'alternative'.

    Returns:
        The list of intentional elements that has been mapped.

    """
    processed = []
    for e in elements:
        if e not in processed:
            processed += add_intentional_element(istar, fm, e, elements_type, root_feature, variability_type)
    return processed

def add_cognitive_model(istarModel, fm, actor, name, root_feature):
    """Map the cognitive model (the intentional elements) for an actor and all the relationships.

    Relationships includes `neededBy` associations with resources, `contributions` of qualities, (and `qualifies` of qualities)?.
    All relationships are mapped to `requires (implies)` constraints.

    Note:
        Each type of intentional element has its own subtree in the feature model.

    Args:
        istarModel (IStarModel): The i* model.
        fm (FeatureModel): The feature model.
        actor (pyecore.ecore.Actor): The actor/role/agent.
        name (str): The actor's name.
        root_feature (pyecore.ecore.Feature): The parent feature of subtree of the intentional elements.

    """
    goalsF = fm.add_feature(name+'Goals', name+'Goals', root_feature, 'mandatory')
    plansF = fm.add_feature(name+'Plans', name+'Plans', root_feature, 'optional')
    contextF = fm.add_feature(name+'Context', name+'Context', root_feature, 'optional')
    qualityattributesF = fm.add_feature(name+'QAs', name+'QAs', root_feature, 'optional')

    goals = add_intentional_elements(istarModel, fm, istarModel.get_goals(actor), 'Goal', goalsF, 'optional')       # ponerlo mandatory creará deade features
    tasks = add_intentional_elements(istarModel, fm, istarModel.get_tasks(actor), 'Task', plansF, 'optional')
    resources = add_intentional_elements(istarModel, fm, istarModel.get_resources(actor), 'Resource', contextF, 'optional')
    qualities = add_intentional_elements(istarModel, fm, istarModel.get_qualities(actor), 'Quality', qualityattributesF, 'optional')

    for r in resources:
        for t in r.neededBy:
            constraint = clean_id(t.id) + " implies " + clean_id(r.id)
            fm.add_constraint('_' + constraint, 'First-order logic', constraint)

    for ie in goals+tasks+resources+qualities:
        for c in ie.contribution:
            qa = c.contributesTo
            if str(c.type) in ['Make', 'Help']:
                constraint = clean_id(ie.id) + " implies " + clean_id(qa.id)
            elif str(c.type) in ['Hurt', 'Break']:
                constraint = clean_id(ie.id) + " implies not " + clean_id(qa.id)
            fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)

    # Qualification is optional for the user, in other case it would create dead features
    # for qa in qualities:
    #     for ie in qa.qualifies:
    #         constraint = clean_str(ie.name) + " implies " + clean(qa.name)
    #         fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)
    #     for r in qa.qualifiesResource:
    #         constraint = clean_str(r.name) + " implies " + clean(qa.name)
    #         fm.add_constraint(clean_str(constraint), 'First-order logic', constraint)

    # print("-----------------")
    # print("Name: " + actor.name)
    # print("Type: " + str(type(actor)))
    # print("#Goals: " + str(len(goals)))
    # print("#Tasks: " + str(len(tasks)))
    # print("#Resources: " + str(len(resources)))
    # print("#QAs: " + str(len(qualities)))
    # print("-----------------")

def add_roles(istarModel, fm, root_feature):
    """It maps the roles of the i* model including all its intentional elements.

    Roles are mapped to `clonable` features.

    Args:
        istarModel (IStarModel): The i* model.
        fm (FeatureModel): The feature model.
        root_feature: Root of the feature model and parent of all roles.

    """
    for r in istarModel.get_roles():
        name = clean_str(r.name)
        id = clean_id(r.id)
        f = fm.add_clonable_feature(id, name, parent=root_feature, variability_type='or')
        add_cognitive_model(istarModel, fm, r, name, f)

def add_actors_only(istarModel, fm, root_feature):
    """It maps the actors of the i* model including all its intentional elements.

    Actors are mapped to normal features.

    Note:
        Actors are includes only if they are not instances of 'Role' or 'Agent' classes.
        This is because Actor is superclass of Role and Agent.

    Args:
        istarModel (IStarModel): The i* model.
        fm (FeatureModel): The feature model.
        root_feature: Root of the feature model and parent of all actors.

    """
    actors = set(istarModel.get_actors())   # actors includes roles and agents.
    roles = set(istarModel.get_roles())
    agents = set(istarModel.get_agents())
    actors -= roles
    actors -= agents

    for a in actors:
        name = clean_str(a.name)
        id = clean_id(a.id)
        f = fm.add_feature(id, name, parent=root_feature, variability_type='or')
        add_cognitive_model(istarModel, fm, a, name, f)

def add_agents(istarModel, fm, root_feature):
    """It maps the agents of the i* model including all its intentional elements.

    Agents are mapped to instance of the `clonable` features of roles.
    Agents are not in the feature model but in configuration models of the FM.

    Args:
        istarModel (IStarModel): The i* model.
        fm (FeatureModel): The feature model.
        root_feature: Root of the feature model and parent of all agents.

    """
    for a in istarModel.get_agents():
        name = clean_str(a.name)
        id = clean_id(a.id)
        f = fm.add_feature(id, name, parent=root_feature, variability_type='or')
        add_cognitive_model(istarModel, fm, a, name, f)

def generate_feature_model(istarModel):
    """It creates an empty feature model and adds all main i* concepts (roles and actors) including all its intentional elements.

    Args:
        istarModel (IStarModel): The i* model.

    """
    fm = featureModel.FeatureModel()
    root = fm.add_feature(id='MyFeatureRoot', name='MyFeatureRoot', variability_type='mandatory')
    add_roles(istarModel, fm, root)
    add_actors_only(istarModel, fm, root)
    #add_agents(istarModel, fm, root)   # Esto es para las configuraciones
    return fm

def generate_configuration_model(istarModel, fm):
    """It creates an empty configuration model and adds all main i* concepts (agents) including all its intentional elements.

    Args:
        istarModel (IStarModel): The i* model.

    """
    config = configurationFM.FMConfiguration(fm)
    instance_number = 1
    for a in istarModel.get_agents():
        if len(a.participatesIn) > 0:
            role = a.participatesIn[0]
            clonable_feature = fm.get_feature(clean_id(role.id))
            instance = config.add_clonable_selection(clean_str(a.name), instance_number, clonable_feature)
            # Add abstract nodes (Goals, Tasks, Resources, Qualities)
            for child in clonable_feature.children:
                config.add_clonable_selection(child.name, instance_number, child)

            # Add intentional_elements
            ies = []
            ies += istarModel.get_goals(a)
            ies += istarModel.get_tasks(a)
            ies += istarModel.get_resources(a)
            ies += istarModel.get_qualities(a)
            for ie in ies:
                #f = fm.get_feature(clean_id(ie.id))    # no se puede hacer por ID porque en i* cada nodo tiene un ID diferente (i* no diferencia configuraciones).
                name = clean_str(ie.name)
                f = fm.get_feature_by_name(name)
                if f != None:
                    config.add_clonable_selection(name, instance_number, f)
            instance_number += 1
    return config

def istar2fm(filename):
    """It loads the i* model and generates a new feature model by mapping the i* model to the FM concepts.

    Args:
        filename (str): Filename of the i* model (.xmi).

    """
    m = istarModel.IStarModel()
    m.load_model(filename)

    fm = generate_feature_model(m)
    fm.save_model(filename[:-4] + "-FM.xmi")
    return fm

    #config = generate_configuration_model(m, fm)
    #config.save_model(filename[:-4] + "-FMconfig.xmi")

def agent2configFM(filename):
    """It loads the i* agent model and generates a new configuration of the feature model by mapping the i* model to the FM concepts.

    Args:
        filename (str): Filename of the i* model (.xmi).

    """
    m = istarModel.IStarModel()
    m.load_model(filename)

    fm = generate_feature_model(m)
    fm.save_model(filename[:-4] + "-FM.xmi")

    config = generate_configuration_model(m, fm)
    config.save_model(filename[:-4] + "-FMconfig.xmi")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""It transforms a i* model (.xmi) to a feature model (.xmi)."""
    )

    parser.add_argument('-f', '--file', required=True, help='i* (istar) model filename',  dest='filename')
    args = parser.parse_args()
    filename = args.filename

    istar2fm(filename)
