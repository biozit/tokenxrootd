import subprocess

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

