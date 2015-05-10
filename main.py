from clean_up import *;
from multiprocessing import Pool;
import time;
import csv;

def write(object, file_name):
	with open(file_name, "wb") as f:
		writer = csv.writer(f);
		writer.writerows(object)

def prepareTrainSet():
	start = time.time()
	train_X, train_Y  = read('./data/train_2013.csv', True);
	write(train_X, "./data/train_X.csv");
	write(train_Y, "./data/train_Y.csv");
	del train_X;
	del train_Y;
	print("training set processed in seconds : " +  str(time.time() - start) + "\n");


if __name__ == "__main__":

	prepareTrainSet();
	#test_X,  test_ids = read('./data/test_2014.csv', False);
