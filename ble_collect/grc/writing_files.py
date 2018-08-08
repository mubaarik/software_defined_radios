from grc.usrp_out import usrp_out as grblock

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
    if self.meta =={}:
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