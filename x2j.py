import xmltodict
import time
import json
import os, sys, getopt, imp
from optparse import OptionParser 

# Global Variables
sFrom = ""
sTo = ""
sMod = ""
sDate = ""
output = {}
aOrigin = {}
parser = OptionParser()
sFunc = {
	'ATC': "def formatATC(aATCOrigin):\n\
	oResult = {\n\
		'high': 0,\n\
		'medium': 0,\n\
		'low': 0\n\
	}\n\
	for check in aATCOrigin:\n\
		if isinstance(check['error'], list):\n\
			for error in check['error']:\n\
				oResult[error['@priority']] += 1\n\
		else:\n\
			oResult[check['error']['@priority']] += 1\n\
	return oResult",
	'eslint': 'import json\n\
def formatEslint(sOrigin):\n\
	oResult = \'{\' + sOrigin + \'}\'\n\
	oResult = oResult.lower()\\\n\
		.replace("very high", \'"veryHigh"\')\\\n\
		.replace(" high", \'"high"\')\\\n\
		.replace("medium", \'"medium"\')\\\n\
		.replace("low", \'"low"\')\\\n\
		.replace("information",\'"information"\')\n\
	return json.loads(oResult)',
	'esSum': "import eslint\n\
import json\n\
def summaryEslint(aOrigin):\n\
	oResult = {}\n\
	for item in aOrigin:\n\
		item = eslint.formatEslint(item)\n\
		for key in item:\n\
			if key in oResult:\n\
				oResult[key] += item[key]\n\
			else:\n\
				oResult[key] = item[key]\n\
	return oResult",
	'UTSum': 'def summaryCoverage(aOrigin):\n\
	length = len(aOrigin)\n\
	for i in range(0, length):\n\
		aOrigin[i] = int(aOrigin[i]) if (len(aOrigin[i]) > 0) else 0\n\
	top = aOrigin[0] + aOrigin[1] + aOrigin[2]\n\
	bottom = aOrigin[3] + aOrigin[4] + aOrigin[5]\n\
	return round(float(top)/bottom, 3) if bottom is not 0 else 0'
}

# system arguments handler
def setOptions():
	parser.add_option("-i", "--init",
		action="store_true",
		default=False,
		dest="bInit",
		help="generate properties and some critical folders and formatters [default: %default]. The properties.json file should be put in the same directory as the exe file")
	parser.add_option("-s", "--save",
		action="store_true",
		default=False,
		dest="bToSet",
		help="save properties [default: %default]")
	parser.add_option("-o", "--original",
		action="store_true",
		default=False,
		dest="bOrigin",
		help="get the original JSON data [default: %default]")
	parser.add_option("-f", "--from",
		action="store",
		type="string",
		default=None,
		dest="sFromI",
		help="select the folder to generate report from")
	parser.add_option("-t", "--to",
		action="store",
		type="string",
		default=None,
		dest="sToI",
		help="select the folder to generate report to")
	parser.add_option("-m", "--module",
		action="store",
		type="string",
		default=None,
		dest="sMod",
		help="select the folder to store modules")
	parser.add_option("-d", "--date",
		action="store",
		type="string",
		default=time.strftime("%Y-%m-%d", time.localtime(int(time.time()))),
		dest="sDate",
		help="save properties [default: %default]")

