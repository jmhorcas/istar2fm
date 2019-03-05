# iStar to Feature Model converter
Set of algorithms and scripts to perform a mapping from an i* (iStar) requirements model to a feature model (FM). 


## Contents
### Algorithm and scripts
* piStar parser (pistarParser.py): Script to parser i* models generated with the [PiStar tool](http://www.cin.ufpe.br/~jhcp/pistar/tool/#).  
* ALG1 and ALG12 (istar2fm.py): Mapping algorithms to convert i* models to FMs and partial configurations of FMs.  
* S.P.L.O.T. generator (fm2splot.py): Script to generate a FM in the S.P.L.O.T. format (SXFM).  

### Core and utils
* metamodel.py: It manages metamodels (.ecore) using the pyecore library.  
* istarModel.py: It manages i* (iStar) models.  
* featureModel.py: It manages feature models (FM models).  
* configurationFM.py: It manages a configuration of a feature model (FM).  

### Metamodels
* metamodels/iStarMetamodel.ecore: Metamodel of i* 2.0 language based on the official [i* 2.0 metamodel](https://arxiv.org/abs/1605.07767).
* metamodels/featureModelMetamodel.ecore: Metamodel of FMs and configurations based on the proposed standards ([CVL](http://caosd.lcc.uma.es/vexgine/about-cvl/) and [EMF](https://projects.eclipse.org/projects/modeling.emft.featuremodel)).  

### Models
* ...


## Requirements
* [Python 3 or higher](https://www.python.org/)  
* [PyEcore library](https://pyecore.readthedocs.io/en/latest/)  


## How to use

### piStar parser (pistarParser.py)
Usage:
    python pistarParser.py --file <istar-model.txt>

Input:
    <istar-model.txt> is the i* model generated with the PiStar tool in JSON format.

Output:
    <istar-model.xmi> is the i* model conformed to the i* 2.0 metamodel.

### ALG1 and ALG12 (istar2fm.py)	
Usage:
    python istar2fm.py --file <istar-model.xmi>

Input:
    <istar-model.xmi> is the i* model conformed to the i* 2.0 metamodel.

Output:
    <fm-model-FM.xmi> is the FM conformed to its metamodel.
    <fm-model-FMconfig.xmi> is a partial configuration of the FM.

### S.P.L.O.T. generator (fm2splot.py)
Usage:
    python fm2splot.py --file <fm-model.xmi>

Input:
    <fm-model.xml> is the feature model conformed to its metamodel.

Output:
    <fm-model-SPLOT.xmi> is the feature model conformed to the S.P.L.O.T. format (SXFM).


## References
* [iStar 2.0 language guide](https://arxiv.org/abs/1605.07767)  
* [piStar tool](http://www.cin.ufpe.br/~jhcp/pistar/tool/#)
* [piStar repository](https://github.com/jhcp/piStar)  
* [PyEcore Documentation](https://pyecore.readthedocs.io/en/latest/)  
* [Feature model information](https://en.wikipedia.org/wiki/Feature_model)  



