from clean_up import *;
from multiprocessing import Pool;
import time;
import csv;
from model import *;

def write(object, file_name):
	with open(file_name, "wb") as f:
		writer = csv.writer(f);
		writer.writerows(object)

def prepareTrainSet(train_X_filename, train_Y_filename):
	start = time.time()
	train_X, train_Y  = read('./data/train_2013.csv', True);
	write(train_X, train_X_filename);

	f = open(train_Y_filename, "wb");
	for r in range(0, len(train_Y)):
		f.write(str(train_Y[r]) + "\n");
	f.close();
	
	del train_X;
	del train_Y;
	print("training set processed in seconds : " +  str(time.time() - start) + "\n");

def loadTrainSet(train_X_filename, train_Y_filename):
	train_X = [];
	train_Y = [];

	with open(train_X_filename, "rb") as f:
		reader = csv.reader(f);
		for row in reader:
			t = [];
			for r in row:
				if r != "NaN":
					t.append(float(r));
				else:
					t.append(r);
			train_X.append(t)

	f = open(train_Y_filename, "rb");
	for row in f:
		train_Y.append(float(row));

	return train_X, train_Y;



if __name__ == "__main__":

	train_X_filename   = "./data/train_X.csv";
	train_Y_filename   = "./data/train_Y.csv";

	#prepareTrainSet(train_X_filename,train_Y_filename);
	print("Loading Training Set...\n")
	train_X, train_Y   = loadTrainSet(train_X_filename,train_Y_filename);
	print("Loaded...\n")
	imputer, estimator = start(train_X, train_Y);

	del train_X;
	del train_Y;


	test_X,  test_ids = read('./data/test_2014.csv', False);

	predict_and_write(estimator, imputer, test_X, test_ids);
