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
EQUAL_DIFF_MAP = {i:np.diff(PACKET_EQUAL_MAP[i]) for i in PACKET_EQUAL_MAP}


###difference map 
PACKET_DIFF_MAP = {}
for i in range(len(PACKET_BODY)):
  PACKET_DIFF_MAP.update(compute_map(PACKET_BODY[i],i,equal=False));


###difference difference map
DIFF_DIFF_MAP = {i:np.diff(PACKET_DIFF_MAP[i]) for i in PACKET_DIFF_MAP}





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
  capture.add_option("-m", "--min_buffer_size", type="int", default=95, help="Minimum buffer size [default=%default]")
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