#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to map i* (istar) models to feature models.

Este será el archivo principal, lee fichero de piStar tool (.json) y lo pasa a clafer (.txt) o lo que sea.
"""

import argparse
import parsers.pistarParser as pistarParser
import istarModel
import featureModel

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


def add_exclusive_constraints(fm, names):
    for n in names:
        constraint = n + ' implies not ('
        for n2 in names:
            if n != n2:
                constraint += n2 + ' or '
        constraint = constraint[:-4] + ')'
        fm.add_constraint(constraint.replace(' ', ''), 'First-order logic', constraint)

def add_goal(istar, fm, goal, parent_feature, variability_type, lower=0, upper=-1):
    processed_goals = []
    feature = fm.get_feature(goal.id)
    if feature is not None:     # si la feature ya existía la elimino y la vuelvo a crear para actualizar su información adecuadamente (padre y tipo de variabilidad)
        feature.delete()

    gF = fm.add_feature(goal.id, goal.name.replace(' ', ''), parent_feature, variability_type, lower, upper)
    processed_goals.append(goal)
    if goal.refines is not None:
        if isinstance(goal.refines, istar.istar_metamodel.get_class('ORRefinement')):
            OR_goals = []
            hasConstraints = False
            for child in goal.refines.to:
                if isinstance(child, istar.istar_metamodel.get_class('Goal')):
                    OR_goals.append(child)
                else:
                    hasConstraints = True

            if not hasConstraints:
                for or_g in OR_goals:
                    processed_goals += add_goal(istar, fm, or_g, gF, 'alternative', -1, -1)
            else:
                if len(OR_goals) == 1:
                    processed_goals += add_goal(istar, fm, OR_goals[0], gF, 'optional')
                elif len(OR_goals) > 1:
                    for or_g in OR_goals:
                        processed_goals += add_goal(istar, fm, or_g, gF, 'or', 0, 1)

                constraint = goal.name.replace(' ', '') + ' implies ('
                for child in goal.refines.to:
                    constraint += child.name.replace(' ', '') + ' or '
                constraint = constraint[:-4] + ')'
                fm.add_constraint(constraint.replace(' ', ''), 'First-order logic', constraint)
                add_exclusive_constraints(fm, [g.name.replace(' ', '') for g in goal.refines.to])
                # for child in goal.refines.to:
                #     constraint = child.name + ' implies not ('
                #     for child2 in goal.refines.to:
                #         if child != child2:
                #             constraint += child2.name + ' or '
                #     constraint = constraint[:-4] + ')'
                #     fm.add_constraint(constraint.replace(' ', ''), 'First-order logic', constraint)
        elif isinstance(goal.refines, istar.istar_metamodel.get_class('ANDRefinement')):
            AND_goals = []
            ie_constraints = []
            for child in goal.refines.to:
                if isinstance(child, istar.istar_metamodel.get_class('Goal')):
                    AND_goals.append(child)
                else:
                    ie_constraints.append(child)

            if len(AND_goals) == 1:
                processed_goals += add_goal(istar, fm, AND_goals[0], gF, 'mandatory')
            elif len(AND_goals) > 1:
                for and_g in AND_goals:
                    processed_goals += add_goal(istar, fm, and_g, gF, 'or', -1, -1)
            if len(ie_constraints) > 0:
                constraint = goal.name.replace(' ', '') + ' implies ('
                for child in ie_constraints:
                    constraint += child.name.replace(' ', '') + ' and '
                constraint = constraint[:-4] + ')'
                fm.add_constraint(constraint.replace(' ', ''), 'First-order logic', constraint)
    return processed_goals

def generate_feature_model(istarModel):
    fm = featureModel.FeatureModel()
    root = fm.add_feature(id='Root', name='Root', variability_type='mandatory')
    for r in istarModel.get_roles()+istarModel.get_actors():
        f = fm.add_clonable_feature(r.id, r.name.replace(' ', ''), parent=root, variability_type='or')

        name = r.name.replace(' ', '')
        goalsF = fm.add_feature(name+'Goals', name+'Goals', f, 'mandatory')
        plansF = fm.add_feature(name+'Plans', name+'Plans', f, 'mandatory')
        contextF = fm.add_feature(name+'Context', name+'Context', f, 'mandatory')
        qualityattributesF = fm.add_feature(name+'QAs', name+'QAs', f, 'optional')

        processed_goals = []
        for g in istarModel.get_goals(r):
            if g not in processed_goals:
                print("----" + str(g.name) + "------")
                processed_goals = add_goal(istarModel, fm, g, goalsF, 'or', -1, -1)

        #if istarModel.get_goals(r) is not None:
        #    print("#Goals: " + str(len(istarModel.get_goals(r))))
        #    print("#Processed Goals: " + str(len(processed_goals)))
        cc = fm.get_constraints()
        for c in cc:
            print(c.code)


def mapping(filename):
    p = pistarParser.PiStarParser(filename)
    p.parse()
    xmi_file = p.generate_xmi_model()

    m = istarModel.IStarModel()
    m.load_model(xmi_file)

    generate_feature_model(m)






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
