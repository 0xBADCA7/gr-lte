/* -*- c++ -*- */
/*
 * Copyright 2013 Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT)
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
#include "lte_pcfich_descrambler_vfvf.h"

#include <cstdio>

lte_pcfich_descrambler_vfvf_sptr
lte_make_pcfich_descrambler_vfvf (std::string tag_key, std::string msg_buf_name)
{
    return gnuradio::get_initial_sptr (new lte_pcfich_descrambler_vfvf(tag_key, msg_buf_name));
}


/*
 * The private constructor
 */
lte_pcfich_descrambler_vfvf::lte_pcfich_descrambler_vfvf (std::string tag_key, std::string msg_buf_name)
    : gr_sync_block ("pcfich_descrambler_vfvf",
                     gr_make_io_signature(1, 1, sizeof(float)*32),
                     gr_make_io_signature(1, 1, sizeof(float)*32)),
                     d_subframe(0)
{
    d_tag_key = pmt::pmt_string_to_symbol(tag_key);

    d_msg_buf = pmt::mp(msg_buf_name);
    message_port_register_in(d_msg_buf);
    set_msg_handler(d_msg_buf, boost::bind(&lte_pcfich_descrambler_vfvf::handle_msg, this, _1));

    set_cell_id(0);

}


/*
 * Our virtual destructor.
 */
lte_pcfich_descrambler_vfvf::~lte_pcfich_descrambler_vfvf()
{
    // Put in <+destructor stuff+> here
}


int
lte_pcfich_descrambler_vfvf::work(int noutput_items,
                                  gr_vector_const_void_star &input_items,
                                  gr_vector_void_star &output_items)
{
    const float *in = (const float *) input_items[0];
    float *out = (float *) output_items[0];

    //This part is for control / stream tag handling
    std::vector <gr_tag_t> v_b;
    get_tags_in_range(v_b, 0, nitems_read(0), nitems_read(0)+noutput_items, d_tag_key);
    if(v_b.size() > 0){
        //std::string srcid = "srcid"; //pmt::pmt_symbol_to_string(v_b[0].srcid );
        long offset = v_b[0].offset;
        int value           = int(pmt::pmt_to_long(v_b[0].value) );
        d_subframe = (value - int(offset-nitems_read(0)) +10)%10;
        //printf("%s\t%ld\tval = %i\tsubframe = %i\n", srcid.c_str(), offset, value, d_subframe );
    }


    // This part is for descrambling logic
    for(int i = 0; i < noutput_items; i++){
        //printf("Hello this is work, subframe = %i\n", d_subframe);
        volk_32f_x2_multiply_32f_u(out, in, d_scr_seq_vec[d_subframe], 32);
        d_subframe = (d_subframe+1)%10;
        out += 32;
        in += 32;
    }


    // Tell runtime system how many output items we produced.
    return noutput_items;
}

inline void
lte_pcfich_descrambler_vfvf::handle_msg(pmt::pmt_t msg)
{
    set_cell_id( int(pmt::pmt_to_long(msg)) );
}

inline void
lte_pcfich_descrambler_vfvf::set_cell_id(int cell_id)
{
    printf("%s set_cell_id = %i\n", name().c_str(), cell_id);
    setup_descr_seqs(cell_id);
}

inline void
lte_pcfich_descrambler_vfvf::setup_descr_seqs(int cell_id)
{
    //printf("setup_descr_seq BEGIN\n");
    d_scr_seq_vec.clear();
    for(int sub = 0; sub < 10; sub++) {
        d_scr_seq_vec.push_back(generate_scr_seq(cell_id, 2*sub) );
    }
}

inline float*
lte_pcfich_descrambler_vfvf::generate_scr_seq(int cell_id, int ns)
{
    //printf("generate_scr_seq BEGIN cell_id = %i\t ns = %i\n", cell_id, ns);
    int cinit = (floor(ns/2)+1) * (2*cell_id+1) * int(pow(2,9)) + cell_id;
    //printf("cinit = %i\t2pow9 = %f\n", cinit, pow(2,9) );
    float* scr_seq = (float*)fftwf_malloc(sizeof(float)*32);
    pn_seq_generator(scr_seq, 32, cinit);
    encode_nrz(scr_seq, scr_seq, 32);
    return scr_seq;
}

inline void
lte_pcfich_descrambler_vfvf::pn_seq_generator(float* vec, int len, int cinit)
{
    const int Nc=1600; //Constant is defined in standard
    char x2[3*len+Nc];
    for (int i = 0; i<31; i++) {
        char val = cinit%2;
        cinit = floor(cinit/2);
        x2[i] = val;
    }
    char *c=new char[len];
    char x1[3*len+Nc];
    // initialization for first 35 elements is needed. (Otherwise READ BEFORE WRITE ERROR)
    for (int i = 0 ; i < 35 ; i++) {
        x1[i]=0;
    }
    x1[0]=1;
    for (int n=0; n <2*len+Nc-3; n++) {
        x1[n+31]=(x1[n+3]+x1[n])%2;
        x2[n+31]=(x2[n+3]+x2[n+2]+x2[n+1]+x2[n])%2;
    }
    for (int n=0; n<len; n++) {
        vec[n]=float( (x1[n+Nc]+x2[n+Nc])%2 );
    }
}

void
lte_pcfich_descrambler_vfvf::encode_nrz(float* out, float* in, int len)
{
    for(int i = 0; i < len; i++) {
        out[i] = 1.0f - (float(in[i]) * 2.0f);
    }
}

std::vector<std::vector<float> >
lte_pcfich_descrambler_vfvf::get_descr_seqs()
{
    std::vector<std::vector<float> > mat;
    for(int i = 0; i < 10; i++) {
        std::vector<float> vec;
        for(int c = 0; c < 32; c++) {
            vec.push_back(d_scr_seq_vec[i][c]);
        }
        mat.push_back((vec));
    }
    return mat;
}



