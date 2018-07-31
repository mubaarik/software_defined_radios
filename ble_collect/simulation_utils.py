from optparse import OptionParser, OptionGroup
from gnuradio.eng_option import eng_option
import itertools
import random as rnd

class GR_Parameter:
  '''
  class representing a GR block parameter(e.g. sample_rate)
  @parameters
  1. default: The default value of the parameter
  2. value: Current value of the parameter
  3. step: For trying different values of the parameter for tuning, this change from one parameter to the next.
  3. min/max:upper and lower bounds of the parameter
  @Methods 
  1. increment: increment the current value of the parameter by @step
  2. start: set the current value to the minimum
  3. set_defafult: Set the parameter value to the default value
  '''
  def __init__(self,val=0,step=0, _min=0,_max=0):
    self.default = val;
    self.value = val
    self.step = step
    self.min = _min;
    self.max = _max
  def incement(self):
    self.value+=self.step
    self.value = round(self.value,6)
  def start(self):
    self.value=self.min;
  def set_default(self):
    self.value=self.default

class ComparisonData:
  """
  This class encapsulates multiple GR_parameters for tuning 
  """
  def __init__(self):
    #objective parameters 
    self.detected = 0
    self.processed = 0
    #tuning parameters
    self.squelch_threshold = GR_Parameter(-100,20,-150,-30)
    self.sensivity = GR_Parameter(1.0,0.1,0.7,1.0)
    self.rf_gain = GR_Parameter(60,10,30,70)
    self.gfsk_omega_limit = GR_Parameter(0.035,.01,.030,.505)
    self.transition_width = GR_Parameter(300,50,150,600)
    self.gfsk_gain_mu = GR_Parameter(0.3,0.01, 0.01,1.40)
    self.cutoff_freq = GR_Parameter(600,0, 600,600)
    self.freq_offset = GR_Parameter(5000,100, -1000,3000)

    #Preparing the tuning parameters 
    self.vars = [self.transition_width,self.gfsk_omega_limit,self.gfsk_gain_mu,self.cutoff_freq, self.freq_offset]
    self.values = [self.get_all_values(var) for var in self.vars]
    self.states = list(itertools.product(*self.values))
    rnd.shuffle(self.states)
    

    ##Other local control parameters
    self.current_param = self.squelch_threshold;
    self.index = 0
    self.max_index = len(self.states)-1
  
  def get_all_values(self,gr_prm):
    """
    @gr_prm: Instance of GR_Parameter
    generate all the possible parameters of @gr_prm as a list 
    """
    gr_prm.start()
    values = [gr_prm.value]
    while gr_prm.value<gr_prm.max:
      gr_prm.incement()
      values.append(gr_prm.value)
    return values
  

  def __set_prm__(self):
    """
    Set the values of the tuned parameters to new state(set of values)
    """
    if self.index<self.max_index:
      for ind,var in enumerate(self.vars):
        var.value = self.states[self.index][ind];
      self.index+=1;
    else:
      self.index=0


  def set_current_prm(self):
    ##current value
    if self.current_param.value<self.current_param.max:
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
          self.current_param=self.squelch_threshold;
      self.current_param.start()
  def set_gr_params(self,gr):
    """
    @gr: GR_BLOCK object(gr_ble object)
    Set values of the GR_block parameters d
    """
    gr.set_squelch_threshold(int(self.squelch_threshold.value))
    gr.set_gfsk_gain_mu(self.gfsk_gain_mu.value)
    gr.set_gfsk_omega_limit(self.gfsk_gain_mu.value)
    gr.set_rf_gain(self.rf_gain.value)
    gr.set_sensivity(self.sensivity.value)
    gr.set_transition_width(self.transition_width.value*1000)
    gr.set_cutoff_freq(self.cutoff_freq.value*1000)
    gr.set_freq_offset(self.freq_offset.value)
  def get_dict(self):
    """
    generate a quick dictionary of the current parameter name to current value for csv storage
    """
    return {
    "processed":self.processed,
    "detected": self.detected,
    #"sqlch_thrsh": self.squelch_threshold.value,#(self.squelch_threshold.default,self.squelch_threshold.value,self.squelch_threshold.min,self.squelch_threshold.max),
    "transition_width": self.transition_width.value,#(self.sensivity.default,self.sensivity.value,self.sensivity.min,self.sensivity.max),
    #"rf_gain": self.rf_gain.value,#(self.rf_gain.default,self.rf_gain.value,self.rf_gain.min,self.rf_gain.max),
    "freq_offset": self.freq_offset.value,
    "gfsk_omega_limit": self.gfsk_omega_limit.value,#(self.gfsk_omega_limit.default,self.gfsk_omega_limit.value,self.gfsk_omega_limit.min,self.gfsk_omega_limit.max),
    "gfsk_gain_mu": self.gfsk_gain_mu.value,#(self.gfsk_gain_mu.default,self.gfsk_gain_mu.value,self.gfsk_gain_mu.min,self.gfsk_gain_mu.max),
    "cutoff_freq":self.cutoff_freq.value
    }
    


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
  capture.add_option("-m", "--min_buffer_size", type="int", default=165, help="Minimum buffer size [default=%default]")
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







def print_settings(gr,opts):
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