def initProp():
	# initialize properties.json
	dProps = {
		"to": os.path.split(os.path.abspath(__file__))[0] + "\\to", 
		"from": os.path.split(os.path.abspath(__file__))[0] + "\\from",
		"modules": os.path.split(os.path.abspath(__file__))[0] + "\\modules",
		"output": {
			"Task":{
				"ESlint": {
					"src": "Task_ESlint.section.field.@value",
					"formatter":"eslint.formatEslint"
				},
				"Frontend_UT_and_OPA_coverage": {
					"src": "Task_UT&OPA_coverage.coverage.@line-rate"
				}
			},
			"Project":{
				"ESlint": {
					"src": "Project_ESlint.section.field.@value",
					"formatter":"eslint.formatEslint"
				},
				"Frontend_UT_and_OPA_coverage": {
					"src": "Project_UT&OPA_coverage.coverage.@line-rate"
				}
			},
			"Frame":{
				"ESlint":{
					"src": "Frame_ESlint.section.field.@value",
					"formatter":"eslint.formatEslint"
				},
				"Frontend_UT_and_OPA_coverage": {
					"src": "Frame_UT&OPA_coverage.coverage.@line-rate"
				}
			},
			"Summary":{
				"ESlint": {
					"src": [
						"Task_ESlint.section.field.@value",
						"Project_ESlint.section.field.@value",
						"Frame_ESlint.section.field.@value"
					],
					"formatter": "eslint_summary.summaryEslint"
				},
				"Frontend_UT_and_OPA_coverage": {
					"src": [
						"Task_UT&OPA_coverage.coverage.@lines-covered", 
						"Project_UT&OPA_coverage.coverage.@lines-covered", 
						"Frame_UT&OPA_coverage.coverage.@lines-covered",
						"Task_UT&OPA_coverage.coverage.@lines-valid", 
						"Project_UT&OPA_coverage.coverage.@lines-valid", 
						"Frame_UT&OPA_coverage.coverage.@lines-valid"
					],
					"formatter": "UT_OPA_summary.summaryCoverage"
				},
				"ATC": {
					"src": "ATC_Result.checkstyle.file",
					"formatter": "ATC.formatATC"
				},
				"Backend_UT":{
					"TestCases": {
						"src": "Backend_UT_Result.testsuites.@tests"
					},
					"line_coverage": {
						"src": "Backend_UT_coverage.coverage.@line-rate"
					},
					"branch_coverage": {
						"src": "Backend_UT_coverage.coverage.@branch-rate"
					}
				}
			}
		}
	}
	fw = file(os.path.split(os.path.abspath(__file__))[0] + "\\properties.json", 'w')
	json.dump(dProps, fw, indent = 4)
	fw.close()
	return dProps

def createFunction(sFunc, sFilePath):
	fFunc = file(sFilePath, 'w')
	fFunc.write(sFunc)
	fFunc.close()

def init():
	# initialize the application
	dProps = initProp()
	
	if not(os.path.exists(dProps['from'])):
		os.makedirs(dProps['from'])
	
	if not(os.path.exists(dProps['modules'])):
		os.makedirs(dProps['modules'])

	createFunction(sFunc['ATC'], dProps['modules'] + "\\ATC.py")
	createFunction(sFunc['eslint'], dProps['modules'] + "\\eslint.py")
	createFunction(sFunc['esSum'], dProps['modules'] + "\\eslint_summary.py")
	createFunction(sFunc['UTSum'], dProps['modules'] + "\\UT_OPA_summary.py")
	
	return dProps

def setPath(sProp, sFromI, oProp):
	# get path from sys argv if any, otherwise get from properties
	if (sFromI):
		return sFromI
	if (oProp[sProp] or (os.path.exists(oProp['from']))):
		return oProp[sProp]

def getProperties():
	dProps = {}
	try:
		fr = open(os.path.split(os.path.abspath(__file__))[0] + "\\properties.json", 'r')
		try:
			sResult = fr.read()
			dProps = json.loads(sResult)
		finally:
			fr.close()
			return dProps
	except IOError:
		return init()

def writeProperties():
	prop = {
		"from":sFrom,
		"to": sTo,
		"modules": sMod,
		"output": output
	}
	fw = file(os.path.split(os.path.abspath(__file__))[0] + '\\properties.json', 'w')
	json.dump(prop, fw, indent = 4)
	fw.close()

