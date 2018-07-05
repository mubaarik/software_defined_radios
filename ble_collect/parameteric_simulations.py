import pickle
from grc.gr_ble import gr_ble as gr_block
from optparse import OptionParser, OptionGroup
from gnuradio.eng_option import eng_option
from datetime import datetime, timedelta
from proto import *

import numpy as np
import time
import pandas as pd
from ble_dump_utils import *


from  bitstring import BitArray
import binascii

from simulation_utils import *

#steps 
#

class SimulatePrm:
	##constants
	MIN_BUFFER_LEN=65

	def __init__(self):
		self.filename = "comparison_data.csv"
		self.param_time  = 10*60
		# Initialize Gnu Radio
		self.gr_block = gr_block()
		self.gr_block.start()
		# Initialize command line arguments
		(self.opts, self.args) = init_opts(gr_block)
		# Verify BLE channels argument
		if ',' not in self.opts.current_ble_channels:
			self.opts.current_ble_channels += ','
		# Prepare BLE channels argument
		self.opts.scan_channels = [int(x) for x in self.opts.current_ble_channels.split(',')]

		# Set Gnu Radio opts
		init_args(self.gr_block, self.opts)

		# Print capture settings
		print_settings(self.gr_block, self.opts)
		self.current_hop = 1
	  self.hopping_time = datetime.now() + timedelta(seconds=opts.ble_scan_window)

	  # Set initial BLE channel
	  self.current_ble_chan = opts.scan_channels[0]
	  gr_block.set_ble_channel(BLE_CHANS[current_ble_chan])

	  # Prepare Gnu Radio receive buffers
	  self.gr_buffer = ''
	  self.lst_buffer = ''

	  ## search parameters
	  self.search_term= '0xaad6be898e'
	  self.data_model = ComparisonData()


	  ##load the simulation output file csv
	  self.model_arr = []

	  
	def run_simulation(self):
		while True:
			##set the new parameters using the simulation utilities
			if time_expired:
				##store the current data 
				##reload the file 
				##save the data
				self.data_model.set_current_prm();
				self.data_model.set_gr_params(self.gr_block);

			## run the the data collection for param_time seconds
			self.detect_advertisement_packet()

			##switch to a new set 

			## store the new data in the file

	def detect_advertisement_packet(self):
		self.gr_buffer += self.gr_block.message_queue.delete_head().to_string()

    if len(self.gr_buffer) > self.opts.min_buffer_size:
      
      # Search for BLE_PREAMBLE in received data
      if self.lst_buffer=='':
        self.lst_buffer=gr_buffer;
        continue
      _buffer = ''.join(str(x) for x in lst_buffer) + gr_buffer
      conv = Convolution(search_term,_buffer);
      
      self.lst_buffer=''
      self.lst_buffer=gr_buffer;
      self.gr_buffer=''
      
      

     


      for pos in [position for position, byte, in enumerate(_buffer) if byte == BLE_PREAMBLE]:

        pos += BLE_PREAMBLE_LEN

        # Check enough data is available for parsing the BLE Access Address
        if len(_buffer[pos:]) < (BLE_ADDR_LEN + BLE_PDU_HDR_LEN):
          continue
        

        # Extract BLE Access Address
        ble_access_address = unpack('I', _buffer[pos:pos + BLE_ADDR_LEN])[0]
        


        pos += BLE_ADDR_LEN

        # Dewhitening received BLE Header
        if opts.disable_dewhitening == False:
          ble_header = dewhitening(_buffer[pos:pos + BLE_PDU_HDR_LEN], current_ble_chan)
        else:
          ble_header = _buffer[pos:pos + BLE_PDU_HDR_LEN]
        
        
        # Check BLE PDU type
        ble_pdu_type = ble_header[0] & 0x0f
        adv_scan_ind = 0b0110==ble_pdu_type;

        if ble_pdu_type not in BLE_PDU_TYPE.values():
          continue


        adver_packet = ble_access_address == BLE_ACCESS_ADDR
        if ble_access_address == BLE_ACCESS_ADDR:
          ble_len = ble_header[1] & 0x3f
        else:
          continue
        self.data_model.processed+=1;
class SaveData(Thread):
	def __init__(self,filename,data):
		self.data = deepcopy(data);
		self.filename = filename;
	def run(self):
		df = self.df_compute()
		df.to_csv(filename)
	def df_compute(self):
		dt = 




          

		

		

		
	
	


