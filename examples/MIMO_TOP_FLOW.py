#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: MIMO TOP FLOW
# Author: Kristian Maier, Johannes Demel
# Description: LTE decoding up to 2 tx antennas
# Generated: Wed Oct  1 15:56:28 2014
##################################################

execfile("/home/maier/.grc_gnuradio/decode_bch_hier_gr37.py")
execfile("/home/maier/.grc_gnuradio/lte_mimo_decode_pbch.py")
execfile("/home/maier/.grc_gnuradio/lte_mimo_estimator.py")
execfile("/home/maier/.grc_gnuradio/lte_mimo_ofdm_rx.py")
execfile("/home/maier/.grc_gnuradio/lte_mimo_pss_based_frey_sync.py")
execfile("/home/maier/.grc_gnuradio/lte_mimo_pss_sync.py")
execfile("/home/maier/.grc_gnuradio/lte_mimo_sss_sync.py")
from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import lte
import sip
import sys

from distutils.version import StrictVersion
class MIMO_TOP_FLOW(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "MIMO TOP FLOW")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("MIMO TOP FLOW")
        try:
             self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
             pass
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

        self.settings = Qt.QSettings("GNU Radio", "MIMO_TOP_FLOW")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.fftl = fftl = 1024
        self.samp_rate = samp_rate = fftl*15e3
        self.rxant = rxant = 2
        self.resampler = resampler = 400
        self.frame_key = frame_key = "slot"
        self.N_rb_dl = N_rb_dl = 50

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0_1 = filter.rational_resampler_ccc(
                interpolation=1536*fftl/1024,
                decimation=resampler,
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_ccc(
                interpolation=1536*fftl/1024,
                decimation=resampler,
                taps=None,
                fractional_bw=None,
        )
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
        	240*5, #size
        	"asummed 2 Tx antenna ports", #name
        	1 #number of inputs
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
                  "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_win)
        self.pbch_layer_demapper_vcvc_1 = lte.layer_demapper_vcvc(2, 240, "tx_diversity", "pbch_layer_demapper_vcvc_1")
        self.lte_mimo_sss_sync_0 = lte_mimo_sss_sync(
            N_rb_dl=N_rb_dl,
            rxant=rxant,
        )
        self.lte_mimo_pss_sync_0 = lte_mimo_pss_sync(
            rxant=rxant,
            synclen=4,
            fftlen=fftl,
        )
        self.lte_mimo_pss_based_frey_sync_0 = lte_mimo_pss_based_frey_sync(
            fftlen=fftl,
            rxant=rxant,
        )
        self.lte_mimo_pre_decoder_0_0 = lte.mimo_pre_decoder(rxant, 2, 240, "tx_diversity")
        self.lte_mimo_pbch_demux_0_1 = lte.mimo_pbch_demux(N_rb_dl, rxant)
        self.lte_mimo_pbch_demux_0_0 = lte.mimo_pbch_demux(N_rb_dl, rxant)
        self.lte_mimo_pbch_demux_0 = lte.mimo_pbch_demux(N_rb_dl, rxant)
        self.lte_mimo_ofdm_rx_0 = lte_mimo_ofdm_rx(
            N_rb_dl=N_rb_dl,
            ofdm_key=frame_key,
            fftlen=fftl,
            rxant=rxant,
        )
        self.lte_mimo_estimator_0 = lte_mimo_estimator(
            N_rb_dl=N_rb_dl,
            estimator_key=frame_key,
            initial_id=123,
            rxant=rxant,
        )
        self.lte_mimo_decode_pbch_0 = lte_mimo_decode_pbch(
            N_rb_dl=N_rb_dl,
            rxant=rxant,
        )
        self.blocks_vector_to_streams_0 = blocks.vector_to_streams(gr.sizeof_gr_complex*1, 2)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, 240)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*2, samp_rate,True)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*2, "/home/maier/LTE test files/live data/lte_capture_Wed_Aug_6_19:36:39_2014_RXant2_4MS_telekom_band1800_wg_karlruhe_hinten raus_messung1.dat", False)
        self.bch_decode_bch_hier_gr37_0 = decode_bch_hier_gr37()
        self.MIB = lte.mib_unpack_vbm("MIB")

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_vector_to_streams_0, 0), (self.rational_resampler_xxx_0_1, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_vector_to_streams_0, 0))
        self.connect((self.lte_mimo_pss_based_frey_sync_0, 0), (self.lte_mimo_ofdm_rx_0, 0))
        self.connect((self.lte_mimo_pss_sync_0, 0), (self.lte_mimo_pss_based_frey_sync_0, 0))
        self.connect((self.blocks_vector_to_streams_0, 1), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.rational_resampler_xxx_0_1, 0), (self.lte_mimo_pss_sync_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.lte_mimo_pss_sync_0, 1))
        self.connect((self.lte_mimo_sss_sync_0, 0), (self.lte_mimo_estimator_0, 0))
        self.connect((self.lte_mimo_sss_sync_0, 0), (self.lte_mimo_decode_pbch_0, 0))
        self.connect((self.lte_mimo_estimator_0, 0), (self.lte_mimo_decode_pbch_0, 1))
        self.connect((self.lte_mimo_estimator_0, 1), (self.lte_mimo_decode_pbch_0, 2))
        self.connect((self.lte_mimo_decode_pbch_0, 0), (self.bch_decode_bch_hier_gr37_0, 0))
        self.connect((self.lte_mimo_pss_sync_0, 1), (self.lte_mimo_pss_based_frey_sync_0, 1))
        self.connect((self.lte_mimo_pss_based_frey_sync_0, 1), (self.lte_mimo_ofdm_rx_0, 1))
        self.connect((self.lte_mimo_ofdm_rx_0, 0), (self.lte_mimo_sss_sync_0, 0))
        self.connect((self.lte_mimo_sss_sync_0, 0), (self.lte_mimo_pbch_demux_0, 0))
        self.connect((self.lte_mimo_pbch_demux_0_1, 0), (self.lte_mimo_pre_decoder_0_0, 2))
        self.connect((self.bch_decode_bch_hier_gr37_0, 0), (self.MIB, 0))
        self.connect((self.bch_decode_bch_hier_gr37_0, 1), (self.MIB, 1))
        self.connect((self.lte_mimo_pbch_demux_0, 0), (self.lte_mimo_pre_decoder_0_0, 0))
        self.connect((self.lte_mimo_pbch_demux_0_0, 0), (self.lte_mimo_pre_decoder_0_0, 1))
        self.connect((self.lte_mimo_estimator_0, 0), (self.lte_mimo_pbch_demux_0_0, 0))
        self.connect((self.lte_mimo_estimator_0, 1), (self.lte_mimo_pbch_demux_0_1, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.pbch_layer_demapper_vcvc_1, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.lte_mimo_pre_decoder_0_0, 0), (self.pbch_layer_demapper_vcvc_1, 0))

        ##################################################
        # Asynch Message Connections
        ##################################################
        self.msg_connect(self.lte_mimo_pss_sync_0, "N_id_2", self.lte_mimo_sss_sync_0, "N_id_2")
        self.msg_connect(self.lte_mimo_sss_sync_0, "cell_id", self.lte_mimo_estimator_0, "cell_id")
        self.msg_connect(self.lte_mimo_sss_sync_0, "cell_id", self.lte_mimo_pbch_demux_0, "cell_id")
        self.msg_connect(self.lte_mimo_sss_sync_0, "cell_id", self.lte_mimo_pbch_demux_0_0, "cell_id")
        self.msg_connect(self.lte_mimo_sss_sync_0, "cell_id", self.lte_mimo_pbch_demux_0_1, "cell_id")
        self.msg_connect(self.lte_mimo_sss_sync_0, "cell_id", self.lte_mimo_decode_pbch_0, "cell_id")

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "MIMO_TOP_FLOW")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_fftl(self):
        return self.fftl

    def set_fftl(self, fftl):
        self.fftl = fftl
        self.set_samp_rate(self.fftl*15e3)
        self.lte_mimo_pss_sync_0.set_fftlen(self.fftl)
        self.lte_mimo_pss_based_frey_sync_0.set_fftlen(self.fftl)
        self.lte_mimo_ofdm_rx_0.set_fftlen(self.fftl)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_rxant(self):
        return self.rxant

    def set_rxant(self, rxant):
        self.rxant = rxant
        self.lte_mimo_pss_sync_0.set_rxant(self.rxant)
        self.lte_mimo_pss_based_frey_sync_0.set_rxant(self.rxant)
        self.lte_mimo_ofdm_rx_0.set_rxant(self.rxant)
        self.lte_mimo_sss_sync_0.set_rxant(self.rxant)
        self.lte_mimo_estimator_0.set_rxant(self.rxant)
        self.lte_mimo_decode_pbch_0.set_rxant(self.rxant)

    def get_resampler(self):
        return self.resampler

    def set_resampler(self, resampler):
        self.resampler = resampler

    def get_frame_key(self):
        return self.frame_key

    def set_frame_key(self, frame_key):
        self.frame_key = frame_key
        self.lte_mimo_ofdm_rx_0.set_ofdm_key(self.frame_key)
        self.lte_mimo_estimator_0.set_estimator_key(self.frame_key)

    def get_N_rb_dl(self):
        return self.N_rb_dl

    def set_N_rb_dl(self, N_rb_dl):
        self.N_rb_dl = N_rb_dl
        self.lte_mimo_ofdm_rx_0.set_N_rb_dl(self.N_rb_dl)
        self.lte_mimo_sss_sync_0.set_N_rb_dl(self.N_rb_dl)
        self.lte_mimo_estimator_0.set_N_rb_dl(self.N_rb_dl)
        self.lte_mimo_decode_pbch_0.set_N_rb_dl(self.N_rb_dl)

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    if(StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0")):
        Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui','style','raster'))
    qapp = Qt.QApplication(sys.argv)
    tb = MIMO_TOP_FLOW()
    tb.start()
    tb.show()
    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None #to clean up Qt widgets
