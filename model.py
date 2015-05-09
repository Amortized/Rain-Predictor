import csv
import sys
import logging
import argparse
import numpy as np
from sklearn.preprocessing import Imputer
from numpy import genfromtxt;

def sigmoid(center, length):
    # http://en.wikipedia.org/wiki/Sigmoid_function
    xs = np.arange(length)
    return 1. / (1 + np.exp(-(xs - center)));

def readfile(myfile):
	with open(myfile,'r') as dest_f:
	    data_iter = csv.reader(dest_f, 
                       delimiter = ",")
	    count = 0;
	    data_  = [];
	    for d_ in data_iter:
	    	count += 1;
	    	if count % 10000  == 0:
	    		print(str(count) + "\n");
	    	data_.append(d_);

   		

	data_array = np.asarray(data_, dtype = float)    
	print(len(data_array));

if __name__ == "__main__":
    readfile("./data/training_set.csv")