import csv
import sys
import logging
import argparse
import numpy as np
from sklearn.preprocessing import Imputer
from evaluation import *
from sklearn import preprocessing, cross_validation;
import math;
import copy;
from sklearn.ensemble import RandomForestRegressor;
from sklearn.ensemble import GradientBoostingRegressor;
from sklearn.grid_search import ParameterGrid;
from multiprocessing import Pool;
from sklearn.cross_validation import KFold;
from sklearn.cross_validation import train_test_split;

def sigmoid(center, length):
    # http://en.wikipedia.org/wiki/Sigmoid_function
    xs = np.arange(length)
    return 1. / (1 + np.exp(-(xs - center)));

def generateParams():

    # Set the parameters by cross-validation
    paramaters_grid    = {'max_depth': [4], 'min_samples_leaf' : [1000, 2000, 5000, 10000], 'n_estimators' : [20]};

    paramaters_search  = list(ParameterGrid(paramaters_grid));

    parameters_to_try  = [];
    for ps in paramaters_search:
        params           = {'max_features' : 'sqrt', 'n_jobs' : -1}
        for param in ps.keys():
            params[str(param)] = ps[param];
        parameters_to_try.append(copy.copy(params));

    return parameters_to_try;     


def predict(estimator, X_validation):
	X_predict = [];
	for X in X_validation:
		y_hat = estimator.predict(X);
		if y_hat > 69.0:
			y_hat = 69.0
		X_predict.append(sigmoid(y_hat, 70));
	return np.array(X_predict);

def train_model(features, label, params):
    #Preprocessing
    #scaled_features = preprocessing.scale(features);
    scaled_features  = features;
    X_train, X_validation, Y_train, Y_validation = train_test_split(scaled_features, label, test_size=0.80, random_state=42);
    estimator             = RandomForestRegressor(**params)
    estimator.fit(X_train, Y_train);
    current_crps          = CRPS(predict(estimator, X_validation), Y_validation);
    print("Validation Set CRPS : " + str(current_crps) + "\n");
    return  (params, current_crps);

def train_model_wrapper(args):
   return train_model(*args);


def start(train_X, train_Y):
	print("Starting imputation of  Training Set...\n")
	imputer = Imputer(missing_values="NaN", strategy='mean', axis=0);
	imputer.fit(train_X);

	train_X = imputer.transform(train_X);

	train_Y = [y if y <= 69.0 else 69.0 for y in train_Y]; #Capping the rain at 69mm/hr
	train_Y = np.array(train_Y);
	print("Imputation  Completed\n")

	parameters_to_try = generateParams();
	print("No of Paramters to test " + str(len(parameters_to_try)));

	print("Copying Parameters");
	results = [];

	#Contruct parameters as  list
	

	batch_size        = 2;
	for i in xrange(0, len(parameters_to_try), batch_size):

		models_to_try     = [ (copy.copy(train_X), copy.copy(train_Y), parameters_to_try[i] ) ];
		print("Releaseing a batch")
		if i+1 < len(parameters_to_try) :
			models_to_try.append( (copy.copy(train_X), copy.copy(train_Y), parameters_to_try[i+1] ) );

		#Create a Thread pool.
		pool              = Pool(2);
		results_t         = pool.map( train_model_wrapper, models_to_try );
		pool.close();
		pool.join();
		del models_to_try;
		results.append(results_t);



	best_params       = None;
	best_crps         = sys.float_info.max;
	for i in range(0, len(results)):
		if results[i][1] < best_crps:
			best_crps   = results[i][1];
			best_params = results[i][0];

	print("Best Params : " + str(best_params));
	print("Best CRPS :   " + str(best_crps));

	estimator               = RandomForestRegressor(**best_params)
	estimator.fit(train_X, train_Y);

	return imputer, estimator;

def predict_and_write(estimator, imputer, test_X, test_ids):
	test_X 		= imputer.transform(test_X);
	predictions = predict(estimator, test_X);
	f 			= open("./data/output.csv", "wb");

	f.write("Id,")
	for i in range(0, 70):
		if i == 0:
			f.write("Predicted" + str(i));	
		else:
			f.write(",Predicted" + str(i));
	f.write("\n");

	assert(len(test_ids) == len(predictions));

	for i in range(0, len(test_ids)):
		f.write(str(i)+",");
		for k in range(0, len(predictions[i])):
			if k == 0:
				f.write(str(predictions[i][k]));
			else:
				f.write("," + str(predictions[i][k]));

		f.write("\n");

	f.close();





