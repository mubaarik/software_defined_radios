import numpy as np 
import matplotlib.pyplot as plt 
from bitstring import BitArray

PACKET = "11010011011100111000000000110001100000111010101100010000100101010011111001001000100100000011100111011101001110110011011000100011011010100010100111110000101100001100011011111000101110100000000010111001";

LEN = len(PACKET)

FILE_NAME = "/Users/mmohamoud/software_defined_radios/ble_collect/demodulated_files/redesigned";

FILE_DATA =  np.fromfile(open(FILE_NAME), np.ubyte).tolist()

CURRENT_BINARY = "";
THRESHOLD=0.70

def compute_prob(_binary_):
	'''
	data
	'''
	islands= 0;
	polar = 1;
	size = 0;
	i = 0;
	while i<len(PACKET):
		if polar==1:
			if _binary_[i]==PACKET[i]:
				size+=1;
			else:
				polar=-1;
				islands+=1;
				size=1;
		else:
			if  _binary_[i]!=PACKET[i]:
				size+=1;
			else:
				polar=-1;
				islands+=1;
				size=1;
		i+=1;
	return (LEN*1.0 - islands)/LEN

i=0;
while(FILE_DATA):
	integer =  FILE_DATA.pop(0);
	i+=1
	if i <10:
		print "integer:",integer

	binary = "{0:b}".format(integer);

	binary = "0"*(8-len(binary))+binary;

	CURRENT_BINARY+=binary;

	if len(CURRENT_BINARY)==LEN:
		# print "reading the book"
		prob = compute_prob(CURRENT_BINARY);
		

		if prob>THRESHOLD:
			print "packet:",BitArray('0b'+CURRENT_BINARY).hex,"prob:",prob
			print "binary:",CURRENT_BINARY
		#print "data:",len(CURRENT_BINARY)
		CURRENT_BINARY = CURRENT_BINARY[8:];



