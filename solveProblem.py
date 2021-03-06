import subprocess
#import argparse
import string
import os
import threading
import sys
import time

import json
import urllib.request

import getInputOutput
import buildContestDir
import openContestUrl
import getVerdict
from config import config

FNULL = open(os.devnull, 'w')

# deprecated
## handle parsing of the contest
#parser = argparse.ArgumentParser()
#parser.add_argument('--contest_id','-cid', default = '4A') # takes in an argument like '491a'
#args = parser.parse_args()
#
## get from the args the contest number and problem alpha, O(n), n is small
#contestNo = ''
#problemAlpha = ''
#for i in args.contest_id:
#    if i in string.digits:
#        contestNo += i
#    else:
#        problemAlpha += i

def solveProblem(contestNo, problemAlpha):
# first, build up the path if it doesn't exist for the contest
    buildContestDir.buildContestDir(contestNo,problemAlpha)

# get solutions and store in directory
    (inputs,outputs) = getInputOutput.getInputOutput(contestNo, problemAlpha)
    i = 0
    for inpt in inputs:
        with open(contestNo+problemAlpha+'_'+str(i)+'.in', 'w') as f:
            lines = ""
            for line in inpt:
                lines += line+'\n'
            i += 1
            f.write(lines)

    i = 0
    for output in outputs:
        with open(contestNo+problemAlpha+'_'+str(i)+'.out', 'w') as f:
            lines = ""
            for line in output:
                lines += line+'\n'
            i += 1
            f.write(lines)

    def writeFile():
        subprocess.run([config['favEditor'],contestNo+problemAlpha+'.'+config['favExtension']])

    def testFile():
        while True:
            i = 0
            correctOutputs = 0

            # compile the program if necessary
            if config['compiles'][config['favExtension']]:
                if config['favExtension'] == 'cpp':
                    try:
                        subprocess.run(['g++', contestNo+problemAlpha+'.cpp', '-o', contestNo+problemAlpha],stdout=FNULL,stderr=subprocess.STDOUT)
                    except:
                        continue
                else:
                    print('language compile syntax not supported; please log as an issue on the repo for byteGun')

            for inpt in inputs:
                with open(contestNo+problemAlpha+'_'+str(i)+'.in') as inStream:
                    if config['favExtension'] == 'cpp':
                        try:
                            testOutput = subprocess.check_output(['./'+contestNo+problemAlpha], stdin=inStream,stderr=subprocess.STDOUT).decode('utf8')
                        except:
                            continue
                    elif config['favExtension'] == 'py':
                        try:
                            testOutput = subprocess.check_output(['python3', contestNo+problemAlpha+'.py'], stdin=inStream,stderr=subprocess.STDOUT).decode('utf8')
                        except:
                            continue
                    else:
                        print('language currently not supported. either fork and add it yourself then make a pull request, or log as an issue on the repo for byteGun.')
                    if testOutput == ''.join(outputs[i]):
                        correctOutputs += 1
                    i += 1
            if correctOutputs == len(inputs):
                print('all cases passed!')
                print('close your editor to begin submission process if you want')
                # lets make the assumption that only 3 threads will be open (main, editor, this one). then, only continue if threading.active_count() == 2
                while threading.active_count() != 2:
                    i = 0
                    time.sleep(1) # be nice
                    # do nothing; busy loop
                shouldSubmit = input('press "y" and enter to submit\n').strip()
                # this solution works for vim
                if shouldSubmit == 'y':
                    openContestUrl.openContestUrl(contestNo, problemAlpha)
                    i = 0
                    verdict = ''
                    while verdict == '':
                        verdict = getVerdict.getVerdict()
                        print('The last result was: ',verdict)
                        time.sleep(1)
                        i += 1
                        if i > config['maxCalls']:
                            print('timeout; judge did not give a verdict within '+str(config['maxCalls'])+' seconds.')
                            break;
                return
            time.sleep(3)


    writeFileThread = threading.Thread(target = writeFile)
    writeFileThread.start()

    testFileThread = threading.Thread(target = testFile)
    testFileThread.start()

    while writeFileThread.is_alive() or testFileThread.is_alive():
        time.sleep(1)

