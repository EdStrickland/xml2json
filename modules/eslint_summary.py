import eslint
import json
def summaryEslint(aOrigin):
	oResult = {}
	for item in aOrigin:
		item = eslint.formatEslint(item)
		for key in item:
			if key in oResult:
				oResult[key] += item[key]
			else:
				oResult[key] = item[key]
	return oResult