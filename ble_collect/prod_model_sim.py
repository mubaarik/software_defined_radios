

from bitstring import BitArray
import random
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

TARGET = "d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9"

SAMPLE = "cd62fe55c151b508b4880378ab3c2f475f3ce7153da7d7b24c"
THRESHHOLD = 8
LF = len(TARGET)*4.0
L = len(TARGET)*4

ITERATIONS = 1000;

BASE = 1.2

TARGET_ARR = BitArray(hex=TARGET);
SAMPLE_ARR = BitArray(hex = TARGET);

for i in range(L):
	if i%2==0:
		SAMPLE_ARR.invert(i);

FILENAME = 'simulations.cvs';

D_FRAME = []

__MAP__ = []

def drop_islands(sample_arr,percent,island_size=3, divisions=(1,3,5)):
	lines = []
	last = 0
	for ind,div in enumerate(divisions):
		l=(L/sum(divisions))*divisions[ind];
		
		lines.append((last,last+l))
		last+=l
		else:
			lines.append((lines[ind],))

	l1 = (L/sum(divisions))*divisions[0];
	l2 = (L/sum(divisions))*divisions[1];
	l3=(L/sum(divisions))*divisions[3];


def drop_uniform_errors(sample_arr, percent):
	ranges = range(L);
	i=0
	while i<=int(L*percent):
		i+=1
		ch = random.choice(ranges)
		ranges.remove(ch)
		sample_arr.invert(ch);
	return sample_arr

def obj_total(islands):
	return sum([(n/LF)**2*(n<THRESHHOLD)+((n+1)/LF)*(n<=THRESHHOLD) for n in islands])

def obj_power_count(islands,offset=3):
	prob = 1.0

	for island in islands:
		prob*=max(island-offset,1.0);

	return 1.0 - 1.0/prob
def obj_exponent(pos_islands,neg_islands,offset=1):
	p_prob = 1.0
	n_prob = 1.0

	for island in pos_islands:
		p_prob*=(BASE)**max(island-offset,0);
	for island in neg_islands:
		n_prob*=(BASE)**max(island-offset,0);

	#print "prob:", prob
	return 1.0 - min(1,n_prob/p_prob)


def run_based_model(pos_islands,neg_islands):
	islands = 0.0
	print len(pos_islands),len(neg_islands)
	for islnd in pos_islands:
		if islnd>1:
			islands+=1.0;
	for island in neg_islands:
		if island>1:
			islands+=1.0;
	print islands
	print (LF-islands)/LF
	return (LF-islands)/LF;



def percent_mutations(percent=0.20):
	pass


def random_mutation():
	for i in range(10000):
		rand_int = random.randint(0,L-1);
		if TARGET_ARR.bin[rand_int]!=SAMPLE_ARR.bin[rand_int]:
			
			SAMPLE_ARR.invert(rand_int);
			
			break
	for i in range(3):
		rand_int = random.randint(0,L-1);
		SAMPLE_ARR.invert(rand_int)
	return SAMPLE_ARR


def simulate(objective_function):
	i = 0
	try:
		while i<ITERATIONS:
			i+=1;
			
			#print "nochange:", bins==SAMPLE_ARR.bin
			pos_error_poses  = [i for i in range(L) if SAMPLE_ARR.bin[i]!=TARGET_ARR.bin[i]];
			neg_error_poses = [i for i in range(L) if SAMPLE_ARR.bin[i]==TARGET_ARR.bin[i] ]
			# error_poses = []
			# for i in range(L):
			# 	if SAMPLE_ARR.bin[i]!=TARGET_ARR.bin[i]:
			if not 0 in pos_error_poses:
				pos_error_poses=[0]+pos_error_poses
			if not L-1 in pos_error_poses:
				pos_error_poses.append(L-1)
			if not 0 in neg_error_poses:
				neg_error_poses=[0]+neg_error_poses
			if not L-1 in neg_error_poses:
				neg_error_poses.append(L-1)

			pos_islands = [pos_error_poses[i] -pos_error_poses[i-1]  for i in range(len(pos_error_poses)) if i>0];
			neg_islands = [neg_error_poses[i] -neg_error_poses[i-1]  for i in range(len(neg_error_poses)) if i>0];


			pos_map_ = {island:0 for island in pos_islands};
			neg_map_ = {island:0 for island in neg_islands};
			for island in pos_islands:
				pos_map_[island]+=1;
			for island in neg_islands:
				neg_map_[island]+=1;
			prob = {"prob":objective_function(pos_islands,neg_islands),"neg_max": max(neg_islands),"pos_max":max(pos_islands),"pos_islands":pos_map_.items(),"neg_islands": neg_map_.items()};
			#print prob
			D_FRAME.append(prob);
			random_mutation()
			if len(pos_islands)==1:
				break
	except:
		data_frame = pd.DataFrame(D_FRAME);
		data_frame.to_csv(FILENAME);
		print "crashed"
		return
	data_frame = pd.DataFrame(D_FRAME);
	data_frame.to_csv(FILENAME);
def bit_error_rate(objective_function):
	percent_list = [i*.1 for i in range(1,6)]

	for percent in percent_list:
		prob = []
		for i in range(ITERATIONS):
			SAMPLE_ARR = drop_errors(BitArray(hex = TARGET),percent);
			pos_error_poses  = [i for i in range(L) if SAMPLE_ARR.bin[i]!=TARGET_ARR.bin[i]];
			neg_error_poses = [i for i in range(L) if SAMPLE_ARR.bin[i]==TARGET_ARR.bin[i] ]
			


			if not 0 in pos_error_poses:
				pos_error_poses=[0]+pos_error_poses
			if not L-1 in pos_error_poses:
				pos_error_poses.append(L-1)
			if not 0 in neg_error_poses:
				neg_error_poses=[0]+neg_error_poses
			if not L-1 in neg_error_poses:
				neg_error_poses.append(L-1)


			pos_islands = [pos_error_poses[i] -pos_error_poses[i-1]  for i in range(len(pos_error_poses)) if i>0];
			neg_islands = [neg_error_poses[i] -neg_error_poses[i-1]  for i in range(len(neg_error_poses)) if i>0];

			p=objective_function(pos_islands,neg_islands)
			prob.append(p)
		__MAP__.append((percent,sorted(prob)))







def plot_data_frame(x,y):
	fig = plt.figure(figsize=(30,5))
	ax = fig.add_subplot(111)
	print "x:",x[0:40],"length:",len(x)
	print "y:",y[0:40],"length:",len(x)
	
	ax.plot(x,y);
	plt.show()
def multi_plot(Y):
	fig = plt.figure(figsize=(30,5))
	ax = fig.add_subplot(111)
	for y in Y:
		label = str(int(y[0]*100))+"%"
		x = range(len(y[1]));
		y = y[1];
		
		ax.plot(y,x,label=label)
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.show()
#multi_plot([(0.5,[12,23,4,4,5,23,23,4,4,2,2]),(0.4,[12,3,5,6,5,3,3,4,4,2,2])])



if __name__=="__main__":
	bit_error_rate(run_based_model);
	# print "exiting"
	# x = [d[0] for d in __MAP__]
	# y = [d[1] for d in __MAP__]

	#plot_data_frame(x,y)
	multi_plot(__MAP__);






	
