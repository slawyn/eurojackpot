
import os
import sys
import time

import datetime
from datetime import timedelta

from statistics import mean

import numpy as np



import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def log(s):
    '''Logging function

    '''
    print("%s ## %s"%(datetime.datetime.now().time(),s))


def format_date(date):
    '''Format date

    '''
    return date.strftime("%2d-%2m-%4Y")


def correlate(x, y):
    '''Pearson's correlation

    '''
    # Assume len(x) == len(y)
    n = len(x)
    sum_x = float(sum(x))
    sum_y = float(sum(y))
    sum_x_sq = sum(xi*xi for xi in x)
    sum_y_sq = sum(yi*yi for yi in y)
    psum = sum(xi*yi for xi, yi in zip(x, y))
    num = psum - (sum_x * sum_y/n)
    den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
    if den == 0:
        return 0
    return num / den



class Helper:

    def updateFile(file, timestamps, numbers):
        if len(timestamps) != len(numbers):
            log("Error: length of timestamps and numbers don't match ")
        elif len(timestamps)>0:
            loadedFile = open(file,"a")
            for t, ln in zip(timestamps, numbers):
                loadedFile.write("\n"+t)
                for x in ln:
                    loadedFile.write("\t"+x)

            loadedFile.close()

    def loadFile(file):
        loadedFile = open(file,"r")
        data = loadedFile.readlines()
        loadedFile.close()
        return data

    '''
    Load data from file
    '''
    def getNumbersFromData(data):
        lottonumbers = {}
        tickcount = len(data)
        for i in range(tickcount):
            splits = data[i].strip().split("\t")
            entry = [int(splits[1]),int(splits[2]),int(splits[3]),int(splits[4]),int(splits[5]),int(splits[6]),int(splits[7])]
            if splits[0] in lottonumbers:
                lottonumbers[splits[0]].append(entry)
            else:
                lottonumbers[splits[0]] = [entry]

        return lottonumbers


    def checkIfNumbersHappened(title, reference, paramlottonumbers, parameuros):
        frequency = {}
        foundNumbersSet = []

        if len(paramlottonumbers)>0:
            log(title%str(paramlottonumbers))
            for key, arrval in reference.items():
                for values in arrval:
                    arr = [values[0],values[1],values[2],values[3],values[4]]
                    if arr[0] == paramlottonumbers[0] and arr[1] == paramlottonumbers[1] and arr[2] == paramlottonumbers[2] and arr[3] == paramlottonumbers[3]and arr[4] == paramlottonumbers[4]:
                        foundNumbersSet.append("Checked numbers found %s %s"%( key, arr))



            if len(foundNumbersSet)>0:
                for line in foundNumbersSet:
                    log(line)
            else:
                log("Checked numbers didn't happen!")


        # 2 Euro Numbers
        if len(parameuros)>0:
            log(title%str(parameuros))
            for key, arrval in reference.items():
                for values in arrval:
                    arr = [values[5],values[6]]
                    if arr[0] == parameuros[0] and arr[1] == parameuros[1]:
                        foundNumbersSet.append("Checked Euro lottonumbers found %s %s "%(key, arr))

            if len(foundNumbersSet)>0:
                for line in foundNumbersSet:
                    log(line)
            else:
                log("Checked euro numbers didn't happen!")



    def checkForRepetitions(reference):
        lottonumbers = []
        frequency = {}

        mostfreqFromFive = []
        mostfreqFromEuro = []
        frequencyFive = []
        frequencyEuro = []

        # Five
        for key, arrval in reference.items():
            for values in arrval:
                arr = [values[0],values[1],values[2],values[3],values[4]]
                found = False
                for x in range(len(lottonumbers)):
                     if arr[0] == lottonumbers[x][0] and arr[1] == lottonumbers[x][1] and arr[2] == lottonumbers[x][2] and arr[3] == lottonumbers[x][3] and arr[4] == lottonumbers[x][4]:
                        frequency[x] = frequency[x] +1
                        found = True
                        break

                if not found:
                    lottonumbers.append(arr)
                    idx = len(lottonumbers)-1
                    frequency[idx]= 1


        # Iterate through as see if there are more frequent lottonumbers
        maximum = 0
        maxidx = -1
        for l in range(len(lottonumbers)):
            if frequency[l] >maximum:
                maxidx = l
                maximum = frequency[l]

        if maximum>1:
            mostfreqFromFive = lottonumbers[maxidx]
            frequencyFive = frequency[maxidx]

        # Euro numbers
        lottonumbers.clear()
        frequency = {}
        for key, arrval in reference.items():
            for values in arrval:
                arr = [values[5],values[6]]
                found = False

                for x in range(len(lottonumbers)):
                    if arr[0] == lottonumbers[x][0] and arr[1] == lottonumbers[x][1]:
                        frequency[x] = frequency[x] +1
                        found = True
                        break

                if not found:
                    lottonumbers.append(arr)
                    idx = len(lottonumbers)-1
                    frequency[idx]= 1

        maximum = 0
        maxidx = -1
        for l in range(len(lottonumbers)):
            if frequency[l] >maximum:
                maxidx = l
                maximum = frequency[l]

        if maximum>1:
            mostfreqFromEuro = lottonumbers[maxidx]
            frequencyEuro = frequency[maxidx]


        return mostfreqFromFive, frequencyFive, mostfreqFromFive, frequencyEuro



    def performCalculations(title, lottodata, ordersdata):
        points= [[],[],[],[],[],[],[]]
        pointsorders = [[],[],[],[],[],[],[]]
        tickcount = len(lottodata)

        for key, arrval in lottodata.items():
            for x in range(7):
                points[x].append(arrval[0][x])

        for key, arrval in ordersdata.items():
            for x in range(7):
                pointsorders[x].append(arrval[0][x])

        means = []
        mins = []
        maxs = []
        devianceplus = []
        devianceminus = []
        auxdirections = [[],[],[],[],[],[],[]]
        auxdistances = [[],[],[],[],[],[],[]]
        auxmeans = []
        for x in range(7):

            currentdata = points[x]
            means.append(mean(currentdata))
            maxs.append(max(currentdata))
            mins.append(min(currentdata))

            # calculate deviance
            accNumber = 0
            currentmean = means[x]
            frequencyNumber = [0]*(maxs[x]+1)
            frequencyMostFrequent = [0,0]
            for b in range(tickcount):
                if b == 0:
                    auxdistances[x].append(0)
                else:
                    auxdistances[x].append(abs(currentdata[b]-currentdata[b-1]))

                if b == 0:
                    auxdirections[x].append(5)
                elif currentdata[b]>currentdata[b-1]:
                    auxdirections[x].append(10)
                elif currentdata[b]<currentdata[b-1]:
                    auxdirections[x].append(0)
                else:
                    auxdirections[x].append(0)

                accNumber = accNumber + math.pow(currentdata[b] - currentmean, 2)
                frequencyNumber[currentdata[b]] = frequencyNumber[currentdata[b]] +1

                if frequencyNumber[currentdata[b]]>frequencyMostFrequent[0]:
                    frequencyMostFrequent[0] = frequencyNumber[currentdata[b]]
                    frequencyMostFrequent[1] = currentdata[b]

            devianceplus.append(currentmean + math.sqrt(accNumber/tickcount))
            devianceminus.append(currentmean - math.sqrt(accNumber/tickcount))
            auxmeans.append(mean(auxdistances[x]))
            log("%s most frequent:%d with %d times"%(title[x], frequencyMostFrequent[1],frequencyMostFrequent[0]))

        return (points, pointsorders, means, mins, maxs, devianceplus, devianceminus, auxdirections, auxdistances, auxmeans)

    def guessNumbers(basevalues, tipped, auxdirections, auxmeans):
        correlations = [[],[],[],[],[]]
        guessedmain = []
        guessedeuro = []
        # highest correlation is always to the next one
        for x in range(0, 5):
            y = x + 1
            while y<5:
                corr = correlate(auxdirections[x],auxdirections[y])
                correlations[x].append(corr)
                log("Correlation: [%d -> %d] %f"%(x+1, y+1, corr))
                y +=1


        # First value
        guessdir = 1
        if auxdirections[0][-1] >=5:
            guessdir = -1

        guessedmain.append(int(basevalues[0][-1] + auxmeans[0]*guessdir)%50)

        # Other values
        for x in range(1, 5):
            corr = abs(max(correlations[x-1]))
            if corr < 0.5:  # correlation higher than 50 % then we use previous direction
                guessdir = 1
                if auxdirections[x][-1] >=5:
                    guessdir =-1

            #print(guessed)
            guessedmain.append(int(basevalues[x][-1]+auxmeans[x]*guessdir)%50)

        # sanity checks
        for x in range(len(guessedmain)):
            guessedNumber = guessedmain.pop(x)
            if guessedNumber <= 0 or guessedNumber in guessedmain:
                value = random.randint(1, 49)
                while value in guessedmain:
                    value = random.randint(1, 49)
                guessedmain.append(value)
            else:
                guessedmain.append(guessedNumber)

        # Euro values
        guessdir = 1
        if auxdirections[5][-1] >=5:
            guessdir = -1

        guessedeuro.append(int(basevalues[5][-1] + auxmeans[5]*guessdir)%10)
        guessedeuro.append(int(basevalues[6][-1] + auxmeans[5]*guessdir)%10)

        # sanity checks
        for x in range(len(guessedeuro)):
            if guessedeuro[x] <= 0:
                value = random.randint(1, 10)
                while value in guessedeuro:
                    value = random.randint(1, 10)
                guessedeuro[x] = value

        guessedmain.sort()
        return guessedmain+guessedeuro
