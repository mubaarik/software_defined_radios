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

def get_errors(packet_arr):
  pos_error_poses  = [PACKET_EQUAL_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN) if PACKET_EQUAL_MAP[(PACKET_BODY[i],packet_arr[i])]];
  neg_error_poses = [PACKET_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN) if PACKET_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])]];
  return pos_error_poses,neg_error_poses;
def diffdiff(pos_error_poses,neg_error_poses):
  pos_diff = [pos_error_poses[i][0]-pos_error_poses[i-1][-1] for i in range(len(pos_error_poses)) if i>0 if pos_error_poses[i][0]-pos_error_poses[i-1][-1]>1];
  neg_diff = [neg_error_poses[i][0]-neg_error_poses[i-1][-1] for i in range(len(neg_error_poses)) if i>0 if neg_error_poses[i][0]-neg_error_poses[i-1][-1]>1];
  return pos_diff,neg_diff;
def diffs(packet_arr):
  pos_diffs = sum([EQUAL_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN)],[]);
  neg_diffs = sum([DIFF_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN)],[]);
  return pos_diffs,neg_diffs;
def combine(pos_diff,neg_diff,pos_diffs,neg_diffs):
  pos_diffs = sum([pos_diff,pos_diffs],[]);
  neg_diffs = sum([neg_diff,neg_diffs],[]);
  return pos_diffs,neg_diffs


def get_hex(hex_data,lost_data):
  return lost_data+[('0'+hex(i)[2:])[-2:] for i in hex_data]

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
  hopping_time = datetime.now() + timedelta(seconds=opts.ble_scan_window)

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

      hex_data+= deepcopy(gr_block.blocks_vector_sink_x_0.data())
      gr_block.blocks_vector_sink_x_0.reset()
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

          ##Collect indices of the bits that are the same
          pos_error_poses  = [PACKET_EQUAL_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN) if PACKET_EQUAL_MAP[(PACKET_BODY[i],packet_arr[i])]];

          ##Collect indices of the bits that are different
          neg_error_poses = [PACKET_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])] for i in range(PACKET_BODY_LEN) if PACKET_DIFF_MAP[(PACKET_BODY[i],packet_arr[i])]];

          ##collect size of the islands of same bits
          pos_diff = [pos_error_poses[i][0]-pos_error_poses[i-1][-1] for i in range(len(pos_error_poses)) if i>0 if pos_error_poses[i][0]-pos_error_poses[i-1][-1]>1];

          ##collect the size of the islands with all different bits 
          neg_diff = [neg_error_poses[i][0]-neg_error_poses[i-1][-1] for i in range(len(neg_error_poses)) if i>0 if neg_error_poses[i][0]-neg_error_poses[i-1][-1]>1];

          ##combine the islands in to two longer lists
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

