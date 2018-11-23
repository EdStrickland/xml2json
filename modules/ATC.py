def formatATC(aATCOrigin):
	oResult = {
		'high': 0,
		'medium': 0,
		'low': 0
	}
	for check in aATCOrigin:
		if isinstance(check['error'], list):
			for error in check['error']:
				oResult[error['@priority']] += 1
		else:
			oResult[check['error']['@priority']] += 1
	return oResult