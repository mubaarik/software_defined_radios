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
'''
aad6be898ed4e0ab617df259c319a4ab5984b1228cab177303314b9c068c6ccba3ec86780d50b9921557dca768f3dd
0225ef41242cb84c0201041bffffefec407551931da46cc101be9c02d1211ebd2588835dc1ab5f8bb534

aad6be898ed4e1ab617df259c319a4ab588402cd62fe55c151b508b4880378ab3c2f475f3ce7153da7d7b24ca02f
0224ef41242cb84c0201041aff4c00021537e3c199e7444f8eaafc9d12e0398c92242cef41c5b44369

aad6be898ed6e1ab617df259c319a4a9588402cd62fe571c85f1dac587fb4dde84eb85171de0153da7d7b2e91cbd
0024ef41242cb84c0201061aff4c000215353e15dd353540769f8925d62271ad95242cef41c511fffb

aad6be898ed6e0ab617df259c319a4a95984b1228cab177303314b9c068c6ccba3ec86780d50b9921557dca734bc45
0025ef41242cb84c0201061bffffefec407551931da46cc101be9c02d1211ebd2588835dc1ab5fd7faac

aad6be898ed6e1ab617df259c319a4a9588402cd62fe571c85f1dac587fb4dde84eb85171de0153da7d7b2e91cbd
0024ef41242cb84c0201061aff4c000215353e15dd353540769f8925d62271ad95242cef41c511fffb

aad6be898ed6e1ab617df259c319a4a9588402cd62fe571c85f1dac587fb4dde84eb85171de0153da7d7b2e91cbd
0024ef41242cb84c0201061aff4c000215353e15dd353540769f8925d62271ad95242cef41c511fffb

aad6be898ed4e0ab617df259c319a4ab5984b1d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9b1d875
0225ef41242cb84c0201041bffff1e136b53a13b3c7ace8f1deb8a9a0b840c998581d7b02c7741529e9c
'''
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
##########    aa d6 be 89 8e d4 e1 bd 3f 46 f2 59 c3 19 a4a
TARGET_ONE = "aad6be898ed4e0ab617df259c319a4ab5984b1d373803183ab10953e489039dd3b36236a29f0b0c6f8ba00b9b1d875"#"aad6be898ed4e0ab617df259c3"

TARGET_TWO = "aad6be898ed6e1ab617df259c319a4a9588402cd62fe571c85f1dac587fb4dde84eb85171de3153da7d7b2e47adf"
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

  print '\ngfsk demodulation:'
  print ' %-22s: %s' % ('Samples per Symbol', '{:.4f}'.format(gr.get_gfsk_sps()))
  print ' %-22s: %s' % ('Gain Mu', '{:.4f}'.format(gr.get_gfsk_gain_mu()))
  print ' %-22s: %s' % ('Mu', '{:,}'.format(gr.get_gfsk_mu()))
  print ' %-22s: %s' % ('Omega Limit', '{:.4f}'.format(gr.get_gfsk_omega_limit()))

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
  gr.set_gfsk_sps(opts.samples_per_symbol)
  gr.set_gfsk_gain_mu(opts.gain_mu)
  gr.set_gfsk_mu(opts.mu)
  gr.set_gfsk_omega_limit(opts.omega_limit)
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

  # gfsk demodulation
  gfsk = OptionGroup(parser, 'gfsk demodulation:')
  gfsk.add_option("-S", "--samples_per_symbol", type="eng_float", default=gr.gfsk_sps, help="Samples per symbol [default=%default]")
  gfsk.add_option("-G", "--gain_mu", type="eng_float", default=gr.gfsk_gain_mu, help="Gain mu [default=%default]")
  gfsk.add_option("-M", "--mu", type="eng_float", default=gr.gfsk_mu, help="Mu [default=%default]")
  gfsk.add_option("-O", "--omega_limit", type="eng_float", default=gr.gfsk_omega_limit, help="Omega limit [default=%default]")

  # Bluetooth L
  ble= OptionGroup(parser, 'Bluetooth LE:')
  ble.add_option("-c", "--current_ble_channels", type="string", default='37,38,39', help="BLE channels to scan [default=%default]")
  ble.add_option("-w", "--ble_scan_window", type="eng_float", default=10.24, help="BLE scan window [default=%default]")
  ble.add_option("-x", "--disable_crc", action="store_true", default=False, help="Disable CRC verification [default=%default]")
  ble.add_option("-y", "--disable_dewhitening", action="store_true", default=False, help="Disable De-Whitening [default=%default]")

  parser.add_option_group(capture)
  parser.add_option_group(filters)
  parser.add_option_group(gfsk)
  parser.add_option_group(ble)
  return parser.parse_args()


