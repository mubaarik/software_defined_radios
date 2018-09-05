import pandas as pd 
import numpy as np
import time
import os 
FILE_NAME = 'time_stamps.csv'

if __name__=="__main__":
	if os.path.exists(FILE_NAME):
		print "file exits"
		df = pd.read_csv(FILE_NAME);
	else:
		print "file doesn't"
		context = {'time': time.time(),"point":0};
		df = pd.DataFrame([context]);
	max_time=max(df['point'].values)
	print max_time
	context = {'time':time.time(),"point":float(max_time)+1};
	df2 = pd.DataFrame([context])
	df = df.T.to_dict().values()
	for dicts in df:
		if 'Unnamed: 0' in dicts:
			del dicts['Unnamed: 0']
	df.append(df2);
	df = pd.DataFrame(df);
	df.to_csv(FILE_NAME);
	
	