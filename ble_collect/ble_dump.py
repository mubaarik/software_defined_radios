#!/opt/local/bin/python2.7
#
#  ble-dump: SDR Bluetooth LE packet dumper
#
#  Copyright (C) 2016 Jan Wagner <mail@jwagner.eu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#

from grc.gr_ble import gr_ble as gr_block
from optparse import OptionParser, OptionGroup
from gnuradio.eng_option import eng_option
from datetime import datetime, timedelta
from proto import *
import binascii
from  bitstring import BitArray
import numpy as np

##########
TARGET_ARRAY = ['0x0201-061B-FFFF-1E13-6B53-A13B-3C7A-CE8F-1DEB-8A9A-0B84-0C99-85-81D7-B02C-7741','0X0201-041A-FF4C-0002-1537-E3C2-99E7-444F-8EAA-FC9D-12E0-398C-9224-2CEF-41C5']
# Print current Gnu Radio capture settings
def print_settings(gr, opts):
  print '\n ble-dump:  SDR Bluetooth LE packet dumper'
  print '\nCapture settings:'
  print ' %-22s: %s Hz' % ('Base Frequency', '{:d}'.format(int(gr.get_ble_base_freq())))
  print ' %-22s: %s Hz' % ('Sample rate', '{:d}'.format(int(gr.get_sample_rate())))
  print ' %-22s: %s dB' % ('Squelch threshold', '{:d}'.format(int(gr.get_squelch_threshold())))

  print '\nLow-pass filter:'
  print ' %-22s: %s Hz' % ('Cutoff frequency', '{:d}'.format(int(gr.get_cutoff_freq())))
  print ' %-22s: %s Hz' % ('Transition width', '{:d}'.format(int(gr.get_transition_width())))

  print '\nGMSK demodulation:'
  print ' %-22s: %s' % ('Samples per Symbol', '{:.4f}'.format(gr.get_gmsk_sps()))
  print ' %-22s: %s' % ('Gain Mu', '{:.4f}'.format(gr.get_gmsk_gain_mu()))
  print ' %-22s: %s' % ('Mu', '{:,}'.format(gr.get_gmsk_mu()))
  print ' %-22s: %s' % ('Omega Limit', '{:.4f}'.format(gr.get_gmsk_omega_limit()))

  print '\nBluetooth LE:'
  print ' %-22s: %s' % ('Scanning Channels', '{:s}'.format(opts.current_ble_channels.replace(',', ', ')))
  print ' %-22s: %ss' % ('Scanning Window', '{:.2f}'.format(opts.ble_scan_window))
  print ' %-22s: %s' % ('Disable CRC check', '{0}'.format(opts.disable_crc))
  print ' %-22s: %s' % ('Disable De-Whitening', '{0}'.format(opts.disable_dewhitening))

  print '\n%-23s: %s\n' % ('PCAP output file', '{:s}'.format(opts.pcap_file))

# Setup Gnu Radio with defined command line arguments
def init_args(gr, opts):
  gr.set_sample_rate(int(opts.sample_rate))
  gr.set_squelch_threshold(int(opts.squelch_threshold))
  gr.set_cutoff_freq(int(opts.cutoff_freq))
  gr.set_transition_width(int(opts.transition_width))
  gr.set_gmsk_sps(opts.samples_per_symbol)
  gr.set_gmsk_gain_mu(opts.gain_mu)
  gr.set_gmsk_mu(opts.mu)
  gr.set_gmsk_omega_limit(opts.omega_limit)
  gr.set_ble_channel(int(opts.scan_channels[0]))

