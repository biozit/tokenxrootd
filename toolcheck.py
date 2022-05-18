import subprocess

def executeCommandBD(com):
	with open('out1.txt','w+') as fout:
		with open('err1.txt','w+') as ferr:
			print(com)
			out=subprocess.call([com],stdout=fout,stderr=ferr,timeout=500,shell=True)
			fout.seek(0)
			output=fout.read()
			ferr.seek(0) 
			errors = ferr.read()
			return output

def checkOuput(data):
	try:
		lines = data.splitlines()
		for l in lines:
			if ( l.find('HTTP/1.1') != -1 ):
				data = l.split(' ')
				if((data[1] != "100") and (data[1] != "200")):
					return "204"
		return "200"
	except:
		return "204"

