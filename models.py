import nn

class PerceptronModel(object):
    def __init__(self, dimensions):
        """
        Initialize a new Perceptron instance.

        A perceptron classifies data points as either belonging to a particular
        class (+1) or not (-1). `dimensions` is the dimensionality of the data.
        For example, dimensions=2 would mean that the perceptron must classify
        2D points.
        """
        self.w = nn.Parameter(1, dimensions)

    def get_weights(self):
        """
        Return a Parameter instance with the current weights of the perceptron.
        """
        return self.w

    def run(self, x):
        """
        Calculates the score assigned by the perceptron to a data point x.

        Inputs:
            x: a node with shape (1 x dimensions)
        Returns: a node containing a single number (the score)
        """
        return nn.DotProduct(self.w, x)
    

    def get_prediction(self, x):
        """
        Calculates the predicted class for a single data point `x`.

        Returns: 1 or -1
        """
        if nn.as_scalar(self.run(x)) >= 0.0 :
            return 1
        else:
            return -1

    def train(self, dataset):
        """
        Train the perceptron until convergence.
        """
        while True:
            outcome = True
            for x, y in dataset.iterate_once(1):
                if nn.as_scalar(y) != self.get_prediction(x):
                    outcome = False
                    self.w.update(x, nn.as_scalar(y))
            if outcome:
                break
    
    