if __name__ == '__main__':
  MIN_BUFFER_LEN = 4*65
  ###The main data map
  data_map = DataMap()

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
  lst_buffer = ''


  ##rejected data map
  rejected_data_map={}

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
      #time.sleep(1)
      gr_buffer += gr_block.message_queue.delete_head().to_string()

      if len(gr_buffer) > opts.min_buffer_size:
        # Prepend lost data
        if len(lost_data) > 0:
          gr_buffer = ''.join(str(x) for x in lost_data) + gr_buffer
          lost_data = ''

        # Search for BLE_PREAMBLE in received data
        
        search_term = TARGET_ONE#'0xaad6be898e'#'0xaa8E89BED6'#'0xaa'#'0x8E89BED6'#"0x71764129"#"0x81D7B02C7741"#'0x558E89BED6'
        #conv = Convolution(search_term,lst_buffer);
        #conv1 = Convolution(search_term,_buffer);
        
        search_len = 4*(len(search_term)-2);

        
        #conv.convolve();
        # max_match = 0
        # if conv.conv_map:
        #   max_match = max(conv.conv_map.keys())
        # if max_match>search_len-5:
        #   data_map.add(conv)
        #Call the print function here
        #conv.info()
        #print "print _utils", gr_buffer
        if lst_buffer=='':
          lst_buffer=gr_buffer;
          continue
        _buffer = ''.join(str(x) for x in lst_buffer) + gr_buffer
        conv = Convolution(search_term,_buffer);
        # print "lst_search:", conv.search_vect
        # print "combined buffer search vector:",conv1.search_vect
        # #_buffer = lst_buffer+gr_buffer
        # print "Contain the older old buffer:", lst_buffer in _buffer
        lst_buffer=''
        lst_buffer=gr_buffer;
        gr_buffer=''
        ##test
        conv.convolve();
        conv.info()
        #continue
        


        

       


        for pos in [position for position, byte, in enumerate(_buffer) if byte == BLE_PREAMBLE]:

          
          #print "Found the BLE_PREAMBLE"
          pos += BLE_PREAMBLE_LEN

          # Check enough data is available for parsing the BLE Access Address
          if len(_buffer[pos:]) < (BLE_ADDR_LEN + BLE_PDU_HDR_LEN):
            #print "Non enough data"
            continue
          #print "printing the buffer", gr_buffer
          invertor  = 0x71764129
          actual_access_address = 0x8E89BED6

          # Extract BLE Access Address
          ble_access_address = unpack('I', _buffer[pos:pos + BLE_ADDR_LEN])[0]
          


          pos += BLE_ADDR_LEN

          # Dewhitening received BLE Header
          if opts.disable_dewhitening == False:
            ble_header = dewhitening(_buffer[pos:pos + BLE_PDU_HDR_LEN], current_ble_chan)
          else:
            ble_header = _buffer[pos:pos + BLE_PDU_HDR_LEN]
          #print "Header:", ble_header
          
          
          # Check BLE PDU type
          ble_pdu_type = ble_header[0] & 0x0f
          adv_scan_ind = 0b0110==ble_pdu_type;

          if ble_pdu_type not in BLE_PDU_TYPE.values():
            #print "wrong type"
            continue


          adver_packet = ble_access_address == BLE_ACCESS_ADDR
          if ble_access_address == BLE_ACCESS_ADDR:
            #print "Me too!"#, [ord(d) for d in _buffer]
            # Extract BLE Length
            #print "access address:",str([i for i in _buffer])
            ble_len = ble_header[1] & 0x3f
          else:
            ##skip non-advertiment packets
            continue
            ble_llid = ble_header[0] & 0x3
            if ble_llid == 0:
              #print "could not extract BLE Lengh"
              continue

            # Extract BLE Length
            ble_len = ble_header[1] & 0x1f

          # Dewhitening BLE packet
          #original_data = unpack('I', gr_buffer[pos:pos + BLE_ADDR_LEN])[0]
          if opts.disable_dewhitening == False:
            ble_data = dewhitening(_buffer[pos:pos + BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len], current_ble_chan)
          else:
            ble_data = _buffer[pos:pos + BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len]
          
          #print "ble_data", ble_data
          import binascii
          mac_address = binascii.hexlify(bytearray(ble_data))
          if "2c7741"==mac_address[0:6]:
            print "finding matches: ",mac_address

          # Verify BLE data length
          #lost_data = _buffer[pos:]
          if len(ble_data) != (BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len):
            #lost_data = _buffer[pos - BLE_PREAMBLE_LEN - BLE_ADDR_LEN:pos + BLE_PREAMBLE_LEN + BLE_ADDR_LEN + BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len]
            #print "Could not verify the BLE data length"
            if is_cmt_tag(mac_address):
              print "length of the data:", ble_len
              print "expected length:",(BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len), "data length:",len(ble_data)
              print "rest of the buffer:", len(_buffer[pos:])
              print "rejected ble address", mac_address
              print "Scan type:", ble_pdu_type
              if not mac_address in rejected_data_map:
                rejected_data_map[mac_address]=1;
              else:
                rejected_data_map[mac_address]+=1;


            #if original_data
            continue
          p_start = pos - BLE_PREAMBLE_LEN - BLE_ADDR_LEN
          p_end = pos+BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len



          # Verify BLE packet checksum
          if opts.disable_crc == False:
            if ble_data[-3:] != crc(ble_data, BLE_PDU_HDR_LEN + ble_len):
              #print "failing to the verify the BLE packet Checksum"
              if adv_scan_ind:
                print "rejected ble address2", mac_address

              else:
               continue
          if is_cmt_tag(mac_address):
            print "releasing cmt packet.........", binascii.hexlify(bytearray([ord(d) for d in _buffer[p_start:p_end]]))
            print "dewhitened.....", mac_address
            if mac_address[-3:] == 'ef41242cb84c':
              print "buffer:", [ord(d) for d in _buffer]
          else:
            continue
          # print "writing data"
          # print "length of the buffer", len(_buffer)
          # Write BLE packet to PCAP file descriptor
          #print "writing the pcap file"
          write_pcap(pcap_fd, current_ble_chan, ble_access_address, ble_data)
          # for i in range(int(10e6)):
          #   8+9;

        #gr_buffer = ''

  except KeyboardInterrupt:
    pass
pd.DataFrame([rejected_data_map]).to_csv("rejected_data1.csv")
pcap_fd.close()
gr_block.stop()
gr_block.wait()
