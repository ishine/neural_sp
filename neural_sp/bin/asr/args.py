#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 Kyoto University (Hirofumi Inaguma)
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

"""Args option for the ASR task."""

import argparse
from distutils.util import strtobool


def parse():
    parser = argparse.ArgumentParser()
    # general
    parser.add_argument('--ngpus', type=int, default=1,
                        help='number of GPUs (0 indicates CPU)')
    parser.add_argument('--model', type=str, default=False,
                        help='directory to save a model')
    parser.add_argument('--resume', type=str, default=False,
                        help='path to the model to resume training')
    parser.add_argument('--job_name', type=str, default='',
                        help='name of job')
    # dataset
    parser.add_argument('--train_set', type=str,
                        help='path to a csv file for the training set')
    parser.add_argument('--train_set_sub1', type=str, default=False,
                        help='path to a csv file for the training set for the 1st auxiliary task')
    parser.add_argument('--train_set_sub2', type=str, default=False,
                        help='path to a csv file for the training set for the 2nd auxiliary task')
    parser.add_argument('--train_set_sub3', type=str, default=False,
                        help='path to a csv file for the training set for the 3rd auxiliary task')
    parser.add_argument('--dev_set', type=str,
                        help='path to a csv file for the development set')
    parser.add_argument('--dev_set_sub1', type=str, default=False,
                        help='path to a csv file for the development set for the 1st auxiliary task')
    parser.add_argument('--dev_set_sub2', type=str, default=False,
                        help='path to a csv file for the development set for the 2nd auxiliary task')
    parser.add_argument('--dev_set_sub3', type=str, default=False,
                        help='path to a csv file for the development set for the 3rd auxiliary task')
    parser.add_argument('--eval_sets', type=str, default=[], nargs='+',
                        help='path to csv files for the evaluation sets')
    parser.add_argument('--dict', type=str,
                        help='path to a dictionary file')
    parser.add_argument('--dict_sub1', type=str, default=False,
                        help='path to a dictionary file for the 1st auxiliary task')
    parser.add_argument('--dict_sub2', type=str, default=False,
                        help='path to a dictionary file for the 2nd auxiliary task')
    parser.add_argument('--dict_sub3', type=str, default=False,
                        help='path to a dictionary file for the 3rd auxiliary task')
    parser.add_argument('--unit', type=str, default='word',
                        choices=['word', 'wp', 'char', 'phone', 'word_char'],
                        help='Output unit for the main task')
    parser.add_argument('--unit_sub1', type=str, default=False,
                        choices=['wp', 'char', 'phone'],
                        help='Output unit for the 1st auxiliary task')
    parser.add_argument('--unit_sub2', type=str, default=False,
                        choices=['wp', 'char', 'phone'],
                        help='Output unit for the 2nd auxiliary task')
    parser.add_argument('--unit_sub3', type=str, default=False,
                        choices=['wp', 'char', 'phone'],
                        help='Output unit for the 3rd auxiliary task')
    parser.add_argument('--wp_model', type=str, default=False, nargs='?',
                        help='path to of the wordpiece model for the main task')
    parser.add_argument('--wp_model_sub1', type=str, default=False, nargs='?',
                        help='path to of the wordpiece model for the 1st auxiliary task')
    parser.add_argument('--wp_model_sub2', type=str, default=False, nargs='?',
                        help='path to of the wordpiece model for the 2nd auxiliary task')
    parser.add_argument('--wp_model_sub3', type=str, default=False, nargs='?',
                        help='path to of the wordpiece model for the 3rd auxiliary task')
    # features
    parser.add_argument('--input_type', type=str, default='speech',
                        choices=['speech', 'text'],
                        help='')
    parser.add_argument('--nsplices', type=int, default=1,
                        help='number of input frames to splice (both for left and right frames)')
    parser.add_argument('--nstacks', type=int, default=1,
                        help='number of input frames to stack (frame stacking)')
    parser.add_argument('--nskips', type=int, default=1,
                        help='number of input frames to skip')
    parser.add_argument('--max_nframes', type=int, default=2000,
                        help='maximum number of input frames')
    parser.add_argument('--min_nframes', type=int, default=40,
                        help='minimum number of input frames')
    parser.add_argument('--dynamic_batching', type=bool, default=True,
                        help='')
    # topology (encoder)
    parser.add_argument('--conv_in_channel', type=int, default=1, nargs='?',
                        help='')
    parser.add_argument('--conv_channels', type=str, default="", nargs='?',
                        help='delimited list input.')
    parser.add_argument('--conv_kernel_sizes', type=str, default="", nargs='?',
                        help='delimited list input.')
    parser.add_argument('--conv_strides', type=str, default="", nargs='?',
                        help='delimited list input.')
    parser.add_argument('--conv_poolings', type=str, default="", nargs='?',
                        help='delimited list input.')
    parser.add_argument('--conv_batch_norm', type=bool, default=False, nargs='?',
                        help='')
    parser.add_argument('--enc_type', type=str, default='blstm',
                        choices=['blstm', 'lstm', 'bgru', 'gru', 'cnn'],
                        help='')
    parser.add_argument('--enc_nunits', type=int, default=320,
                        help='number of units in each encoder RNN layer.')
    parser.add_argument('--enc_nprojs', type=int, default=0,
                        help='number of units in each projection layer after the RNN layer.')
    parser.add_argument('--enc_nlayers', type=int, default=5,
                        help='number of encoder RNN layers')
    parser.add_argument('--enc_nlayers_sub1', type=int, default=0,
                        help='')
    parser.add_argument('--enc_nlayers_sub2', type=int, default=0,
                        help='')
    parser.add_argument('--enc_nlayers_sub3', type=int, default=0,
                        help='')
    parser.add_argument('--enc_residual', type=bool, default=False, nargs='?',
                        help='')
    parser.add_argument('--subsample', type=str, default="",
                        help='delimited list input.')
    parser.add_argument('--subsample_type', type=str, default='drop',
                        choices=['drop', 'concat', 'max_pool'],
                        help='')
    # topology (decoder)
    parser.add_argument('--attn_type', type=str, default='location',
                        choices=['location', 'add', 'dot',
                                 'luong_dot', 'luong_general', 'luong_concat'],
                        help='')
    parser.add_argument('--attn_dim', type=int, default=128,
                        help='')
    parser.add_argument('--attn_conv_nchannels', type=int, default=10,
                        help='')
    parser.add_argument('--attn_conv_width', type=int, default=100,
                        help='')
    parser.add_argument('--attn_nheads', type=int, default=1,
                        help='')
    parser.add_argument('--attn_sharpening', type=float, default=1.0,
                        help='')
    parser.add_argument('--attn_sigmoid', type=bool, default=False, nargs='?',
                        help='')
    parser.add_argument('--bridge_layer', type=bool, default=False,
                        help='')
    parser.add_argument('--dec_type', type=str, default='lstm',
                        choices=['lstm', 'gru'],
                        help='')
    parser.add_argument('--dec_nunits', type=int, default=320,
                        help='')
    parser.add_argument('--dec_nprojs', type=int, default=0,
                        help='')
    parser.add_argument('--dec_nlayers', type=int, default=1,
                        help='')
    parser.add_argument('--dec_nlayers_sub1', type=int, default=1,
                        help='')
    parser.add_argument('--dec_nlayers_sub2', type=int, default=1,
                        help='')
    parser.add_argument('--dec_nlayers_sub3', type=int, default=1,
                        help='')
    parser.add_argument('--dec_loop_type', type=str, default='normal', nargs='?',
                        choices=['normal', 'lmdecoder', 'conditional', 'rnmt'],
                        help='')
    parser.add_argument('--dec_residual', type=bool, default=False, nargs='?',
                        help='')
    parser.add_argument('--input_feeding', type=bool, default=False, nargs='?',
                        help='')
    parser.add_argument('--emb_dim', type=int, default=320,
                        help='')
    parser.add_argument('--tie_embedding', type=bool, default=False, nargs='?',
                        help='If True, tie weights between an embedding matrix and a linear layer before the softmax layer.')
    parser.add_argument('--ctc_fc_list', type=str, default="", nargs='?',
                        help='')
    parser.add_argument('--ctc_fc_list_sub1', type=str, default="", nargs='?',
                        help='')
    parser.add_argument('--ctc_fc_list_sub2', type=str, default="", nargs='?',
                        help='')
    parser.add_argument('--ctc_fc_list_sub3', type=str, default="", nargs='?',
                        help='')
    # optimization
    parser.add_argument('--batch_size', type=int, default=50,
                        help='size of mini-batch')
    parser.add_argument('--optimizer', type=str, default='adam',
                        choices=['adam', 'adadelta', 'sgd'],
                        help='')
    parser.add_argument('--learning_rate', type=float, default=1e-3,
                        help='')
    parser.add_argument('--eps', type=float, default=1e-6,
                        help='')
    parser.add_argument('--nepochs', type=int, default=25,
                        help='number of epochs')
    parser.add_argument('--convert_to_sgd_epoch', type=int, default=20,
                        help='')
    parser.add_argument('--print_step', type=int, default=200,
                        help='the step to print log')
    parser.add_argument('--metric', type=str, default='edit_distance',
                        choices=['edit_distance', 'loss', 'acc', 'ppl', 'bleu'],
                        help='')
    parser.add_argument('--decay_type', type=str, default='epoch',
                        choices=['epoch', 'metric', 'warmup'],
                        help='')
    parser.add_argument('--decay_start_epoch', type=int, default=10,
                        help='')
    parser.add_argument('--decay_rate', type=float, default=0.9,
                        help='')
    parser.add_argument('--decay_patient_epoch', type=int, default=0,
                        help='')
    parser.add_argument('--sort_stop_epoch', type=int, default=10000,
                        help='')
    parser.add_argument('--not_improved_patient_epoch', type=int, default=5,
                        help='')
    parser.add_argument('--eval_start_epoch', type=int, default=1,
                        help='')
    parser.add_argument('--warmup_start_learning_rate', type=float, default=1e-4,
                        help='')
    parser.add_argument('--warmup_step', type=int, default=0,
                        help='')
    parser.add_argument('--warmup_epoch', type=int, default=0,
                        help='')
    # initialization
    parser.add_argument('--param_init', type=float, default=0.1,
                        help='')
    parser.add_argument('--param_init_dist', type=str, default='uniform',
                        choices=['uniform', 'he', 'glorot', 'lecun'],
                        help='')
    parser.add_argument('--rec_weight_orthogonal', type=bool, default=False,
                        help='')
    parser.add_argument('--pretrained_model', default=False, nargs='?',
                        help='')
    # regularization
    parser.add_argument('--clip_grad_norm', type=float, default=5.0,
                        help='')
    parser.add_argument('--dropout_in', type=float, default=0.0,
                        help='dropout probability for the input')
    parser.add_argument('--dropout_enc', type=float, default=0.0,
                        help='dropout probability for the')
    parser.add_argument('--dropout_dec', type=float, default=0.0,
                        help='dropout probability for the decoder')
    parser.add_argument('--dropout_emb', type=float, default=0.0,
                        help='dropout probability for the embedding')
    parser.add_argument('--dropout_att', type=float, default=0.0,
                        help='dropout probability for the attention weights')
    parser.add_argument('--weight_decay', type=float, default=0,
                        help='')
    parser.add_argument('--gaussian_noise_std', type=float, default=0,
                        help='standard deviation of Gaussian noise')
    parser.add_argument('--gaussian_noise_timing', type=str, default='saturation',
                        choices=['constant', 'saturation'],
                        help='timing to start Gaussian noise injection')
    parser.add_argument('--logits_temp', type=float, default=1.0,
                        help='')
    parser.add_argument('--ss_prob', type=float, default=0.0,
                        help='')
    parser.add_argument('--ss_type', type=str, default='constant',
                        choices=['constant', 'saturation'],
                        help='')
    parser.add_argument('--lsm_prob', type=float, default=0.0,
                        help='')
    parser.add_argument('--layer_norm', default=False,
                        help='If true, apply layer normalization (see https://arxiv.org/abs/1607.06450).')
    parser.add_argument('--focal_loss_weight', type=float, default=0.0,
                        help='')
    parser.add_argument('--focal_loss_gamma', type=float, default=2.0,
                        help='')
    # MTL
    parser.add_argument('--ctc_weight', type=float, default=0.0,
                        help='CTC loss weight for the main task')
    parser.add_argument('--ctc_weight_sub1', type=float, default=0.0,
                        help='CTC loss weight for the 1st auxiliary task')
    parser.add_argument('--ctc_weight_sub2', type=float, default=0.0,
                        help='CTC loss weight for the 2nd auxiliary task')
    parser.add_argument('--ctc_weight_sub3', type=float, default=0.0,
                        help='CTC loss weight for the 3rd auxiliary task')
    parser.add_argument('--sub1_weight', type=float, default=0.0,
                        help='total loss weight for the 1st auxiliary task')
    parser.add_argument('--sub2_weight', type=float, default=0.0,
                        help='total loss weight for the 2nd auxiliary task')
    parser.add_argument('--sub3_weight', type=float, default=0.0,
                        help='total loss weight for the 3rd auxiliary task')
    parser.add_argument('--mtl_per_batch', type=bool, default=False, nargs='?',
                        help='If True, change mini-batch per task')
    parser.add_argument('--task_specific_layer', type=bool, default=False, nargs='?',
                        help='If True, insert a task-specific encoder layer per task')
    # foroward-backward
    parser.add_argument('--bwd_weight', type=float, default=0.0,
                        help='cross etnropy loss weight for the backward decoder in the main task')
    parser.add_argument('--bwd_weight_sub1', type=float, default=0.0,
                        help='cross etnropy loss weight for the backward decoder in the 1st auxiliary task')
    parser.add_argument('--bwd_weight_sub2', type=float, default=0.0,
                        help='cross etnropy loss weight for the backward decoder in the 2nd auxiliary task')
    parser.add_argument('--bwd_weight_sub3', type=float, default=0.0,
                        help='cross etnropy loss weight for the backward decoder in the 3rd auxiliary task')
    parser.add_argument('--twin_net_weight', type=float, default=0.0,
                        help='1.5 is recommended in the orignial paper.')
    parser.add_argument('--twin_net_weight_sub1', type=float, default=0.0,
                        help='1.5 is recommended in the orignial paper.')
    parser.add_argument('--twin_net_weight_sub2', type=float, default=0.0,
                        help='1.5 is recommended in the orignial paper.')
    parser.add_argument('--twin_net_weight_sub3', type=float, default=0.0,
                        help='1.5 is recommended in the orignial paper.')
    parser.add_argument('--agreement_weight', type=float, default=0.0,
                        help='agreement loss weight for the backwar decoder in the main task')
    parser.add_argument('--agreement_weight_sub1', type=float, default=0.0,
                        help='agreement loss weight for the backwar decoder in the 1st auxiliary task')
    parser.add_argument('--agreement_weight_sub2', type=float, default=0.0,
                        help='agreement loss weight for the backwar decoder in the 2nd auxiliary task')
    parser.add_argument('--agreement_weight_sub3', type=float, default=0.0,
                        help='agreement loss weight for the backwar decoder in the 3rd auxiliary task')
    # cold fusion
    parser.add_argument('--cold_fusion', type=str, default='hidden', nargs='?',
                        choices=['hidden', 'prob'],
                        help='')
    parser.add_argument('--rnnlm_cold_fusion', type=str, default=False, nargs='?',
                        help='RNNLM parameters for cold fusion.')
    # RNNLM initialization, objective
    parser.add_argument('--rnnlm_init', type=str, default=False, nargs='?',
                        help='')
    parser.add_argument('--lmobj_weight', type=float, default=0.0, nargs='?',
                        help='LM objective weight for the main task')
    parser.add_argument('--lmobj_weight_sub1', type=float, default=0.0, nargs='?',
                        help='LM objective weight for the 1st auxiliary task')
    parser.add_argument('--lmobj_weight_sub2', type=float, default=0.0, nargs='?',
                        help='LM objective weight for the 2nd auxiliary task')
    parser.add_argument('--lmobj_weight_sub3', type=float, default=0.0, nargs='?',
                        help='LM objective weight for the 3rd auxiliary task')
    parser.add_argument('--share_lm_softmax', type=bool, default=False, nargs='?',
                        help='')
    # transformer
    parser.add_argument('--transformer', type=bool, default=False,
                        help='')
    parser.add_argument('--d_model', type=int, default=512,
                        help='')
    parser.add_argument('--d_ff', type=int, default=2048,
                        help='')
    parser.add_argument('--pre_process', type=str, default=False,
                        help='')
    parser.add_argument('--post_process', type=str, default='dal',
                        help='')
    parser.add_argument('--share_embedding', type=bool, default=True,
                        help='')
    # decoding parameters
    parser.add_argument('--recog_sets', type=str, default=[], nargs='+',
                        help='path to csv files for the evaluation sets')
    parser.add_argument('--recog_model', type=str, default=None, nargs='+',
                        help='path to the model')
    parser.add_argument('--recog_model_bwd', type=str, default=None, nargs='?',
                        help='path to the model in the reverse direction')
    parser.add_argument('--recog_epoch', type=int, default=-1,
                        help='the epoch to restore')
    parser.add_argument('--recog_dir', type=str, default=None,
                        help='directory to save decoding results')
    parser.add_argument('--recog_unit', type=str, default=False, nargs='?',
                        choices=['word', 'wp', 'char', 'phone', 'word_char'],
                        help='')
    parser.add_argument('--recog_batch_size', type=int, default=1,
                        help='size of mini-batch in evaluation')
    parser.add_argument('--recog_beam_width', type=int, default=1,
                        help='size of beam')
    parser.add_argument('--recog_max_len_ratio', type=float, default=1,
                        help='')
    parser.add_argument('--recog_min_len_ratio', type=float, default=0.0,
                        help='')
    parser.add_argument('--recog_length_penalty', type=float, default=0.0,
                        help='length penalty')
    parser.add_argument('--recog_coverage_penalty', type=float, default=0.0,
                        help='coverage penalty')
    parser.add_argument('--recog_coverage_threshold', type=float, default=0.0,
                        help='coverage threshold')
    parser.add_argument('--recog_gnmt_decoding', type=strtobool, default=False, nargs='?',
                        help='If True, adopt Google NMT beam search decoding.')
    parser.add_argument('--recog_rnnlm_weight', type=float, default=0.0,
                        help='the weight of RNNLM score')
    parser.add_argument('--recog_ctc_weight', type=float, default=0.0,
                        help='the weight of CTC score')
    parser.add_argument('--recog_rnnlm', type=str, default=None, nargs='?',
                        help='path to the RMMLM')
    parser.add_argument('--recog_rnnlm_bwd', type=str, default=None, nargs='?',
                        help='path to the RMMLM in the reverse direction')
    parser.add_argument('--recog_resolving_unk', type=strtobool, default=False,
                        help='resolving UNK for the word-based model.')
    parser.add_argument('--recog_fwd_bwd_attention', type=strtobool, default=False,
                        help='forward-backward attention decoding.')
    parser.add_argument('--recog_checkpoint_ensemble', type=int, default=1,
                        help='number of checkpoints to use.')
    # distillation related
    parser.add_argument('--recog_nbest', type=float, default=1,
                        help='N-best list for sampling')
    parser.add_argument('--recog_softmax_temperature', type=float, default=1,
                        help='Temperature parameter for the final softmax layer.')
    parser.add_argument('--distillation_type', type=str, default='prob',
                        choices=['teacher_forcing', 'beam_search'],
                        help='')

    args = parser.parse_args()
    return args
