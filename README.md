# iStar to Feature Model converter
Set of algorithms and scripts to perform a mapping from an i* (iStar) requirements model to a feature model (FM). 


## Contents
* piStar parser: Script to parser i* models generated with the [PiStar tool](http://www.cin.ufpe.br/~jhcp/pistar/tool/#).  


## Requirements
* Python 3 or higher


## How to use

### piStar parser (pistarParser.py)
Usage:
    python pistarParser.py --file <istar-model.txt>

Input:
    <istar-model.txt> is the i* model generated with the PiStar tool in JSON format.

Output:
    <istar-model.xmi> is the i* model conformed to the i* 2.0 metamodel.



## References
* [iStar 2.0 language guide](https://arxiv.org/abs/1605.07767)  
* [piStar tool](http://www.cin.ufpe.br/~jhcp/pistar/tool/#)
* [piStar repository](https://github.com/jhcp/piStar)  



