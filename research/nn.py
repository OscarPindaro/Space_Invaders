'''Trains a simple deep NN on the MNIST dataset.
Gets to 98.40% test accuracy after 20 epochs
(there is *a lot* of margin for parameter tuning).
2 seconds per epoch on a K520 GPU.

from: https://github.com/fchollet/keras/blob/master/examples/mnist_mlp.py
overview: https://www.youtube.com/watch?v=Tp3SaRbql4k
'''

from __future__ import print_function

import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import RMSprop

#for model recognition
from keras.models import model_from_json
import json

#for weight saving
import numpy as np

'''
Should probably look into this.
(venv) &e$python test.py 
Using TensorFlow backend.
/Users/andykeene/Desktop/pg/venv/lib/python3.6/importlib/_bootstrap.py:219: RuntimeWarning: compiletime version 3.5 of module 'tensorflow.python.framework.fast_tensor_util' does not match runtime version 3.6
  return f(*args, **kwds)
2017-11-12 18:09:55.616182: I tensorflow/core/platform/cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA
'''


#returns the number of corrent predictions over len(x_train) images
def test(model, x_train, y_train):
	score = 0
	for i, img in enumerate(x_train):
		#hack: see https://stackoverflow.com/questions/39950311/keras-error-on-predict
		# returns [[0, 0, ..., 1, 0]] guess (using softmax layer)
		model_prediction = model.predict(np.array([img]), batch_size=1, verbose=0)[0]

		#get the label for this prediction (i.e. index of classification)
		#and get the prediction (max output)
		#note: there's a better way to get the index of the max using numpy...
		label = list(y_train[i]).index(max(y_train[i]))
		prediction = list(model_prediction).index(max(model_prediction))

		if(label == prediction):
			score += 1

	return score



batch_size = 128
num_classes = 10
epochs = 1

# note, not really sure whats happening in prepping the input for test / train
# the data, shuffled and split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)


# Lets build the model! (3 layer with softmax output)
# Dense() and Dropout() documentation here: https://keras.io/layers/core/
model = Sequential()
#Dense(output number, activation function, input shape - only necessary for first layer)
#NOTE: the _initializers describe the distributions to the weights
model.add(Dense(512, kernel_initializer='random_uniform', bias_initializer='random_normal', activation='relu', input_shape=(784,)))
#randomly drops output during training updates at the rate given? probs. not necessary...
model.add(Dropout(0.2))
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.2))
#catagorizer to 10 classes, see https://keras.io/activations/
model.add(Dense(num_classes, activation='softmax'))
#prints layer overview to stdout, the model is now defined
model.summary()


# lets create a population, using the same model but
# different initialized weights, the model.to_json gives a description of 
# the nets architecture such as, weigh initilization, layers, connectivity, etc.
model_json = model.to_json()
population = []
for genes_to_add in range(10):
	# this should create a new net using the same architecture, but
	# with different weights for each layer?
	population.append(model_from_json(model_json))


# lets score the population by testing each one on the same 100 images
scores = []
for member in population:
	scores.append(test(member, x_train[:100], y_train[:100]))

#yay! each one is different and so implies diff. weight initilizations.
print('scores', scores)

#TODO: now the hard part... breeding these kids.



'''
	GARBAGE BIN:

# this is a test to see if the models have the same weights... they dont!
# but they ALL predict with the same accuracy?
model1 = model_from_json(model_json)
model2 = model_from_json(model_json)

weights1 = model1.get_weights()
weights2 = model2.get_weights()

print('np equal ? ', np.array_equal(weights1, weights2))
print('w1 ', weights1)
print('w1 ', weights2)



# get the layers weights and print them
w = model.get_weights()
print('weight layers....', len(w))
for i, layer in enumerate(w):
	print('layer: {}, length: {} \nValues:{}'.format(i, len(layer), layer))


# get dictionary config from model (can be used to instantiate new model)
base_model_config = model.get_config()
print('config : {}'.format(base_model_config))
weights = model.get_weights()

#gets the config for the network (not the wieghts!) as a JSON obj.
end_model_config = model.to_json()
print('config : {}'.format(end_model_config))



		if(label == pred):
			print('Correct prediction')
		else:
			print('Incorrect prediction')


for i, member in enumerate(population):
	if np.array_equal(population[i].get_weights(), population[i+1].get_weights()):
		print('same weightS!')

print('models prediction ', model_prediction, ' label ', y_train[i])


#this is needed for gradient descent methods, but shouldn't be for
# our manual one...
model.compile(loss='categorical_crossentropy',
              optimizer=RMSprop(),
              metrics=['accuracy'])

history = model.fit(x_train, y_train,
                    batch_size=batch_size,
                    epochs=epochs,
                    verbose=1,
                    validation_data=(x_test, y_test))
score = model.evaluate(x_test, y_test, verbose=0)

print('Test loss:', score[0])
print('Test accuracy:', score[1])

'''



