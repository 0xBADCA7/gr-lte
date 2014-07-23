/* -*- c++ -*- */
/*
 * Copyright 2014 Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT)
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

#include <gnuradio/io_signature.h>
#include "mimo_pre_decoder_impl.h"

#include <cstdio>
#include <cmath>
#include <volk/volk.h>

namespace gr {
  namespace lte {

    mimo_pre_decoder::sptr
    mimo_pre_decoder::make(int rxant, int N_ant, int vlen, std::string style)
    {
      return gnuradio::get_initial_sptr
        (new mimo_pre_decoder_impl(rxant, N_ant, vlen, style));
    }

    /*
     * The private constructor
     */
    mimo_pre_decoder_impl::mimo_pre_decoder_impl(int rxant, int N_ant, int vlen, std::string style)
      : gr::sync_block("mimo_pre_decoder",
              gr::io_signature::make( 2, 3, sizeof(gr_complex) * vlen * rxant),
              gr::io_signature::make( 1, 1, sizeof(gr_complex) * vlen)),
              d_vlen(vlen),
              d_rxant(rxant)
    {
        set_N_ant(N_ant);
		set_decoding_style(style);
		setup_volk_vectors(vlen);

		pmt::pmt_t msg_buf = pmt::mp("N_ant");
		message_port_register_in(msg_buf);
		set_msg_handler(msg_buf, boost::bind(&mimo_pre_decoder_impl::handle_msg, this, _1));
	}

    /*
     * Our virtual destructor.
     */
    mimo_pre_decoder_impl::~mimo_pre_decoder_impl()
    {
        volk_free(d_h0);
        volk_free(d_h1);
        volk_free(d_r0);
        volk_free(d_r1);

        volk_free(d_out);
        volk_free(d_out0);
        volk_free(d_out1);

        volk_free(d_mult0);
        volk_free(d_mult1);
    }

    int
    mimo_pre_decoder_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
		const gr_complex *ce0 = (const gr_complex *) input_items[1];    //channel estimate ant port 0
		gr_complex *out = (gr_complex *) output_items[0];

		if (d_N_ant == 1){
			for(int i = 0; i < noutput_items; i++){
                decode_1_ant(out, in, ce0, d_vlen);
				in  += d_vlen * d_rxant;
				ce0 += d_vlen * d_rxant;
				out += d_vlen;
			}
		}
		else if(d_N_ant == 2){
			const gr_complex *ce1 = (const gr_complex *) input_items[2];      //channel estimate ant port 1
			for(int i = 0; i < noutput_items; i++){
//                memset(out, 0, sizeof(gr_complex)*d_vlen);

//                prepare_2_ant_vectors(d_h0, d_h1, d_r0, d_r1, in, ce0, ce1, d_vlen);
                decode_2_ant(d_out0, d_out1, d_h0, d_h1, d_r0, d_r1, in, ce0, ce1, d_vlen);
                combine_output(out, d_out0, d_out1, d_vlen);
//                    volk_32f_x2_add_32f_a((float*) out, (float*) out, (float*) d_out, d_vlen*2);

                in  += d_vlen * d_rxant;
                ce0 += d_vlen * d_rxant;
                ce1 += d_vlen * d_rxant;
                out += d_vlen;
//				volk_32fc_s32fc_multiply_32fc_a(out, out, gr_complex(1.0/d_rxant,0), d_vlen);

			}
		}


		// Tell runtime system how many output items we produced.
		return noutput_items;
    }

    void
	mimo_pre_decoder_impl::decode_1_ant(gr_complex* out,
									   const gr_complex* rx,
									   const gr_complex* h,
                                       int len)
	{
        /*
            RX
            r_ant0 = h0 x0
            r_ant1 = h1 x0

            estimate
            e_x0 = (h0* r_ant0 + h1* r_ant1) / (|h0|² + |h1|²)

        */
        //binary representation of 0.0 is 0b0;
        memset(d_mag, 0, sizeof(float)*len);
        memset(out, 0, sizeof(gr_complex)*len);

        for(int i=0; i<d_rxant; i++){

            volk_32fc_x2_multiply_conjugate_32fc_a(d_out, rx, h, len);
            volk_32f_x2_add_32f_a((float*) out, (float*) out, (float*) d_out, len*2);

            volk_32fc_magnitude_squared_32f_a(d_mag_h, h, len);
            volk_32f_x2_add_32f_a(d_mag, d_mag, d_mag_h, len);

            rx  += len;
            h += len;
		}

		//invert sum of squared channel coeffs
		for(int i=0; i<len; i++){
            d_mag[i] = 1.0/d_mag[i];
		}

		volk_32fc_32f_multiply_32fc_a(out, out, d_mag, len);

    }

	void
	mimo_pre_decoder_impl::prepare_2_ant_vectors(gr_complex* h0,
                                                gr_complex* h1,
                                                gr_complex* r0,
                                                gr_complex* r1,
                                                const gr_complex* rx,
												const gr_complex* ce0,
												const gr_complex* ce1,
												int len)
	{
		for(int n = 0; n < len/2; n++){
			h0[n] = ce0[2*n];           //assume adjacent carriers are fading similiar
			h1[n] = ce1[2*n];
			r0[n] = rx[2*n];
			r1[n] = rx[2*n+1];
		}
	}

	void
	mimo_pre_decoder_impl::decode_2_ant(gr_complex* out0,
                                        gr_complex* out1,
                                        gr_complex* h0,
                                        gr_complex* h1,
                                        gr_complex* r0,
                                        gr_complex* r1,
                                        const gr_complex* rx,
                                        const gr_complex* ce0,
                                        const gr_complex* ce1,
                                        int len)
	{
		/*
		alamouti Coding
                freq0  freq1
		tx_ant0  x0    x1
		tx_ant1 -x1*   x0*

		RX_antX
		r_antX_f0 = h0_X x0 - h1_X x1*
		r_antX_f1 = h0_X x1 + h1_X x0*

		estimate
		e_x0 = ( SUM_X (h0_X* r_antX_f0 + h1_X r_antX_f1*) ) / SUM_X(|h0_X|²+|h1_X|²)
		e_x1 = ( SUM_x (h0_X* r_antX_f1 - h1_X r_antX_f0*) ) / SUM_X(|h0_X|²+|h1_X|²)
		*/

		int len2 = len/2;

        //binary representation of 0.0 is 0b0;
        memset(d_mag, 0, sizeof(float)*len2);
        memset(out0, 0, sizeof(gr_complex)*len2);
        memset(out1, 0, sizeof(gr_complex)*len2);

        for(int i=0; i<d_rxant; i++){

            prepare_2_ant_vectors(h0, h1, r0, r1, rx, ce0, ce1, len);

            // e_x0, layer0
            volk_32fc_x2_multiply_conjugate_32fc_a(d_mult0, r0, h0, len2);
            volk_32fc_x2_multiply_conjugate_32fc_a(d_mult1, h1, r1, len2);
            volk_32f_x2_add_32f_a( (float*)d_mult0, (float*)d_mult0, (float*)d_mult1, 2*len2);
            volk_32f_x2_add_32f_a( (float*)out0,    (float*)out0,    (float*)d_mult0, 2*len2);

            //e_x1, layer1
            volk_32fc_x2_multiply_conjugate_32fc_a(d_mult0, r1, h0, len2);
            volk_32fc_x2_multiply_conjugate_32fc_a(d_mult1, h1, r0, len2);
            volk_32f_x2_subtract_32f_a( (float*)d_mult0, (float*)d_mult0, (float*)d_mult1, 2*len2);
            volk_32f_x2_add_32f_a( (float*)out1,    (float*)out1,    (float*)d_mult0, 2*len2);

            //sum of squared channel coeffs
            volk_32fc_magnitude_squared_32f_a(d_mag_h, h0, len2);
            volk_32f_x2_add_32f_a(d_mag, d_mag, d_mag_h, len2);
            volk_32fc_magnitude_squared_32f_a(d_mag_h, h1, len2);
            volk_32f_x2_add_32f_a(d_mag, d_mag, d_mag_h, len2);

            rx += len;
            ce0 += len;
            ce1 += len;

        }

        //invert sum of squared channel coeffs and divide
		for(int i=0; i<len/2; i++){
            d_mag[i] = 1.0/d_mag[i];
		}
		//divide by sum of channel coeffs
		volk_32fc_32f_multiply_32fc_a(out0, out0, d_mag, len/2);
		volk_32fc_32f_multiply_32fc_a(out1, out1, d_mag, len/2);

        // Do correct scaling
        gr_complex divsqrt2 = gr_complex(std::sqrt(2),0);
        volk_32fc_s32fc_multiply_32fc_a(out0, out0, divsqrt2, len/2);
        volk_32fc_s32fc_multiply_32fc_a(out1, out1, divsqrt2, len/2);
	}

	void
	mimo_pre_decoder_impl::combine_output(gr_complex* out,
										 gr_complex* out0,
										 gr_complex* out1,
										 int len)
	{
		memcpy(out, out0, sizeof(gr_complex) * len/2 );
		memcpy(out+len/2, out1, sizeof(gr_complex) * len/2 );
	}


	void
	mimo_pre_decoder_impl::set_N_ant(int N_ant)
	{
		if(N_ant != 1 && N_ant != 2 && N_ant != 4){
			printf("%s\t N_ant = %i is INVALID!\n", name().c_str(), N_ant);
		}
		else{
			printf("%s\tset N_ant to %i\n",name().c_str(), N_ant);
			d_N_ant = N_ant;
		}
	}

	void
	mimo_pre_decoder_impl::handle_msg(pmt::pmt_t msg)
	{
		//pmt::pmt_t msg_ant = pmt::pmt_cons(d_port_N_ant, pmt::pmt_from_long(long(d_state_info.N_ant) ) );
		//printf("is pair %s\n", pmt::pmt_is_pair(msg) ? "true" : "false");
		//pmt::pmt_t car = pmt::pmt_car(msg);
		pmt::pmt_t cdr = pmt::cdr(msg);
		//printf("pair car = %s\tcdr = %ld\n", pmt::pmt_symbol_to_string(car).c_str(), pmt::pmt_to_long(cdr) );
		set_N_ant(int( pmt::to_long(cdr) ));
	}

	void
	mimo_pre_decoder_impl::set_decoding_style(std::string style)
	{
		if(style != "tx_diversity"){
			if (style == "spatial_multiplexing"){
				printf("\"%s\" decoding style is valid but not supported\n", style.c_str() );
			}
			else{
				printf("\"%s\" decoding style is invalid\n", style.c_str() );
			}
		}
		else{
			printf("%s\tset decoding style to \"%s\"\n", name().c_str(), style.c_str() );
			d_style = style;
		}
	}

	//gr_complex* d_h0, d_h1, d_r0, d_r1, d_out0, d_out1, d_mult0, d_mult1;
	void
	mimo_pre_decoder_impl::setup_volk_vectors(int len)
	{
        int alig = volk_get_alignment();

		d_mag_h = (float*)volk_malloc(sizeof(float)*len, alig);
		d_mag   = (float*)volk_malloc(sizeof(float)*len, alig);
		d_out   = (gr_complex*)volk_malloc(sizeof(gr_complex)*len, alig);

		d_h0 = (gr_complex*)volk_malloc(sizeof(gr_complex)*len/2, alig);
		d_h1 = (gr_complex*)volk_malloc(sizeof(gr_complex)*len/2, alig);
		d_r0 = (gr_complex*)volk_malloc(sizeof(gr_complex)*len/2, alig);
		d_r1 = (gr_complex*)volk_malloc(sizeof(gr_complex)*len/2, alig);

		d_out0 = (gr_complex*)volk_malloc(sizeof(gr_complex)*len/2, alig);
		d_out1 = (gr_complex*)volk_malloc(sizeof(gr_complex)*len/2, alig);

		d_mult0 = (gr_complex*)volk_malloc(sizeof(gr_complex)*len/2, alig);
		d_mult1 = (gr_complex*)volk_malloc(sizeof(gr_complex)*len/2, alig);


	}


  } /* namespace lte */
} /* namespace gr */

