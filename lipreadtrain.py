from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility
import json
from keras.layers.wrappers import *
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Masking, TimeDistributedDense
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM
from keras.optimizers import *
from keras.datasets import imdb
import time
from keras.models import model_from_json

NIL = 0.0


def save_model(model, save_weight_to, save_topo_to):
    json_string = model.to_json()
    model.save_weights(save_weight_to, overwrite=True)
    with open(save_topo_to, 'w') as outfile:
        json.dump(json_string, outfile)
        


## batchsize  x 30 x (40,40) ===> [30x(40x40)]

# Masking(mask_value=NIL)

def build_network(max_seqlen=30, image_size=(40, 40), fc_size=128,
                  save_weight_to='untrained_weight.h5', save_topo_to='untrained_topo.json', save_result=True,
                  lr=0.001, momentum=0.6,decay=0.0005,nesterov=True,
                  rho=0.9,epsilon=1e-6, 
                  optimizer='sgd', load_cache=False,   # the optimizer here could be 'sgd', 'adagrad', 'rmsprop'
                  cnn=False,dict_size=53):

    try:
        if load_cache:
            return read_model(weights_filename=save_weight_to,
                              topo_filename=save_topo_to)
    except:
        pass
    
    
    start_time = time.time()    
    
    print("Creating Model...")    
    model = Sequential()

    if not cnn:        
        print("Adding TimeDistributeDense Layer...")    
        model.add(TimeDistributedDense(fc_size, input_shape=(max_seqlen, image_size[0]*image_size[1])))
    else:
        print("Adding TimeDistributeConvolution Layer...")
        # TODO
        # Reshape -> conv -> reshape
        # model.add(TimeDistributed(Convolution1D(nb_filter, filter_length)))


    print("Adding Masking Layer...")
    model.add(Masking(mask_value=0.0))
    
    print("Adding First LSTM Layer...")
    model.add(LSTM(fc_size, return_sequences=True))

    print("Adding Second LSTM Layer...")
    model.add(LSTM(fc_size, return_sequences=False))

    print("Adding Final Dense Layer...")
    model.add(Dense(dict_size))

    print("Adding Softmax Layer...")
    model.add(Activation('softmax'))

    print("Compiling the model to runnable code, which will take a long time...")
    if optimizer == 'sgd':
        optimizer = SGD(lr=lr, momentum=momentum, decay=decay, nesterov=nesterov)
    elif optimizer == 'rmsprop':
        optimizer = RMSprop(lr=lr, rho=rho, epsilon=epsilon)
    elif optimizer == 'adagrad':
        optimizer = Adagrad(lr=lr, epsilon=epsilon)
    
    ## Takes my macbook pro 1-2min to finish.    
    model.compile(loss='categorical_crossentropy', optimizer=optimizer)

    end_time = time.time()
    
    print("----- Compilation Takes %s Seconds -----" %  (end_time - start_time))


    
    if save_result:        
        print("Saving Model to file...")
        save_model(model, save_weight_to, save_topo_to)

    print("Finished!")
    return model





def train(model=None, 
          X_train=[], y_train=[],
          X_test=[], y_test=[], batch_size=100,
          iter_times=7, show_accuracy=True,
          save_weight_to='trained_weight.h5',
          save_topo_to='trained_topo.json',
          save_result=True, validation_split=0.1):
    
    if (not model) or len(X_train) == 0:
        print("Please provide legal input parameters!")
        return

    start_time = time.time()
    print("Training the model, which will take a long long time...")
    model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=iter_times,
             validation_split=validation_split, show_accuracy=show_accuracy)
    end_time = time.time()
    print("----- Training Takes %s Seconds -----" %  (end_time - start_time))


    print("Testing the model...")
    score, acc = model.evaluate(X_test, y_test, batch_size=batch_size,
                                show_accuracy=show_accuracy)
    print('Test score:', score)
    print('Test accuracy:', acc)

    if save_result:        
        print("Saving Model to file...")
        save_model(model, save_weight_to, save_topo_to)

    print("Finished!")
    return score, acc
    

def read_model(weights_filename='trained_weight.h5',
               topo_filename='trained_topo.json'):
    print("Reading Model from "+weights_filename + " and " + topo_filename)
    print("Please wait, it takes time.")
    with open(topo_filename) as data_file:
        topo = json.load(data_file)
        model = model_from_json(topo)
        model.load_weights(weights_filename)
        print("Finish Reading!")
        return model




def test():
    print (build_network())
    print (read_model(weights_filename='untrained_weight.h5',
                  topo_filename='untrained_topo.json'))


## The data format we probably need:
### - Data:(totalDataNumber, maxSeqLen, 40x40)
### - Label:(totalDataNumber)
# test()
    
