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

import numpy as np
import math
from gruel import pmt
from gnuradio import gr
from lte import utils

class estimator_parameterizer_msg(gr.sync_block):
    """
    docstring for block estimator_parameterizer_msg
    This block takes in a message with the extacted cell ID.
    Calculates the corresponding pilot symbols and positions and passes them on as a message
    """
    def __init__(self, msg_buf_name_in, msg_buf_name_out, N_rb_dl, ant_port):
        gr.sync_block.__init__(self,
            name="estimator_parameterizer_msg",
            in_sig=None,
            out_sig=None)
        #print msg_buf_name_in
        #print msg_buf_name_out
        #print N_rb_dl
        #print ant_port
        
        self.N_rb_dl = N_rb_dl
        self.ant_port = ant_port
        self.msg_buf_in = pmt.pmt_intern(msg_buf_name_in)
        self.msg_buf_out = pmt.pmt_intern(msg_buf_name_out)
        
        self.message_port_register_in(self.msg_buf_in)
        self.set_msg_handler(self.msg_buf_in, self.handle_msg)
        self.message_port_register_out(self.msg_buf_out)
        #self.message_port

    def handle_msg(self, msg):
        cell_id = pmt.pmt_to_long(msg)
        #print "generate pilot map: cell_id = " + str(cell_id) + "\tant_port = " + str(self.ant_port) 
        Ncp = 1 # Always 1 for our purposes --> thus it's hard coded
        [rs_poss, rs_vals] = self.frame_pilot_value_and_position(self.N_rb_dl, cell_id, Ncp, self.ant_port)
        
            
        pmt_rs = self.rs_pos_to_pmt(rs_poss)        
        pmt_vals = self.rs_val_to_pmt(rs_vals)
        pmt_pilots = pmt.pmt_list2(pmt_rs, pmt_vals)
        
        self.message_port_pub(self.msg_buf_out, pmt_pilots)
        #print "generate pilot map, ant_port = " + str(self.ant_port) + "\tFINISHED"
        
    def rs_val_to_pmt(self, rs_vals):
        pmt_vals = pmt.pmt_list1(self.complex_list_to_pmt(rs_vals[0]))
        for i in range(len(rs_vals)-1):
            pmt_vals = pmt.pmt_list_add(pmt_vals, self.complex_list_to_pmt(rs_vals[i+1]))
        return pmt_vals

    def complex_list_to_pmt(self, items):
        if len(items) == 0:
            return pmt.pmt_from_bool(pmt.PMT_F)
        else:
            pmtl = pmt.pmt_list1(pmt.pmt_from_complex(items[0]))
            for i in range(len(items)-1):
                pmtl = pmt.pmt_list_add(pmtl, pmt.pmt_from_complex(items[i+1]))
            return pmtl

    def rs_pos_to_pmt(self, rs_poss):
        pmt_rs = pmt.pmt_list1(self.int_list_to_pmt(rs_poss[0]))
        for i in range(len(rs_poss)-1):
            pmt_rs = pmt.pmt_list_add(pmt_rs, self.int_list_to_pmt(rs_poss[i+1]))
        return pmt_rs
            
    def int_list_to_pmt(self, items):
        if len(items) == 0:
            return pmt.pmt_from_bool(pmt.PMT_F)
        else:
            pmtl = pmt.pmt_list1(pmt.pmt_from_long(items[0]))
            for i in range(len(items)-1):
                pmtl = pmt.pmt_list_add(pmtl, pmt.pmt_from_long(items[i+1]))
            return pmtl
            

    def work(self, input_items, output_items):
        out = output_items[0]
        # <+signal processing here+>
        out[:] = 1
        
        return len(output_items[0])
        
    def frame_pilot_value_and_position(self, N_rb_dl, cell_id, Ncp, p):
        rs_pos_frame = []
        rs_val_frame = []
        for ns in range(20):
            sym0 = self.symbol_pilot_value_and_position(N_rb_dl, ns, 0, cell_id, Ncp, p)
            sym4 = self.symbol_pilot_value_and_position(N_rb_dl, ns, 4, cell_id, Ncp, p)
            rs_pos_frame.extend([sym0[0], [], [], [], sym4[0], [], [] ])
            rs_val_frame.extend([sym0[1], [], [], [], sym4[1], [], [] ])
        return [rs_pos_frame, rs_val_frame]
         
    def symbol_pilot_value_and_position(self, N_rb_dl, ns, l, cell_id, Ncp, p):
        N_RB_MAX = 110
        rs_seq = self.rs_generator(ns, l, cell_id, Ncp)
        offset = self.calc_offset(ns, l, cell_id, p)
        rs_sym_pos = range(offset, 12*N_rb_dl, 6)
        rs_sym_val = rs_seq[N_RB_MAX-N_rb_dl:N_RB_MAX+N_rb_dl]
        return [rs_sym_pos, rs_sym_val]
        
    def rs_generator(self, ns, l, cell_id, Ncp):
        N_RB_MAX = 110
        SQRT2 = np.sqrt(2.0)
        cinit = 1024*(7*(ns+1)+l+1)*(2*cell_id+1)+2*cell_id+Ncp
        pn_seq = self.pn_generator(4*N_RB_MAX,cinit)
        rs_seq = []
        for m in range(2*N_RB_MAX):
            rs_seq.append(complex((1-2*pn_seq[2*m])/SQRT2, (1-2*pn_seq[2*m+1])/SQRT2 ) )
        return rs_seq
        
    def pn_generator(self, vector_len, cinit):
        NC=1600
        x2 = [0]*(3*vector_len+NC)
        for i in range(31):
            x2[i] = cinit%2
            cinit = int(math.floor(cinit/2))
        x1 = [0]*(3*vector_len+NC)
        x1[0] = 1
        for n in range(2*vector_len+NC-3):
            x1[n+31]=(x1[n+3]+x1[n])%2
            x2[n+31]=(x2[n+3]+x2[n+2]+x2[n+1]+x2[n])%2
        output = [0] * vector_len
        for n in range(vector_len):
            output[n]=(x1[n+NC]+x2[n+NC])%2
        return output
        
    def calc_offset(self, ns, l, cell_id, p):
        v = self.calc_v(ns, l,  p)
        return ( v + (cell_id%6) )%6

    def calc_v(self, ns, l, p):
        v = 0
        if p == 0 and l == 0:
            v = 0
        elif p == 0 and l != 0:
            v = 3
        elif p == 1 and l == 0:
            v = 3
        elif p == 1 and l != 0:
            v = 0
        elif p == 2:
            v = 3*(ns%2)
        elif p==3:
            v = 3*3*(ns%2)
        return v

