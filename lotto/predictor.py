import random

from .utils import log, correlate


class Predictor:

    def __init__(self, history_db, orders_db):
        self.history_db = history_db
        self.orders_db = orders_db

    def predict_simple(self, history_points, statistics):
        correlations = []

        means = statistics.get_means()
        distance_means = statistics.get_distance_means()
        devianceplus = statistics.get_devianceplus()
        devianceminus = statistics.get_devianceminus()
        directions = statistics.get_directions()
        last_numbers = statistics.get_latest_history_numbers()

        # highest correlation is always to the next one
        for x in range(len(directions)-1):
            y = x + 1
            corr = correlate(directions[x], directions[y])
            correlations.append(corr)
            log("Correlation: [%d -> %d] %f" % (x, x+1, correlations[x]))

        guessed_movement = []
        for x in range(len(directions)):
            dir = directions[x][-1]
            if dir != 0:
                dir = dir/abs(dir)*-1.0

            guessed_number1 = int(last_numbers[x] + distance_means[x] * dir)
            guessed_number2 = int(last_numbers[x] + distance_means[x] * dir*-1.0)
            guessed_number3 = int(means[x])
            if guessed_number1 > 0 and guessed_number1 not in guessed_movement:
                guessed_movement.append(guessed_number1)
            elif guessed_number2 > 0 and guessed_number2 not in guessed_movement:
                guessed_movement.append(guessed_number2)
            elif guessed_number3 > 0 and guessed_number3 not in guessed_movement:
                guessed_movement.append(guessed_number3)
            else:
                return []

        guessed_numbers = []
        guessed_numbers.extend(sorted(guessed_movement[:-2]))
        guessed_numbers.extend(guessed_movement[-2:])
        return guessed_numbers
