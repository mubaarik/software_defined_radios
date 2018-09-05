#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Redesigned Gfsk
# Generated: Sun Aug 19 14:25:01 2018
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import math
import time


class redesigned_gfsk(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Redesigned Gfsk")

        ##################################################
        # Variables
        ##################################################
        self.trans_wdth = trans_wdth = 300e3
        self.samp_rate = samp_rate = 4e6
        self.ntaps = ntaps = 5*32
        self.data_rate = data_rate = 1e6
        self.cutoff_freq = cutoff_freq = 500e3
        self.taps = taps = firdes.low_pass(1, samp_rate, cutoff_freq, trans_wdth, firdes.WIN_HAMMING, 6.76)
        self.sqlch_threshold = sqlch_threshold = -100
        self.sqlch_alpha = sqlch_alpha = .1
        self.sensivity = sensivity = .20
        self.samp_per_sym_4 = samp_per_sym_4 = int(samp_rate/data_rate)
        self.samp_per_sym = samp_per_sym = int(samp_rate/data_rate)
        self.rf_gain = rf_gain = 70
        self.out_sps = out_sps = 1
        self.max_rate_dev = max_rate_dev = 1.5
        self.loop_bandwidth = loop_bandwidth = 0.06283185307179587
        self.initial_phase = initial_phase = 0
        self.freq_offset = freq_offset = 0
        self.filter_taps = filter_taps = firdes.root_raised_cosine(1.0,samp_rate,data_rate,.3,ntaps)
        self.filter_size = filter_size = 32
        self.filename = filename = "/Users/mmohamoud/software_defined_radios/ble_collect/demodulated_files/resigned_demod"
        self.cntr_freq = cntr_freq = 2426e6

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(cntr_freq, 0)
        self.uhd_usrp_source_0.set_gain(rf_gain, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, (taps), 0, samp_rate)
        self.digital_pfb_clock_sync_xxx_0 = digital.pfb_clock_sync_fff(samp_per_sym, loop_bandwidth, (taps), filter_size, initial_phase, max_rate_dev, out_sps)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(1, gr.GR_LSB_FIRST)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, '/Users/mmohamoud/software_defined_radios/ble_collect/demodulated_files/redesigned', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(1.0/sensivity)
        self.analog_pwr_squelch_xx_0 = analog.pwr_squelch_cc(sqlch_threshold, sqlch_alpha, 0, True)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_pwr_squelch_xx_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.digital_pfb_clock_sync_xxx_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.digital_pfb_clock_sync_xxx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.analog_pwr_squelch_xx_0, 0))

    def get_trans_wdth(self):
        return self.trans_wdth

    def set_trans_wdth(self, trans_wdth):
        self.trans_wdth = trans_wdth
        self.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff_freq, self.trans_wdth, firdes.WIN_HAMMING, 6.76))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff_freq, self.trans_wdth, firdes.WIN_HAMMING, 6.76))
        self.set_samp_per_sym(int(self.samp_rate/self.data_rate))
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.set_samp_per_sym_4(int(self.samp_rate/self.data_rate))
        self.set_filter_taps(firdes.root_raised_cosine(1.0,self.samp_rate,self.data_rate,.3,self.ntaps))

    def get_ntaps(self):
        return self.ntaps

    def set_ntaps(self, ntaps):
        self.ntaps = ntaps
        self.set_filter_taps(firdes.root_raised_cosine(1.0,self.samp_rate,self.data_rate,.3,self.ntaps))

    def get_data_rate(self):
        return self.data_rate

    def set_data_rate(self, data_rate):
        self.data_rate = data_rate
        self.set_samp_per_sym(int(self.samp_rate/self.data_rate))
        self.set_samp_per_sym_4(int(self.samp_rate/self.data_rate))
        self.set_filter_taps(firdes.root_raised_cosine(1.0,self.samp_rate,self.data_rate,.3,self.ntaps))

    def get_cutoff_freq(self):
        return self.cutoff_freq

    def set_cutoff_freq(self, cutoff_freq):
        self.cutoff_freq = cutoff_freq
        self.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff_freq, self.trans_wdth, firdes.WIN_HAMMING, 6.76))

    def get_taps(self):
        return self.taps

    def set_taps(self, taps):
        self.taps = taps
        self.freq_xlating_fir_filter_xxx_0.set_taps((self.taps))
        self.digital_pfb_clock_sync_xxx_0.update_taps((self.taps))

    def get_sqlch_threshold(self):
        return self.sqlch_threshold

    def set_sqlch_threshold(self, sqlch_threshold):
        self.sqlch_threshold = sqlch_threshold
        self.analog_pwr_squelch_xx_0.set_threshold(self.sqlch_threshold)

    def get_sqlch_alpha(self):
        return self.sqlch_alpha

    def set_sqlch_alpha(self, sqlch_alpha):
        self.sqlch_alpha = sqlch_alpha
        self.analog_pwr_squelch_xx_0.set_alpha(self.sqlch_alpha)

    def get_sensivity(self):
        return self.sensivity

    def set_sensivity(self, sensivity):
        self.sensivity = sensivity
        self.analog_quadrature_demod_cf_0.set_gain(1.0/self.sensivity)

    def get_samp_per_sym_4(self):
        return self.samp_per_sym_4

    def set_samp_per_sym_4(self, samp_per_sym_4):
        self.samp_per_sym_4 = samp_per_sym_4

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.uhd_usrp_source_0.set_gain(self.rf_gain, 0)


    def get_out_sps(self):
        return self.out_sps

    def set_out_sps(self, out_sps):
        self.out_sps = out_sps

    def get_max_rate_dev(self):
        return self.max_rate_dev

    def set_max_rate_dev(self, max_rate_dev):
        self.max_rate_dev = max_rate_dev

    def get_loop_bandwidth(self):
        return self.loop_bandwidth

    def set_loop_bandwidth(self, loop_bandwidth):
        self.loop_bandwidth = loop_bandwidth
        self.digital_pfb_clock_sync_xxx_0.set_loop_bandwidth(self.loop_bandwidth)

    def get_initial_phase(self):
        return self.initial_phase

    def set_initial_phase(self, initial_phase):
        self.initial_phase = initial_phase

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset

    def get_filter_taps(self):
        return self.filter_taps

    def set_filter_taps(self, filter_taps):
        self.filter_taps = filter_taps

    def get_filter_size(self):
        return self.filter_size

    def set_filter_size(self, filter_size):
        self.filter_size = filter_size

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        self.filename = filename

    def get_cntr_freq(self):
        return self.cntr_freq

    def set_cntr_freq(self, cntr_freq):
        self.cntr_freq = cntr_freq
        self.uhd_usrp_source_0.set_center_freq(self.cntr_freq, 0)


def main(top_block_cls=redesigned_gfsk, options=None):

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