def execOptions():
	# get settings from system arguments
	options = parser.parse_args()[0]
	oParams = {
		'bInit': options.bInit,
		'bToSet': options.bToSet,
		'bOrigin': options.bOrigin,
		'sFromI':options.sFromI,
		'sToI': options.sToI,
		'sMod': options.sMod,
		'sDate': options.sDate
	}
	if(oParams['bInit']):
	# initialize the application properties if '--init or -i' is in the sys args
		dProps = init()
	else:
	# otherwise get the properties from the properties.json file
		dProps = getProperties()

	# initialze global variables from sys params and properties
	global sFrom
	sFrom = setPath('from', oParams['sFromI'], dProps)
	global sTo
	sTo = setPath('to', oParams['sToI'], dProps)
	global sMod
	sMod = setPath('modules', oParams['sMod'], dProps)
	global sDate
	sDate = oParams["sDate"]
	global output
	output = dProps["output"]

	# write current settings into properties.json if '--save or -s' is in the sys args
	if(oParams['bToSet']):
		writeProperties()
	
	return oParams['bOrigin']

# main functions
def readFiles():
	oResult = {}
	try:
		aFileList = os.listdir(sFrom)
		for sFile in aFileList:
			(sFilename, sExtension) = os.path.splitext(sFile)
			if sExtension == '.xml':
				fr = open(sFrom + '\\' + sFile, 'r')
				try:
					sContent = fr.read()
					oResult[sFilename] = xmltodict.parse(sContent)
				finally:
					print(sFile + ' conversion ... complete')
					fr.close()
	except Exception as e:
		print (e.message)
	finally:
		return oResult

def generateData(aPaths):
	# look for the data in original result
	aResult = []
	for aPath in aPaths:
		sResult = aOrigin
		for sAttr in aPath:
			if (sAttr in list(sResult.keys())):
				sResult = sResult[sAttr]
			else:
				sResult = ""
				break
		aResult.append(sResult)
	if len(aResult) == 1:
		aResult = aResult[0]
	elif len(aResult) == 0:
		aResult = ""
	return aResult

def getResultFromOriginalData(oDict, sKey):
	# find the data regressively and replace the value of sKey attribute of oDict
	
	# generate the path array
	if isinstance(oDict[sKey], str):
		aPath = [oDict[sKey].split('.')]
	elif isinstance(oDict[sKey], dict):
		if isinstance(oDict[sKey]['src'], list):
			aPath = [item.split('.') for item in oDict[sKey]['src']]
		else:
			aPath = [oDict[sKey]['src'].split('.')]
	
	# get data with the path
	oResult = generateData(aPath)

	# if fomatter exists, format the data
	if 'formatter' in oDict[sKey] and oDict[sKey]['formatter']:
		aFormatter = oDict[sKey]['formatter'].split('.')
		try:
			aFormatterFunc = aFormatter.pop()
			oMod = imp.load_source(aFormatter[0], sMod + '\\' + '\\'.join(aFormatter) + '.py')
			oResult = eval('oMod.' + aFormatterFunc)(oResult)
		except Exception as e:
			print(e.message)
	oDict[sKey] = oResult

def replaceDict(oDict):
	for sKey in list(oDict.keys()):
	# if value is string, or contains attribute 'src', it is the path of the data
		if isinstance(oDict[sKey], str) or isinstance(oDict[sKey], dict) and 'src' in oDict[sKey]:
			getResultFromOriginalData(oDict, sKey)
	# otherwise, regression call of this function is needed
		elif isinstance(oDict[sKey], dict):
			replaceDict(oDict[sKey])

def generateResult():
	oResult = output
	replaceDict(oResult)
	oResult['DataCollectingDate'] = sDate
	return oResult

def writeFile(dResult):
	print("generating report")
	if not(os.path.exists(sTo)):
		os.makedirs(sTo)
	fw = file(sTo + '\\result.json', 'w')
	try:
		json.dump(dResult, fw, indent = 4)
	finally:
		print("report is now in " + sTo + "\\result.json")
		fw.close()

# Main
def main():
	# handle options
	setOptions()
	bOrigin = execOptions()
	
	# get data from xml
	global aOrigin
	aOrigin = readFiles()
	
	# convert data and put into json file
	oResult = aOrigin if bOrigin else generateResult()
	writeFile(oResult)

if __name__ == '__main__':
	main()