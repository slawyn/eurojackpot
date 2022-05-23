from helpers import log

from updater import Updater
import datetime
from datetime import timedelta

import os

from helpers import Helper

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
        timestamps, numbers = Updater.fetch_difference(Helper.loadFile(lotto_database), self.dateStartOfEuroJackpot, self.dateToday)
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
