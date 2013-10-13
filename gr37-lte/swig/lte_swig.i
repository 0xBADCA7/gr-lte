/* -*- c++ -*- */

#define LTE_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "lte_swig_doc.i"

%{
#include "lte/mib_unpack_vbm.h"
#include "lte/crc_check_vbvb.h"
#include "lte/bch_crc_check_ant_chooser_bb.h"
#include "lte/subblock_deinterleaver_vfvf.h"
#include "lte/pbch_descrambler_vfvf.h"
#include "lte/repeat_message_source_vf.h"
#include "lte/qpsk_soft_demod_vcvf.h"
#include "lte/layer_demapper_vcvc.h"
#include "lte/pre_decoder_vcvc.h"
#include "lte/pbch_demux_vcvc.h"
#include "lte/channel_estimator_vcvc.h"
#include "lte/extract_subcarriers_vcvc.h"
#include "lte/remove_cp_cvc.h"
#include "lte/sss_calculator_vcm.h"
%}


%include "lte/mib_unpack_vbm.h"
GR_SWIG_BLOCK_MAGIC2(lte, mib_unpack_vbm);

%include "lte/crc_check_vbvb.h"
GR_SWIG_BLOCK_MAGIC2(lte, crc_check_vbvb);
%include "lte/bch_crc_check_ant_chooser_bb.h"
GR_SWIG_BLOCK_MAGIC2(lte, bch_crc_check_ant_chooser_bb);
%include "lte/subblock_deinterleaver_vfvf.h"
GR_SWIG_BLOCK_MAGIC2(lte, subblock_deinterleaver_vfvf);
%include "lte/pbch_descrambler_vfvf.h"
GR_SWIG_BLOCK_MAGIC2(lte, pbch_descrambler_vfvf);
%include "lte/repeat_message_source_vf.h"
GR_SWIG_BLOCK_MAGIC2(lte, repeat_message_source_vf);
%include "lte/qpsk_soft_demod_vcvf.h"
GR_SWIG_BLOCK_MAGIC2(lte, qpsk_soft_demod_vcvf);
%include "lte/layer_demapper_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(lte, layer_demapper_vcvc);
%include "lte/pre_decoder_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(lte, pre_decoder_vcvc);
%include "lte/pbch_demux_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(lte, pbch_demux_vcvc);
%include "lte/channel_estimator_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(lte, channel_estimator_vcvc);
%include "lte/extract_subcarriers_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(lte, extract_subcarriers_vcvc);
%include "lte/remove_cp_cvc.h"
GR_SWIG_BLOCK_MAGIC2(lte, remove_cp_cvc);
%include "lte/sss_calculator_vcm.h"
GR_SWIG_BLOCK_MAGIC2(lte, sss_calculator_vcm);
