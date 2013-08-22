/* -*- c++ -*- */
/*
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_io_signature.h>
#include "lte_descrambler_vfvf.h"
#include <cstdio>

lte_descrambler_vfvf_sptr
lte_make_descrambler_vfvf (std::string tag_key, std::string msg_buf_name, int len)
{
	return gnuradio::get_initial_sptr (new lte_descrambler_vfvf(tag_key, msg_buf_name, len));
}


/*
 * The private constructor
 */
lte_descrambler_vfvf::lte_descrambler_vfvf (std::string tag_key, std::string msg_buf_name, int len)
  : gr_sync_block ("descrambler_vfvf",
		   gr_make_io_signature(1, 1, sizeof(float) * len),
		   gr_make_io_signature(1, 1, sizeof(float) * len)),
		   d_len(len),
		   d_seq_index(0)
{
    d_tag_key = pmt::pmt_string_to_symbol(tag_key);

    d_msg_buf = pmt::mp(msg_buf_name);
    message_port_register_in(d_msg_buf);
    set_msg_handler(d_msg_buf, boost::bind(&lte_descrambler_vfvf::handle_msg, this, _1));
}


/*
 * Our virtual destructor.
 */
lte_descrambler_vfvf::~lte_descrambler_vfvf()
{
	// Put in <+destructor stuff+> here
}


int
lte_descrambler_vfvf::work(int noutput_items,
		  gr_vector_const_void_star &input_items,
		  gr_vector_void_star &output_items)
{
	const float *in = (const float *) input_items[0];
	float *out = (float *) output_items[0];

    int part = 0;
    int seq_num = get_seq_num(0);
    for(int i = 0; i < noutput_items; i++){
        int next = get_seq_num(i);
        if(seq_num !=  next){
            part = 0;
            seq_num = next;
        }
        //printf("seq_num = %i\tpart = %i\tidx = %i\n", seq_num, part, i);
        volk_32f_x2_multiply_32f_u(out, in, &d_scr_seq_vec[seq_num][part*d_len], d_len);
        part = (part+1)%(d_scr_seq_len/d_len);
        out += d_len;
        in += d_len;
    }

	// Tell runtime system how many output items we produced.
	return noutput_items;
}

int
lte_descrambler_vfvf::get_seq_num(int idx)
{
    int seq_num = 0;
    int pos = nitems_read(0)+idx;
    std::vector <gr_tag_t> v_b;
    get_tags_in_range(v_b, 0, pos, pos+1, d_tag_key);
    if(v_b.size() > 0){
        //std::string srcid = "srcid"; //pmt::pmt_symbol_to_string(v_b[0].srcid );
        long offset = v_b[0].offset;
        int value = int(pmt::pmt_to_long(v_b[0].value) );
        seq_num = (value - int(offset-pos) +d_num_seqs)%d_num_seqs;
        d_seq_index = seq_num;
//        printf("NEW\t");
    }
    else{
        seq_num = d_seq_index;
//        printf("OLD\t");
    }
    //printf("get_seq_num = %i\tidx = %i\tpos = %i\n", seq_num, idx, pos);
    return seq_num;
}

inline void
lte_descrambler_vfvf::handle_msg(pmt::pmt_t msg)
{
    pmt::pmt_print(msg);
}

void
lte_descrambler_vfvf::set_descr_seqs(std::vector<std::vector<float> > seqs)
{

    d_scr_seq_len = seqs[0].size();
    d_num_seqs = seqs.size();
    //printf("setup_descr_seq BEGIN\t%i\n", d_scr_seq_len);
    d_scr_seq_vec.clear();
    for(int n = 0; n < seqs.size(); n++) {
        d_scr_seq_vec.push_back(get_aligned_sequence(seqs[n]));
    }
//    for(int i = 0; i < d_scr_seq_len; i++){
//        for(int el = 0; el < seqs.size(); el++){
//            printf("%+1.2f  ", seqs[el][i]-d_scr_seq_vec[el][i]);
//        }
//        printf("\n");
//    }
}

float*
lte_descrambler_vfvf::get_aligned_sequence(std::vector<float> seq)
{
    float* vec = (float*)fftwf_malloc(sizeof(float)*seq.size() );
    memcpy(vec, &seq[0], sizeof(float)*seq.size() );
}








