from pyecore.resources import URI
from metamodel import Metamodel

ISTAR_METAMODEL = 'metamodels/iStarMetamodel.ecore'

class IStarModel():
    def __init__(self):
        self.istar_metamodel = Metamodel(ISTAR_METAMODEL)
        self.istar_model = self.istar_metamodel.create_instance('IStarModel')()

    def add_actor(self, type, id, name):
        actor = self.istar_metamodel.create_instance(type)(id=id, name=name)
        self.istar_model.actors.append(actor)
        return actor

    def add_intentional_element(self, actor, type, id, name):
        ie = self.istar_metamodel.create_instance(type)(id=id, name=name)
        actor.wants.add(ie)
        return ie

    def add_dependency(self, type, source, target, id, name):
        """ El actor al que pertenece el Intentional Element (Goal, Task, Resource, or Quality) es el destino de la dependencia, es decir el Dependee, que es el que tiene que proporcionarla"""
        dependency = self.istar_metamodel.create_instance('Dependency')(id=id, name=name)

        dependerElmt = self.__search_intentional_element(source)
        depender = next((a for a in self.istar_model.actors if dependerElmt in a.wants), None)
        if depender is None:
            depender = self.__search_actor(source)

        dependeeElmt = self.__search_intentional_element(target)
        dependee = next((a for a in self.istar_model.actors if dependeeElmt in a.wants), None)
        if dependee is None:
            dependee = self.__search_actor(target)

        dependency.dependerElmt = dependerElmt          # is the intentional element within the depender's actor boundary where the dependency starts from, which explains why the dependency exists.
        dependency.depender = depender                  # is the actor that depends for something (the dependum) to be provided.
        dependency.dependeeElmt = dependeeElmt          # is the intentional element that explains how the dependee intends to provide the dependum.
        dependency.dependee = dependee                  # is the actor that should provide the dependum.
        dependency.dependum = self.istar_metamodel.create_instance(type)(id=id, name=name)            # is an intentional element that is the object of the dependency.
        self.istar_model.dependencies.append(dependency)

        return dependency

    def add_contribution(self, source, target, contribution_type):
        ie = self.__search_intentional_element(source)
        quality = self.__search_intentional_element(target)
        contribution = self.istar_metamodel.create_instance('Contribution')(type=contribution_type, contributesTo=quality)
        ie.contribution.append(contribution)

        return contribution

    def add_refinement(self, type, source, target):
        ie_father = self.__search_intentional_element(target)
        ie_child = self.__search_intentional_element(source)
        refinement = ie_father.refines
        if refinement is None:
            refinement = self.istar_metamodel.create_instance(type)()
            ie_father.refines = refinement
        refinement.to.append(ie_child)

        return refinement

    def add_qualifies_association(self, source, target):
        quality = self.__search_intentional_element(source)
        ie = self.__search_intentional_element(target)
        quality.qualifies.append(ie)

    def add_needby_association(self, source, target):
        resource = self.__search_intentional_element(source)
        ie = self.__search_intentional_element(target)
        resource.neededBy.append(ie)

    def add_isa_association(self, source, target):
        actor1 = self.__search_actor(source)
        actor2 = self.__search_actor(target)
        actor1.isA.append(actor2)

    def add_participatesin_association(self, source, target):
        actor1 = self.__search_actor(source)
        actor2 = self.__search_actor(target)
        actor1.participatesIn.append(actor2)

    def __search_intentional_element(self, id):
        for a in self.istar_model.actors:
            ie = next((ie for ie in a.wants if ie.id == id), None)
            if ie is not None:
                return ie
        for d in self.istar_model.dependencies:
            if d.dependum.id == id:
                return d.dependum
        return None

    def __search_actor(self, id):
        return next((a for a in self.istar_model.actors if a.id == id), None)

    def save_model(self, filename):
        resource = self.istar_metamodel.rset.create_resource(URI(filename))
        resource.append(self.istar_model)
        resource.save()

    def load_model(self, filename):
        resource = self.istar_metamodel.rset.get_resource(URI(filename))
        self.istar_model = resource.contents[0]

    def get_model(self):
        return self.istar_model
