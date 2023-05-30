from numpy import exp, array, random, dot
from utils import *


class NeuralNetwork():
    def __init__(self, n, m):
        # Seed the random number generator, so it generates the same numbers
        # every time the program runs.
        random.seed(1)

        # We model a single neuron, with 3 input connections and 1 output connection.
        # We assign random weights to a 3 x 1 matrix, with values in the range -1 to 1
        # and mean 0.
        self.synaptic_weights = 2 * random.random((n, m)) - 1

    def get_synaptic_weights(self):
        return self.synaptic_weights

    # The Sigmoid function, which describes an S shaped curve.
    # We pass the weighted sum of the inputs through this function to
    # normalise them between 0 and 1.
    def __sigmoid(self, x):
        return 1 / (1 + exp(-x))

    # The derivative of the Sigmoid function.
    # This is the gradient of the Sigmoid curve.
    # It indicates how confident we are about the existing weight.
    def __sigmoid_derivative(self, x):
        return x * (1 - x)

    # We train the neural network through a process of trial and error.
    # Adjusting the synaptic weights each time.
    def train(self, training_set_inputs, training_set_outputs, number_of_training_iterations):
        for iteration in range(number_of_training_iterations):
            # Pass the training set through our neural network (a single neuron).
            output = self.think(training_set_inputs)

            # Calculate the error (The difference between the desired output
            # and the predicted output).

            error = training_set_outputs - output

            # Multiply the error by the input and again by the gradient of the Sigmoid curve.
            # This means less confident weights are adjusted more.
            # This means inputs, which are zero, do not cause changes to the weights.
            adjustment = dot(training_set_inputs.T, error * self.__sigmoid_derivative(output))

            # Adjust the weights.
            p = False
            if p:
                print(f"{len(adjustment)} x {len(adjustment[0])}")
                print(adjustment)
                print(self.synaptic_weights)
            self.synaptic_weights += adjustment

    # The neural network thinks.
    def think(self, inputs):
        # Pass inputs through our neural network (our single neuron).
        return self.__sigmoid(dot(inputs, self.synaptic_weights))


def combine(lst):
    out = lst[0]
    for i in lst[1:]:
        out <<= 8
        out += i

    return out


def decombine(out):
    lst = []
    while out != 0:
        i = out & 0x00FF
        lst.append(i)
        out >>= 8
    lst.reverse()
    return lst


def getXandY(n, m):
    idx = 0
    inputs = []
    outputs = []
    LOTTO_HISTORY_DB = os.path.join("database", "lottoDB")

    db = load_db(LOTTO_HISTORY_DB)
    tkeys = list(db.keys())
    while idx < (len(tkeys)-1):
        input = db[tkeys[idx]][0][0:n]
        if input not in inputs:
            inputs.append(input)

            output = combine(db[tkeys[idx + 1]][0][0:m])
            outputs.append(output)
            idx += 1

    return inputs, outputs


def function1():
    '''
    log("Random starting synaptic weights: ")
    log("neural_network.synaptic_weights")

    # The training set. We have 4 examples, each consisting of 3 input values
    # and 1 output value.
    training_set_inputs = array([[0, 0, 1], [1, 1, 1], [1, 0, 1], [0, 1, 1]])
    training_set_outputs = array([[0, 1, 1, 0]]).T

    # Train the neural network using a training set.
    # Do it 10,000 times and make small adjustments each time.
    # Intialise a single neuron neural network.
    neural_network = NeuralNetwork(3, 1)
    neural_network.train(training_set_inputs, training_set_outputs, 10000)

    log("New synaptic weights after training: ")
    log(neural_network.synaptic_weights)

    # Test the neural network with a new situation.
    log("Considering new situation [1, 0, 0] -> ?: ")
    log(neural_network.think(array([1, 0, 0])))
    '''

    # 5 to 1

    SIZE_N = 5
    SIZE_M = 2
    ITERATIONS_COUNT = 10000

    inputs, outputs = getXandY(SIZE_N, SIZE_M)

    # print(outputs)
    training_set_inputs = array(inputs)
    training_set_outputs = array(outputs).T
    neural_network = NeuralNetwork(SIZE_N, len(outputs))
    neural_network.train(training_set_inputs, training_set_outputs, ITERATIONS_COUNT)

    guess = [4, 4, 41, 42, 47]
    guess_last_input = [8, 13, 16, 44, 47]

    outs = []
    outs.append(neural_network.think(array(guess[0:SIZE_N])))
    outs.append(neural_network.think(array(guess_last_input[0:SIZE_N])))

    for i in range(len(outs[0])):
        f = [True if outs[x][i] > 0.5 else False for x in range(len(outs))]

        positive_printables = ""
        for y in range(len(f)):
            if f[y] == True:
                positive_printables += f"[{i}]({y}) {decombine(outputs[i])} with {outs[y][i]*100.0} %"

        if len(positive_printables) > 0:
            log("".join(positive_printables))


if __name__ == "__main__":
    import keras
    from keras.models import Sequential
    from keras.layers import Dense

    SIZE_N = 5
    SIZE_M = 5
    ITERATIONS_COUNT = 100
    X, Y = getXandY(SIZE_N, SIZE_M)

    print(len(X))
    print(len(Y))

    SIZE_IN = 5
    SIZE_OUT = 50
    model = Sequential()
    model.add(Dense(SIZE_OUT, input_shape=(SIZE_IN,), activation='relu'))
    model.compile(loss='binary_crossentropy', optimizer='adam')  # , metrics=['accuracy'])

    # Load values
    LOTTO_HISTORY_DB = os.path.join("database", "lottoDB")
    db = load_db(LOTTO_HISTORY_DB)
    tkeys = list(db.keys())

    idx = 0
    X = []
    Y = []
    while idx < (len(tkeys)-1):
        inputs = db[tkeys[idx]][0][0:SIZE_IN]
        o = db[tkeys[idx + 1]][0][0:SIZE_IN]

        outputs = [0]*SIZE_OUT
        for i in o:
            outputs[i] = 1

        X.append(inputs)
        Y.append(outputs)
        idx += 1

    model.fit(X, Y, epochs=ITERATIONS_COUNT, batch_size=10)

    # make class predictions with the model
    predictions = model.predict(X) > 0.5
    # summarize the first 5 cases
    for i in range(5):
        print('%s => %s (expected %s)' % (X[i], predictions[i], decombine(Y[i])))
