#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: LTE flowgraph
# Author: Johannes Demel
# Generated: Mon Nov 12 11:19:33 2012
##################################################

from PyQt4 import Qt
from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.qtgui import qtgui
from optparse import OptionParser
import lte
import sip
import sys

class LTE_flowgraph(gr.top_block, Qt.QWidget):

	def __init__(self):
		gr.top_block.__init__(self, "LTE flowgraph")
		Qt.QWidget.__init__(self)
		self.setWindowTitle("LTE flowgraph")
		self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
		self.top_scroll_layout = Qt.QVBoxLayout()
		self.setLayout(self.top_scroll_layout)
		self.top_scroll = Qt.QScrollArea()
		self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
		self.top_scroll_layout.addWidget(self.top_scroll)
		self.top_scroll.setWidgetResizable(True)
		self.top_widget = Qt.QWidget()
		self.top_scroll.setWidget(self.top_widget)
		self.top_layout = Qt.QVBoxLayout(self.top_widget)
		self.top_grid_layout = Qt.QGridLayout()
		self.top_layout.addLayout(self.top_grid_layout)


		##################################################
		# Variables
		##################################################
		self.fftlen = fftlen = 512
		self.cpl0 = cpl0 = 160*fftlen/2048
		self.cpl = cpl = 144*fftlen/2048
		self.slotl = slotl = 7*fftlen+6*cpl+cpl0
		self.samp_rate = samp_rate = slotl/0.0005
		self.style = style = "tx_diversity"
		self.interp_val = interp_val = int(samp_rate/1e4)
		self.N_rb_dl = N_rb_dl = 6

		##################################################
		# Blocks
		##################################################
		self.eq = lte.linear_OFDM_equalizer_hier_vcvc(N_rb_dl)
		self.descr = lte.descrambling_vfvf()
		self.demux = lte.pbch_demux_vcvc(N_rb_dl)
		self.daemon = lte.cell_id_daemon(self.eq.eq, self.demux, self.descr)
		self.qtgui_sink_x_0 = qtgui.sink_c(
			1024, #fftsize
			firdes.WIN_BLACKMAN_hARRIS, #wintype
			0, #fc
			samp_rate, #bw
			"QT GUI Plot", #name
			True, #plotfreq
			True, #plotwaterfall
			True, #plottime
			True, #plotconst
		)
		self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)
		self.top_layout.addWidget(self._qtgui_sink_x_0_win)
		self.lte_viterbi_vfvb_0 = lte.viterbi_vfvb()
		self.lte_remove_cp_cvc_1 = lte.remove_cp_cvc(fftlen)
		self.lte_rate_unmatch_vff_0 = lte.rate_unmatch_vff()
		self.lte_qpsk_soft_demod_vcvf_0 = lte.qpsk_soft_demod_vcvf()
		self.lte_pss_sync_hier_cc_0 = lte.pss_sync_hier_cc(fftlen)
		self.lte_pre_decoder_vcvc_0_0 = lte.pre_decoder_vcvc(2, style)
		self.lte_pre_decoder_vcvc_0 = lte.pre_decoder_vcvc(1, style)
		self.lte_mib_unpack_vb_0 = lte.mib_unpack_vb()
		self.lte_layer_demapper_vcvc_0_0 = lte.layer_demapper_vcvc(2, style)
		self.lte_layer_demapper_vcvc_0 = lte.layer_demapper_vcvc(1, style)
		self.lte_hier_sss_sync_cc_0 = lte.hier_sss_sync_cc(self.daemon, fftlen)
		self.lte_hier_freq_estimate_cc_0 = lte.hier_freq_estimate_cc(fftlen)
		self.lte_extract_occupied_tones_vcvc_0 = lte.extract_occupied_tones_vcvc(N_rb_dl,fftlen)
		self.lte_crc_calculator_vbvb_0 = lte.crc_calculator_vbvb()
		self.lte_cp_time_freq_sync_cc_0 = lte.cp_time_freq_sync_cc(fftlen)
		self.gr_vector_to_stream_0 = gr.vector_to_stream(gr.sizeof_gr_complex*1, 240)
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, samp_rate)
		self.gr_interleave_0 = gr.interleave(gr.sizeof_gr_complex*240)
		self.gr_file_source_0 = gr.file_source(gr.sizeof_gr_complex*1, "/home/demel/Dokumente/Messungen_31_10_2012/samples_12.5MSps_20dB.iq", False)
		self.fft_vxx_0 = fft.fft_vcc(fftlen, True, (window.rectangular(fftlen)), False, 1)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_ccc(
			interpolation=interp_val,
			decimation=1250,
			taps=None,
			fractional_bw=None,
		)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_file_source_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.lte_hier_freq_estimate_cc_0, 0), (self.lte_hier_sss_sync_cc_0, 0))
		self.connect((self.lte_pss_sync_hier_cc_0, 0), (self.lte_hier_freq_estimate_cc_0, 0))
		self.connect((self.lte_cp_time_freq_sync_cc_0, 0), (self.lte_pss_sync_hier_cc_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.lte_cp_time_freq_sync_cc_0, 0))
		self.connect((self.lte_hier_sss_sync_cc_0, 0), (self.lte_remove_cp_cvc_1, 0))
		self.connect((self.fft_vxx_0, 0), (self.lte_extract_occupied_tones_vcvc_0, 0))
		self.connect((self.lte_remove_cp_cvc_1, 0), (self.fft_vxx_0, 0))
		self.connect((self.lte_extract_occupied_tones_vcvc_0, 0), (self.eq, 0))
		self.connect((self.lte_pre_decoder_vcvc_0, 0), (self.lte_layer_demapper_vcvc_0, 0))
		self.connect((self.eq, 0), (self.demux, 0))
		self.connect((self.eq, 1), (self.demux, 1))
		self.connect((self.eq, 2), (self.demux, 2))
		self.connect((self.lte_pre_decoder_vcvc_0_0, 0), (self.lte_layer_demapper_vcvc_0_0, 0))
		self.connect((self.lte_layer_demapper_vcvc_0_0, 0), (self.gr_interleave_0, 1))
		self.connect((self.demux, 1), (self.lte_pre_decoder_vcvc_0_0, 1))
		self.connect((self.demux, 1), (self.lte_pre_decoder_vcvc_0, 1))
		self.connect((self.demux, 0), (self.lte_pre_decoder_vcvc_0, 0))
		self.connect((self.demux, 2), (self.lte_pre_decoder_vcvc_0_0, 2))
		self.connect((self.demux, 0), (self.lte_pre_decoder_vcvc_0_0, 0))
		self.connect((self.lte_qpsk_soft_demod_vcvf_0, 0), (self.descr, 0))
		self.connect((self.gr_interleave_0, 0), (self.lte_qpsk_soft_demod_vcvf_0, 0))
		self.connect((self.lte_layer_demapper_vcvc_0, 0), (self.gr_interleave_0, 0))
		self.connect((self.descr, 0), (self.lte_rate_unmatch_vff_0, 0))
		self.connect((self.lte_crc_calculator_vbvb_0, 1), (self.lte_mib_unpack_vb_0, 1))
		self.connect((self.lte_crc_calculator_vbvb_0, 0), (self.lte_mib_unpack_vb_0, 0))
		self.connect((self.lte_viterbi_vfvb_0, 0), (self.lte_crc_calculator_vbvb_0, 0))
		self.connect((self.lte_rate_unmatch_vff_0, 0), (self.lte_viterbi_vfvb_0, 0))
		self.connect((self.gr_interleave_0, 0), (self.gr_vector_to_stream_0, 0))
		self.connect((self.gr_vector_to_stream_0, 0), (self.qtgui_sink_x_0, 0))

	def get_fftlen(self):
		return self.fftlen

	def set_fftlen(self, fftlen):
		self.fftlen = fftlen
		self.set_cpl0(160*self.fftlen/2048)
		self.set_slotl(7*self.fftlen+6*self.cpl+self.cpl0)
		self.set_cpl(144*self.fftlen/2048)

	def get_cpl0(self):
		return self.cpl0

	def set_cpl0(self, cpl0):
		self.cpl0 = cpl0
		self.set_slotl(7*self.fftlen+6*self.cpl+self.cpl0)

	def get_cpl(self):
		return self.cpl

	def set_cpl(self, cpl):
		self.cpl = cpl
		self.set_slotl(7*self.fftlen+6*self.cpl+self.cpl0)

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
		self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)

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
	qapp = Qt.QApplication(sys.argv)
	tb = LTE_flowgraph()
	tb.start()
	tb.show()
	qapp.exec_()
	tb.stop()

