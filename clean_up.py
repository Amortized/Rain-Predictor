import sys;
from debian.debtags import output
import numpy as np;
from scipy.stats import variation;
from multiprocessing import Pool;
import operator;

def identify_radar_end_points(readings, metric):
	start     = 0;
	end       = 0;
	prev      = float(readings[0]);

	radar_pos = [];    

	for k in range(1, len(readings)):
		if metric == "time" and float(readings[k]) < prev:
			 #Same radar as time should decrease
			 end = k;
		elif metric == "time" and float(readings[k]) > prev:
			 #Diff radar
			 radar_pos.append((start,end));
			 start = k;
			 end   = k;
			 prev  = float(readings[k]);
		elif metric == "distance" and float(readings[k]) == prev:
			 #Same radar as time should decrease
			 end = k;
		elif metric == "distance" and float(readings[k]) != prev:   
			 #Diff radar
			 radar_pos.append((start,end));
			 start = k;
			 end   = k;
			 prev  = float(readings[k]);

	radar_pos.append((start,end));
	return radar_pos;




def preprocess(line, train):


	ids    = None;
	X	   = None;
	Y	   = None;
	
	x = line.strip().split(',');
	
	if train:
		label_range = len(x) - 1;
		Y           = float(x[len(x)-1]);
	else:
		ids         = int(x[0]);
		label_range = len(x);
			

	radar_pos_time = identify_radar_end_points(x[1].split(), "time");
	radar_pos_dis  = identify_radar_end_points(x[2].split(), "distance");

	all_radar_features = [];
	
	for radar in radar_pos_time:
	
		radar_features = [];

		for i in range(1, label_range):

			readings = x[i].split();
			 
			if i == 1:
				time_to_end = [float(readings[z]) for z in range(radar[0] , (1 + radar[1]))];

				if len(time_to_end) > 1:
					diff = [(float(time_to_end[k]) - float(time_to_end[k+1])) for k in range(0, len(time_to_end) - 1)];
				else:
					diff = [float(time_to_end[0])];

																		
				#Avg time difference between observations; min, max time of observation, total no of observations
				radar_features.append(len(time_to_end));
				radar_features.append(min(time_to_end));
				radar_features.append(max(time_to_end));
				radar_features.append(round((sum(diff) / float(len(diff))), 2));

			elif i == 2:
				distance_to_radar = [float(readings[z]) for z in range(radar[0] , (1 + radar[1]))];
				#Average distance
				radar_features.append(round((sum(distance_to_radar) / float(len(distance_to_radar))), 2));						

			elif i in [3,4,6,7,8,9,10,11,12,13,14,15,16,17,18]:
				other_f		  = [float(readings[z]) for z in range(radar[0] , (1 + radar[1])) if readings[z] \
																					not in ["-99900.0", "-99901.0", "-99903.0", "nan", "999.0"]];

				if len(other_f) > 0:																	
					radar_features.append(round((sum(other_f) / float(len(other_f))), 2));
				else:
					if i == 10:
						#Append poor quality radar index
						radar_features.append(0.001);
					else:
						radar_features.append("NaN");

			elif i == 5:
				HydrometeorType   = dict();
				for z in range(radar[0] , (1 + radar[1])):
					if readings[z] not in ["-99900.0", "-99901.0", "-99903.0", "nan", "999.0"]:
						if float(readings[z]) in HydrometeorType:
							HydrometeorType[float(readings[z])] += 1;
						else:
							HydrometeorType[float(readings[z])]  = 1;

				#Not converted into a feature yet	
				radar_features.append(HydrometeorType);			
		all_radar_features.append(radar_features);

	#Sort the radars based on quality index
	all_radar_features.sort(key = lambda z : z[12] if z[12] != "NaN" else 0.001);

	#Now we compute the features
	X = generateFeatures(all_radar_features);
	del all_radar_features;

	if train:
		return X, Y;
	else:
		return X, ids;		

def generateFeatures(all_radar_features):
	features = [];					 

	####################Take aggregate statistics based on the radar quality index
	features.append(len(all_radar_features)) # No of Radars;

	for i in range(0, len(all_radar_features[0])):
		if i in [0, 1, 2, 3, 4, 12]:
			# Time based observations
			observations = [r[i] for r in all_radar_features];	 
			features.append(round(np.mean(observations), 2)); 
			features.append(round(np.std(observations), 2)); 

		elif i == 7:
			#HydrometeorType
			#For each of the HydrometeorType, compute the weighted mean of the counts
			HydrometeorType = dict();

			for r in all_radar_features:
				for k in r[i].keys():
					if float(k) in HydrometeorType:
						HydrometeorType[float(k)] += (r[12] * r[i][k])
					else:
						HydrometeorType[float(k)]  = (r[12] * r[i][k])

			for hm in range(0, 15):
				if float(hm) in HydrometeorType.keys():
					features.append(HydrometeorType[hm]);
				else:
					features.append(0);

			#Add the most frequent HydrometeorType
			HydrometeorType = dict();
			for r in all_radar_features:
				for k in r[i].keys():
					if float(k) in HydrometeorType:
						HydrometeorType[float(k)] += (r[i][k])
					else:
						HydrometeorType[float(k)]  = (r[i][k])

			most_frequent_meteor = sorted(HydrometeorType.items(), key=operator.itemgetter(1))
			if most_frequent_meteor:
				features.append(most_frequent_meteor[0][0]);
			else:
				features.append("NaN");

		else:
			#Only compute the stats of radar values which aren't missing
			observations = [r[12] * float(r[i]) for r in all_radar_features if r[i] != "NaN"];

			if len(observations) > 0:
				features.append(round(np.mean(observations), 2)); 
				features.append(round(np.std(observations), 2));  
				features.append(round(np.median(observations), 2));
				if np.mean(observations) > 0:
					features.append(round(variation(observations), 2)); #Coefficient of variations
				else:
					features.append("NaN"); #Coefficient of variations
			else:
				features.append("NaN"); 
				features.append("NaN");
				features.append("NaN");
				features.append("NaN");

	
	return features;
		

				
def preprocess_wrapper(args):
	return preprocess(*args);

def read(inp_file, train):
	with open(inp_file, "r") as f:
		header = f.readline().strip().split(',');
		lines  = [];
		for line in f:
			lines.append(line)

	data = [ (lines[i], train) for i in range(0, len(lines)) ];

	#Create a Thread pool.
	pool 		 = Pool(8);
	results 	 = pool.map( preprocess_wrapper, data );
	pool.close();
	pool.join();


	result1 	 = [];
	result2 	 = [];
	for r in results:
		result1.append(r[0]);
		result2.append(r[1]);

	return result1, result2;
				
					 
		
		
	





