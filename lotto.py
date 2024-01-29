import os
import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy as np
from utils import log, load_db, update_db, analysis_get_statistics, analysis_find_frequencies, analysis_find_numbers, convert_db_to_points
from updater import fetch_difference_db
from predictor import *
from statistics import mean
import math
from flask import Flask, render_template

VERSION = "Lotto Numbers: ver. 2022-05-22"
FOLDER = "database"
LOTTO_HISTORY_DB = os.path.join(FOLDER, "lottoDB")
LOTTO_ORDERS_DB = os.path.join(FOLDER, "ordersDB")


app = Flask(__name__)


class Statistics:
    def __init__(self, points):
        """Statistics
        """
        n_dim = len(points)
        self.means = []
        self.mins = []
        self.maxs = []
        self.deviance_positive = []
        self.deviance_negative = []

        self.accumulative = [[], [], [], [], [], [], []]
        self.directions = [[], [], [], [], [], [], []]
        self.distances = [[], [], [], [], [], [], []]
        self.distance_means = []

        most_frequent = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        for x in range(n_dim):

            c_data = points[x]
            self.means.append(mean(c_data))
            self.maxs.append(max(c_data))
            self.mins.append(min(c_data))

            # calculate deviance
            accumulator = 0
            c_acc = 0
            frequency_number_count = [0] * (self.maxs[x] + 1)

            m_dim = len(c_data)
            for y in range(m_dim):
                c_acc += c_data[y]
                c_mean = c_acc/(y + 1)
                self.accumulative[x].append(c_mean)

                accumulator += math.pow(c_data[y] - self.means[x], 2)
                frequency_number_count[c_data[y]] = frequency_number_count[c_data[y]] + 1

                # Most frequent numbers
                if frequency_number_count[c_data[y]] > most_frequent[x][0]:
                    most_frequent[x][0] = frequency_number_count[c_data[y]]
                    most_frequent[x][1] = c_data[y]

                # Distances
                if y == 0:
                    self.distances[x].append(0)
                else:
                    self.distances[x].append(abs(c_data[y]-c_data[y-1]))

                # first is zero, the rest are scalars
                if y == 0:
                    self.directions[x].append(0)

                elif c_data[y] > c_data[y-1]:
                    self.directions[x].append(c_data[y]-c_data[y-1])
                else:
                    self.directions[x].append(c_data[y-1] - c_data[y])

            self.distance_means.append(mean(self.distances[x]))
            self.deviance_positive.append(self.means[x] + math.sqrt(accumulator/m_dim))
            self.deviance_negative.append(self.means[x] - math.sqrt(accumulator/m_dim))

    def get_accumulative(self):
        return self.accumulative

    def get_means(self):
        return self.means

    def get_devianceplus(self):
        return self.deviance_positive

    def get_devianceminus(self):
        return self.deviance_negative

    def get_directions(self):
        return self.directions


