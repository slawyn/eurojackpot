from utils import log

from utils import correlate
import random

class Predictor:

    def __init__(self, history_db, orders_db):
        self.history_db = history_db
        self.orders_db = orders_db

    def predict_simple(self, history_points, statistics):
        correlations = [[],[],[],[],[]]
        guessedmain = []
        guessedeuro = []

        means, mins, maxs, distance_means, devianceplus, devianceminus, directions, distances, most_frequent = statistics

        # highest correlation is always to the next one
        for x in range(0, 5):
            y = x + 1
            while y<5:
                corr = correlate(directions[x],directions[y])
                correlations[x].append(corr)
                log("Correlation: [%d -> %d] %f"%(x+1, y+1, corr))
                y +=1


        # First value
        guessdir = 1
        if directions[0][-1] >=5:
            guessdir = -1

        guessedmain.append(int(history_points[0][-1] + means[0]*guessdir) % 50)

        # Other vals
        for x in range(1, 5):
            corr = abs(max(correlations[x-1]))
            if corr < 0.5:  # correlation higher than 50 % then we use previous direction
                guessdir = 1
                if directions[x][-1] >=5:
                    guessdir =-1

            #print(guessed)
            guessedmain.append(int(history_points[x][-1]+means[x]*guessdir) % 50)

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

        # Euro vals
        guessdir = 1
        if directions[5][-1] >=5:
            guessdir = -1

        guessedeuro.append(int(history_points[5][-1] + means[5]*guessdir)%10)
        guessedeuro.append(int(history_points[6][-1] + means[5]*guessdir)%10)

        # sanity checks
        for x in range(len(guessedeuro)):
            if guessedeuro[x] <= 0:
                value = random.randint(1, 10)
                while value in guessedeuro:
                    value = random.randint(1, 10)
                guessedeuro[x] = value

        guessedmain.sort()
        return guessedmain+guessedeuro
