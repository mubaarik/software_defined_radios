from grc.usrp_out import usrp_out as grblock

from datetime import datetime, timedelta
from proto import *

from copy import deepcopy

import itertools
from threading import Thread

import numpy as np
import pandas as pd
import os
import time
import random
##########
from optparse import OptionParser, OptionGroup
from gnuradio.eng_option import eng_option
from bitstring import BitArray
import numpy as np

############
############
'''
constants
'''
############
############

####ERROR constants 
PRE_ERROR_LIMIT = 4
PAYLOAD_ERROR_LIMIT = 21


####
characters = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"];
BYTES = [a+b for a in characters for b in characters];
#pre-amble and access code data
PREA_AND_ADDR_STR = "aad6be898e"
PREA_AND_ADDR = [PREA_AND_ADDR_STR[st:st+2] for st in range(len(PREA_AND_ADDR_STR)) if st%2==0]
PREA_AND_ADDR_LEN = len(PREA_AND_ADDR);
###

def compute_map(_byte,index,equal = True):
  data_points = {};
  for b in BYTES:
    if equal:
      data_points[(_byte,b)]=[index*8+i for i in range(8) if BitArray(hex=b).bin[i]==BitArray(hex=_byte).bin[i]];
    else:
      data_points[(_byte,b)]=[index*8+i for i in range(8) if BitArray(hex=b).bin[i]!=BitArray(hex=_byte).bin[i]];
  return data_points;







# packet of interest
PACKET_BODY_STR="d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9"#"d4e0ab617df259c319a4ab5984b1d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9"
PACKET_BODY = [PACKET_BODY_STR[st:st+2] for st in range(len(PACKET_BODY_STR)) if st%2==0] #"b1d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9";

PACKET_BYTE_MAP = []
LF = len(PACKET_BODY_STR)*4.0;
L =  len(PACKET_BODY_STR)*4;

#####PROBABILITY THRESHOLD
THRESHOLD=0.65;

##
PACKET_ARRAY = BitArray(hex = PACKET_BODY_STR).bin;
#PARKED_PACKET
PACKET_BODY_LEN = len(PACKET_BODY);

##hamming distance map

CHAR_DISTS = {(i,j):bin(int(i,16)^int(j,16)).count('1') for i in characters for j in characters}

###equality map
PACKET_EQUAL_MAP ={}
for i in range(len(PACKET_BODY)):
  PACKET_EQUAL_MAP.update(compute_map(PACKET_BODY[i],i));

####equality difference map
EQUAL_DIFF_MAP = {i:[j for j in np.diff(PACKET_EQUAL_MAP[i]) if j>1] for i in PACKET_EQUAL_MAP}
#EQUAL_DIFF_MAP = {key:EQUAL_DIFF_MAP[key] for key in EQUAL_DIFF_MAP if EQUAL_DIFF_MAP[key]}


###difference map 
PACKET_DIFF_MAP = {}
for i in range(len(PACKET_BODY)):
  PACKET_DIFF_MAP.update(compute_map(PACKET_BODY[i],i,equal=False));


###difference difference map
DIFF_DIFF_MAP = {i:[j for j in np.diff(PACKET_DIFF_MAP[i]) if j>1] for i in PACKET_DIFF_MAP}
#DIFF_DIFF_MAP = {key:DIFF_DIFF_MAP[key] for key in DIFF_DIFF_MAP if DIFF_DIFF_MAP[key]}





#####################
#####################
'''
debug and control functions
'''
####################
####################


# Print current Gnu Radio capture settings
def print_settings(gr, opts):
  print '\n ble-dump:  SDR Bluetooth LE packet dumper'
  print '\nCapture settings:'
  
  print ' %-22s: %s Hz' % ('Sample rate', '{:d}'.format(int(gr.get_sample_rate())))
  



# Setup Gnu Radio with defined command line arguments
def init_args(gr, opts,filename):
  gr.set_sample_rate(int(opts.sample_rate))
  gr.set_filename(filename)

# Initialize command line arguments
def init_opts(gr):
  parser = OptionParser(option_class=eng_option, usage="%prog: [opts]")

  # Capture
  capture = OptionGroup(parser, 'Capture settings')
  capture.add_option("-o", "--pcap_file", type="string", default='', help="PCAP output file or named pipe (FIFO)")
  capture.add_option("-m", "--min_buffer_size", type="int", default=95, help="Minimum buffer size [default=%default]")
  capture.add_option("-s", "--sample-rate", type="eng_float", default=gr.sample_rate, help="Sample rate [default=%default]")
  #capture.add_option("-f", "--filename", type="eng_float", default=gr.filename, help="Squelch threshold (simple squelch) [default=%default]")

  

  parser.add_option_group(capture)
  
  return parser.parse_args()





HOPE_SIZE = 10;
GAIN = 40

class Circular:
  def __init__(self):
    self.base = "/Users/mmohamoud/software_defined_radios/ble_collect/test_files/"
    self.files = ["file_zero","file_one","file_two","file_three","file_four","file_five","file_six","file_seven","file_eight","file_nine"];
    self.meta_file = "meta_file.csv"
    self.meta = {}
    self.current_file = self.files[-1]
    self.update_meta()
  def update_meta(self):
    if self.meta =={}:
      self.meta = {filename:time.time() for filename in self.files};
      pd.DataFrame([self.meta]).to_csv(self.base+self.meta_file);
    else:
      self.meta[self.current_file] = time.time();
      pd.DataFrame([self.meta]).to_csv(self.base+self.meta_file);
  def set_current(self):
    self.current_file = self.files.pop(0);
    self.files.append(self.current_file);
  def set_rand_current(self):
    rand_int = random.randint(0,10);
    if len(self.files)<9:
      print "data"
    self.current_file = self.files.pop();
    self.files.append(self.current_file);

def worker():
  # Initialize Gnu Radio
  gr_block = grblock()
  gr_block.start()

  #####circular
  circular = Circular()
  filename = circular.base+circular.current_file;


  # Initialize command line arguments
  (opts, args) = init_opts(gr_block)

  if not opts.pcap_file:
    print '\nerror: please specify pcap output file (-p)'
    exit(1)

  

  # Set Gnu Radio opts
  init_args(gr_block, opts,filename)

  # Print capture settings
  print_settings(gr_block, opts)

  # Open PCAP file descriptor
  pcap_fd = open_pcap(opts.pcap_file)

  current_hop = 1
  hopping_time = datetime.now() + timedelta(seconds=HOPE_SIZE)

  try:
    
    while True:

      if datetime.now()>hopping_time:
        circular.set_rand_current()
        filename = circular.base+circular.current_file;
        gr_block.set_filename(filename);
        circular.update_meta();
        hopping_time = datetime.now() + timedelta(seconds=HOPE_SIZE);


  except KeyboardInterrupt:
    pass
  gr_block.stop()
  gr_block.wait()
if __name__=="__main__":
  worker()