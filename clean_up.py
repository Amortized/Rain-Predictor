import sys;
from debian.debtags import output


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
		elif metric == "distance" and float(readings[k]) <> prev:   
		   #Diff radar
		   radar_pos.append((start,end));
		   start = k;
		   end   = k;
		   prev  = float(readings[k]);

	radar_pos.append((start,end));
	return radar_pos;



def clean(inp_file, output_file, train):
  data = [];
  
  file_output = open(output_file, 'w');
  
  X	  = [];
  Y	  = [];
  
  with open(inp_file, "r") as f:

    header = f.readline().strip().split(',')

    count  = 0;
    for line in f:
    	
    	if count % 10000 == 0:
    		print("Read " + str(count) + " lines");
    	
    	count += 1;
    	
        x = line.strip().split(',');
        
        label_range = len(x);
        if train:
			label_range = len(x) - 1;
			

        
        radar_pos_time = identify_radar_end_points(x[1].split(), "time");
        radar_pos_dis  = identify_radar_end_points(x[2].split(), "distance");

        #Output multiple data points for this gauge
        data_points_X  = [];
        data_points_Y  = [];

        for i in range(0, len(x[1].split())):
           data_points_X.append( [int(x[0])] ); #Append Gauge Id

        for i in range(1, label_range):
           readings = x[i].split();
           for j in range(0,len(readings)):
           	  if readings[j] != 'nan':
           	  	 data_points_X[j].append(float(readings[j]));
           	  else:
           	     data_points_X[j].append("nan");
           del readings;
        
        if train:
           for j in range(0, len(x[1].split())):
              data_points_Y.append(float(x[len(x)-1]));
        
    	X.extend(data_points_X);
    	Y.extend(data_points_Y);
    	
    	if len(X) > 50:
    		for k in range(0, len(X)):
    			if train:
	    			for z in X[k]:
	    			   file_output.write(str(z) + ",");
		    		file_output.write(str(Y[k]));
		    	else:
		    		for z in range(0, len(X[k])):
		    		   file_output.write(str(X[k][z]));
		    		   if z < len(X[k]) - 1:
		    		   	  file_output.write(",")
		    		
	    		file_output.write("\n");
	    		
	    	X = [];
	    	Y = [];
	    		 
    
    
	
  for k in range(0, len(X)):
  	if train:
  		for z in X[k]:
  			file_output.write(str(z) + ",");
  		file_output.write(str(Y[k]));
	else:
		for z in range(0, len(X[k])):
			file_output.write(str(X[k][z]));
			if z < len(X[k]) - 1:
				file_output.write(",")
	
	file_output.write("\n");
				
  file_output.close();





if __name__ == "__main__":
   clean('./data/train_2013.csv', './data/train_preprocessed.csv', True);
   clean('./data/test_2014.csv', './data/test_preprocessed.csv', False);