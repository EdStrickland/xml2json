import json
def formatEslint(sOrigin):
	oResult = '{' + sOrigin + '}'
	oResult = oResult.lower()\
		.replace("very high", '"veryHigh"')\
		.replace(" high", '"high"')\
		.replace("medium", '"medium"')\
		.replace("low", '"low"')\
		.replace("information",'"information"')
	return json.loads(oResult)