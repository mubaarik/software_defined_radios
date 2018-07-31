
from  bitstring import BitArray
import binascii
import time
from threading import Thread
import pandas as pd
import os

##
BIT_ERROR_THRESHOLD = 6;
COVL_RECORDING_THRESHOLD = 6
SEARCH_PACKETS = ["aad6be898ed4e1ab617df259c319a4ab588402cd62fe55c151b508b4880378ab3c2f475f3ce7153da7d7b2",
"aad6be898ed4e0ab617df259c319a4ab5984b1d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9",
"aad6be898ed6e0ab617df259c319a4a95984b1228cab177303314b9c068c6ccba3ec86780d50b9921557dca7",
"aad6be898ed6e1ab617df259c319a4a9588402cd62fe571c85f1dac587fb4dde84eb85171de0153da7d7b2"]

#SEARCH_PACKETS=["aad6be898e95c9bedccf7fc9eff4e48b6ec30212710c","aad6be898e95c9d900e27776daf4e48b6ec3023ee663","aad6be898e95c909c7ec2c1febf4e48b6ec30248a08a","",""]

SEARCH_PACKET = ["aad6be898e95c9","b2647e33cce2","f4e48b6ec302"]
#SEARCH_PACKET = ["aad6be898ed5c9","7366a2569b0b","f4e48b6ec302"]



# "aad6be898e95c95fc641f5caf1f4e48b6ec302","aad6be898ed2c3ab617df259c3","aad6be898e95c9c41e8b8786e9f4e48b6ec302",
# "aad6be898e95c9d588da7ae1d4f4e48b6ec302","aad6be898e95c972c05c9347d5f4e48b6ec302","aad6be898e95c96e238d60a8f5f4e48b6ec302",
# "aad6be898e95c91b146c61bbc2f4e48b6ec302","aad6be898e95c93223856a54eaf4e48b6ec302","aad6be898ed5c9575183a3fb8ff4e48b6ec302"]

def is_cmt_tag(data, target="2cb84c"):
  return target in data
class DataMap:
  def __init__(self):
    self.conv_map = []
  def __save__(self):
    print "saving the data!.........."
    file_name = "data/data_"+self.__getTime__()+'.pickle'
    with open(file_name, 'wb') as f:
      pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
  def __getTime__(self):
    return str(int(time.time()))
  def add(self,data):
    
    self.conv_map.append(data)


class ByteMap:
  def __init__(self, num_items):
    self.arr = [0]*num_items
  def push(self,item):
    self.arr.append(item)
    self.arr.pop(0)
def attach(byte_map):
  mac_address = binascii.hexlify(bytearray(byte_map))


def search_bites(byte1,byte2,gr_buffer,num_bites):
  old_bytes = ByteMap(num_bites);
  for position, byte, in enumerate(gr_buffer):
    
    if byte1==byte and byte2 in old_bytes.arr:
      print "old_bytes:", old_bytes.arr
      print str(byte)+"="+str(byte1)
      print BLE_PREAMBLE
    old_bytes.push(byte)

