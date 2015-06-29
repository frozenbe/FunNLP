# -*- coding: utf-8 -*-
'''
A python script that uses the pymorphy2 morphological analyzer
to return nouns in normal forms in a map file where the inflected and normalized values are tab separated.

@author: frozenbe@alumni.uwo.ca
'''

import pymorphy2, codecs, os, sys
morph = pymorphy2.MorphAnalyzer()

def read_file(inputFilePath):

    global listOfNames

    if os.path.exists(inputFilePath):
        print "The file you provided to read the list of names is: \n"
        print os.path.basename(inputFilePath)

        listOfNamesReader = codecs.open(inputFilePath, encoding='utf-8')
        listOfNames = listOfNamesReader.readlines()
        listOfNamesReader.close()        

def normalize(outputFilePath):        
    fOut = codecs.open(outputFilePath,'w')

    print "Writing normalization map... \n"
    for line in listOfNames:
        stringKey = line.strip()
        result = morph.parse(unicode(stringKey))[0]
        stringValue = (result.normal_form)
        outputLine = stringKey + "\t" + stringValue + "\n"
        fOut.write(outputLine.encode('utf-8', 'replace'))

    fOut.close()
    print "Writing normalization map is complete... \n"
    if os.path.exists(outputFilePath):
        print "The file where I wrote the normalization map is: \n"
        print os.path.basename(outputFilePath)
    
if __name__ == '__main__':
    read_file(sys.argv[1])
    normalize(sys.argv[2])