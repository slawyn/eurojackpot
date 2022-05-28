
import os


import datetime

from statistics import mean

import math


def log(s):
    """Logging function
    """
    print("%s ## %s"%(datetime.datetime.now().time(),s))


def format_date(date):
    """Format date
    """
    return date.strftime("%2d-%2m-%4Y")


def correlate(x, y):
    """Pearson's correlation
    """
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


def load_db(filename):
    """Load DB file
    """
    database = {}
    if not os.path.exists(filename):
        with open(filename, 'w'):
            pass
    else:
        with open(filename,"r") as f:
            lines = f.readlines()
            for line in lines:
                splits = line.strip().split(" ")
                entry = [int(splits[1]),int(splits[2]),int(splits[3]),int(splits[4]),int(splits[5]),int(splits[6]),int(splits[7])]
                if splits[0] in database:
                    database[splits[0]].append(entry)
                else:
                    database[splits[0]] = [entry]
    return database


def update_db(filename, database, difference):
    """Update DB file
    """

    with open(filename, "a") as f:
        for t, numbers in zip(difference[0], difference[1]):
            database[t] = []
            f.write("\n" + t)
            for n in numbers:
                database[t].append(int(n))
                f.write(" " + n)

    return database


def convert_db_to_points(database):
    """Convert db dictionary to list of points for each number
    """
    points = [[],[],[],[],[],[],[]]
    for key, data in database.items():
        numbers = data[0]
        for x in range(len(numbers)):
            points[x].append(numbers[x])

    return points


def analysis_find_frequencies(database):
    """Find most frequent number combinations
    """

    frequency_five = {}
    max_combi_five = []
    max_freq_five = []
    max_five = 0

    frequency_euro = {}
    max_combi_euro = []
    max_freq_euro = []
    max_euro = 0

    try:
        #
        for key, numbers in database.items():
            for vals in numbers:
                arg_five_or_seven_numbers = [vals[0], vals[1], vals[2],vals[3],vals[4]]
                arg_euro_numbers = [vals[5],vals[6]]

                # Find maximumg between fives
                five_key = "%d-%d-%d-%d-%d"%(vals[0], vals[1], vals[2], vals[3], vals[4])
                if five_key in frequency_five:
                    frequency_five[five_key] +=1
                else:
                    frequency_five[five_key] = 1

                if frequency_five[five_key] > max_five:
                    max_five = frequency_five[five_key]
                    max_freq_five = frequency_five[five_key]
                    max_combi_five = arg_five_or_seven_numbers

                # Find maximum between euros
                euro_key = "%d-%d"%(vals[5], vals[6])
                if euro_key in frequency_euro:
                    frequency_euro[euro_key] +=1
                else:
                    frequency_euro[euro_key] = 1

                if frequency_euro[euro_key] > max_euro:
                    max_euro = frequency_euro[euro_key]
                    max_freq_euro = frequency_euro[euro_key]
                    max_combi_euro = arg_euro_numbers

    except Exception as e:
        log(e)

    return max_combi_five, max_freq_five, max_combi_euro, max_freq_euro


def analysis_find_numbers( database, arg_five_or_seven_numbers):
    """Find numbers
    """
    found_five = {}
    found_euro = {}

    for key, numbers in database.items():
        for vals in numbers:
            if len(arg_five_or_seven_numbers) >= 5:
                numbers_five = [vals[0],vals[1],vals[2],vals[3],vals[4]]
                if numbers_five[0] == arg_five_or_seven_numbers[0] and numbers_five[1] == arg_five_or_seven_numbers[1] and numbers_five[2] == arg_five_or_seven_numbers[2] and numbers_five[3] == arg_five_or_seven_numbers[3] and numbers_five[4] == arg_five_or_seven_numbers[4]:
                    found_five[key] = numbers_five

                if len(arg_five_or_seven_numbers) == 7:
                    numbers_euro = [vals[5], vals[6]]
                    if numbers_euro[0] == arg_five_or_seven_numbers[5] and numbers_euro[1] == arg_five_or_seven_numbers[6]:
                        found_euro[key] = numbers_euro

    return found_five, found_euro


def analysis_get_statistics( points):
    """Statistics
    """

    point_count   = len(points)

    means = []
    mins = []
    maxs = []
    deviance_positive = []
    deviance_negative = []

    directions = [[], [], [], [], [], [], []]
    distances = [[], [], [], [], [], [], []]
    distance_means = []

    most_frequent = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    for x in range(7):

        c_data = points[x]
        means.append(mean(c_data))
        maxs.append(max(c_data))
        mins.append(min(c_data))

        # calculate deviance
        accumulator = 0
        frequency_number_count = [0] * (maxs[x] + 1)

        for y in range(point_count):
            accumulator += math.pow(c_data[y] - means[x], 2)
            frequency_number_count[c_data[y]] = frequency_number_count[c_data[y]] + 1

            # Most frequent numbers
            if frequency_number_count[c_data[y]] > most_frequent[x][0]:
                most_frequent[x][0] = frequency_number_count[c_data[y]]
                most_frequent[x][1] = c_data[y]

            # Distances
            if y == 0:
                distances[x].append(0)
            else:
                distances[x].append(abs(c_data[y]-c_data[y-1]))

            #
            if y == 0:
                directions[x].append(5)
            elif c_data[y] > c_data[y-1]:
                directions[x].append(10)
            elif c_data[y] < c_data[y-1]:
                directions[x].append(0)
            else:
                directions[x].append(0)

        distance_means.append(mean(distances[x]))

        deviance_positive.append(means[x] + math.sqrt(accumulator/point_count))
        deviance_negative.append(means[x] - math.sqrt(accumulator/point_count))

    return (means, mins, maxs, distance_means, deviance_positive, deviance_negative, directions, distances, most_frequent)