
from  bitstring import BitArray
import binascii
import time
from threading import Thread

##
BIT_ERROR_THRESHOLD = 2;
COVL_RECORDING_THRESHOLD = 6

def is_cmt_tag(data, target="b84c020"):
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
  def __init__(self,target, gr_buffer,detected_addr):
    self.target_vect = self.hex_to_binary(target);
    self.search_vect = self.gr_buffer_to_binary_array(gr_buffer)
    

    self.index = 0
    self.n = len(self.target_vect)
    self.conv_map = {};
    #####
    #####
    self.detected_addr = detected_addr
  def convolve(self):
    while True:
      try:
        xor_result = self.compute_hamming_distance()
        
        if xor_result==None:
          return self.conv_map
        if xor_result>self.n-COVL_RECORDING_THRESHOLD:
          if xor_result in self.conv_map:
            self.conv_map[xor_result].append(self.index);
          else:
            self.conv_map[xor_result]=[self.index];
            

        self.index+=1;
      except IndexError:
        return self.conv_map


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
      strt = max(0,matching_index-8)

      data = self.binary_to_hex(self.search_vect[matching_index:matching_index+9*search_len])
      self.detected_addr.append(data)
      print "detected:", data
      return True
    #print "found nothing"
    return False

class CollectionThread(Thread):
  def __init__(self, _key_="",_buff_="", err_thresh = BIT_ERROR_THRESHOLD):
    Thread.init(self);
    self.data_buffer = _buff_;
    self.key = _key_;
    self.err_thresh = err_thresh
    ##data cutOffs
    self.low_cutOff = 0;
    self.high_cutOff = 0;
    self.filename = "ble_data_files/detection_"+self.key+".csv";

  def run(self):
    conv = Convolution(self.key,self.data_buffer);
    conv.convolve();

    max_match = 0
    if conv.conv_map:
      max_match =max(conv.conv_map.keys())

    if max_match>(conv.n-1)-self.err_thresh:
      matching_index
      

      time = time.time()
      key = self.key;
      detected = self.binary_to_hex(self.search_vect[max(0,matching_index-low_cutOff):matching_index+high_cutOff])
      error = conv.n - max_match;
      context = {"time":time,"key":key,"detected":detected,"error":error}

      df = pd.read_csv(self.filename);
      df2 = pd.DataFrame(context);
      df.append(df2);
      df.to_csv(self.filename)
class Expanded:
  def __init__(self, _buff_,keys = []):
    self._buff_ = _buff_;
    self.keys = keys;
  def __map__(self):
    for key in self.keys:
      collector = CollectionThread(_key_ = key.key,_buff_ = self._buff_,err_thresh=key.err_thresh);
      collector.low_cutOff = key.low_cutOff;
      collector.high_cutOff = key.high_cutOff;
      collector.start();
class SrchKey:
  def __init__(self,key,low_cutOff,high_cutOff,err_thresh):
    self.key = key;
    self.low_cutOff = low_cutOff;
    self.high_cutOff = high_cutOff;
    self.err_thresh = err_thresh;




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