class RegressionModel(object):
    """
    A neural network model for approximating a function that maps from real
    numbers to real numbers. The network should be sufficiently large to be able
    to approximate sin(x) on the interval [-2pi, 2pi] to reasonable precision.
    """
    def __init__(self):
        X = 100
        self.batch_size = 10
        self.weight1 = nn.Parameter(1, X)  
        self.bias1 = nn.Parameter(1, X)
        self.weight2 = nn.Parameter(X, 1)
        self.bias2 = nn.Parameter(1, 1)
        self.learning_rate = -0.02

        
    def run(self, x):
        """
        Runs the model for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
        Returns:
            A node with shape (batch_size x 1) containing predicted y-values
        """
        return nn.AddBias(nn.Linear(nn.ReLU(nn.AddBias(nn.Linear(x, self.weight1), self.bias1)), self.weight2), self.bias2)
        

    def get_loss(self, x, y):
        """
        Computes the loss for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
            y: a node with shape (batch_size x 1), containing the true y-values
                to be used for training
        Returns: a loss node
        """
        return nn.SquareLoss(self.run(x), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        
        for i in range(1000):
            for x, y in dataset.iterate_once(10):
                gradients = nn.gradients(self.get_loss(x,y), [self.weight1, self.weight2, self.bias1, self.bias2])
                
                self.weight1.update(gradients[0], self.learning_rate)
                self.weight2.update(gradients[1], self.learning_rate)
                self.bias1.update(gradients[2], self.learning_rate)
                self.bias2.update(gradients[3], self.learning_rate)
               
      
                    

            

class DigitClassificationModel(object):
    """
    A model for handwritten digit classification using the MNIST dataset.

    Each handwritten digit is a 28x28 pixel grayscale image, which is flattened
    into a 784-dimensional vector for the purposes of this model. Each entry in
    the vector is a floating point number between 0 and 1.

    The goal is to sort each digit into one of 10 classes (number 0 through 9).

    """
    def __init__(self):
        X = 100
        self.batch_size = 10
        self.weight1 = nn.Parameter(784, X)  
        self.bias1 = nn.Parameter(1, X)
        self.weight2 = nn.Parameter(X, 10)
        self.bias2 = nn.Parameter(1, 10)
        self.learning_rate = -0.02

    def run(self, x):
        """
        Runs the model for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 784)
        Output:
            A node with shape (batch_size x 10) containing predicted scores
                (also called logits)
        """
        first = nn.Linear(x, self.weight1)
        rectified = nn.ReLU(nn.AddBias(first, self.bias1))
        second = nn.Linear(rectified, self.weight2)
        return nn.AddBias(second, self.bias2)

    def get_loss(self, x, y):
        """
        Computes the loss for a batch of examples.

        The correct labels `y` are represented as a node with shape
        (batch_size x 10). Each row is a one-hot vector encoding the correct
        digit class (0-9).

        Inputs:
            x: a node with shape (batch_size x 784)
            y: a node with shape (batch_size x 10)
        Returns: a loss node
        """
        return nn.SoftmaxLoss(self.run(x), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        for i in range(2000):
            for x, y in dataset.iterate_once(self.batch_size):
                gradients = nn.gradients(self.get_loss(x,y), [self.weight1, self.weight2, self.bias1, self.bias2])
                
                self.weight1.update(gradients[0], self.learning_rate)
                self.weight2.update(gradients[1], self.learning_rate)
                self.bias1.update(gradients[2], self.learning_rate)
                self.bias2.update(gradients[3], self.learning_rate)

            if dataset.get_validation_accuracy() >= 0.97:
                return

class LanguageIDModel(object):
    """
    A model for language identification at a single-word granularity.

    """
    def __init__(self):
        '''
        Our dataset contains words from five different languages, and the
        combined alphabets of the five languages contain a total of 47 unique
        characters.
        '''
        self.num_chars = 47
        self.languages = ["English", "Spanish", "Finnish", "Dutch", "Polish"]

        
        self.learning_rate = -0.005
        self.batch_size = 2
        hidden = 300
        dimension = 5

        self.weight = nn.Parameter(self.num_chars, hidden)  
        self.weight_h = nn.Parameter(hidden, hidden)
        self.weight_f = nn.Parameter(hidden, dimension)
        


    def run(self, xs):
        """
        Runs the model for a batch of examples.

        Although words have different lengths, our data processing guarantees
        that within a single batch, all words will be of the same length (L).

        Here `xs` will be a list of length L. Each element of `xs` will be a
        node with shape (batch_size x self.num_chars), where every row in the
        array is a one-hot vector encoding of a character. For example, if we
        have a batch of 8 three-letter words where the last word is "cat", then
        xs[1] will be a node that contains a 1 at position (7, 0). Here the
        index 7 reflects the fact that "cat" is the last word in the batch, and
        the index 0 reflects the fact that the letter "a" is the inital (0th)
        letter of our combined alphabet for this task.

        This model uses a Recurrent Neural Network to summarize the list
        `xs` into a single node of shape (batch_size x hidden_size), for a
        choice of hidden_size. It then calculates a node of shape
        (batch_size x 5) containing scores, where higher scores correspond to
        greater probability of the word originating from a particular language.

        Inputs:
            xs: a list with L elements (one per character), where each element
                is a node with shape (batch_size x self.num_chars)
        Returns:
            A node with shape (batch_size x 5) containing predicted scores
                (also called logits)
        """
        
        first = nn.Linear(xs[0], self.weight)
        
        for node in xs[1:]:
            first = nn.ReLU(nn.Add(nn.Linear(node, self.weight), nn.Linear(first, self.weight_h)))

        return nn.Linear(first, self.weight_f)


    def get_loss(self, xs, y):
        """
        Computes the loss for a batch of examples.

        The correct labels `y` are represented as a node with shape
        (batch_size x 5). Each row is a one-hot vector encoding the correct
        language.

        Inputs:
            xs: a list with L elements (one per character), where each element
                is a node with shape (batch_size x self.num_chars)
            y: a node with shape (batch_size x 5)
        Returns: a loss node
        """
        return nn.SoftmaxLoss(self.run(xs), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        
        while True:
            for x, y in dataset.iterate_once(self.batch_size):
                gradients = nn.gradients(self.get_loss(x,y), [self.weight, self.weight_h, self.weight_f])
                self.weight.update(gradients[0], self.learning_rate)
                self.weight_h.update(gradients[1], self.learning_rate)
                self.weight_f.update(gradients[2], self.learning_rate)
                
            if dataset.get_validation_accuracy() >= 0.82:
                return

