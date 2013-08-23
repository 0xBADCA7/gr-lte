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


#ifndef INCLUDED_LTE_DESCRAMBLER_VFVF_H
#define INCLUDED_LTE_DESCRAMBLER_VFVF_H

#include <lte_api.h>
#include <gr_sync_block.h>

#include <fftw3.h>
#include <volk/volk.h>

class lte_descrambler_vfvf;

typedef boost::shared_ptr<lte_descrambler_vfvf> lte_descrambler_vfvf_sptr;

LTE_API lte_descrambler_vfvf_sptr lte_make_descrambler_vfvf (std::string tag_key, std::string msg_buf_name, int len);

/*!
 * \brief LTE descrambler
 * \ingroup lte
 *
 */
class LTE_API lte_descrambler_vfvf : public gr_sync_block
{
 private:
	friend LTE_API lte_descrambler_vfvf_sptr lte_make_descrambler_vfvf (std::string tag_key, std::string msg_buf_name, int len);

	lte_descrambler_vfvf(std::string tag_key, std::string msg_buf_name, int len);

    pmt::pmt_t d_tag_key;
    pmt::pmt_t d_msg_buf;
    int d_len;

    std::vector<float*> d_scr_seq_vec;
    int d_scr_seq_len;
    int d_num_seqs;
    int d_seq_index;
    int d_part;

    inline void handle_msg(pmt::pmt_t msg);
    float* get_aligned_sequence(std::vector<float> seq);
    int get_seq_num(int idx);

 public:
  ~lte_descrambler_vfvf();

	// Where all the action really happens
	int work (int noutput_items,
	    gr_vector_const_void_star &input_items,
	    gr_vector_void_star &output_items);

    void set_descr_seqs(std::vector<std::vector<float> > seqs);
};

#endif /* INCLUDED_LTE_DESCRAMBLER_VFVF_H */

