from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from grc.gr_ble_file import gr_ble_file as grblock

from datetime import datetime, timedelta
from proto import *

from copy import deepcopy
from packet_search_v2_utils import *
import itertools
from threading import Thread

import numpy as np
import pandas as pd
import os
import time


HOPE_SIZE = 30;
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
    if meta =={}:
      self.meta = {filename:time.time() for filename in self.files};
      pd.DataFrame(meta).to_csv(self.base+self.meta_file);
    else:
      self.meta[self.current_file] = time.time();
      pd.DataFrame(meta).to_csv(self.base+self.meta_file);
  def set_current(self):
    self.current_file = self.files.pop(0);
    self.files.append(self.current_file);
  def set_rand_current(self):
    rand_int = random.randint(0,10);
    self.current_file = self.files[rand_int];
    self.files.append(self.current_file);






class Populate(Thread):
  def __init__(self,_buffer, _data):
    Thread.__init__(self)
    self.buff = _buffer;
    self.data = _data
  def run(self):
    for i in self.data:
      self.buff.append(('0'+hex(i)[2:])[-2:]) 

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

  # Verify BLE channels argument
  if ',' not in opts.current_ble_channels:
    opts.current_ble_channels += ','
  
  # Prepare BLE channels argument
  opts.scan_channels = [int(x) for x in opts.current_ble_channels.split(',')]

  # Set Gnu Radio opts
  init_args(gr_block, opts)

  # Print capture settings
  print_settings(gr_block, opts)

  # Open PCAP file descriptor
  pcap_fd = open_pcap(opts.pcap_file)

  current_hop = 1
  hopping_time = datetime.now() + timedelta(seconds=HOPE_SIZE)

  # Set initial BLE channel
  current_ble_chan = opts.scan_channels[1]
  gr_block.set_ble_channel(BLE_CHANS[current_ble_chan])

  # Prepare Gnu Radio receive buffers
  lost_data = []
  hex_data = ()

  #REMOVE ME THE PACKETS ARE SELECTED
  count=0
  found_ad = False

  print 'Capturing on BLE channel [ {:d} ] @ {:d} MHz'.format(current_ble_chan, int(gr_block.get_freq() / 1000000))

  try:
    
    while True:

      if time.now()>hopping_time:
        circular.set_current()
        filename = circular.base+circular.current_file;
        gr_block.set_filename(filename);
        circular.update_meta();
        hopping_time = datetime.now() + timedelta(seconds=HOPE_SIZE*GAIN);

      hex_data+= deepcopy(gr_block.blocks_vector_sink_x_0.data());
      gr_block.blocks_vector_sink_x_0.reset();
      print "too small:",len(hex_data)


      

      if len(hex_data) > opts.min_buffer_size:
        hex_buffer = lost_data
        thread = Populate(hex_buffer,hex_data);
        thread.start()
        lost_data = hex_buffer[-15:];
        size = len(hex_data)
        hex_data = ()
        print "length of the buffer:",len(hex_buffer)
        print "bytes already in the sink:",len(gr_block.blocks_vector_sink_x_0.data())
        

        
        ##pre-convert the data 
        #hex_buffer = [binascii.hexlify(d) for d in _buffer]
        #hex_buffer = ["aa","d6","be","89","8e", "d4", "e0" ,"ab","61","7d", "f2","59","c3","19","a4","ab" ,"59" ,"84","b1" ,"d3","73","80","31","83","ab","10","95","3e","48","90","39","dd","3b","36","23","6a","29","f0","b0","c6","f8","ba","00","b9","b1","d8","75"]


        for pos ,byte, in enumerate(hex_buffer):

          ###generate the array
          packet_arr = hex_buffer[pos:pos+PACKET_BODY_LEN]

          if len(packet_arr)<PACKET_BODY_LEN:
            lost_data=hex_buffer[pos:pos+PACKET_BODY_LEN]
            break
          
          pos_error_poses  = [PACKET_EQUAL_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN) if PACKET_EQUAL_MAP[(PACKET_BODY[i],packet_arr[i])]];
          neg_error_poses = [PACKET_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN) if PACKET_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])]];

          pos_diff = [pos_error_poses[i][0]-pos_error_poses[i-1][-1] for i in range(len(pos_error_poses)) if i>0 if pos_error_poses[i][0]-pos_error_poses[i-1][-1]>1];
          neg_diff = [neg_error_poses[i][0]-neg_error_poses[i-1][-1] for i in range(len(neg_error_poses)) if i>0 if neg_error_poses[i][0]-neg_error_poses[i-1][-1]>1];

          pos_diffs = sum([EQUAL_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN)],[]);
          neg_diffs = sum([DIFF_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN)],[]);

          pos_diffs = sum([pos_diff,pos_diffs],[]);
          neg_diffs = sum([neg_diff,neg_diffs],[]);

          prob = (LF-(len(pos_diffs)+len(neg_diffs)))/LF;
          
          if prob>=THRESHOLD:
            print "prob:",prob
            print "detected packet:",("").join(packet_arr);



  except KeyboardInterrupt:
    pass
  gr_block.stop()
  gr_block.wait()
if __name__=="__main__":
  #worker()
  with PyCallGraph(output=GraphvizOutput()):
    worker()

