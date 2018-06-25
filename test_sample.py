import base64
import mimetypes
import os
import pprint
import uuid
import re
import config
import pytest
from sample import isForm, isRecord, getPartsOfFile, ISODocumentFactory, ISODocument, RaiseError

test_fn = "F1ABC1ABC_DEF_G_HGIUDSIUDISHD.txt"
test_results = {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#Collection(driveItem)",
    "value": [
        {
            "@odata.type": "#microsoft.graph.driveItem",
            "name": "Attachments"
        },
        {
            "@odata.type": "#microsoft.graph.driveItem",
            "name": "2.jpg"
        },
        {
            "@odata.type": "#microsoft.graph.driveItem",
            "name": "R001ABC4ABC_DEF.docx"
        },
        {
            "@odata.type": "#microsoft.graph.driveItem",
            "name": "R001ABC5ABC_DEF.docx"
        },
        {
            "@odata.type": "#microsoft.graph.driveItem",
            "name": "F1ABC4ABC_DEF_G_HGIUDSIUDISHD.txt"
        }
    ]
}


def isForm(string):
    if string[0:1] == "f" or string[0:1] == "F":
        return True
    else:
        return False

def isRecord(string):
    if string[0:1] == "r" or string[0:1] == "R":
        return True
    else:
        return False

def getPartsOfFile(string):
    match = re.search('([f|F|R|r]\d*)([A-Za-z_]+?)(\d+)([A-Za-z_]+?)\.(\w+)',string)
    if match:
        return (match.group(1), match.group(2), match.group(3), match.group(4) , match.group(5))
    else:
        return ("None", "None", "None", "None", "None")

class ISODocumentFactory():
    @staticmethod
#     @pytest.mark.parametrize("earned,spent,expected", [
#     ("F1ABC2ABC_DEF_G_HGIUDSIUDISHD.docx"),
#     ("Attachments"),
#     ("2.jpg"),
#     ("R001ABC2ABC_DEF.docx")
# ])
    def createDocument(input_string):
        if isRecord(input_string) == True:
            return ISODocument(getPartsOfFile(input_string)[0],getPartsOfFile(input_string)[1],getPartsOfFile(input_string)[2],getPartsOfFile(input_string)[3],getPartsOfFile(input_string)[4])
            
        elif isForm(input_string) == True: 
            return ISODocument(getPartsOfFile(input_string)[0],getPartsOfFile(input_string)[1],getPartsOfFile(input_string)[2],getPartsOfFile(input_string)[3],getPartsOfFile(input_string)[4])
        else:
            raise ValueError('Document is not a record or string.')

    @staticmethod
    def CreateDocParts(input_string):
        if isRecord(input_string) == True:
            return (getPartsOfFile(input_string))
        elif isForm(input_string) == True: 
            return (getPartsOfFile(input_string))
        else:
            pass

    @staticmethod
    def NoExisting(input_string):
        if isRecord(input_string) == True or isForm(input_string) == True:
            return
        else:
            RaiseError()
        
class ISODocument():
    # [FormNumericId][FormStringId][FormVersion][StringDescription][Extension]
    def __init__(self, numericId, stringId, version, description, extension):
        self.numericId = numericId
        self.stringId = stringId
        self.version = version
        self.description = description
        self.extension = extension

    def file_name(self):
        return self.numericId+self.stringId+str(int(self.version)+1)+self.description+ '.' + self.extension

    def sameFile(self, test_fn):
        if ((getPartsOfFile(self)[0][0:1] == 'F' or getPartsOfFile(self)[0][0:1] == 'R') and (getPartsOfFile(self)[4] == "docx" or getPartsOfFile(self)[4] == "txt")):
            if getPartsOfFile(self)[0] == getPartsOfFile(test_fn)[0] and self[self.rfind("."):] == test_fn[test_fn.rfind("."):]:
                return True
            else:
                return False
        else:
            RaiseError()

def RaiseError():
    return "<h1>Error 404</h1><p>Selected file is not a record or form.</p>"
    # pass#raise error for when error needs to be raised; replaces all the hardcoded return errors

############<class = "??">





def test_isREc():
    assert isRecord("R00100") == True
    assert isRecord("F00100") == False

def test_isForm():
    assert isForm("F00ABC2") == True

def test_getPartsOfFile():
    assert getPartsOfFile(test_fn)[0] == "F1"
    assert getPartsOfFile(test_fn)[1] ==  'ABC'
    assert getPartsOfFile(test_fn)[2] ==  '1'
    assert getPartsOfFile(test_fn)[3] == 'ABC_DEF_G_HGIUDSIUDISHD'
    assert getPartsOfFile(test_fn)[4] == 'txt'

def test_filename():
    Test_File = ISODocument(getPartsOfFile(test_fn)[0],getPartsOfFile(test_fn)[1],getPartsOfFile(test_fn)[2],getPartsOfFile(test_fn)[3],getPartsOfFile(test_fn)[4])
    assert Test_File.file_name() == "F1ABC2ABC_DEF_G_HGIUDSIUDISHD.txt" #should be version + 1

def test_samefile():
    test1 = "F1ABC2ABC_DEF_G_HGIUDSIUDISHD.docx"
    test2 = "F1ABC2ABC_DEF_G_HGIUDSIUDISHD.docx"
    test3 = "F001ABC2ABC_DEF_G_HGIUDSIUDISHD.docx"

    assert ISODocument.sameFile(test1,test2) == True
    assert ISODocument.sameFile(test1,test3) != True
    assert ISODocument.sameFile(test3,test2) != True

def test_integrate_ok():
    match = re.search('([f|F|R|r]\d*)([A-Za-z_]+?)(\d+)([A-Za-z_]+?)\.(\w+)',test_fn)
    if not match:
        print("Test")
        return "<h1>Error</h1><p>Selected file is not a record or form.</p>"
    else:
        InitialDocument = ISODocument(getPartsOfFile(test_fn)[0], getPartsOfFile(test_fn)[1], getPartsOfFile(test_fn)[2], getPartsOfFile(test_fn)[3], getPartsOfFile(test_fn)[4])
        documents = [ISODocumentFactory.CreateDocParts(result['name']) for result in test_results['value'] if ISODocument.sameFile(result['name'],test_fn) == True]# documents = [ISODocumentFactory.returnVersion(result['name']) for result in test_results['value'] if ((File_ext == result['name'][result['name'].rfind(".")+1:]) and (getPartsOfFile(result['name'])[0] == getPartsOfFile(searched_File_ID)[0]))]
        print (documents)
        if not documents:
            #verify that filename is a record or form first DONE
            ISODocumentFactory.NoExisting(test_fn)
            filename = test_fn
            # do something -- create documents with that name and version DO NOT RAISE ERROR DONE
        else:
            sortedDocuments = sorted(documents, reverse = True, key=lambda doc:doc[2])
            # print (sortedDocuments)
            Latest_Doc_version = sortedDocuments[0][2]
            # if (int(Latest_Doc_version) < int(getPartsOfFile(test_fn)[2])):
            #     filename = test_fn
            # else:
            if sortedDocuments[0][2]< getPartsOfFile(test_fn)[2]:
                filename = test_fn
            else:
                InitialDocument.version = Latest_Doc_version 
                filename = InitialDocument.file_name()
    assert filename == "F1ABC5ABC_DEF_G_HGIUDSIUDISHD.txt"

