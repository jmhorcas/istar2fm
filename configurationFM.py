"""
It manages a configuration of a feature model (FM).

References:
    Feature Model: https://en.wikipedia.org/wiki/Feature_model

"""

import metamodel
import featureModel

FM_METAMODEL = 'metamodels/featureModelMetamodel.ecore'

class FMConfiguration():
    """It represents a configuration of a feature model (FM).

    Attributes:
        metamodel (metamodel.Metamodel): The FM configuration metamodel.
        fm (featureModel.FeatureModel): The FM.
        configuration (pyecore.ecore.Configuration): The configuration.

    """

    def __init__(self, model):
        """Create a new empty configuration for the specified FM.

        Args:
            model (featureModel.FeatureModel)

        """
        self.metamodel = model.metamodel
        self.fm = model
        self.configurationModel = self.metamodel.get_class('ConfigurationModel')()

    # def __create_empty_configuration(self):
    #     for f in self.fm.get_features():
    #         if isistance(f, self.fm.metamodel.get_class('ClonableFeature')):
    #             self.configurationModel.selections.append(self.metamodel.get_class('ClonableInstance')(id=f.id, instances=0))
    #         elif not self.fm.is_clonable_child(f):
    #             self.configurationModel.selections.append(self.metamodel.get_class('Selection')(id=f.id))

    def get_FM(self):
        return self.fm

    def get_configuration(self):
        return self.configurationModel

    def save_model(self, filename):
        """Save the model in a .xmi file."""
        resource = self.metamodel.create_resource(filename)
        resource.append(self.configurationModel)
        resource.save()

    def load_model(self, filename):
        """Load a model from the .xmi file."""
        resource = self.metamodel.get_resource(filename)
        self.configurationModel = resource.contents[0]

    def get_selections(self):
        return self.configurationModel.selections

    def add_selection(self, name, feature):
        selection = self.metamodel.get_class('Selection')(state='selected', name=name)
        self.configurationModel.selections.append(selection)
        selection.feature = feature
        return selection

    def add_clonable_selection(self, name, instance_number, feature):
        cf = self.metamodel.get_class('ClonableFeature')()
        selection = self.metamodel.get_class('ClonableSelection')(instance=instance_number, state='selected', name=name+'_'+str(instance_number))
        self.configurationModel.selections.append(selection)
        selection.feature = feature
        return selection


    # def select_clonable(self, feature, instances):
    #     assert isistance(feature, self.fm.metamodel.get_class('ClonableFeature')), "Feature is not clonable!"
    #
    #     selection = next((x for x in self.configurationModel.selections if x.id == feature.id), None)
    #     if selection is None:
    #         clonableConf = self.configurationModel.selections.append(self.metamodel.get_class('ClonableInstance')(id=feature.id, state='selected', instances=instances))
    #         clonableConf.feature = feature
    #
    #         for i in range(1, instances+1):
    #             clonableInstance = self.configurationModel.selections.append(self.metamodel.get_class('Selection')(id=feature.id + str(i), state='selected'))
    #             clonableInstance.feature = feature
    #
    #
    # def select(self, feature, clonableInstance=None):
    #
    #     selection = next((x for x in self.configurationModel.selections if x.id == feature.id), None)
    #     selection.state = 'selected'
