#!/usr/bin/env python
# 
# Copyright 2013 Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT)
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

from gnuradio import gr, gr_unittest, blocks
from gruel import pmt
import lte
from lte_test import *

class qa_cfi_unpack_vf (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        
        key = "subframe"
        print "setup test"
        
        data = []
        for i in range(3):
            cfi = get_cfi_sequence(i+1)
            data.extend(nrz_encoding(cfi))
        
        reps = 5
        taglist = get_tag_list(3*reps, key, 10)
        
        data = [float(data[i]) for i in range(len(data))]
        ext_data = []
        for i in range(reps):
            ext_data.extend(data)
        data = ext_data
        
        self.src = blocks.vector_source_f(data, False, 32, taglist)
        self.cfi = lte.cfi_unpack_vf(key)
        self.dbg = blocks.message_debug()
        
        self.tb.connect(self.src, self.cfi)
        self.tb.msg_connect(self.cfi, "cfi", self.dbg, "print")
        print "setup finished"

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        print "run test"
        # set up fg
        self.tb.run ()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_cfi_unpack_vf)