# Initialize command line arguments
def init_opts(gr):
  parser = OptionParser(option_class=eng_option, usage="%prog: [opts]")

  # Capture
  capture = OptionGroup(parser, 'Capture settings')
  capture.add_option("-o", "--pcap_file", type="string", default='', help="PCAP output file or named pipe (FIFO)")
  capture.add_option("-m", "--min_buffer_size", type="int", default=65, help="Minimum buffer size [default=%default]")
  capture.add_option("-s", "--sample-rate", type="eng_float", default=gr.sample_rate, help="Sample rate [default=%default]")
  capture.add_option("-t", "--squelch_threshold", type="eng_float", default=gr.squelch_threshold, help="Squelch threshold (simple squelch) [default=%default]")

  # Low Pass filter
  filters = OptionGroup(parser, 'Low-pass filter:')
  filters.add_option("-C", "--cutoff_freq", type="eng_float", default=gr.cutoff_freq, help="Filter cutoff [default=%default]")
  filters.add_option("-T", "--transition_width", type="eng_float", default=gr.transition_width, help="Filter transition width [default=%default]")

  # GMSK demodulation
  gmsk = OptionGroup(parser, 'GMSK demodulation:')
  gmsk.add_option("-S", "--samples_per_symbol", type="eng_float", default=gr.gmsk_sps, help="Samples per symbol [default=%default]")
  gmsk.add_option("-G", "--gain_mu", type="eng_float", default=gr.gmsk_gain_mu, help="Gain mu [default=%default]")
  gmsk.add_option("-M", "--mu", type="eng_float", default=gr.gmsk_mu, help="Mu [default=%default]")
  gmsk.add_option("-O", "--omega_limit", type="eng_float", default=gr.gmsk_omega_limit, help="Omega limit [default=%default]")

  # Bluetooth L
  ble= OptionGroup(parser, 'Bluetooth LE:')
  ble.add_option("-c", "--current_ble_channels", type="string", default='37,38,39', help="BLE channels to scan [default=%default]")
  ble.add_option("-w", "--ble_scan_window", type="eng_float", default=10.24, help="BLE scan window [default=%default]")
  ble.add_option("-x", "--disable_crc", action="store_true", default=False, help="Disable CRC verification [default=%default]")
  ble.add_option("-y", "--disable_dewhitening", action="store_true", default=False, help="Disable De-Whitening [default=%default]")

  parser.add_option_group(capture)
  parser.add_option_group(filters)
  parser.add_option_group(gmsk)
  parser.add_option_group(ble)
  return parser.parse_args()
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
  def __init__(self,target, gr_buffer):
    self.target_vect = self.hex_to_binary(target);
    self.search_vect = self.gr_buffer_to_binary_array(gr_buffer)
    #print "target vector:",self.target_vect
    #print "search vector:", self.search_vect

    self.index = len(self.target_vect)
    self.n = len(self.target_vect)
    self.conv_map = {};
  def convolve(self):

    while True:
      try:
        xor_result = self.compute_hamming_distance()
        if xor_result==None:
          return self.conv_map
        if xor_result>self.n/2:
          if xor_result in self.conv_map:
            self.conv_map[xor_result].append(self.index);
          else:
            self.conv_map[xor_result]=[self.index];

        self.index+=1;
      except IndexError:
        return self.conv_map
  def compute_hamming_distance(self):
    xor_segment = self.search_vect[self.index:self.index+self.n];
    ###########
    if len(xor_segment)!=len(self.target_vect):
      #print "segment length: ", len(xor_segment), "binary_array len:", len(self.target_vect)
      #print xor_segment,type(xor_segment)
      return None
    target = self.binary_to_integer(self.target_vect)
    new_segment  = self.binary_to_integer(xor_segment)
    ########
    return self.n-"{0:b}".format(target^new_segment).count('1');
  def hex_to_binary(self,_hex):
    '''
    Examples 
    >>> hex_to_binary('0xfe')
    '11111110'
    '''
    bin_obj = BitArray(hex = _hex);
    return bin_obj.bin[2:];
  def gr_buffer_to_binary_array(self, gr_buff):
    '''
    Examples
    >>> 
    '''
    binary_array = ''
    for position, byte, in enumerate(gr_buffer):
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
    return  byte_arr.bin[2:]
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


