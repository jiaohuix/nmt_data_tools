#!/usr/bin/env python
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import sentencepiece as spm


if __name__ == "__main__":
    # https://github.com/facebookresearch/fairseq/blob/a24880bd10f3c3101b3bc993947ef92a83f1ad4f/examples/translation/prepare-iwslt17-multilingual.sh#L100-L126
    print("cmd: python nmt_data_tools/my_tools/spm_train.py  --input=datasets/raw/train.zh --model_prefix=spm.16k.model --vocab_size=16000 --character_coverage=1 --model_type=bpe")
    spm.SentencePieceTrainer.Train(" ".join(sys.argv[1:]))