class Lotto:
    """Main class
    """

    def __init__(self, filename_lotto_db, filename_orders_db):
        self.opt_analyze_find_numbers = []
        self.opt_analyze_find_euronumbers = []
        self.opt_plot_orders_db = False
        self.opt_plot_data = False
        self.opt_plot_aux = False

        # Load database
        self.history_db = load_db(filename_lotto_db)
        self.orders_db = load_db(filename_orders_db)

        # Update database
        difference_db = fetch_difference_db(self.history_db)
        self.history_db = update_db(filename_lotto_db, self.history_db, difference_db)

        # Predictor
        self.predictor = Predictor(self.history_db, self.orders_db)

    def process_arguments(self, args):
        """Process Arguments
        """

        if len(args) > 1:
            parameters = args[1:]
            paramtickcount = len(parameters)

            i = 0
            while i < paramtickcount:
                switch = "".join(parameters[i])
                if switch == "-plot":
                    self.opt_plot_data = True
                    if i+1 < paramtickcount and "".join(parameters[i+1]) == "orders_db":
                        log("Parameter: Plot orders_db")
                        self.opt_plot_orders_db = True
                        i += 2
                    elif i+1 < paramtickcount and "".join(parameters[i+1]) == "aux":
                        log("Parameter: Plot auxilary")
                        self.opt_plot_aux = True
                        i += 2
                    else:
                        log("Parameter: Plot")
                        i += 1

                elif switch == "-ln":
                    if i+5 < paramtickcount:
                        log("Parameter: Check Numbers")
                        self.opt_analyze_find_numbers.append(int(parameters[i+1]))
                        self.opt_analyze_find_numbers.append(int(parameters[i+2]))
                        self.opt_analyze_find_numbers.append(int(parameters[i+3]))
                        self.opt_analyze_find_numbers.append(int(parameters[i+4]))
                        self.opt_analyze_find_numbers.append(int(parameters[i+5]))
                        i += 6

                        if i+1 < paramtickcount:
                            log("Parameter: Check Euro Numbers")
                            self.opt_analyze_find_numbers.append(int(parameters[i]))
                            self.opt_analyze_find_numbers.append(int(parameters[i+1]))
                            i += 2
                else:
                    i = paramtickcount

    def analyze(self):
        """Execute
        """

        history_points = convert_db_to_points(self.history_db)
        orders_points = convert_db_to_points(self.orders_db)

        self.statistics = Statistics(history_points)
        freqs_history = analysis_find_frequencies(self.history_db)
        if (len(freqs_history) > 1):
            log("Repetitions found in history_db: %s" % (str(freqs_history)))

        freqs_orders = analysis_find_frequencies(self.orders_db)
        if (len(freqs_orders) > 1):
            log("Repetitions found in orders_db: %s" % (str(freqs_orders)))

        # Check if numbers are in the database
        if len(self.opt_analyze_find_numbers) > 0:
            found_in_history = analysis_find_numbers(self.history_db, self.opt_analyze_find_numbers)
            found_in_orders = analysis_find_numbers(self.orders_db, self.opt_analyze_find_numbers)
            if (len(found_in_history) > 0):
                log("Checked numbers found in history_db: %s" % (str(found_in_history)))
            else:
                log("Checked numbers are unique for history_db")

            if (len(found_in_orders) > 0):
                log("Checked numbers found in orders_db: %s" % (str(found_in_orders)))
            else:
                log("Checked numbers are unique for orders_db")

        # Try to guess
        else:
            guessed = self.predictor.predict_simple(history_points, self.statistics)
            log("Guessed: %s" % (guessed))
            guessed_in_history = analysis_find_numbers(self.history_db, guessed)
            if (len(guessed_in_history) > 0):
                log("Guessed numbers found in history_db: %s" % (str(guessed_in_history)))
            else:
                log("Guessed numbers are unique for history_db")

            guessed_in_orders = analysis_find_numbers(self.orders_db, guessed)
            if (len(guessed_in_orders) > 0):
                log("Guessed numbers found in orders_db: %s" % (str(guessed_in_orders)))
            else:
                log("Guessed numbers are unique for orders_db")

        # Draw
        if self.opt_plot_data:
            fig, axes = plt.subplots(7, 1, constrained_layout=True)
            fig.canvas.set_window_title(VERSION)
            fig.suptitle(VERSION, fontsize=16)

            # Times
            orderkeys = list(self.orders_db.keys())
            numberkeys = list(self.history_db.keys())

            # when plotting orders_db align on the first date
            orderoffset = 0
            if self.opt_plot_orders_db:
                orderoffset = numberkeys.index(orderkeys[0])

            tickcount = len(numberkeys)-orderoffset
            xticks = range(tickcount)

            # Create plotlines_data
            plotlines_data = [[], [], [], [], [], [], []]
            scatters_order_data = [[], [], [], [], [], [], []]
            plotlines_order_data = [[], [], [], [], [], [], []]

            # Draw
            log("Plotting...")
            titles = ["1. Number", "2. Number", "3. Number", "4. Number", "5. Number", "1. Euro", "2. Euro"]
            for x in range(len(axes)):
                axes[x].margins(0)
                axes[x].set_title(titles[x])
                axes[x].set_ylim([mins[x]-2, maxs[x]+2])
                axes[x].set_xticks(ticks=xticks)
                axes[x].xaxis.set_visible(False)
                plotlines_data[x].append(axes[x].plot([], [], "b-", zorder=+3)[0])

            # Draw specifics, findout which history_db were hit and when
            if self.opt_plot_orders_db:
                hitticks = [[], [], [], [], [], [], []]
                hitsdata = [[], [], [], [], [], [], []]
                colors = [[], [], [], [], [], [], []]
                sizes = [[], [], [], [], [], [], []]
                cmap = plt.cm.get_cmap('RdYlBu')

                for x in range(len(axes)):
                    axes[x].fill_between(xticks[:], [devianceplus[x]] * (tickcount), [devianceminus[x]] * (tickcount), facecolor='green', alpha=0.45, zorder=3)
                    axes[x].plot(xticks[:], [means[x]]*(tickcount), zorder=3)

                def animate(i):
                    out = []
                    if i < tickcount:
                        for y in range(len(plotlines_data)):
                            plotlines_data[y][0].set_xdata(xticks[:i+1])
                            plotlines_data[y][0].set_ydata(history_points[y][orderoffset:orderoffset+i+1])

                        key = numberkeys[i+orderoffset]
                        if key in orderkeys:
                            realdata = self.history_db[key][0]
                            for y in range(len(realdata)):
                                for j in range(len(self.orders_db[key])):
                                    mydata = self.orders_db[key][j]
                                    if j >= len(hitticks[y]):      # create if not present
                                        hitticks[y].append([])
                                        hitsdata[y].append([])
                                        colors[y].append(np.array([]))
                                        sizes[y].append(np.array([]))
                                        scatters_order_data[y].append(axes[y].scatter([], [], c="red", s=50, cmap=cmap, marker="o", vmin=0, vmax=10))

                                        if j == 0:
                                            plotlines_order_data[y].append(axes[y].plot([], [], "r-")[0])
                                        else:
                                            plotlines_order_data[y].append(axes[y].plot([], [], "r*")[0])

                                    # fill datasets
                                    if mydata[y] == realdata[y]:
                                        hitticks[y][j].append(xticks[i])
                                        hitsdata[y][j].append(mydata[y])
                                        sizes[y][j] = np.append(sizes[y][j], [60])
                                    else:
                                        hitticks[y][j].append(xticks[i])
                                        hitsdata[y][j].append(mydata[y])
                                        sizes[y][j] = np.append(sizes[y][j], [20])

                                    # colors[y][j] = np.append(colors[y][j],[abs(mydata[y]-realdata[y])])
                                    scatters_order_data[y][j].set_offsets(np.c_[hitticks[y][j], hitsdata[y][j]])
                                    # scatters_order_data[y][j].set_array(colors[y][j])
                                    scatters_order_data[y][j].set_sizes(sizes[y][j])
                                    plotlines_order_data[y][j].set_xdata(hitticks[y][j])
                                    plotlines_order_data[y][j].set_ydata(hitsdata[y][j])

                    # Draw
                    for y in range(len(plotlines_data)):
                        out.append(plotlines_data[y][0])
                        for j in range(len(scatters_order_data[y])):
                            out.append(scatters_order_data[y][j])
                            out.append(plotlines_order_data[y][j])

                    return out

                ani = animation.FuncAnimation(fig, animate, repeat=False, interval=0, blit=True)

            # normal plot
            else:
                for x in range(len(axes)):
                    axes[x].fill_between(xticks[:], [devianceplus[x]]*(tickcount), [devianceminus[x]]*(tickcount), facecolor='green', alpha=0.45, zorder=3)
                    axes[x].plot(xticks[:], [means[x]]*(tickcount), zorder=3)

                def animateData(i):
                    out = []
                    for y in range(len(plotlines_data)):
                        plotlines_data[y][0].set_xdata(xticks[:i+1])
                        plotlines_data[y][0].set_ydata(history_points[y][:i+1])
                        out.append(plotlines_data[y][0])
                    return out

                ani = animation.FuncAnimation(fig, animateData, repeat=False, interval=0, blit=True)
            mng = plt.get_current_fig_manager()
            mng.full_screen_toggle()
            plt.show()


