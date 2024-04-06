
import os


import datetime

from statistics import mean

import math


def log(s):
    """Logging function
    """
    print("%s ## %s" % (datetime.datetime.now().time(), s))


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
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                splits = line.strip().split(" ")
                entry = [int(splits[1]), int(splits[2]), int(splits[3]), int(splits[4]), int(splits[5]), int(splits[6]), int(splits[7])]
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
            database[t] = [numbers]
            f.write("\n" + t)
            for n in numbers:
                f.write(" " + str(n))

    return database

def convert_db_to_points_extended(keys, database):
    '''Extend points
    '''
    points = [[], [], [], [], [], [], []] 
    for key in keys:
        if key in database:
            numbers = database[key][0]
            for x in range(len(numbers)):
                points[x].append(numbers[x])
        else:
            for x in range(len(points)):
                points[x].append('null')
    return points

def convert_db_to_points(database):
    """Convert db dictionary to list of points for each number
    """
    points = [[], [], [], [], [], [], []]
    for key, data in database.items():
        numbers = data[0]
        for x in range(len(numbers)):
            points[x].append(numbers[x])

    return points


def analysis_find_matched(to_match, tips):
    '''Find tips that matched the lotto numbers
    '''
    matched = {}
    for key, values in tips.items():
        tipped = []
        for numbers in values:
            tipped.extend(numbers)
        
        if key not in to_match:
            print(f"WARNING: ordered key {key} not yet in history")
            
        else:
            lotto5, lotto2= tipped[:5], tipped[5:]
            history5, history2 = to_match[key][0][:5],to_match[key][0][5:]


            incorrect5 = set(history5) - set(lotto5)
            correct5 = set(history5) - incorrect5

            incorrect2 = set(history2) - set(lotto2)
            correct2 = set(history2) - incorrect2

            matched[key] = [[history5, list(correct5), list(incorrect5)],[history2, list(correct2), list(incorrect2)]]
    return matched 

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
                arg_five_or_seven_numbers = [vals[0], vals[1], vals[2], vals[3], vals[4]]
                arg_euro_numbers = [vals[5], vals[6]]

                # Find maximumg between fives
                five_key = "%d-%d-%d-%d-%d" % (vals[0], vals[1], vals[2], vals[3], vals[4])
                if five_key in frequency_five:
                    frequency_five[five_key] += 1
                else:
                    frequency_five[five_key] = 1

                if frequency_five[five_key] > max_five:
                    max_five = frequency_five[five_key]
                    max_freq_five = frequency_five[five_key]
                    max_combi_five = arg_five_or_seven_numbers

                # Find maximum between euros
                euro_key = "%d-%d" % (vals[5], vals[6])
                if euro_key in frequency_euro:
                    frequency_euro[euro_key] += 1
                else:
                    frequency_euro[euro_key] = 1

                if frequency_euro[euro_key] > max_euro:
                    max_euro = frequency_euro[euro_key]
                    max_freq_euro = frequency_euro[euro_key]
                    max_combi_euro = arg_euro_numbers

    except Exception as e:
        log(e)

    return max_combi_five, max_freq_five, max_combi_euro, max_freq_euro


def analysis_find_numbers(database, arg_five_or_seven_numbers):
    """Find numbers
    """
    found_five = {}
    found_euro = {}

    for key, numbers in database.items():
        for vals in numbers:
            if len(arg_five_or_seven_numbers) >= 5:
                numbers_five = [vals[0], vals[1], vals[2], vals[3], vals[4]]
                if numbers_five[0] == arg_five_or_seven_numbers[0] and numbers_five[1] == arg_five_or_seven_numbers[1] and numbers_five[2] == arg_five_or_seven_numbers[2] and numbers_five[3] == arg_five_or_seven_numbers[3] and numbers_five[4] == arg_five_or_seven_numbers[4]:
                    found_five[key] = numbers_five

                if len(arg_five_or_seven_numbers) == 7:
                    numbers_euro = [vals[5], vals[6]]
                    if numbers_euro[0] == arg_five_or_seven_numbers[5] and numbers_euro[1] == arg_five_or_seven_numbers[6]:
                        found_euro[key] = numbers_euro

    return found_five, found_euro


def analysis_get_statistics(points):
    """Statistics
    """
    n_dim = len(points)
    means = []
    mins = []
    maxs = []
    deviance_positive = []
    deviance_negative = []

    accumulative = [[], [], [], [], [], [], []]
    directions = [[], [], [], [], [], [], []]
    distances = [[], [], [], [], [], [], []]
    distance_means = []

    most_frequent = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    for x in range(n_dim):

        c_data = points[x]
        means.append(mean(c_data))
        maxs.append(max(c_data))
        mins.append(min(c_data))

        # calculate deviance
        accumulator = 0
        c_acc = 0
        frequency_number_count = [0] * (maxs[x] + 1)

        m_dim = len(c_data)
        for y in range(m_dim):
            c_acc += c_data[y]
            c_mean = c_acc/(y + 1)
            accumulative[x].append(c_mean)

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

            # first is zero, the rest are scalars
            if y == 0:
                directions[x].append(0)

            elif c_data[y] > c_data[y-1]:
                directions[x].append(c_data[y]-c_data[y-1])
            else:
                directions[x].append(c_data[y-1] - c_data[y])

        distance_means.append(mean(distances[x]))
        deviance_positive.append(means[x] + math.sqrt(accumulator/m_dim))
        deviance_negative.append(means[x] - math.sqrt(accumulator/m_dim))

    return (means, mins, maxs, distance_means, deviance_positive, deviance_negative, directions, distances, most_frequent, accumulative)
