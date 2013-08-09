#!/usr/bin/env python
# 
# Copyright 2013 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
import lte

class decode_pcfich_vcm(gr.hier_block2):
    """
    This is a hierarchical block which includes all parameterized blocks to decode the PCFICH
    """
    def __init__(self, N_rb_dl, key, out_key, msg_buf_name):
        gr.hier_block2.__init__(self,
            "decode_pcfich_vcm",
            gr.io_signature(3, 3, gr.sizeof_gr_complex * 12 * N_rb_dl),  # Input signature
            gr.io_signature(0, 0, 0)) # Output signature
        self.message_port_register_hier_out(msg_buf_name)
        
        # define some variables
        cvlen = 16
        fvlen = 2 * cvlen
        N_ant = 2
        style = "tx_diversity"
        
        self.demux = lte.pcfich_demux_vcvc(N_rb_dl, key, out_key, msg_buf_name)
        self.predecoder = lte.pre_decoder_vcvc(N_ant, cvlen, style)
        self.demapper = lte.layer_demapper_vcvc(N_ant, cvlen, style)
        self.qpsk = lte.qpsk_soft_demod_vcvf(cvlen)
        self.descrambler = lte.pcfich_descrambler_vfvf(out_key, msg_buf_name)
        self.unpack = lte.cfi_unpack_vf(out_key)

        # Define blocks and connect them
        self.connect((self, 0), (self.demux, 0), (self.predecoder, 0))
        self.connect((self, 1), (self.demux, 1), (self.predecoder, 1))
        self.connect((self, 2), (self.demux, 2), (self.predecoder, 2))
        self.connect(self.predecoder, self.demapper, self.qpsk, self.descrambler, self.unpack)