class Convolution:
  def __init__(self,target, gr_buffer,detected_addr=[]):
    self.target_vect = self.hex_to_binary(target);
    self.search_vect = self.gr_buffer_to_binary_array(gr_buffer)
    

    self.index = 0
    self.n = len(self.target_vect)
    self.conv_map = {};
    #####
    #####
    self.detected_addr = detected_addr
    ###packet max detection
    self.num_elm = 0;
    self.distances = 0;
    self.indices = []


  def convolve(self,structured = False):
    """
    Slide the target vector across the search vector
    """
    while True:
      try:
        ##compute the hammig distances 
        if structured:
          xor_result = self.structured_hamming_dist()
        else:
          xor_result = self.compute_hamming_distance()

        
        if xor_result==None:
          self.set_detections()
          
          return self.conv_map
        if xor_result>self.n-self.n/7:
          #print "value:", xor_result, "n:", self.n
          if xor_result in self.conv_map:
            self.conv_map[xor_result].append(self.index);
          else:
            self.conv_map[xor_result]=[self.index];
            

        self.index+=1;
      except IndexError:
        self.set_detections()
        return self.conv_map
  def set_detections(self):
    """
    set the number of detected close enough portions of the search vector to the target vector
    """
    self.distances = []
    self.indices = []
    self.num_elm = 0
    candidate_indices = range(self.n -BIT_ERROR_THRESHOLD-1, self.n);
    
    self.distances = [d for d in candidate_indices if d in self.conv_map];
    self.indices = [self.conv_map[d] for d in self.distances];
    self.num_elm = sum([len(d) for d in self.indices])

  def compute_hamming_distance(self):
    """
    compute hamming distance between @target_vect and segment of the buffer
    """
    
    xor_segment = self.search_vect[self.index:self.index+self.n];
    
    if len(xor_segment)!=len(self.target_vect):
      return None

    target = self.binary_to_integer(self.target_vect)

    new_segment  = self.binary_to_integer(xor_segment)
 
    return self.n-"{0:b}".format(target^new_segment).count('1');
  def structured_hamming_dist(self,search=SEARCH_PACKET):
    start = self.hex_to_binary(search[0]);
    middle = self.hex_to_binary(search[1]);
    end = self.hex_to_binary(search[2]);

    length = len(start)+len(middle)+len(end);
    xor_segment = self.search_vect[self.index:self.index+length];

    seg_begin = xor_segment[0:len(start)]
    seg_end = xor_segment[-len(end):]

    n_b = "{0:b}".format(int(start,16)^int(seg_begin,16)).count('1');
    if len(end)!=len(seg_end):
      return None
    n_e = "{0:b}".format(int(end,16)^int(seg_end,16)).count('1');
    #print "detection:",self.n -n_b-n_e,"expected:",self.n, "index:",self.index

    return self.n -n_b-n_e



  def hex_to_binary(self,_hex):
    '''
    Examples 
    >>> hex_to_binary('0xfe')
    '11111110'
    '''
    bin_obj = BitArray(hex = _hex);
    return bin_obj.bin;


  def gr_buffer_to_binary_array(self, gr_buff):
    '''
    Examples
    >>> 
    '''
    binary_array = ''
    for position, byte, in enumerate(gr_buff):
      binary_array+=self.get_binary(byte)
    return binary_array


  def get_binary(self,byte_hex, prefix = '0x'):
    '''
    examples 
    >>> get_binary('\xAA')
    '10101010'
    '''
    digits = binascii.hexlify(byte_hex);
    byte_arr =BitArray(hex=prefix+digits);
    return  byte_arr.bin;


  def attach_prefix(self, arr,prefix = '0b'):
    '''
    examples
    >>> attach_prex('01010101')
    '0b01010101'
    >>> >>> attach_prex('01010101',prefix='0x')
    '0x01010101'
    '''
    return prefix+arr;


  def binary_to_integer(self,binary_string):
    '''
    examples
    >>> binary_to_integer('11111111')
    255
    >>> binary_to_integer('0b11111111')
    255
    '''
    #print "n:",self.n
    #print "binary_string: ", binary_string
    try:
      return int(binary_string,2)
    except:
      print "binary_string xun: ", binary_string
  def binary_to_hex(self,binary_arr):
    '''
    examples
    >>> binary_to_hex('1110010010111110111001000010100110011110')
    'e4bee4299e'
    '''
    resulting_hex = hex(int(binary_arr,2))[2:]
    if binary_arr[0:4]=='0000':
      resulting_hex='0'+resulting_hex
    return resulting_hex


  def info(self):
    
    search_len = len(self.target_vect)
    max_match = 0

    if self.conv_map:
      max_match = max(self.conv_map.keys())
    
      
    if max_match>(search_len-1)-BIT_ERROR_THRESHOLD:
      matching_index = min(self.conv_map[max_match])
      strt = max(0,matching_index)


      data = self.binary_to_hex(self.search_vect[matching_index:matching_index+self.n])
      print "detected:",data;
      print "errors:",self.n - max_match
      
      return True
    return False
  def sim_info(self):
    search_len = len(self.target_vect)
    max_match = 0

    if self.conv_map:
      max_match = max(self.conv_map.keys())
    
      
    if max_match>(search_len-1)-BIT_ERROR_THRESHOLD:
      matching_index = min(self.conv_map[max_match])
      strt = max(0,matching_index-8)

      return True
    return False

"""
CODE FOR DETECTING THE PACKETS FROM SPECIFIC TAG

"""
class CollectionThread(Thread):
  def __init__(self, _key_="",_buff_="", err_thresh = BIT_ERROR_THRESHOLD):
    Thread.__init__(self);
    self.data_buffer = _buff_;
    self.key = _key_;
    self.err_thresh = err_thresh
    ##data cutOffs
    self.low_cutOff = 0;
    self.high_cutOff = 0;
    self.filename = "ble_data_files/detection_"+self.key[-8:]+".csv";

  def run(self):
    conv = Convolution(self.key,self.data_buffer,[]);
    conv.convolve();

    max_match = 0
    if conv.conv_map:
      max_match =max(conv.conv_map.keys())

    if max_match>(conv.n-1)-self.err_thresh:
      matching_index = min(conv.conv_map[max_match])
      print "found packet:", self.key[-8:]," matched by: ", max_match, "length was:",conv.n
      

      # _time = time.time()
      # key = self.key;
      # detected = conv.binary_to_hex(conv.search_vect[max(0,matching_index-self.low_cutOff):matching_index+self.high_cutOff])
      # error = conv.n - max_match;
      # context = {"time":_time,"key":key,"detected":detected,"error":error}
      # df = pd.DataFrame([context]);
      # if os.path.exists(self.filename):
      #   df = pd.read_csv(self.filename);
      #   df2 = pd.DataFrame([context]);
      #   df=pd.concat([df,df2],ignore_index=True);
      # df.to_csv(self.filename)

class Expanded:
  def __init__(self, _buff_,keys = SEARCH_PACKETS):
    self._buff_ = _buff_;
    self.keys = keys;
  def __map__(self):
    for key in self.keys:
      collector = CollectionThread(_key_ = key,_buff_ = self._buff_,err_thresh=int(len(key)//2.5));
      collector.low_cutOff = 0
      collector.high_cutOff = len(key)*4;
      collector.start();



def hex_arr_to_hex(hex_arr):
    return binascii.hexlify(bytearray(hex_arr))


def hex_to_byte_arr(hex_str):
  return hex_str.decode('hex');

def hamming2(s1, s2):
  """Calculate the Hamming distance between two bit strings"""
  assert len(s1) == len(s2)
  return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def hex_to_binary(_hex):
  '''
  Examples 
  >>> hex_to_binary('0xfe')
  '11111110'
  '''
  bin_obj = BitArray(hex = _hex);
  return bin_obj.bin;
