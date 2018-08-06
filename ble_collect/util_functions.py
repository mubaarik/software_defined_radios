from bitstring import BitArray
import random
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt


TARGET = "d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9"

SAMPLE = "cd62fe55c151b508b4880378ab3c2f475f3ce7153da7d7b24c"

PATH = "/Users/mmohamoud/Documents/transfer_curves/"
THRESHHOLD = 8
LF = len(TARGET)*4.0
L = len(TARGET)*4

ITERATIONS = 10000;

BASE = 1.2

TARGET_ARR = BitArray(hex=TARGET);
SAMPLE_ARR = BitArray(hex = TARGET);

REDISTRIBUTION_ISLAND_MAP = {
	"divisions_1_2_3_4": (1,2,3,4),
	"divisions_1_4_1_4":(1,4,1,4),
	"divisions_0_3_5_7":(0,3,5,7),
	"divisions_2_4_6_3":(2,4,6,3)
}

ERR_FREE_MAP = {
	"err_free_12_12_12":(12,12,12),
	"err_free_16_16_16":(16,16,16),
	"err_free_24_16_12":(24,16,12),
	"err_free_24_48_8":(24,48,8)
}

ERR_PERCENTS = {
	"err_percents_10_20_30":(.10,.20,.30),
	"err_percents_10_20_40":(.10,.20,.40),
	"err_percents_10_20_50":(.10,.20,.50),
	"err_percents_10_30_40":(.10,.30,.40),
	"err_percents_10_30_50":(.10,.30,.50),
	"err_percents_20_30_50":(.20,.30,.50),
	"err_percents_10_50_40":(.10,.50,.40)
}

for i in range(L):
	if i%2==0:
		SAMPLE_ARR.invert(i);

FILENAME = 'simulations.cvs';

D_FRAME = []




def drop_uniform_errors(sample_arr, percent):
	ranges = range(L);
	i=0
	while i<=int(L*percent):
		i+=1
		ch = random.choice(ranges)
		ranges.remove(ch)
		sample_arr.invert(ch);
	return sample_arr

def varying_err_rate(sample_arr,percent,divisions=(.10,.20,.30)):

	segments = [(L/(2*len(divisions))*i+L/2,L/(len(divisions)*2)*(i+1)+L/2) for i in range(len(divisions))];
	for ind,segment in enumerate(segments):
		ranges = range(segment[0],segment[1]);
		i=0
		while i<(segment[1]-segment[0])*divisions[ind]:
			char = random.choice(ranges);
			sample_arr.invert(char);
			i+=1
		i=0
		ranges = range(L/2)
		while i<(L/2)*percent:
			char = random.choice(ranges);
			sample_arr.invert(char);
			i+=1

	return sample_arr
	 




def error_free_segments(sample_arr,percent,divisions = (12,12,12)):
	
	insert = (L-(L/sum(divisions))*sum(divisions))/len(divisions);
	start = insert;
	sample_arr = drop_uniform_errors(sample_arr, percent)


	for segment in divisions:
		#print "segment:",segment, "start:",start
		for i in range(start,start+segment):
			sample_arr.set(int(TARGET_ARR.bin[i]), i);
		start+=segment+insert;
	return sample_arr;



def drop_islands(sample_arr,percent, divisions=(1,3,5)):
	lines = []
	last = 0
	divs = L/len(divisions);
	for ind,div in enumerate(divisions):
		l=int((LF/sum(divisions))*divisions[ind]*percent);
		
		lines.append(l);
	start = 0
	for line in lines:
		i=0
		ranges = range(start,start+divs)
		if len(ranges)<line:
			print""
			print "line:",line,"ranges:",len(ranges)
			print ""
		while i<=line:
			i+=1;
			char = random.choice(ranges);
			ranges.remove(char);
			sample_arr.invert(char);
		start+=divs;
	return sample_arr;

		

#drop_islands(BitArray(hex=TARGET), .5)


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
	
	for islnd in pos_islands:
		if islnd>1:
			islands+=1.0;
	for island in neg_islands:
		if island>1:
			islands+=1.0;
	
	return (LF-islands)/LF;



def probability(target,sample,obj_function = run_based_model):
	"""
	definition:
	"""
	pos_error_poses = [i for i in range(L) if sample.bin[i]!=target.bin[i]];
	neg_error_poses = [i for i in range(L) if sample.bin[i]==target.bin[i]];

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


	###
	return obj_function(pos_islands,neg_islands)