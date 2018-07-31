from grc.gr_ble import gr_ble as gr_block

from datetime import datetime, timedelta
from proto import *

from copy import deepcopy
from packet_search_utils import *
def error_poses(byte_1, byte_2,i):

if __name__ == '__main__':
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

      

      if len(hex_data) > opts.min_buffer_size:
        # Prepend lost data
        _buffer=  gr_buffer
        
        gr_buffer=''
        hex_buffer = lost_data+[('0'+hex(i)[2:])[-2:] for i in hex_data]
        lost_data = hex_buffer[-15:];
        hex_data = ()

        hex_buffer_str = ('').join(hex_buffer)
        


        for pos ,byte, in enumerate(_buffer):

          ##packet body
          packet_body  = hex_buffer[pos:pos+PACKET_BODY_LEN];


          #check for enough data
          if len(hex_buffer[pos:])<PACKET_BODY_LEN:
            lost_data = hex_buffer[pos:]
            break
          data_str = BitArray(hex = packet_body);

          error_poses  = [i for i in range(len(data_str)) if (data_str.bin[i]!=PACKET_BUFFER.bin[i])];

          islands = [error_poses[i-1] -error_poses[i]  for i in range(len(error_poses)) if i>0]


          

          ##check for enough data in the packet
          if len(packet_body)<PACKET_BODY_LEN:
            lost_data = hex_buffer[pos-(BLE_PREAMBLE_LEN+BLE_ADDR_LEN):]
            break

          

          packet_dist = sum([CHAR_DISTS[(packet_body[i][0],PACKET_BODY[i][0])]+CHAR_DISTS[(packet_body[i][1],PACKET_BODY[i][1])] for i in range(PACKET_BODY_LEN)])

          if packet_dist<PAYLOAD_ERROR_LIMIT:
            print "packet:",("").join(packet_body),"errors:",packet_dist
  except KeyboardInterrupt:
    pass
gr_block.stop()
gr_block.wait()
