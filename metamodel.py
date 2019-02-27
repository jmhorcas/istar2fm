"""
It manages metamodels (.ecore) using the pyecore library.

References:
    PyEcore: https://pyecore.readthedocs.io/en/latest/

"""

from pyecore.resources import ResourceSet, URI
import pyecore.ecore as Ecore

class Metamodel():
    """It loads a metamodel and allows creating instances of its entities.

    Attributes:
        metamodel (Ecore): The Ecore metamodel.

    """

    def __init__(self, metamodel):
        """Load the metamodel.

        Args:
            metamodel (str): Filename (.ecore) of the metamodel.

        """
        self._rset = ResourceSet()
        resource = self._rset.get_resource(URI(metamodel))
        mm_root = resource.contents[0]
        self._rset.metamodel_registry[mm_root.nsURI] = mm_root
        self.metamodel = mm_root
        self._add_external_resources()

    def get_class(self, entity):
        """Obtain the EClass of the specified entity concept.

        Note:
            Use this method to create new instances of a metamodel's entity.

        Args:
            entity (str): Name of the EClass in the metamodel.

        """
        return self.metamodel.getEClassifier(entity)

    def get_resource(self, filename):
        """Obtain a resource.

        Note:
            Use this method to load a model conformed to the metamodel.

        Args:
            filename (str): Filename of the resource.

        Returns:
            The resource.
        """
        return self._rset.get_resource(URI(filename))

    def create_resource(self, filename):
        """Create a new resource.

        Note:
            Use this method to save a model conformed to the metamodel.

        Args:
            filename (str): Filename for the resource.

        Returns:
            The resource.
        """
        return self._rset.create_resource(URI(filename))

    def _add_external_resources(self):
        """Add external resources for the metamodel such as XMLType."""
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
        self._rset.metamodel_registry[xmltype.nsURI] = xmltype
