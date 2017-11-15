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
from keras.models import model_from_json	#for model recognition
import json
import numpy as np 						#for weight saving
import random
import math



#returns the number of corrent predictions over len(x_train) images
def evaluate(model, x_train, y_train):
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

	return score / len(x_train)

def cross_over(A, B, mutation_pct):
	'''
	A and B are weight sets for neural nets
	Returns: Weight sets C and D for children, which mutations
	  of A and B
	'''
	C = []
	D = []
	for i, row in enumerate(A):
		gene = random.randint(1, len(A)-1)
		t = np.concatenate([A[i][:gene], B[i][gene:]])
		if mutation_pct():
			t[gene] = math.sqrt(A[i][gene] * B[i][gene])
		s = np.concatenate([B[i][:gene], A[i][gene:]])
		if mutation_pct():
			s[gene] = math.sqrt(A[i][gene] * B[i][gene])
		C.append(t)
		D.append(s)
	return C, D

def get_model_JSON():
	'''
	Returns a JSON obj representing te network architcure
	3-layer CNN
	documentation here: https://keras.io/layers/core/
	notes: maybe change to sigmoid activation, check biases, remove dropout?
	'''
	model = Sequential()
	model.add(Dense(512, kernel_initializer='random_uniform', bias_initializer='random_normal', activation='relu', input_shape=(784,)))
	model.add(Dropout(0.2))
	model.add(Dense(512, activation='relu'))
	model.add(Dropout(0.2))
	model.add(Dense(num_classes, activation='softmax'))
	model.summary()
	return model.to_json()

def init_gene_pool(model_json, population_size):
	'''
	Returns a list, of size population_size, of initialized neurel nets
	according to the architecture described by the model_json
	Note: the model_json describes the functions for weight distributions
	'''
	return [
		model_from_json(model_json).get_weights()
		for x in range(population_size)
	]

def choose_pairs(pairs_to_breed):
	'''
	Returns (0,1), (2,3), ...
	'''
	return [
		(i*2, i*2+1) for i in range(pairs_to_breed)
	]


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



# start here:
population_size = 100
generations = 20
fitness = lambda n: evaluate(n, x_train[:100], y_train[:100])
mutation_count = 15
mutation_pct = lambda: random.randint(0,500) == 1
pairs_to_breed = 2

# lets create a population, using the same model but
# different initialized weights, the model.to_json gives a description of 
# the nets architecture such as, weigh initilization, layers, connectivity, etc.
model_json = get_model_JSON()
base_agent = model_from_json(model_json)

#list of weights
gene_pool = init_gene_pool(model_json, population_size)


# lets score the population by testing each one on the same 100 images
ranking = []
for weights in gene_pool:
	base_agent.set_weights(weights)
	ranking.append((fitness(base_agent), weights))

#now lets run over some generations
for generation in range(generations):
	#keep the population constant
	ranking.sort(key=lambda m: m[0], reverse=True)
	ranking = ranking[:population_size]

	#now kill the weakest members of the population
	scores = [score[0] for score in ranking]
	print('Generation: ', generation, ' top 20 rankings: ', scores[:20])

	for m, n in choose_pairs(pairs_to_breed):
		print('breeding ', m, ' and ', n)
		
		father_score, father = ranking[m]
		mother_score, mother = ranking[n]

		child1, child2 = cross_over(father, mother, mutation_pct)

		base_agent.set_weights(child1)
		ranking.append((fitness(base_agent), child1))
		base_agent.set_weights(child2)
		ranking.append((fitness(base_agent), child2))


'''

print('type child {} type father {}'.format(type(child1), type(father)))
		for i, x in enumerate(father):
			if len(father[i]) != len(child1[i]):
				print('len row ', i, ' not equal')
				print(len(father[i]), ' ',len(child1[i]))
			if type(father[i]) != type(child1[i]):
				print('type row ', i, ' not equal')
				print(type(father[i]), ' ', type(child1[i]))

		#print(' ', child1)
		#print(' ', child2)

'''


#TODO: now the hard part... breeding these kids.