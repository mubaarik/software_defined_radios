class GR_Parameter:
  def __init__(self,val=0,step=0, _min=0,_max=0):
    self.default = val;
    self.value = val
    self.step = step
    self.min = _min;
    self.max = _max
  def incement(self):
    self.value+=self.step
  def start(self):
    self.value=self.min;
  def set_default(self):
    self.value=self.default

class ComparisonData:
  def __init__(self):
    self.detected = 0
    self.processed = 0
    #self.transition_width = 300e3
    #self.sample_rate = 4e6
    #self.cutoff_freq = 850e3
    self.squelch_threshold = GR_Parameter(-100,10,-150,-30)
    self.sensivity = GR_Parameter(1.0,0.1,0.7,1.0)
    self.rf_gain = GR_Parameter(60,10,20,70)
    self.gfsk_omega_limit = GR_Parameter(0.035,.01,.015,.105)
    self.gfsk_mu = 0.5
    self.gfsk_gain_mu = GR_Parameter(0.3,0.1, 0.1,.8)
    #self.freq_offset =  GR_Parameter(0,.1,0,.4)



    ##local control parameters
    self.current_param = self.squelch_threshold;

  def set_current_prm(self):
    ##current value
    if self.current_param.value<self.current_param.min:
      self.current_param.incement()
    #next value
    else:
      self.current_param.set_default()
      if self.current_param==self.squelch_threshold:
          self.current_param = self.sensivity
      elif self.current_param==self.sensivity:
          self.current_param = self.rf_gain
      elif self.current_param ==self.rf_gain:
          self.current_param = self.gfsk_omega_limit
      elif self.current_param==self.gfsk_omega_limit:
          self.current_param = self.gfsk_gain_mu
      else:
          self.current_param=squelch_threshold;
      self.current_param.start()
  def set_gr_params(self,gr):
    gr.set_squelch_threshold(int(self.squelch_threshold))
    gr.set_gfsk_gain_mu(self.gfsk_gain_mu)
    gr.set_gfsk_omega_limit(self.gfsk_gain_mu)
    gr.set_rf_gain(self.rf_gain)
    gr.set_sensivity(self.sensivity)
    


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







def print_settings(gr_blk,options):
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



