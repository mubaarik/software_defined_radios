#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Usrp Out
# Generated: Tue Aug 21 10:48:06 2018
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import time


class usrp_out(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Usrp Out")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

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
        self.uhd_usrp_source_0.set_samp_rate(4e6)
        self.uhd_usrp_source_0.set_center_freq(2426e6, 0)
        self.uhd_usrp_source_0.set_gain(70, 0)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, 'raw_stream', False)
        self.blocks_file_sink_0.set_unbuffered(False)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_file_sink_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate


def main(top_block_cls=usrp_out, options=None):

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
