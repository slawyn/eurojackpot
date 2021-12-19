import os
import os
import sys
import time

import datetime
from datetime import timedelta

from statistics import mean

import numpy as np

import requests
from bs4 import  BeautifulSoup

import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation



'''
log print
'''
def log(s):
    print("%s ## %s"%(datetime.datetime.now().time(),s))

'''
format date
'''
def formatDate(date):
    return date.strftime("%2d-%2m-%4Y")

'''
pearson's correlation
'''
def correlate(x, y):
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



'''
Updater
'''
class Updater:
    months = ['','Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez',]
    website = 'https://www.lottoland.com/eurojackpot/zahlen-quoten/'
    monthsID = "dateSelect-selectDrawingsForYear-drawingsForYear"
    yearsID ="dateSelect-selectYearAndDrawing-drawingYearRange"

    dateFormatForRequest = "%02d-%02d-%4d"

    lottoNumbersID = "l-results-lottonumbers js-results-lottonumbers"
    lottoNumbersNewId = "ll-lottery-balls"

    def checkForUpdates(date):
        update = False
        response = requests.get(Updater.website)
        parsedHTML = BeautifulSoup(response.text,"html.parser")

        yrs = parsedHTML.find('select',attrs={'id':Updater.yearsID})
        mts = parsedHTML.find('select',attrs={'id':Updater.monthsID})

        if yrs != None and mts != None:
            entriesYears = yrs.text
            entriesMonths = mts.text
            try:
                entriesSplit = entriesMonths.split("\n")[1].replace(",",".")
                oneEntry = entriesSplit.split(".")
                day = oneEntry[1].strip()
                month = oneEntry[2].strip()
                year = entriesYears.split("\n")[0].strip()

                for i in range(len(Updater.months)):
                    if month == Updater.months[i]:
                        pageDate = datetime.datetime(int(year),int(i),int(day),12,0)
                        if date <pageDate:
                            update = True
                            break
            except Exception as e:
                 log("Problem:couldn't parse months and years ")
                 log(e)
        else:
            log("Problem:couldn't get info from the page")
        return update


    def fetchLottoNumbers(srdate):
        lottoNumbers = None
        try:
            response = requests.get(Updater.website + srdate)
            parsedHTML = BeautifulSoup(response.text,"html.parser")
            lottos = parsedHTML.find('div',attrs={'class':Updater.lottoNumbersID})
            if lottos != None and len(lottos.text.split()) == 7:
                lottoNumbers = lottos.text.strip().split()

            # New Data Container on the website since 01.02.2021
            else:
                lottos = parsedHTML.find(Updater.lottoNumbersNewId)

                # Integer arrays
                nums = eval(lottos["numbers"] )
                nums.extend(eval(lottos["extranumbers"]))

                if len(nums) == 7:
                    lottoNumbers = list(map(str,nums))

        except Exception as e:
            log(e)

        return lottoNumbers


    def fetchDifference(db, startdate, today):
        timestamps = []
        numbers = []

        requestDate = startdate #self.dateStartOfEuroJackpot-timedelta(days=7)
        if len(db) > 0:
            lastLine = db[len(db)-1]
            lastDate = lastLine.split("\t")[0]
            day, month, year= lastDate.split("-")
            requestDate = datetime.datetime(int(year),int(month),int(day), 12, 0) + timedelta(days=7)

        # Check for updates
        updateRequired = Updater.checkForUpdates(requestDate)
        if updateRequired:

            log("Updating database... ")
            while requestDate < today:
                    srdate = Updater.dateFormatForRequest%(requestDate.day,requestDate.month,requestDate.year)
                    ln = Updater.fetchLottoNumbers(srdate)

                    if ln != "":
                        timestamps.append(srdate)
                        numbers.append(ln)

                        log(srdate+"\t"+str(ln))
                    else:
                        log("Problem: wrong lotto lottonumbers for %s"%(srdate))
                        break

                    requestDate = requestDate + timedelta(days=7)

        else:
            log("Database is already up-to-date")


        return timestamps, numbers

