#!/usr/bin/env python3

import scitokens
import subprocess
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import random
import os
import sys

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

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


issuerToken = "https://osg-htc.org/monitoring"

with open("/root/scitoken/pkm.key", "r") as file_pointer:
        private_key_contents = file_pointer.read()

loaded_private_key = serialization.load_pem_private_key(
        private_key_contents.encode(),
        password=None,
        backend=default_backend()
    )

# file size in bytes
size = 1024;


filename = "test"+str(random.random())
filepath = "/tmp/"+filename

# random content
with open('%s'%filepath, 'wb') as fout:
        fout.write(os.urandom(size))


# writing the file on the origin
token = scitokens.SciToken(loaded_private_key,key_id="071a")
token.update_claims({"scope":"write:/"});
token.update_claims({"aud":"ANY"});
token.update_claims({"ver":"scitoken:2.0"});
token.update_claims({"sub":"osgmon"});
serialized_token = token.serialize(issuer=issuerToken)

e = executeCommandBD("curl -i -X 'PUT' --upload-file "+ filepath  +" -H 'Authorization: Bearer " +serialized_token.decode()+"' -k https://stash-xrd.osgconnect.net:1094/ospool/monitoring/PROTECTED/"+filename)
respWriteFileOrigin = checkOuput(e)
if (respWriteFileOrigin != "200"):
	print("Error writing origin "+respWriteFileOrigin) 
else:
	print("file on origin "+filename)


# reading to the cache
token = scitokens.SciToken(loaded_private_key,key_id="071a")
token.update_claims({"scope":"read:/"});
token.update_claims({"aud":"ANY"});
token.update_claims({"ver":"scitoken:2.0"});
token.update_claims({"sub":"osgmon"});
serialized_token = token.serialize(issuer=issuerToken)

e = executeCommandBD("curl -i  -H 'Authorization: Bearer " +serialized_token.decode()+"' -k "+sys.argv[1]+":8444/ospool/monitoring/PROTECTED/"+ filename)
respReadCached = checkOuput(e)
if (respReadCached != 200):
	print("Error reading cache "+respReadCached) 
else:
	print("file on origin "+filename)


# delete on local file system
executeCommandBD("rm "+filepath)

# delete file on the origin
token = scitokens.SciToken(loaded_private_key,key_id="071a")
token.update_claims({"scope":"write:/"});
token.update_claims({"aud":"ANY"});
token.update_claims({"ver":"scitoken:2.0"});
token.update_claims({"sub":"osgmon"});
serialized_token = token.serialize(issuer=issuerToken)

e = executeCommandBD("curl -i -X 'DELETE' -H 'Authorization: Bearer " +serialized_token.decode()+"' -k https://stash-xrd.osgconnect.net:1094/ospool/monitoring/PROTECTED/"+filename)
respDeleteFileOrigin = checkOuput(e)
if (respDeleteFileOrigin != "200"):
	print("Error delete origin "+respDeleteFileOrigin) 
else:
	print("file delete origin "+filename)

if(respDeleteFileOrigin == "200" and respWriteFileOrigin == "200" and respReadCached == "200"):
	 sys.exit(STATE_OK)
else:
	 sys.exit(STATE_CRITICAL)
