### Tests for the util functions

from ble_dump_utils import *
##CONSTANTS
GR_BUFFER = ''.join(['\xe4', '\xbe', '\xe4', ')', '\x9e', 'w', '1', '\xf1', '\xbc', '\xd1', '\xd4', ')', '\x9d', ' ', '\x08', 'j', '\xf9', ']', '\xea', '\xb4', '\xd1', '\x81', ',', '-', '\xe9', '\xe2', '\xdd', 'R', '\x86', 'c', 'r', 'e', '\xd6', '2', '\x13', '3', '\x13', '[', ']', '\xea', 'q', 'o', '\x19', 't', '\xff', '<', '\xb2', '\xb6', '8', '\x0b', '\xe0', '-', 'a', 'M', 'K', '\x9a', '\x9e', '\xcf', 'Y', '\xca', '\x81', '"', '*', '\x99', '\x8a', '\xcb', ':', '\xdc', '\x1b', '\xa8', '\xb5', 'd', '\x19', '\xbe', '\xff', '\xd6', '\t', 'w', '|', '\xb2', '\\', '*', 'l', '\x1d', '.', '\x13', '<', '\x7f', '\xaa', '\xaa', '\xd6', '\xbe', '\x89', '\x8e', '\xcd', '\xc3', '\xf9', '\xc1', '\xdb', '\xbc', 'w', '\xc4', 'w', '0', '\x17', 'O', 'i', ';', '\xf8', '\xf3', 'D', '\xe2', '\xab', 'U', '\xd2', 'M', '[', ')', '\x17', '|', '\xab', '\xec', 'L', '\x11', '\x13', '\xb0', '\xfb', '/', '\xb8', '\x17', '{', '\n', 'r', '\x89', '8', '\xc7', '\x06', '\xfa', '\xbd', '\xd5', '\x08', '\x97', 'C', '\xee', 'F', '\x83', '*', '\xcc', '\xaf', '\xfa', '\x1e', '\xa3', 'q', '$', 'Y', '\x10', '\x93', 'O', ']', '\xb0', '\xff', '\xa7', 'y', '0', 'M', 'M', '\xe4', 'h', 'l', '\x9c', '_', '$', 'b', ')', ')', '\x05', "'", '-', '>', '\xc4', '\x82'])
TARGET_VECT = "aad6be898e"

#print "buffer", GR_BUFFER

### Testing match filter class 

conv = Convolution(TARGET_VECT, GR_BUFFER);

## testing convolve 
expected_map = {40:[712]}

def test_convolve():
	conv_map = conv.convolve();
	print conv_map
	assert len(conv_map)==len(expected_map), "The generated map doesn't have the same length as the expect map";
	assert all([ind in expected_map for ind in conv_map]), "The generated map doesn't contain the same elements as the expected map";
	assert all([len(expected_map[ind])==len(conv_map[ind]) for ind in conv_map]), "The generated map doesn't seem to contain the same data as the expect map";

test_convolve();


##testing compute hamming distance 

def test_compute_hammming_distance(index, expected_dist):
	conv.index = index;

	hamming_dist  =  conv.compute_hamming_distance();
	assert (hamming_dist==expected_dist), "Found the hamming distance of "+str(hamming_dist)+" at index "+str(index)+" expected hamming distance was "+str(expected_dist)

dist_map = {0: 26,28: 20 ,40: 13}
for ind in dist_map:
	conv.index = ind;
	test_compute_hammming_distance(ind, dist_map[ind])





## test hex_to_binary
def test_hex_to_binary(in_hex, expected_bin):
	out_bin = conv.hex_to_binary(in_hex);
	assert (out_bin==expected_bin), "Found the binary "+str(out_bin)+" hex "+str(in_hex)+" expected "+str(expected_bin)

hex_binary_map = [("e4bee4299e",'1110010010111110111001000010100110011110'),("7731f1bcd1",'0111011100110001111100011011110011010001'),("99e7731f1b",'1001100111100111011100110001111100011011')]
for h,b in hex_binary_map:
	test_hex_to_binary(h,b)




## test buffer to binary array

def test_gr_buffer_to_binary_array(buff, binary_arr):
	out_binary = conv.gr_buufer_to_binary_array(buff)
	assert (buff==binary_arr), 'found the binary string'+str(out_binary)+ " for buffer "+str(buff)+" expected "+str(binary_arr)

buffer_binary_map = []

for buff,binary in buffer_binary_map:
	test_gr_buffer_to_binary_array(buff,binary)





## test get binary

def test_get_binary(byte_str,expected_bin):
	out_binary = conv.get_binary(byte_str);
	assert(out_binary==expected_bin),"Found the binary string"+str(out_binary)+" for byte string "+str(byte_str)+" expected binary string "+str(expected_bin)

byte_str_to_binary_str_map = []
for byte,binary in byte_str_to_binary_str_map:
	test_get_binary(byte,binary)