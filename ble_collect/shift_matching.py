import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 


def worker(stream_file, target_vect_file,opt_func, start_frac = 0,end_frac = 1):
	##Setup
	file_data = np.fromfile(open(stream_file), dtype=np.complex64);
	target_data = np.fromfile(open(target_vect_file),dtype=np.complex64);
	n = len(file_data)
	m = len(target_data)
	file_data = file_data[int(start_frac*n):int(end_frac*n)]
	n = len(file_data)

	##map
	op_map = []


	shift= 0
	while shift<n-m:
		##
		segment = file_data[shift:shift+m];

		op_result = opt_func(segment,target_data);

		##Store the result
		op_map.append(op_result);

		#increment
		shift+=1;
	return np.array(op_map)

##operation functions 

def segment_target_conj_multiply(segment,target):
	"""
	compute the conjugate 
	"""
	target_conj = np.conjugate(target);
	output = np.dot(segment,target_conj);
	return output.real+output.imag;
def segment_conj_target_multiply(segment,target):
	"""

	"""
	segment_conj = np.conjugate(segment);
	output = np.dot(segment_conj,target);
	return output;
def segment_conj_target_prod_sq(segment,target):
	"""
	"""
	return np.absolute(segment_conj_target_multiply(segment,target));




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
def absolute_difference(segment,target):
	"""
	"""
	result = np.absolute(np.subtract(segment,target));
	return result
def diff_real_imag_prod(segment,target):
	"""
	"""
	result= np.dot(segment,target)
	return result.imag-result.real;
def norm_segment_target_sum(segment,target):
	"""
	"""
	result = np.add(segment,target)
	return sum(np.absolute(result))
def sign_addition(a,b):
	"""
	"""
	if a*b>0:
		return abs(a+b);
	return -(abs(a)+abs(b))
def signed_addition_of_vectors(a,b):
	"""
	"""
	f = np.vectorize(sign_addition);
	return f(a,b);
def signed_addition_real_imag_parts(segment,target):
	"""
	"""
	return np.sum(np.add(signed_addition_of_vectors(segment.real,target.real),signed_addition_of_vectors(segment.imag,target.imag)))
def sum_real_parts_of_conj_multi(segment,target):
	"""
	"""
	conj = np.conjugate(segment);
	prod = np.multiply(conj,target)
	real = np.sum(prod.real)
	return real
def fft_matching(segment,target):
	"""
	1. take the fourier transform
	2. lowpass filter
	3. take the inverse fourier transform
	"""

	return 
def band_pass_filter(fft_signal, cuttoff_freq=850e6):
	"""
	1. band pass filter 
	"""
	return 




