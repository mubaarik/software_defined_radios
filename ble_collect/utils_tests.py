### Tests for the util functions

from ble_dump_utils import *
##CONSTANTS 
GR_BUFFER = None
TARGET_VECT = None

### Testing match filter class 

conv = Convolution(TARGET_VECT, GR_BUFFER);

## testing convolve 
expected_map = {}

def test_convolve():
	conv_map = conv.convolve();
	assert len(conv_map)==len(expected_map), "The generated map doesn't have the same length as the expect map";
	assert all([ind in expected_map for ind in conv_map]), "The generated map doesn't contain the same elements as the expected map";
	assert all([len(expected_map[ind])==len(conv_map[ind]) for ind in conv_map]), "The generated map doesn't seem to contain the same data as the expect map";


	

##testing compute hamming distance 

def test_compute_hammming_distance(index, expected_dist):
	conv.index = index;

	hamming_dist  =  conv.compute_hamming_distance();
	assert (hamming_dist==expected_dist), "Found the hamming distance of",hamming_dist,"at index",index, "expected hamming distance was", expected_dist

dist_map = {}
for ind in dist_map:
	test_compute_hammming_distance(ind, dist_map[ind])





## test hex_to_binary
def test_hex_to_binary(in_hex, expected_bin):
	out_bin = conv.hex_to_binary(in_hex);
	assert (out_bin==expected_bin), "Found the binary", out_bin, "hex", in_hex,"expected",expected_bin

hex_binary_map = []
for h,b in hex_binary_map:
	test_hex_to_binary(h,b)




## test buffer to binary array

def test_gr_buffer_to_binary_array(buff, binary_arr):
	out_binary = conv.gr_buufer_to_binary_array(buff)
	assert (buff==binary_arr), 'found the binary string', out_binary, "for buffer", buff,"expected", binary_arr

buffer_binary_map = []

for buff,binary in buffer_binary_map:
	test_gr_buffer_to_binary_array(buff,binary)





## test get binary

def test_get_binary(byte_str,expected_bin):
	out_binary = conv.get_binary(byte_str);
	assert(out_binary==expected_bin),"Found the binary string",out_binary, "for byte string",byte_str,"expected binary string", expected_bin

byte_str_to_binary_str_map = []
for byte,binary in byte_str_to_binary_str_map:
	test_get_binary(byte,binary)