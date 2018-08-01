

from bitstring import BitArray
import random
import pandas as pd

TARGET = "d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9"
SAMPLE = "cd62fe55c151b508b4880378ab3c2f475f3ce7153da7d7b24c"
THRESHHOLD = 8
LF = len(TARGET)*4.0
L = len(TARGET)*4

ITERATIONS = 1e6;

TARGET_ARR = BitArray(hex=TARGET);
SAMPLE_ARR = BitArray(hex = SAMPLE);
FILENAME = 'simulations.cvs';

D_FRAME = []




def compute_prob(islands):
	return sum([(n/LF)**2*(n<THRESHHOLD)+((n+1)/LF)*(n<=THRESHHOLD) for n in islands])



def random_mutation():
	for i in range(10000):
		rand_int = random.randint(0,L-1);
		if TARGET_ARR.bin[rand_int]!=SAMPLE_ARR.bin[rand_int]:
			print "before:",SAMPLE_ARR.bin[rand_int]
			SAMPLE_ARR.invert(rand_int);
			print "after:",SAMPLE_ARR.bin[rand_int]
			break
	return SAMPLE_ARR


def simulate():
	i = 0
	try:
		while i<ITERATIONS:
			i+=1;
			bins = SAMPLE_ARR.bin
			random_mutation()
			print "nochange:", bins==SAMPLE_ARR.bin
			error_poses  = [i for i in range(L) if (SAMPLE_ARR.bin[i]!=TARGET_ARR[i])];
			islands = [error_poses[i] -error_poses[i-1]  for i in range(len(error_poses)) if i>0];
			_map_ = {island:0 for island in islands};
			for island in islands:
				_map_[island]+=1;
			prob = {"prob":compute_prob(islands),"islands":_map_.items()};
			D_FRAME.append(prob);
	except:
		data_frame = pd.DataFrame(D_FRAME);
		data_frame.to_csv(FILENAME);
		print "crashed"



if __name__=="__main__":
	simulate()






	
