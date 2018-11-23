def summaryCoverage(aOrigin):
	length = len(aOrigin)
	for i in range(0, length):
		aOrigin[i] = int(aOrigin[i]) if (len(aOrigin[i]) > 0) else 0
	top = aOrigin[0] + aOrigin[1] + aOrigin[2]
	bottom = aOrigin[3] + aOrigin[4] + aOrigin[5]
	return round(float(top)/bottom, 3) if bottom is not 0 else 0