import pickle
#from grc.gr_ble import gr_ble as gr_block
from grc.file_transfer import file_transfer as gr_block
from proto import *

from datetime import datetime, timedelta
from proto import *

import numpy as np
import time
import pandas as pd
from ble_dump_utils import *


from  bitstring import BitArray
import binascii

from simulation_utils import *
from copy import deepcopy
from threading import Thread

#steps 
#

class SimulatePrm:
	##constants
	MIN_BUFFER_LEN=65
	HOPE_TIME=15

	def __init__(self):
		self.filename = "file_based_sim8.csv"
		self.param_time  = 10*60
		# Initialize Gnu Radio
		self.gr_block = gr_block()
		self.gr_block.start()
		# Initialize command line arguments
		(self.opts, self.args) = init_opts(self.gr_block)
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
		self.hopping_time = datetime.now() + timedelta(seconds=self.HOPE_TIME)

		# Set initial BLE channel
		self.current_ble_chan = self.opts.scan_channels[1]
		self.gr_block.set_ble_channel(BLE_CHANS[self.current_ble_chan])

		# Prepare Gnu Radio receive buffers
		self.gr_buffer = ''
		self.lst_buffer = ''

		## search parameters
		self.search_term= '0xaad6be898e'
		self.data_model = ComparisonData()


		##load the simulation output file csv
		self.model_arr = []
		print "running...."
		self.run_simulation()

	  
	def run_simulation(self):
		while True:
			##set the new parameters using the simulation utilities

			if datetime.now()>self.hopping_time:
				print "setting a new"
				self.hopping_time=datetime.now()+timedelta(seconds=	self.HOPE_TIME)
				
				self.gr_block.file_source.seek(0,0)

				##store the current data
				model = deepcopy(self.data_model.get_dict())
				self.model_arr.append(model)
				file_saver = SaveData(self.filename,self.model_arr);
				file_saver.start()
				##save the data
				self.data_model.__set_prm__();
				self.data_model.set_gr_params(self.gr_block);
				self.data_model.processed=0
				



			## run the the data collection for param_time seconds
			self.detect_advertisement_packet()

			##switch to a new set 

			## store the new data in the file

	def detect_advertisement_packet(self):
		self.gr_buffer += self.gr_block.message_queue.delete_head().to_string()


		if len(self.gr_buffer) > self.opts.min_buffer_size:
			
		  	
			# Search for BLE_PREAMBLE in received data
			
			_buffer = ''.join(str(x) for x in self.lst_buffer) + self.gr_buffer
			self.lst_buffer=self.gr_buffer[-7:]
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
				if self.opts.disable_dewhitening == False:
				  ble_header = dewhitening(_buffer[pos:pos + BLE_PDU_HDR_LEN], self.current_ble_chan)
				else:
				  ble_header = _buffer[pos:pos + BLE_PDU_HDR_LEN]


				# Check BLE PDU type
				

				if ble_access_address == BLE_ACCESS_ADDR:
					print "I have a BLE ADDRESS"
				if ble_access_address == BLE_ACCESS_ADDR:
				  ble_len = ble_header[1] & 0x3f
				else:
				  continue
				
				self.data_model.processed+=1;

				###
				ble_pdu_type = ble_header[0] & 0x0f
				adv_scan_ind = 0b0110==ble_pdu_type;

				if ble_pdu_type not in BLE_PDU_TYPE.values():
				  continue




class SaveData(Thread):
	def __init__(self,filename,data):
		Thread.__init__(self)
		self.data = deepcopy(data);
		self.filename = filename;
	def run(self):
		

		df = pd.DataFrame(self.data)
		df.to_csv(self.filename)


if __name__=="__main__":
	SimulatePrm().run_simulation()
          

		

		

		
	
	