@app.route('/')
def index():
    points = convert_db_to_points(lt.history_db)
    orders = convert_db_to_points(lt.orders_db)

    accumulative = lt.statistics.get_accumulative()
    return render_template('index.html',
                           range1=[int(lt.statistics.get_devianceminus()[0]), int(lt.statistics.get_devianceplus()[0])],
                           range2=[int(lt.statistics.get_devianceminus()[1]), int(lt.statistics.get_devianceplus()[1])],
                           range3=[int(lt.statistics.get_devianceminus()[2]), int(lt.statistics.get_devianceplus()[2])],
                           range4=[int(lt.statistics.get_devianceminus()[3]), int(lt.statistics.get_devianceplus()[3])],
                           range5=[int(lt.statistics.get_devianceminus()[4]), int(lt.statistics.get_devianceplus()[4])],
                           x1_values=list(lt.history_db.keys()),
                           y1_accumulative1=accumulative[0],
                           y1_accumulative2=accumulative[4],
                           y1_values1=points[0],
                           y1_values2=points[1],
                           y1_values3=points[2],
                           y1_values4=points[3],
                           y1_values5=points[4],
                           y2_values1=points[5],
                           y2_values2=points[6],
                           x2_values=list(lt.orders_db.keys()),
                           z2_values=orders[0]
                           )


####################################################
if __name__ == "__main__":
    try:
        lt = Lotto(LOTTO_HISTORY_DB, LOTTO_ORDERS_DB)
        # lt.process_arguments(sys.argv)
        lt.analyze()

        app.run(debug=True)
    except Exception as e:
        log(e,)
