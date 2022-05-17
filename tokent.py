#!/usr/bin/env python3

import scitokens
import subprocess
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import random
import os
from toolcheck import executeCommandBD
from toolcheck import checkOuput

# private key used for the issuer
with open("/root/scitoken/pkm.key", "r") as file_pointer:
        private_key_contents = file_pointer.read()



loaded_private_key = serialization.load_pem_private_key(
        private_key_contents.encode(),
        password=None,
        backend=default_backend()
    )

# file size in bytes
size = 1024*10;

# caches list
file_lcache = open("/root/scitoken/caches.txt", "r")
lcache = lines = file_lcache.read().splitlines()

# create the tokem
token = scitokens.SciToken(loaded_private_key,key_id="071a")

# radon file name
random.seed(667)
filename = "/tmp/test"+str(random.random())

# random content
with open('%s'%filename, 'wb') as fout:
        fout.write(os.urandom(size))

# creates the token top write the file in the origin
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

# try to fetch the files from the caches
for cache in lcache:

	token.update_claims({"scope":"read:/ospool/monitoring/PROTECTED"});
	token.update_claims({"aud":"ANY"});
	token.update_claims({"ver":"scitoken:2.0"});
	token.update_claims({"sub":"osgmon"});

	e = executeCommandBD("curl -v -H 'Authorization: Bearer " +serialized_token.decode()+"' -k "+cache+"/ospool/monitoring/PROTECTED/"+ filename +" > /tmp/")
	resp = checkOuput(e)
	if (resp != 200):
		print("Error writing origin "+resp) 


