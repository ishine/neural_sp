#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""The Connectionist Temporal Classification model (chainer)."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import chainer
from chainer import functions as F
from models.chainer.ctc.ctc_loss_from_chainer import connectionist_temporal_classification

from models.chainer.base import ModelBase
from models.chainer.linear import LinearND
from models.chainer.criterion import cross_entropy_label_smoothing
from models.chainer.encoders.load_encoder import load
from models.pytorch.ctc.decoders.greedy_decoder import GreedyDecoder
from models.pytorch.ctc.decoders.beam_search_decoder import BeamSearchDecoder
# from models.pytorch.ctc.decoders.beam_search_decoder2 import BeamSearchDecoder
from utils.io.variable import np2var, var2np

NEG_INF = -float("inf")
LOG_0 = NEG_INF
LOG_1 = 0


class CTC(ModelBase):
    """The Connectionist Temporal Classification model.
    Args:
        input_size (int): the dimension of input features
        encoder_type (string): the type of the encoder. Set lstm or gru or rnn.
        encoder_bidirectional (bool): if True create a bidirectional encoder
        encoder_num_units (int): the number of units in each layer
        encoder_num_proj (int): the number of nodes in recurrent projection layer
        encoder_num_layers (int): the number of layers of the encoder
        fc_list (list):
        dropout_input (float): the probability to drop nodes in input-hidden connection
        dropout_encoder (float): the probability to drop nodes in hidden-hidden connection
        num_classes (int): the number of classes of target labels
            (excluding the blank class)
        parameter_init_distribution (string, optional): uniform or normal or
            orthogonal or constant distribution
        parameter_init (float, optional): Range of uniform distribution to
            initialize weight parameters
        recurrent_weight_orthogonal (bool, optional): if True, recurrent
            weights are orthogonalized
        init_forget_gate_bias_with_one (bool, optional): if True, initialize
            the forget gate bias with 1
        subsample_list (list, optional): subsample in the corresponding layers (True)
            ex.) [False, True, True, False] means that subsample is conducted
                in the 2nd and 3rd layers.
        subsample_type (string, optional): drop or concat
        logits_temperature (float):
        num_stack (int, optional): the number of frames to stack
        splice (int, optional): frames to splice. Default is 1 frame.
        conv_channels (list, optional):
        conv_kernel_sizes (list, optional):
        conv_strides (list, optional):
        poolings (list, optional):
        activation (string, optional): The activation function of CNN layers.
            Choose from relu or prelu or hard_tanh or maxout
        batch_norm (bool, optional):
        label_smoothing_prob (float, optional):
        weight_noise_std (float, optional):
        encoder_residual (bool, optional):
        encoder_dense_residual (bool, optional):
    """

    def __init__(self,
                 input_size,
                 encoder_type,
                 encoder_bidirectional,
                 encoder_num_units,
                 encoder_num_proj,
                 encoder_num_layers,
                 fc_list,
                 dropout_input,
                 dropout_encoder,
                 num_classes,
                 parameter_init_distribution='uniform',
                 parameter_init=0.1,
                 recurrent_weight_orthogonal=False,
                 init_forget_gate_bias_with_one=True,
                 subsample_list=[],
                 subsample_type='drop',
                 logits_temperature=1,
                 num_stack=1,
                 splice=1,
                 conv_channels=[],
                 conv_kernel_sizes=[],
                 conv_strides=[],
                 poolings=[],
                 activation='relu',
                 batch_norm=False,
                 label_smoothing_prob=0,
                 weight_noise_std=0,
                 encoder_residual=False,
                 encoder_dense_residual=False):

        super(ModelBase, self).__init__()
        self.model_type = 'ctc'

        # Setting for the encoder
        self.input_size = input_size
        self.num_stack = num_stack
        self.encoder_type = encoder_type
        self.num_directions = 2 if encoder_bidirectional else 1
        self.fc_list = fc_list
        self.subsample_list = subsample_list

        # Setting for CTC
        self.num_classes = num_classes + 1  # Add the blank class
        self.blank_index = num_classes
        self.logits_temperature = logits_temperature

        # Setting for regualarization
        self.parameter_init = parameter_init
        self.weight_noise_injection = False
        self.weight_noise_std = float(weight_noise_std)
        self.label_smoothing_prob = label_smoothing_prob

        with self.init_scope():
            # Load the encoder
            if encoder_type in ['lstm', 'gru', 'rnn']:
                self.encoder = load(encoder_type=encoder_type)(
                    input_size=input_size,
                    rnn_type=encoder_type,
                    bidirectional=encoder_bidirectional,
                    num_units=encoder_num_units,
                    num_proj=encoder_num_proj,
                    num_layers=encoder_num_layers,
                    dropout_input=dropout_input,
                    dropout_hidden=dropout_encoder,
                    subsample_list=subsample_list,
                    subsample_type=subsample_type,
                    use_cuda=self.use_cuda,
                    merge_bidirectional=False,
                    num_stack=num_stack,
                    splice=splice,
                    conv_channels=conv_channels,
                    conv_kernel_sizes=conv_kernel_sizes,
                    conv_strides=conv_strides,
                    poolings=poolings,
                    activation=activation,
                    batch_norm=batch_norm,
                    residual=encoder_residual,
                    dense_residual=encoder_dense_residual)
            elif encoder_type == 'cnn':
                assert num_stack == 1 and splice == 1
                self.encoder = load(encoder_type='cnn')(
                    input_size=input_size,
                    conv_channels=conv_channels,
                    conv_kernel_sizes=conv_kernel_sizes,
                    conv_strides=conv_strides,
                    poolings=poolings,
                    dropout_input=dropout_input,
                    dropout_hidden=dropout_encoder,
                    use_cuda=self.use_cuda,
                    activation=activation,
                    batch_norm=batch_norm)
            else:
                raise NotImplementedError

            if len(fc_list) > 0:
                self.fc_layers = []
                for i in range(len(fc_list)):
                    if i == 0:
                        if encoder_type == 'cnn':
                            bottle_input_size = self.encoder.output_size
                        else:
                            bottle_input_size = encoder_num_units * self.num_directions
                        # if batch_norm:
                        #     self.fc_layers.append(
                        #         L.BatchNormalization(bottle_input_size))
                        # TODO: to_gpu()
                        self.fc_layers.append(
                            LinearND(bottle_input_size, fc_list[i],
                                     dropout=dropout_encoder, use_cuda=self.use_cuda))
                    else:
                        # if batch_norm:
                        #     self.fc_layers.append(
                        #         L.BatchNormalization(fc_list[i - 1]))
                        # TODO: to_gpu()
                        self.fc_layers.append(
                            LinearND(fc_list[i - 1], fc_list[i],
                                     dropout=dropout_encoder, use_cuda=self.use_cuda))
                # TODO: remove a bias term in the case of batch normalization

                self.fc = LinearND(fc_list[-1], self.num_classes,
                                   use_cuda=self.use_cuda)
            else:
                self.fc = LinearND(
                    encoder_num_units * self.num_directions, self.num_classes,
                    use_cuda=self.use_cuda)

            ##################################################
            # Initialize parameters
            ##################################################
            self.init_weights(parameter_init,
                              distribution=parameter_init_distribution,
                              ignore_keys=['bias'])

            # Initialize all biases with 0
            self.init_weights(0, distribution='constant', keys=['bias'])

            # Recurrent weights are orthogonalized
            if recurrent_weight_orthogonal and encoder_type != 'cnn':
                self.init_weights(parameter_init,
                                  distribution='orthogonal',
                                  keys=[encoder_type, 'weight'],
                                  ignore_keys=['bias'])

            # Initialize bias in forget gate with 1
            if init_forget_gate_bias_with_one:
                self.init_forget_gate_bias_with_one()

        # Set CTC decoders
        self._decode_greedy_np = GreedyDecoder(blank_index=self.blank_index)
        self._decode_beam_np = BeamSearchDecoder(blank_index=self.blank_index)
        # TODO: set space index

    def __call__(self, xs, ys, x_lens, y_lens, is_eval=False):
        """Forward computation.
        Args:
            xs (list of np.ndarray): A tensor of size `[B, T_in, input_size]`
            ys (np.ndarray): A tensor of size `[B, T_out]`
            x_lens (np.ndarray): A tensor of size `[B]`
            y_lens (np.ndarray): A tensor of size `[B]`
            is_eval (bool, optional): if True, the history will not be saved.
                This should be used in inference model for memory efficiency.
        Returns:
            loss (chainer.Variable(float) or float): A tensor of size `[1]`
        """
        if is_eval:
            with chainer.no_backprop_mode(), chainer.using_config('train', False):
                loss = self._forward(xs, ys, x_lens, y_lens).data
        else:
            loss = self._forward(xs, ys, x_lens, y_lens)
            # TODO: Gaussian noise injection

        return loss

    def _forward(self, xs, ys, x_lens, y_lens):
        # Wrap by Variable
        xs = np2var(xs, use_cuda=self.use_cuda, backend='chainer')
        ys = np2var(ys, use_cuda=self.use_cuda, backend='chainer')
        x_lens = np2var(x_lens, use_cuda=self.use_cuda, backend='chainer')
        y_lens = np2var(y_lens, use_cuda=self.use_cuda, backend='chainer')

        # Encode acoustic features
        logits, x_lens = self._encode(xs, x_lens)

        # Output smoothing
        if self.logits_temperature != 1:
            logits /= self.logits_temperature

        if self.blank_index == 0:
            # NOTE: index 0 is reserved for the blank class
            ys = ys + 1

        # Compute CTC loss
        loss = connectionist_temporal_classification(
            x=F.separate(logits, axis=1),  # list of Variable
            t=ys,  # Variable
            blank_symbol=self.blank_index,
            input_length=x_lens,  # Variable
            label_length=y_lens,  # Variable
            reduce='no')
        loss = F.sum(loss, axis=0) / len(xs)

        # Label smoothing (with uniform distribution)
        if self.label_smoothing_prob > 0:
            # XE
            xe_loss_ls = cross_entropy_label_smoothing(
                logits,
                y_lens=x_lens,  # NOTE: CTC is frame-synchronous
                label_smoothing_prob=self.label_smoothing_prob,
                distribution='uniform',
                size_average=False) / len(xs)
            loss = loss * (1 - self.label_smoothing_prob) + xe_loss_ls
            # print(xe_loss_ls)

        return loss

    def _encode(self, xs, x_lens, is_multi_task=False):
        """Encode acoustic features.
        Args:
            xs (list of chainer.Variable(float)):
                A list of tensors of size `[T_in, input_size]`
            x_lens (np.ndarray): A tensor of size `[B]`
            is_multi_task (bool, optional):
        Returns:
            logits (chainer.Variable, float): A tensor of size
                `[B, T, num_classes (including the blank class)]`
            x_lens (np.ndarray): A tensor of size `[B]`
            OPTION:
                logits_sub (chainer.Variable, float): A tensor of size
                    `[B, T, num_classes_sub (including the blank class)]`
                x_lens_sub (np.ndarray): A tensor of size `[B]`
        """
        if is_multi_task:
            xs, x_lens, xs_sub, x_lens_sub = self.encoder(xs, x_lens)
        else:
            xs, x_lens = self.encoder(xs, x_lens)

        # Concatenate
        xs = F.pad_sequence(xs, padding=0)

        if len(self.fc_list) > 0:
            for fc in self.fc_layers:
                xs = fc(xs)
        logits = self.fc(xs)

        if is_multi_task:
            # Concatenate
            xs_sub = F.pad_sequence(xs_sub, padding=0)

            logits_sub = self.fc_sub(xs_sub)
            return logits, x_lens, logits_sub, x_lens_sub
        else:
            return logits, x_lens

    def posteriors(self, xs, x_lens, temperature=1,
                   blank_prior=None, is_sub_task=False):
        """Returns CTC posteriors (after the softmax layer).
        Args:
            xs (list of np.ndarray):
                A list of tensors of size `[B, T_in, input_size]`
            x_lens (np.ndarray): A tensor of size `[B]`
            temperature (float, optional): the temperature parameter for the
                softmax layer in the inference stage
            blank_prior (float, optional):
            is_sub_task (bool, optional):
        Returns:
            probs (np.ndarray): A list of tensors of size `[B, T, num_classes]`
        """
        with chainer.no_backprop_mode(), chainer.using_config('train', False):

            # Wrap by Variable
            xs = np2var(xs, use_cuda=self.use_cuda, backend='chainer')

            # Encode acoustic features
            if hasattr(self, 'main_loss_weight'):
                if is_sub_task:
                    _, _, logits, _ = self._encode(
                        xs, x_lens, is_multi_task=True)
                else:
                    logits, _, _, _ = self._encode(
                        xs, x_lens, is_multi_task=True)
            else:
                logits, _ = self._encode(xs, x_lens)

            probs = F.softmax(logits / temperature)

            # Divide by blank prior
            if blank_prior is not None:
                raise NotImplementedError

            return var2np(probs, backend='chainer')

    def decode(self, xs, x_lens, beam_width=1,
               max_decode_len=None, is_sub_task=False):
        """
        Args:
            xs (list of np.ndarray):
                A list of tensors of size `[B, T_in, input_size]`
            x_lens (np.ndarray): A tensor of size `[B]`
            beam_width (int, optional): the size of beam
            max_decode_len: not used (to make CTC compatible with attention)
            is_sub_task (bool, optional):
        Returns:
            best_hyps (np.ndarray): A tensor of size `[B]`
            perm_idx (np.ndarray): For interface with pytorch, not used
        """
        with chainer.no_backprop_mode(), chainer.using_config('train', False):

            # Wrap by Variable
            xs = np2var(xs, use_cuda=self.use_cuda, backend='chainer')

            # Encode acoustic features
            if hasattr(self, 'main_loss_weight'):
                if is_sub_task:
                    _, _, logits, x_lens = self._encode(
                        xs, x_lens, is_multi_task=True)
                else:
                    logits, x_lens, _, _ = self._encode(
                        xs, x_lens, is_multi_task=True)
            else:
                logits, x_lens = self._encode(xs, x_lens)

            if beam_width == 1:
                best_hyps = self._decode_greedy_np(
                    var2np(logits, backend='chainer'), x_lens)
            else:
                best_hyps = self._decode_beam_np(
                    var2np(F.log_softmax(logits), backend='chainer'),
                    x_lens, beam_width=beam_width)

        if self.blank_index == 0:
            best_hyps -= 1
            # NOTE: index 0 is reserved for the blank class

        perm_idx = np.arange(0, len(xs), 1)
        return best_hyps, perm_idx

    def decode_from_probs(self, probs, x_lens, beam_width=1,
                          max_decode_len=None):
        """
        Args:
            probs (np.ndarray):
            x_lens (np.ndarray):
            beam_width (int, optional):
            max_decode_len (int, optional):
        Returns:
            best_hyps (np.ndarray): A tensor of size `[B]`
        """
        raise NotImplementedError
