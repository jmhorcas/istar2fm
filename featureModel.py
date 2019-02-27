from pyecore.ecore import EClass, EAttribute, EString, EObject
from pyecore.resources import URI
from metamodel import Metamodel

FM_METAMODEL = 'metamodels/featureModelMetamodel.ecore'

class FeatureModel():
    def __init__(self):
        self.metamodel = Metamodel(FM_METAMODEL)
        self.model = self.metamodel.get_class('FeatureModel')()

    def get_model(self):
        """ The model."""
        return self.model

    def save_model(self, filename):
        """Save the model in a .xmi file."""
        resource = self.metamodel.rset.create_resource(URI(filename))
        resource.append(self.model)
        resource.save()

    def load_model(self, filename):
        """Load a model from the .xmi file."""
        resource = self.metamodel.rset.get_resource(URI(filename))
        self.model = resource.contents[0]

    def add_feature(self, id, name, parent=None, variability_type='optional', gMultLower=1, gMultUpper=-1, feature_type='Feature'):
        if parent is None and variability_type in ['alternative', 'or']:
            return None

        feature = self.metamodel.get_class(feature_type)(id=id, name=name, variabilityType=variability_type)
        feature.parent = parent
        if variability_type in ['alternative', 'or']:
            if parent.groupMultiplicity is None:
                parent.groupMultiplicity = self.metamodel.get_class('GroupMultiplicity')(lower=gMultLower, upper=gMultUpper)
            parent.groupMultiplicity.features.append(feature)

        if parent is None:
            self.model.root = feature
        else:
            parent.children.append(feature)
        self.model.features.append(feature)
        return feature

    def add_clonable_feature(self, id, name, instanceMultLower=1, instanceMultUpper=-1, parent=None, variability_type='optional', gMultLower=1, gMultUpper=-1):
        feature = self.add_feature(id, name, parent, variability_type, gMultLower, gMultUpper, 'ClonableFeature')
        feature.instanceMultiplicity = self.metamodel.get_class('Multiplicity')(lower=instanceMultLower, upper=instanceMultUpper)
        return feature

    def add_constraint(self, id, language, code):
        constraint = self.metamodel.get_class('Constraint')(id=id, language=language, code=code)
        self.model.constraints.append(constraint)
        return constraint

    def get_feature(self, id):
        return next((f for f in self.model.features if f.id == id), None)

    def get_root(self):
        return next((f for f in self.model.features if f.parent == None), None)

    def get_features(self):
        return list(self.model.features)

    def get_constraints(self):
        return list(self.model.constraints)
