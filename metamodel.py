from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
import pyecore.ecore as Ecore

class Metamodel():
    def __init__(self, metamodel):
        self.__import_xmi_metamodel(metamodel)
        self.__adding_external_resources()

    def __import_xmi_metamodel(self, metamodel):
        self.rset = ResourceSet()
        resource = self.rset.get_resource(URI(metamodel))
        mm_root = resource.contents[0]
        self.rset.metamodel_registry[mm_root.nsURI] = mm_root
        self.metamodel = mm_root

    def __adding_external_resources(self):
        """External resources for metamodel loading should be added in the resource set.
        For example, some metamodels use the XMLType instead of the Ecore one.
        The resource creation should be done by hand first:
        """
        int_conversion = lambda x: int(x)  # translating str to int durint load()
        String = Ecore.EDataType('String', str)
        Double = Ecore.EDataType('Double', int, 0, from_string=int_conversion)
        Int = Ecore.EDataType('Int', int, from_string=int_conversion)
        IntObject = Ecore.EDataType('IntObject', int, None,
                                    from_string=int_conversion)
        Boolean = Ecore.EDataType('Boolean', bool, False,
                                  from_string=lambda x: x in ['True', 'true'],
                                  to_string=lambda x: str(x).lower())
        Long = Ecore.EDataType('Long', int, 0, from_string=int_conversion)
        EJavaObject = Ecore.EDataType('EJavaObject', object)
        xmltype = Ecore.EPackage()
        xmltype.eClassifiers.extend([String,
                                     Double,
                                     Int,
                                     EJavaObject,
                                     Long,
                                     Boolean,
                                     IntObject])
        xmltype.nsURI = 'http://www.eclipse.org/emf/2003/XMLType'
        xmltype.nsPrefix = 'xmltype'
        xmltype.name = 'xmltype'
        self.rset.metamodel_registry[xmltype.nsURI] = xmltype

    def create_instance(self, entity):
        """Create a new instance of a entity of the metamodel (actor, agent, goal, task,...)"""
        return self.metamodel.getEClassifier(entity)
