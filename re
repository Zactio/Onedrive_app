re.
re split.
string join method.

def getVersion(string):
	return None if no version, else return version number

def getFileName(string):
	return filename

def makeFullFileName(filename, version, extension):
	return entirefilename

def makeOneDriveFilepath(originalPath, filename):
	return path

def getHighestVersion(listOfStrings):
	pass

Forms:
F[FormNumericId][FormStringId][FormVersion][StringDescription]
e.g. F1ABC2ABC_DEF_G_HGIUDSIUDISHD.docx

Records:
R[3-Digit-RecordNumericId][FormStringId][RecordVersion][StringDescription]
e.g. R001ABC2ABC_DEF.docx

<Letter><Integer><String><Integer><String>

#if file to upload is not of the correct format, throw error

def isForm(string):
	return True/False

def isRecord(string):
	return True/False

def getPartsOfForm(string):
	return formNumericId, formStringId, formVersion, stringDescription #for numericid/version, you can return integer or string

def getPartsOfRecord(string):
	return ....

def makeNextFormString(initialFormString):
	#assume that fform string is of the corrrect format
	return string

def makeNextRecordString(initialRecordString):
	return string

def makeFormNumericId(integer):
	e.g. when integer = 1
	return  "001"

def getLatestVersionForm(formNumericId):
	pass

def getLatestVersionReport():
	pass
 
---------------
check for whether is form or is record, if not discard. make page.
if no latest version, keep version.
have 00 for records, ignore for forms

Given a file,
identify if its a form or template. create a class with the base interface for mutation. use that class downstream.

class ISODocumentFactory():
	def createDocument(input string):
		if isRecord:
			return Record(*args)
		else if matches Form:
			return Form(*args)
		else:
			throw error

results = onedrive
#preproocessing
documents = [ISODocumentFactory.createDocument(result) for result in  results]
sortedDocuments = sorted(documents, lambda document: document.version)
latestDocument = ???
nextDocumentName = latestDocument.makeNextDocumentString()


class ISODocument():
	[FormNumericId][FormStringId][FormVersion][StringDescription]
	def __init__(self, numericId, stringId, version, description):
		self.numeric..
		self.stringId...
		self.version = 

	def makeNextDocumentString():
		raise Error

class ISOForm(ISODocument):
	def __init__(self, args):
		super().__init__(args)
		pass

	def makeNextDoumentString():
		implement this
		returns the filename of the next version

class ISORecord(ISODocument):
	def __init__(self, args):
		super().__init__(args)

	def makeNextDocumentString():
		implement this