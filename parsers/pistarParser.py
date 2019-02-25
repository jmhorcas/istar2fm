import json
from istarModel import IStarModel

class PiStarParser():
    """Parser for istar model generated with the Pi Star tool (.txt file in JSON format).

    Attributes:
        filename: Model to be parsed (in JSON format).
    """

    def __init__(self, filename):
        self.filename = filename
        self.istar_model = IStarModel()

    def read(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        return data

    def parse(self):
        data = self.read()
        for a in data['actors']:
            actor_type = self.__extract_type(a)
            actor = self.istar_model.add_actor(a['id'], a['text'], actor_type)

            for n in a['nodes']:
                ie_type = self.__extract_type(n)
                ie = self.istar_model.add_intentional_element(n['id'], n['text'], actor, ie_type)

        for d in data['dependencies']:
            dependency_type = self.__extract_type(d)
            self.istar_model.add_dependency_from_source_target(d['id'], d['text'], d['source'], d['target'], dependency_type)

        for l in data['links']:
            link_type = self.__extract_type(l)
            if link_type == "ContributionLink":
                contribution = self.istar_model.add_contribution(l['source'], l['target'], l['label'].capitalize())
            elif link_type == "AndRefinementLink":
                refinement = self.istar_model.add_refinement(l['source'], l['target'], link_type[:4].upper() + link_type[4:-4])
            elif link_type == "OrRefinementLink":
                refinement = self.istar_model.add_refinement(l['source'], l['target'], link_type[:3].upper() + link_type[3:-4])
            elif link_type == "QualificationLink":
                self.istar_model.add_qualifies_association(l['source'], l['target'])
            elif link_type == "NeededByLink":
                self.istar_model.add_needby_association(l['source'], l['target'])
            elif link_type == "IsALink":
                self.istar_model.add_isa_association(l['source'], l['target'])
            elif link_type == "ParticipatesInLink":
                self.istar_model.add_participatesin_association(l['source'], l['target'])

    def __extract_type(self, node):
        type = node['type']
        return type[type.index('.')+1:]

    def generate_xmi_model(self):
        filename = self.filename[:-4] + ".xmi"
        self.istar_model.save_model(filename)
