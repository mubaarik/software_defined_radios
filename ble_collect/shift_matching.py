import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 


def worker(stream_file, target_vect_file,opt_func):
	##Setup
	file_data = np.fromfile(open(stream_file), dtype=np.complex64);
	target_data = np.fromfile(open(target_vect_file),dtype=np.complex64);
	n = len(file_data)
	m = len(target_data)

	##map
	op_map = []


	shift= 0
	while shift<n-m:
		##
		segment = stream_file[shift:shift+m];

		op_result = opt_func(segment,target_data);

		##Store the result
		op_map.append(op_result);

		#increment
		shift+=1;

##operation functions 

def segment_target_conj_multiply(segment,target):
	"""
	compute the conjugate 
	"""
	target_conj = np.conjugate(target);
	output = np.dot(segment,target_conj);
	return output;
def segment_conj_target_multiply(segment,target):
	"""

	"""
	segment_conj = np.conjugate(segment);
	output = np.dot(segment_conj,target);
	return output; 
def sum_real_imag_multiply(segment,target):
	"""
	"""
	target_sum = np.add(target.real,target.imag);
	segment_sum  = np.add(segment.real,segment.imag);

	output  = np.dot(segment_sum,segment_sum)
	return output 
def multiply_complex_vectors(segment,target):
	"""
	"""

	return np.dot(segment,target);

