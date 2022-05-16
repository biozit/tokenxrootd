#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import scitokens
import subprocess
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import random
import os

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

def executeCommandBD(com):
	with open('out1.txt','w+') as fout:
		with open('err1.txt','w+') as ferr:
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
				return (data[1]);
	except:
		return "204"




with open("/root/scitoken/pkm.key", "r") as file_pointer:
        private_key_contents = file_pointer.read()



loaded_private_key = serialization.load_pem_private_key(
        private_key_contents.encode(),
        password=None,
        backend=default_backend()
    )


size = 1024*10;

file_lcache = open("/root/scitoken/caches.txt", "r")

lcache = lines = file_lcache.read().splitlines()

token = scitokens.SciToken(loaded_private_key,key_id="071a")


random.seed(667)
filename = "/tmp/test"+str(random.random())

with open('%s'%filename, 'wb') as fout:
        fout.write(os.urandom(size))

token.update_claims({"scope":"write:/ospool/monitoring/PROTECTED"});
token.update_claims({"aud":"ANY"});
token.update_claims({"ver":"scitoken:2.0"});
token.update_claims({"sub":"osgmon"});

serialized_token = token.serialize(issuer="https://osg-htc.org/monitoring")


e = executeCommandBD("curl -i -X PUT --upload-file "+ filename  +" -H 'Authorization: Bearer " +serialized_token.decode()+"' -k https://stash-xrd.osgconnect.net:1094/ospool/monitoring/PROTECTED/")
resp = checkOuput(e)
if (resp != 200):
	print("Error writing origin "+resp) 
	exit()

for cache in lcache:

	token.update_claims({"scope":"read:/ospool/monitoring/PROTECTED"});
	token.update_claims({"aud":"ANY"});
	token.update_claims({"ver":"scitoken:2.0"});
	token.update_claims({"sub":"osgmon"});

	e = executeCommandBD("curl -v -H 'Authorization: Bearer " +serialized_token.decode()+"' -k "+cache+"/ospool/monitoring/PROTECTED/"+ filename +" > /tmp/")
	resp = checkOuput(e)
	if (resp != 200):
		print("Error writing origin "+resp) 


