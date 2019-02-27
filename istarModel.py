"""
It manages i* (iStar) models.

References:
    i* 2.0 language guide: https://arxiv.org/abs/1605.07767

"""

import metamodel

ISTAR_METAMODEL = 'metamodels/iStarMetamodel.ecore'

class IStarModel():
    """It represents a i* model.

    Attributes:
        metamodel (metamodel.Metamodel): The i* metamodel.
        model (pyecore.ecore.IStarModel): The i* model.

    """

    def __init__(self):
        """Create a new empty i* model."""
        self.metamodel = metamodel.Metamodel(ISTAR_METAMODEL)
        self.model = self.metamodel.get_class('IStarModel')()

    def get_model(self):
        return self.model

    def save_model(self, filename):
        """Save the model in a .xmi file."""
        resource = self.metamodel.create_resource(filename)
        resource.append(self.model)
        resource.save()

    def load_model(self, filename):
        """Load a model from the .xmi file."""
        resource = self.metamodel.get_resource(filename)
        self.model = resource.contents[0]

    def get_actors(self):
        return [a for a in self.model.actors if isinstance(a, self.metamodel.get_class('Actor'))]

    def get_agents(self):
        return [a for a in self.model.actors if isinstance(a, self.metamodel.get_class('Agent'))]

    def get_roles(self):
        return [a for a in self.model.actors if isinstance(a, self.metamodel.get_class('Role'))]

    def get_goals(self, actor):
        return self.__get_intentional_elements(actor, 'Goal')

    def get_tasks(self, actor):
        return self.__get_intentional_elements(actor, 'Task')

    def get_resources(self, actor):
        return self.__get_intentional_elements(actor, 'Resource')

    def get_qualities(self, actor):
        return self.__get_intentional_elements(actor, 'Quality')

    def __get_intentional_elements(self, actor, class_type=None):
        intentional_elements = list(actor.wants)
        intentional_elements += [d.dependum for d in self.model.dependencies if d.dependee == actor]

        if class_type is None:
            return intentional_elements
        else:
            return [g for g in intentional_elements if isinstance(g, self.metamodel.get_class(class_type))]

    def add_actor(self, id, name, class_type=None):
        if class_type is None:
            class_type = 'Actor'
        actor = self.metamodel.get_class(class_type)(id=id, name=name)
        self.model.actors.append(actor)
        return actor

    def add_role(self, id, name):
        return self.add_actor('Role', id, name)

    def add_agent(self, id, name):
        return self.add_actor('Agent', id, name)

    def add_goal(self, id, name, actor):
        return self.add_intentional_element('Goal', id, name, actor)

    def add_task(self, id, name, actor):
        return self.add_intentional_element('Task', id, name, actor)

    def add_resource(self, id, name, actor):
        return self.add_intentional_element('Resource', id, name, actor)

    def add_quality(self, id, name, actor):
        return self.add_intentional_element('Quality', id, name, actor)

    def add_intentional_element(self, id, name, actor, class_type):
        ie = self.metamodel.get_class(class_type)(id=id, name=name)
        actor.wants.add(ie)
        return ie

    def add_dependency(self, id, name, depender, dependerElmt, dependee, dependeeElmt, class_type):
        dependency = self.metamodel.get_class('Dependency')(id=id, name=name)

        dependency.dependerElmt = dependerElmt          # is the intentional element within the depender's actor boundary where the dependency starts from, which explains why the dependency exists.
        dependency.depender = depender                  # is the actor that depends for something (the dependum) to be provided.
        dependency.dependeeElmt = dependeeElmt          # is the intentional element that explains how the dependee intends to provide the dependum.
        dependency.dependee = dependee                  # is the actor that should provide the dependum.
        dependency.dependum = self.metamodel.get_class(class_type)(id=id, name=name)            # is an intentional element that is the object of the dependency.

        self.model.dependencies.append(dependency)
        return dependency

    def add_dependency_from_source_target(self, id, name, source, target, class_type):
        """ El actor al que pertenece el Intentional Element (Goal, Task, Resource, or Quality) es el destino de la dependencia, es decir el Dependee, que es el que tiene que proporcionarla"""
        dependerElmt = self.__search_intentional_element(source)
        depender = next((a for a in self.model.actors if dependerElmt in a.wants), None)
        if depender is None:
            depender = self.__search_actor(source)

        dependeeElmt = self.__search_intentional_element(target)
        dependee = next((a for a in self.model.actors if dependeeElmt in a.wants), None)
        if dependee is None:
            dependee = self.__search_actor(target)

        # print("dependum: " + name)
        # print("depender: " + str(depender))
        # print("dependerElmt: " + str(dependerElmt))
        # print("dependee: " + str(dependee))
        # print("dependeeElmt: " + str(dependeeElmt))
        return self.add_dependency(id, name, depender, dependerElmt, dependee, dependeeElmt, class_type)

    def add_contribution(self, source, target, contribution_type):
        ie = self.__search_intentional_element(source)
        quality = self.__search_intentional_element(target)
        contribution = self.metamodel.get_class('Contribution')(type=contribution_type, contributesTo=quality)
        ie.contribution.append(contribution)
        return contribution

    def add_refinement(self, source, target, class_type):
        ie_father = self.__search_intentional_element(target)
        ie_child = self.__search_intentional_element(source)
        refinement = ie_father.refines
        if refinement is None:
            refinement = self.metamodel.get_class(class_type)()
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
        for a in self.model.actors:
            ie = next((ie for ie in a.wants if ie.id == id), None)
            if ie is not None:
                return ie
        for d in self.model.dependencies:
            if d.dependum.id == id:
                return d.dependum
        return None

    def __search_actor(self, id):
        return next((a for a in self.model.actors if a.id == id), None)