if __name__ == '__main__':
  MIN_BUFFER_LEN = 65

  # Initialize Gnu Radio
  gr_block = gr_block()
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
  current_ble_chan = opts.scan_channels[0]
  gr_block.set_ble_channel(BLE_CHANS[current_ble_chan])

  # Prepare Gnu Radio receive buffers
  gr_buffer = ''
  lost_data = ''

  print 'Capturing on BLE channel [ {:d} ] @ {:d} MHz'.format(current_ble_chan, int(gr_block.get_freq() / 1000000))

  try:
    current_ble_chan = opts.scan_channels[current_hop%len(opts.scan_channels)]
    gr_block.set_ble_channel(BLE_CHANS[current_ble_chan])
    print 'Listening to BLE channel [ {:d} ] @ {:d} MHz'.format(current_ble_chan, int(gr_block.get_freq() / 1000000))
    while True:
      # Move to the next BLE scanning channel

      # if datetime.now() >= hopping_time:
      #   current_ble_chan = opts.scan_channels[current_hop % len(opts.scan_channels)]
      #   gr_block.set_ble_channel(BLE_CHANS[current_ble_chan])
      #   hopping_time = datetime.now() + timedelta(seconds=opts.ble_scan_window)
      #   current_hop +=1
      #   print 'Switching to BLE channel [ {:d} ] @ {:d} MHz'.format(current_ble_chan, int(gr_block.get_freq() / 1000000))

      # Fetch data from Gnu Radio message queue
      gr_buffer += gr_block.message_queue.delete_head().to_string()

      if len(gr_buffer) > opts.min_buffer_size:
        # Prepend lost data
        if len(lost_data) > 0:
          gr_buffer = ''.join(str(x) for x in lost_data) + gr_buffer
          lost_data = ''

        # Search for BLE_PREAMBLE in received data
        #print "buffer ka wixii ku jiray", len(gr_buffer)
        #print "bytes",[byte for position, byte, in enumerate(gr_buffer)]
        #search_bites('\x24','\x2c',gr_buffer,7)81D7
        # search_term = "0x81D7B02C7741"#'0x55 8E 89 BE D6'
        # conv = Convolution(search_term,gr_buffer);
        # conv.convolve();
        # max_match = 0
        # if conv.conv_map:
        #   max_match = max(conv.conv_map.keys())
        # if max_match>300:
        #   print len(conv.target_vect)
        # if max_match>38:
        #   print "maximum mapping of the access address", max(conv.conv_map.keys())
        # if max_match>38:
        #   print "target vector: ", conv.target_vect
        #   print "search space:",conv.search_vect
        #   print "map:", conv.conv_map[max_match], len(conv.search_vect)

        for pos in [position for position, byte, in enumerate(gr_buffer) if byte == BLE_PREAMBLE]:
          
          #print "Found the BLE_PREAMBLE"
          pos += BLE_PREAMBLE_LEN

          # Check enough data is available for parsing the BLE Access Address
          if len(gr_buffer[pos:]) < (BLE_ADDR_LEN + BLE_PDU_HDR_LEN):
            #print "Non enough data"
            continue
          #print "printing the buffer", gr_buffer
          actual_access_address = 0x8E89BED6

          # Extract BLE Access Address
          ble_access_address = unpack('I', gr_buffer[pos:pos + BLE_ADDR_LEN])[0]
          #print "types", type(ble_access_address), type(actual_access_address)
          detected = hex_to_binary(str(hex(ble_access_address)))
          actual_bin = hex_to_binary(str(hex(actual_access_address)))
          hamm = 100
          if len(detected)==len(actual_bin):
            hamm =  hamming2(detected,actual_bin);
          if hamm<7:
            print "actual:",str(hex(actual_access_address)),"detected:",str(hex(ble_access_address)), "distance:",hamm

          if ble_access_address==actual_access_address:
            print "access Address: ", ble_access_address==0x8E89BED6

          pos += BLE_ADDR_LEN

          # Dewhitening received BLE Header
          if opts.disable_dewhitening == False:
            ble_header = dewhitening(gr_buffer[pos:pos + BLE_PDU_HDR_LEN], current_ble_chan)
          else:
            ble_header = gr_buffer[pos:pos + BLE_PDU_HDR_LEN]
          #print "Header:", ble_header
          # Check BLE PDU type
          ble_pdu_type = ble_header[0] & 0x0f
          if ble_pdu_type not in BLE_PDU_TYPE.values():
            #print "wrong type"
            continue

          if ble_access_address == BLE_ACCESS_ADDR:
            # Extract BLE Length
            ble_len = ble_header[1] & 0x3f
          else:
            ble_llid = ble_header[0] & 0x3
            if ble_llid == 0:
              #print "could not extract BLE Lengh"
              continue

            # Extract BLE Length
            ble_len = ble_header[1] & 0x1f

          # Dewhitening BLE packet
          if opts.disable_dewhitening == False:
            ble_data = dewhitening(gr_buffer[pos:pos + BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len], current_ble_chan)
          else:
            ble_data = gr_buffer[pos:pos + BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len]
          


          # Verify BLE data length
          if len(ble_data) != (BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len):
            lost_data = gr_buffer[pos - BLE_PREAMBLE_LEN - BLE_ADDR_LEN:pos + BLE_PREAMBLE_LEN + BLE_ADDR_LEN + BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len]
            #print "Could not verify the BLE data length"
            continue

          #print "ble_data", ble_data
          import binascii
          mac_address = binascii.hexlify(bytearray(ble_data))
          if "2c7741"==mac_address[0:6]:
            print "finding matches: ",mac_address

          # Verify BLE packet checksum
          if opts.disable_crc == False:
            if ble_data[-3:] != crc(ble_data, BLE_PDU_HDR_LEN + ble_len):
              #print "failing to the verify the BLE packet Checksum"
              continue

          # Write BLE packet to PCAP file descriptor
          #print "writing the pcap file"
          write_pcap(pcap_fd, current_ble_chan, ble_access_address, ble_data)

        gr_buffer = ''

  except KeyboardInterrupt:
    pass

pcap_fd.close()
gr_block.stop()
gr_block.wait()
