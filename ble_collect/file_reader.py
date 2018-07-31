from gnuradio import gr, blocks
import os
import time

def file_reader(filename, d_type = gr.sizeof_float):
	print os.stat(filename)
	src = blocks.file_source(d_type, filename, False);
	snk = blocks.vector_sink_f()
	tb = gr.top_block()
	tb.connect(src,snk);
	print os.stat(filename)
	print snk.data()
	data = snk.data()
	time.sleep(2)
	return data
print file_reader('/Users/mmohamoud/software_defined_radios/data_files/demoded_data')