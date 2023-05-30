from utils import log

from utils import correlate
import random


class Predictor:

    def __init__(self, history_db, orders_db):
        self.history_db = history_db
        self.orders_db = orders_db

    def predict_simple(self, history_points, statistics):
        correlations = []

        means, mins, maxs, distance_means, devianceplus, devianceminus, directions, distances, most_frequent = statistics

        MAX_VALUE = 51

        # highest correlation is always to the next one
        for x in range(5-1):
            y = x + 1
            corr = correlate(directions[x], directions[y])
            correlations.append(corr)

        # count positive directions for first value
        first_direction_up = 0
        first_direction_len = len(directions[0])
        for x in range(first_direction_len):
            if directions[0][x] > 0:
                first_direction_up += 1

        first_weight_up = first_direction_up/first_direction_len
        weights = [first_weight_up]
        weights.extend(correlations)

        # Calculate the first correlation based on the amplitude of the last direction
        rang = (devianceplus[0] - devianceminus[0])
        if rang > abs(directions[0][-1]):
            gg = (abs(directions[0][-1]))/rang
        else:
            gg = (rang)/abs(directions[0][-1])
        reserved_movement = [gg]
        log(f"Reserved-Movement: {reserved_movement}")

        ##
        for x in range(len(weights)):
            log("Correlation: [%d -> %d] %f" % (x, x+1, weights[x]))

        # Guess first value in the mean range of deviance
        # the statistical weight devices if the value goes up or down
        x = 0
        guessedmain = []
        while x < 5:
            # + 1
            weight = weights[x]
            minus = devianceminus[x]
            plus = devianceplus[x]
            value = int(plus - minus)
            previous = reserved_movement[x]*value

            # Calculate weighted sum
            c_1 = random.randint(0, value)*(1-weight)
            c_2 = previous*weight
            rx = c_1 + c_2

            reserved_movement.append(rx/value)
            guessedmain.append(int(rx + minus))
            x += 1

        # Euro vals
        ###########################
        guessdir = 1
        if directions[5][-1] >= 5:
            guessdir = -1

        guessedeuro = []
        guessedeuro.append(int(history_points[5][-1] + means[5]*guessdir) % 13)
        guessedeuro.append(int(history_points[6][-1] + means[5]*guessdir) % 13)

        # sanity checks
        for x in range(len(guessedeuro)):
            if guessedeuro[x] <= 0:
                value = random.randint(1, 12)
                while value in guessedeuro:
                    value = random.randint(1, 12)
                guessedeuro[x] = value

        guessedmain.sort()
        return guessedmain+guessedeuro
