#Vasileios Gewrgoulas
#AM 2954

import time
import ast
import sys

tr = ''

runtimes = [0 for i in range(0, 4)]
shouldPrint = True

transactions = []
queries = []

sigfile = []
bitslice = []
invFile = []

maxi = -1

#########################################helpers######################################

def domain():
    global transactions, maxi

    for t in transactions:
        maxt = max(t)
        if maxi < maxt:
            maxi = maxt

def mapper(lst):

    maxItem = max(lst)
    bitList = [str(0) for i in range(0, maxItem + 1)]
    for i in lst:
        bitList[maxItem - i] = str(1)
    return(int(''.join(bitList), 2))

def checkSigs(qsig, tsig):

    if qsig & ~tsig == 0:
        return True
    return False

def intersection(l1, l2):

    temp = []
    lp = rp = 0
    while lp < len(l1) and rp < len(l2):
        if l1[lp] < l2[rp]:
            lp += 1
        elif l1[lp] > l2[rp]:
            rp += 1
        else:
            temp.append(l2[rp])                                                                  
            rp += 1
            lp += 1
    return temp

#############################################files#################################

def exactSigFile():
    global transactions, sigfile

    out = ''
    try:
        out = open('sigfile.txt', 'w')
    except:
        print('file could not be opened, aborting operation')
        exit(1)

    for t in transactions:
        signature = mapper(t)
        sigfile.append(signature)
        out.write(str(signature) + '\n')
    out.close()

def bitsliceSig():
    global sigfile, maxi, bitslice

    out = ''
    try:
        out = open('bitslice.txt', 'w')
    except:
        print('file could not be opened')
        exit(1)

    for i in range(0, maxi + 1):
        sig = mapper([i])
        bitmap = 0
        for s in range(0, len(sigfile)):
            if checkSigs(sig, sigfile[s]):
                bitmap += pow(2, s)
        bitslice.append(bitmap)
        out.write(str(i) + ': ' + str(bitmap) + '\n')
    out.close()

def invertedFile():
    global transactions, invFile, maxi

    out = ''
    try:
        out = open('invfile.txt', 'w')
    except:
        print('file could not be opened')
        exit(1)

    for i in range(0, maxi + 1):
        result = []
        for t in range(0, len(transactions)):
            if i in transactions[t]:
                result.append(t)
        invFile.append(result)
        out.write(str(i) + ': ' + str(result) + '\n')
    out.close()

#####################################################################

#transactions.txt queries.txt -1 -1

def naiveQueries(qid):
    global transactions, queries, runtimes

    start = time.time()
    ids = []
    for i in range(0, len(transactions)):
        if all(e in transactions[i] for e in queries[qid]):
            ids.append(i)
    runtimes[0] += time.time() - start
    printResults(ids, 0, 'naive')

def esfQueries(qid):
    global sigfile, queries

    ids = []
    start = time.time()
    qsig = mapper(queries[qid])
    for i in range(0, len(sigfile)):
        if checkSigs(qsig, sigfile[i]):
            ids.append(i)
    runtimes[1] += time.time() - start
    printResults(ids, 1, 'exact sig file')

def sliceQueries(qid):
    global bitslice, queries

    start = time.time()
    result = bitslice[queries[qid][0]]
    for i in queries[qid][1:]:
        result = result & bitslice[i]
    slice = bin(result)
    ids = []
    j = 0
    for i in slice[::-1]:
        if i == 'b':
            break
        if i == '1':
            ids.append(j)
        j += 1
    runtimes[2] += time.time() - start
    printResults(ids, 2, 'bitslice file')

def invQueries(qid):
    global queries, invFile

    start = time.time()
    ids = invFile[queries[qid][0]]
    for i in queries[qid][1:]:
        ids = intersection(ids, invFile[i])
    runtimes[3] += time.time() - start
    printResults(list(ids), 3, 'inv file')

def invQueries2(qid):
    global queries, invFile

    start = time.time()
    tr = [invFile[i] for i in queries[qid]]
    ids = set(tr[0]).intersection(*tr)
    runtimes[3] += time.time() - start
    printResults(list(ids), 3, 'inv file')

####################################################################################

def printResults(ids, index, method):
    global shouldPrint, runtimes

    if shouldPrint:
        print(method + ' method results: ')
        print(ids)
        print(method + ' runtime: ' + str(runtimes[index]))

def methodPicker(qid, method):

    if method == 0:
        naiveQueries(qid)
    elif method == 1:
        esfQueries(qid)
    elif method == 2:
        sliceQueries(qid)
    elif method == 3:
        #invQueries(qid)
        invQueries2(qid)
    elif method == -1:
        naiveQueries(qid)
        esfQueries(qid)
        sliceQueries(qid)
        #invQueries(qid)
        invQueries2(qid)

def queryPicker(q, method):
    global queries, shouldPrint  

    if q == -1:
        shouldPrint = False
        for i in range(0, len(queries)):
            methodPicker(i, method)
    else:
        methodPicker(q, method)

q = ''
tr = ''
try:
    tr = open(sys.argv[1], 'r')
    q = open(sys.argv[2], 'r')
except:
    exit(1)

query = q.readline().rstrip("\n")
while query:
    queries.append(ast.literal_eval(query))
    query = q.readline().rstrip("\n")
q.close()

t = tr.readline().rstrip("\n")
while t:
    transactions.append(ast.literal_eval(t))
    t = tr.readline().rstrip("\n")
tr.close()

domain()
exactSigFile()
bitsliceSig()
invertedFile()   #qid, method
queryPicker(int(sys.argv[3]), int(sys.argv[4]))

if not shouldPrint:
    if runtimes[0] > 0:
        print('naive runtime: ' + str(runtimes[0]))
    if runtimes[1] > 0:
        print('exact sig runtime: ' + str(runtimes[1]))
    if runtimes[2] > 0:
        print('slice file runtime: ' + str(runtimes[2]))
    if runtimes[3] > 0:
        print('inv file runtime: ' + str(runtimes[3]))


