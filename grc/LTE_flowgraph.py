#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: LTE flowgraph
# Author: Johannes Demel
# Generated: Thu Apr 18 16:31:18 2013
##################################################

from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from optparse import OptionParser
import lte

class LTE_flowgraph(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "LTE flowgraph")

		##################################################
		# Variables
		##################################################
		self.fft_len = fft_len = 2048
		self.cpl0 = cpl0 = 160*fft_len/2048
		self.cpl = cpl = 144*fft_len/2048
		self.slotl = slotl = 7*fft_len+6*cpl+cpl0
		self.samp_rate = samp_rate = slotl/0.0005
		self.style = style = "tx_diversity"
		self.interp_val = interp_val = int(samp_rate/1e4)
		self.N_rb_dl = N_rb_dl = 6

		##################################################
		# Blocks
		##################################################
		self.lte_remove_cp_cvc_1 = lte.remove_cp_cvc(fft_len)
		self.lte_pbch_demux_vcvc_1 = lte.pbch_demux_vcvc(N_rb_dl)
		self.lte_mib_unpack_vb_0 = lte.mib_unpack_vb()
		self.lte_hier_sss_sync_cc_1 = lte.hier_sss_sync_cc(fft_len)
		self.lte_hier_pss_sync_cc_0 = lte.hier_pss_sync_cc(fft_len)
		self.lte_hier_freq_estimate_cc_0 = lte.hier_freq_estimate_cc(fft_len)
		self.lte_extract_occupied_tones_vcvc_0 = lte.extract_occupied_tones_vcvc(N_rb_dl,fft_len)
		self.lte_decode_pbch_vcvf_0 = lte.decode_pbch_vcvf()
		self.lte_decode_bch_vfvb_0 = lte.decode_bch_vfvb()
		self.lte_cp_time_freq_sync_cc_0 = lte.cp_time_freq_sync_cc(fft_len)
		self.lte_channel_estimator_0 = lte.channel_estimator(N_rb_dl)
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, samp_rate)
		self.gr_file_source_0 = gr.file_source(gr.sizeof_gr_complex*1, "/home/demel/Dokumente/Messungen/Messung_LTE_2012-05-23_12:47:32.dat", False)
		self.fft_vxx_0 = fft.fft_vcc(fft_len, True, (window.rectangular(fft_len)), False, 1)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_ccc(
			interpolation=interp_val,
			decimation=1000,
			taps=None,
			fractional_bw=None,
		)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_file_source_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.lte_cp_time_freq_sync_cc_0, 0), (self.lte_hier_pss_sync_cc_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.lte_cp_time_freq_sync_cc_0, 0))
		self.connect((self.lte_hier_pss_sync_cc_0, 0), (self.lte_hier_freq_estimate_cc_0, 0))
		self.connect((self.lte_extract_occupied_tones_vcvc_0, 0), (self.lte_channel_estimator_0, 0))
		self.connect((self.lte_decode_bch_vfvb_0, 0), (self.lte_mib_unpack_vb_0, 0))
		self.connect((self.lte_decode_bch_vfvb_0, 1), (self.lte_mib_unpack_vb_0, 1))
		self.connect((self.lte_decode_pbch_vcvf_0, 0), (self.lte_decode_bch_vfvb_0, 0))
		self.connect((self.lte_pbch_demux_vcvc_1, 0), (self.lte_decode_pbch_vcvf_0, 0))
		self.connect((self.lte_pbch_demux_vcvc_1, 1), (self.lte_decode_pbch_vcvf_0, 1))
		self.connect((self.lte_pbch_demux_vcvc_1, 2), (self.lte_decode_pbch_vcvf_0, 2))
		self.connect((self.lte_channel_estimator_0, 1), (self.lte_pbch_demux_vcvc_1, 1))
		self.connect((self.lte_channel_estimator_0, 0), (self.lte_pbch_demux_vcvc_1, 0))
		self.connect((self.lte_remove_cp_cvc_1, 0), (self.fft_vxx_0, 0))
		self.connect((self.fft_vxx_0, 0), (self.lte_extract_occupied_tones_vcvc_0, 0))
		self.connect((self.lte_hier_sss_sync_cc_1, 0), (self.lte_remove_cp_cvc_1, 0))
		self.connect((self.lte_hier_freq_estimate_cc_0, 0), (self.lte_hier_sss_sync_cc_1, 0))
		self.connect((self.lte_channel_estimator_0, 2), (self.lte_pbch_demux_vcvc_1, 2))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.gr_throttle_0, 0))

		##################################################
		# Asynch Message Connections
		##################################################
		self.msg_connect(self.lte_hier_sss_sync_cc_1, "cell_id", self.lte_decode_pbch_vcvf_0, "cell_id")
		self.msg_connect(self.lte_hier_sss_sync_cc_1, "cell_id", self.lte_pbch_demux_vcvc_1, "cell_id")
		self.msg_connect(self.lte_hier_sss_sync_cc_1, "cell_id", self.lte_channel_estimator_0, "cell_id")

	def get_fft_len(self):
		return self.fft_len

	def set_fft_len(self, fft_len):
		self.fft_len = fft_len
		self.set_cpl(144*self.fft_len/2048)
		self.set_cpl0(160*self.fft_len/2048)
		self.set_slotl(7*self.fft_len+6*self.cpl+self.cpl0)

	def get_cpl0(self):
		return self.cpl0

	def set_cpl0(self, cpl0):
		self.cpl0 = cpl0
		self.set_slotl(7*self.fft_len+6*self.cpl+self.cpl0)

	def get_cpl(self):
		return self.cpl

	def set_cpl(self, cpl):
		self.cpl = cpl
		self.set_slotl(7*self.fft_len+6*self.cpl+self.cpl0)

	def get_slotl(self):
		return self.slotl

	def set_slotl(self, slotl):
		self.slotl = slotl
		self.set_samp_rate(self.slotl/0.0005)

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.set_interp_val(int(self.samp_rate/1e4))
		self.gr_throttle_0.set_sample_rate(self.samp_rate)

	def get_style(self):
		return self.style

	def set_style(self, style):
		self.style = style

	def get_interp_val(self):
		return self.interp_val

	def set_interp_val(self, interp_val):
		self.interp_val = interp_val

	def get_N_rb_dl(self):
		return self.N_rb_dl

	def set_N_rb_dl(self, N_rb_dl):
		self.N_rb_dl = N_rb_dl

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = LTE_flowgraph()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

