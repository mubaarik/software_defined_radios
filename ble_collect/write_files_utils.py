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
    self.default = _min;
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
    self.processed = 0
    self.rf_gain = GR_Parameter(60,10,40,70)
    self.gfsk_omega_limit = GR_Parameter(0.005,.001,.001,.49)
    self.transition_width = GR_Parameter(300,100,300,800)
    self.gfsk_gain_mu = GR_Parameter(0.3,0.01, 0.02,.90)
    self.cutoff_freq = GR_Parameter(600,100, 300,600)

    #Preparing the tuning parameters 
    self.vars = [self.transition_width,self.gfsk_omega_limit,self.gfsk_gain_mu,self.cutoff_freq,self.rf_gain]
    self.values = [self.get_all_values(var) for var in self.vars]
    self.states = list(itertools.product(*self.values))
    rnd.shuffle(self.states)
    

    ##Other local control parameters
    self.current_param = self.rf_gain;
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
      if self.current_param==self.rf_gain:
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
    gr.set_gfsk_gain_mu(self.gfsk_gain_mu.value)
    gr.set_gfsk_omega_limit(self.gfsk_gain_mu.value)
    gr.set_rf_gain(self.rf_gain.value)
    gr.set_transition_width(self.transition_width.value*1000)
    gr.set_cutoff_freq(self.cutoff_freq.value*1000)

  def get_dict(self):
    """
    generate a quick dictionary of the current parameter name to current value for csv storage
    """
    return {
    "processed":self.processed,
    "transition_width": self.transition_width.value,
    "rf_gain": self.rf_gain.value,
    "gfsk_omega_limit": self.gfsk_omega_limit.value,
    "gfsk_gain_mu": self.gfsk_gain_mu.value,
    "cutoff_freq":self.cutoff_freq.value
    }