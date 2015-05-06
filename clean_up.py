import sys;


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



def clean(myfile):
  data = [];

  with open(myfile, "r") as f:

    header = f.readline().strip().split(',')

    X      = [];
    Y      = [];
    count  = 0;
    for line in f:
    	if count % 10000 == 0:
    		print("Read " + str(count) + " lines");
    	count += 1;
    	
        x = line.strip().split(',');

        radar_pos_time = identify_radar_end_points(x[1].split(), "time");
        radar_pos_dis  = identify_radar_end_points(x[2].split(), "distance");

        #Output multiple data points for this gauge
        data_points_X  = [];
        data_points_Y  = [];

        for i in range(0, len(x[1].split())):
        	data_points_X.append( [int(x[0])] ); #Append Gauge Id

        for i in range(1, len(x) - 1):
           readings = x[i].split();
           for j in range(0,len(readings)):
           	  if readings[j] != 'nan':
           	  	 data_points_X[j].append(float(readings[j]));
           	  else:
           	     data_points_X[j].append("nan");


        for j in range(0, len(x[1].split())):
        	data_points_Y.append(float(x[len(x)-1]));
        
    	X.extend(data_points_X);
    	Y.extend(data_points_Y);

    assert(len(X) == len(Y))






if __name__ == "__main__":
   clean('./data/train_2013.csv');
   clean('./data/test.csv');