'''
Main class
'''
class Lotto:

    def __init__(self, version):
        self.paramCheckNumbers = []
        self.paramCheckEuroNumbers = []
        self.paramPlotOrders = False
        self.paramPlotData = False
        self.paramPlotAux = False
        self.version = version

        self.dateStartOfEuroJackpot = datetime.datetime(2012, 3, 23, 12, 00)
        self.dateToday= datetime.datetime.today()


    def processParameters(self, args):
        if len(args) > 1:
            parameters = args[1:]
            paramtickcount = len(parameters)

            i = 0
            while i< paramtickcount:
                switch = "".join(parameters[i])
                if switch == "-plot":
                    self.paramPlotData = True
                    if i+1<paramtickcount and "".join(parameters[i+1]) == "orders":
                        log("Parameter: Plot orders")
                        self.paramPlotOrders = True
                        i +=2
                    elif i+1<paramtickcount and "".join(parameters[i+1]) == "aux":
                        log("Parameter: Plot auxilary")
                        self.paramPlotAux = True
                        i +=2
                    else:
                        log("Parameter: Plot")
                        i +=1

                elif switch == "-ln":
                    if i+5<paramtickcount:
                        log("Parameter: Check Numbers")
                        self.paramCheckNumbers.append(int(parameters[i+1]))
                        self.paramCheckNumbers.append(int(parameters[i+2]))
                        self.paramCheckNumbers.append(int(parameters[i+3]))
                        self.paramCheckNumbers.append(int(parameters[i+4]))
                        self.paramCheckNumbers.append(int(parameters[i+5]))
                        i += 6

                        if i+1 <paramtickcount:
                            log("Parameter: Check Euro Numbers")
                            self.paramCheckEuroNumbers.append(int(parameters[i]))
                            self.paramCheckEuroNumbers.append(int(parameters[i+1]))
                            i +=2
                else:
                    i = paramtickcount

    def execute(self, args, lotto_database, tips_database):
        self.processParameters(args)

        if not os.path.exists(lotto_database):
            with open(lotto_database, 'w'): pass

        if not os.path.exists(tips_database):
            with open(tips_database, 'w'): pass

        # Check for updates and write them into the database
        timestamps, numbers = Updater.fetchDifference(Helper.loadFile(lotto_database), self.dateStartOfEuroJackpot, self.dateToday)
        Helper.updateFile(lotto_database, timestamps, numbers)

        # Load numbers
        lottonumbers = Helper.getNumbersFromData(Helper.loadFile(lotto_database))
        orders = Helper.getNumbersFromData(Helper.loadFile(tips_database))

        # Analysis: Repetitions
        # Check for repititions and if lottonumbers already happened
        #############################################################
        five,freqfive, euro, freqeuro = Helper.checkForRepetitions(lottonumbers)
        if len(five)>0:
            log("Most frequent Numbers in History:%s with %d"%(five,freqfive))
        if len(euro)>0:
            log("Most frequent Numbers in Orders:%s with %d"%(euro,freqeuro))

        five,freqfive, euro, freqeuro = Helper.checkForRepetitions(orders)
        if len(five)>0:
            log("Most frequent Numbers in History:%s with %d"%(five,freqfive))
        if len(euro)>0:
            log("Most frequent Numbers in Orders:%s with %d"%(euro,freqeuro))

        # Analysis: Repetitions of chosen numbers
        title = "-> Checking if %s already happened in #lottoDB# "
        Helper.checkIfNumbersHappened(title, lottonumbers, self.paramCheckNumbers, self.paramCheckEuroNumbers)

        title = "-> Checking if %s were already used in #ordersDB# "
        Helper.checkIfNumbersHappened(title, orders, self.paramCheckNumbers, self.paramCheckEuroNumbers)

        titles = ["1. Number","2. Number","3. Number","4. Number","5. Number","1. Euro","2. Euro"]
        data, ordersdata, means, mins, maxs, devianceplus, devianceminus, auxdirections, auxdistances, auxmeans = Helper.performCalculations(titles, lottonumbers, orders)
        guessed = Helper.guessNumbers(data, ordersdata, auxdirections, auxmeans)

        log("->Guessed lotto numbers: %s"%(str(guessed)))

        title = "-> Checking if %s already happened in #lottoDB# "
        Helper.checkIfNumbersHappened(title, lottonumbers, guessed[:5], guessed[5:])

        title = "-> Checking if %s already happened in #ordersDB# "
        Helper.checkIfNumbersHappened(title, orders, guessed[:5], guessed[5:])

        ## Plotting
        ##------------------------
        if self.paramPlotData:
            fig, axes = plt.subplots(7, 1, constrained_layout=True)
            fig.canvas.set_window_title(self.version)
            fig.suptitle(self.version, fontsize=16)

            # Times
            orderkeys  = list(orders.keys())
            numberkeys = list(lottonumbers.keys())

            # when plotting orders align on the first date
            orderoffset = 0
            if self.paramPlotOrders:
                orderoffset = numberkeys.index(orderkeys[0])

            tickcount = len(numberkeys)-orderoffset
            xticks = range(tickcount)

            # Create plotlinesData
            plotlinesData = [[],[],[],[],[],[],[]]
            scattersMyData =  [[],[],[],[],[],[],[]]
            plotlinesMyData =  [[],[],[],[],[],[],[]]

            # Draw
            log("Plotting...")
            for x in range(len(axes)):
                axes[x].margins(0)
                axes[x].set_title(titles[x])
                axes[x].set_ylim([mins[x]-2,maxs[x]+2])
                axes[x].set_xticks(ticks=xticks)
                axes[x].xaxis.set_visible(False)
                plotlinesData[x].append(axes[x].plot([],[],"b-", zorder=+3)[0])

            # Draw specifics, findout which lottonumbers were hit and when
            if self.paramPlotOrders:
                hitticks = [[],[],[],[],[],[],[]]
                hitsdata = [[],[],[],[],[],[],[]]
                colors = [[],[],[],[],[],[],[]]
                sizes = [[],[],[],[],[],[],[]]
                cmap = plt.cm.get_cmap('RdYlBu')

                for x in range(len(axes)):
                    axes[x].fill_between(xticks[:],[devianceplus[x]]*(tickcount),[devianceminus[x]]*(tickcount),facecolor='green', alpha=0.45,zorder=3)
                    axes[x].plot(xticks[:], [means[x]]*(tickcount), zorder=3)

                def animate(i):
                    out = []
                    if i <tickcount:
                        for y in range(len(plotlinesData)):
                            plotlinesData[y][0].set_xdata(xticks[:i+1])
                            plotlinesData[y][0].set_ydata(data[y][orderoffset:orderoffset+i+1])

                        key = numberkeys[i+orderoffset]
                        if key in orderkeys:
                            realdata = lottonumbers[key][0]
                            for y in range(len(realdata)):
                                for j in range(len(orders[key])):
                                    mydata = orders[key][j]
                                    if j>=len(hitticks[y]):      # create if not present
                                        hitticks[y].append([])
                                        hitsdata[y].append([])
                                        colors[y].append(np.array([]))
                                        sizes[y].append(np.array([]))
                                        scattersMyData[y].append(axes[y].scatter([],[], c="red", s=50, cmap=cmap, marker="o",vmin=0, vmax=10))

                                        if j==0:
                                            plotlinesMyData[y].append(axes[y].plot([],[], "r-")[0])
                                        else:
                                            plotlinesMyData[y].append(axes[y].plot([],[], "r*")[0])

                                    # fill datasets
                                    if mydata[y] == realdata[y]:
                                        hitticks[y][j].append(xticks[i])
                                        hitsdata[y][j].append(mydata[y])
                                        sizes[y][j]=np.append(sizes[y][j], [60])
                                    else:
                                        hitticks[y][j].append(xticks[i])
                                        hitsdata[y][j].append(mydata[y])
                                        sizes[y][j]=np.append(sizes[y][j], [20])

                                    #colors[y][j] = np.append(colors[y][j],[abs(mydata[y]-realdata[y])])
                                    scattersMyData[y][j].set_offsets(np.c_[hitticks[y][j], hitsdata[y][j]])
                                    #scattersMyData[y][j].set_array(colors[y][j])
                                    scattersMyData[y][j].set_sizes(sizes[y][j])
                                    plotlinesMyData[y][j].set_xdata(hitticks[y][j])
                                    plotlinesMyData[y][j].set_ydata(hitsdata[y][j])

                    # Draw
                    for y in range(len(plotlinesData)):
                        out.append(plotlinesData[y][0])
                        for j in range(len(scattersMyData[y])):
                            out.append(scattersMyData[y][j])
                            out.append(plotlinesMyData[y][j])

                    return out

                ani = animation.FuncAnimation(fig, animate, repeat = False, interval=0, blit = True)
            elif self.paramPlotAux:
                for x in range(len(axes)):
                    axes[x].fill_between(xticks[:],  [0]*(tickcount), [auxmeans[x]]*(tickcount), zorder=3)
                    axes[x].plot(xticks[:], auxdirections[x], color="red",zorder=3)

                def animateAux(i):
                    out = []
                    for y in range(len(plotlinesData)):
                        plotlinesData[y][0].set_xdata(xticks[:i+1])
                        plotlinesData[y][0].set_ydata(auxdistances[y][:i+1])
                        out.append(plotlinesData[y][0])
                    return out

                ani = animation.FuncAnimation(fig, animateAux, repeat = False, interval=0, blit = True)
            else:
                for x in range(len(axes)):
                    axes[x].fill_between(xticks[:],[devianceplus[x]]*(tickcount),[devianceminus[x]]*(tickcount),facecolor='green', alpha=0.45,zorder=3)
                    axes[x].plot(xticks[:], [means[x]]*(tickcount), zorder=3)


                def animateData(i):
                    out = []
                    for y in range(len(plotlinesData)):
                        plotlinesData[y][0].set_xdata(xticks[:i+1])
                        plotlinesData[y][0].set_ydata(data[y][:i+1])
                        out.append(plotlinesData[y][0])
                    return out

                ani = animation.FuncAnimation(fig, animateData, repeat = False, interval=0, blit = True)
            mng = plt.get_current_fig_manager()
            mng.full_screen_toggle()
            plt.show()


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
