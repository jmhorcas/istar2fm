#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to generate a S.P.L.O.T. model in the SXFM format from a .xmi feature model.
"""

import argparse
import datetime
import featureModel
import sympy

EOL = '\n'
TAB = '\t'
ORGANIZATION = "CAOSD group (Universidad de Málaga)"
ADDRESS = "Málaga (Spain)"
WEBSITE = "http://caosd.lcc.uma.es/"


def headers(filename):
    feature_model_name = filename.split('/')[-1][:-4].replace('-', '')
    headers = '<feature_model name="' + feature_model_name + '">' + EOL
    headers += '<meta>' + EOL
    #headers += '<data name="description">Model description</data>' + EOL
    headers += '<data name="creator">fm2splot converter tool</data>' + EOL
    #headers += '<data name="email">Model creator\'s email</data>' + EOL
    headers += '<data name="date">' + str(datetime.datetime.now()).split(' ')[0] + '</data>' + EOL
    #headers += '<data name="department">Model creator\'s department</data>' + EOL
    headers += '<data name="organization">' + ORGANIZATION + '</data>' + EOL
    headers += '<data name="address">' + ADDRESS + '</data>' + EOL
    #headers += '<data name="phone">Model creator\'s phone</data>' + EOL
    headers += '<data name="website">' + WEBSITE + '</data>' + EOL
    #headers += '<data name="reference">Model\'s related publication</data>' + EOL
    headers += '</meta>' + EOL
    return headers


def add_feature(fm, feature, n_tabs, root=False, id=0):
    name_id = feature.name + ' (' + feature.id + ')'
    tabs = TAB*n_tabs

    if root:
        code = tabs + ':r ' + name_id + EOL
    else:
        type = str(feature.variabilityType)
        if type == 'optional':
            code = tabs + ':o ' + name_id + EOL

        if type == 'mandatory':
            code = tabs + ':m ' + name_id + EOL

        if type in ['or', 'alternative']:
            code = tabs + ': ' + name_id + EOL

    if feature.groupMultiplicity is not None:
        lower = feature.groupMultiplicity.lower
        upper = feature.groupMultiplicity.upper
        if lower == -1: lower = 1                   # limitation of SPLOT.
        if upper == -1: upper = '*'
        #code += tabs + TAB + ':g (_id' + str(id) + ') [' + str(lower) + ',' + str(upper) + ']' + EOL    # Con IDs
        code += tabs + TAB + ':g [' + str(lower) + ',' + str(upper) + ']' + EOL                         # Sin IDs
        for child in feature.groupMultiplicity.features:
            code += add_feature(fm, child, n_tabs+2, id=id+1)

    for child in feature.children:
        if str(child.variabilityType) not in ['or', 'alternative']:
            code += add_feature(fm, child, n_tabs+1, id=id+1)

    return code


def feature_tree(fm):
    root = fm.get_root()
    features = set(fm.get_features()).remove(root)

    tree = '<feature_tree>' + EOL
    tree += add_feature(fm, root, 0, True)
    tree += '</feature_tree>' + EOL

    return tree

CONSTRAINTS_RESERVED = ['implies', 'or', 'and', 'not']

def extract_symbols(constraint):
    symbols = constraint.split()
    symbols = [x for x in symbols if x not in CONSTRAINTS_RESERVED]
    symbols = [x.replace('(', '').replace(')', '') for x in symbols]
    return symbols

def from_constraint_to_formula(constraint):
    symbols = constraint.split()
    symbols = map(lambda x: '>>' if x == 'implies' else x, symbols)
    symbols = map(lambda x: '|' if x == 'or' else x, symbols)
    symbols = map(lambda x: '&' if x == 'and' else x, symbols)
    symbols = map(lambda x: '~' if x == 'not' else x, symbols)
    return "".join(list(symbols))

def to_cnf(constraint):
    #print("C: " + constraint)
    symbols = extract_symbols(constraint)
    formula_str = from_constraint_to_formula(constraint)

    #print("F: " + formula_str)
    #print("S: " + str(symbols))
    x = sympy.symbols(symbols)
    formula = sympy.to_cnf(formula_str)

    splot_formula = str(formula).replace('|', 'or')
    return splot_formula

def __imprimir_constraint(fm, c):
    for f in fm.get_features():
        if f.id in c:
            c = c.replace(f.id, f.name)
    print("F: " + c)

def constraints(fm):
    code = '<constraints>' + EOL

    constraints_cnf = set()
    for c in fm.get_constraints():
        __imprimir_constraint(fm, c.code)
        constraints_cnf.add(to_cnf(c.code))

    count = 1
    for c in constraints_cnf:
        code += 'C' + str(count) + ': ' + c + EOL
        count += 1

    code += '</constraints>' + EOL
    return code

def write_file(code, filename):
    with open(filename, 'w+') as f:
        f.write(code)

def fm2splot(filename):
    fm = featureModel.FeatureModel()
    fm.load_model(filename)

    code = headers(filename[:-4])
    code += feature_tree(fm)
    code += constraints(fm)
    code += '</feature_model>' + EOL

    write_file(code, filename[:-4] + '-SPLOT.xml')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Generate a S.P.L.O.T. model in the SXFM format from a .xmi feature model."""
    )

    parser.add_argument('-f', '--file', required=True, help='Feature model (.xmi) file',  dest='filename')
    args = parser.parse_args()
    filename = args.filename

    fm2splot(filename)
