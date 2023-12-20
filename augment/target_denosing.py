# encoding=utf-8
import sys
import pandas as pd
from tqdm import tqdm
import numpy as np
import random
from tqdm import tqdm
import argparse


def read_text_pair(src_file, tgt_file):
    print("Reading text pair...")
    with open(src_file, 'r', encoding='utf-8') as fs, open(tgt_file, 'r', encoding='utf-8') as ft:
        res = list(zip(fs.readlines(), ft.readlines()))
    return res


def write_file(res, file):
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


def write_text_pair(text_pair_ls, out_src_file, out_tgt_file):
    src_pairs = [pair[0] for pair in text_pair_ls]
    tgt_pairs = [pair[1] for pair in text_pair_ls]
    write_file(src_pairs, out_src_file)
    write_file(tgt_pairs, out_tgt_file)


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)


def get_args():
    # 参数src tgt prefix outprefix
    # epoch seed sent_prob=0.3 tok_prob=0.15
    parser = argparse.ArgumentParser(description="target_denosing")
    parser.add_argument('-s', '--src-lang', required=True, type=str, default='zh')
    parser.add_argument('-t', '--tgt-lang', required=True, type=str, default='en')
    parser.add_argument('-i', '--in-prefix', required=True, type=str, default=None)
    parser.add_argument('-o', '--out-prefix', required=True, type=str, default=None)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--epoch', type=int, default=1)
    parser.add_argument('--sent-prob', type=float, default=0.3)
    parser.add_argument('--tok-prob', type=float, default=0.15)

    args = parser.parse_args()
    return args


def target_denoising_finetune(sentence_pairs, args):
    noisy_pairs = []
    clean_pairs = []

    for source, target in sentence_pairs:
        if random.random() < args.sent_prob:  # 30% probability to add noise
            target_words = target.split()
            noisy_target = target.split()
            for i in range(len(noisy_target)):
                if random.random() < args.tok_prob:  # 15% probability to replace with random token

                    noisy_target[i] = random.choice(target_words)
            noisy_pairs.append((source, ' '.join(noisy_target)))
        else:
            clean_pairs.append((source, target))

    return clean_pairs + noisy_pairs


def target_denoising_dynamic_finetune(sentence_pairs, args):
    noisy_pairs = []
    clean_pairs = []

    for source, target in sentence_pairs:
        '''
        在这个场景中，我们使用 max() 而不是 min() 的原因在于我们希望确保有足够的噪声加入到我们的数据中。如果我们使用 min()，那么对于较长的句子，即使它们的动态概率值可能较高，我们也可能由于固定的噪声概率（args.sent_prob）较低而限制了噪声的添加，这可能会使我们的数据噪声不足。
        另一方面，如果我们使用 max()，那么无论句子的长度如何，至少会有一个较高的概率值被用来决定是否添加噪声。对于较短的句子，这个概率值可能就是固定的噪声概率（args.sent_prob）；对于较长的句子，这个概率值可能就是根据句子长度计算出来的动态概率值（sent_prob_dynamic）。这样可以确保在不同长度的句子中都有足够的噪声被添加。
        '''
        sent_prob_dynamic = max(0.1,  min(1.0, sent_length / 100.0))  # adjust the sentence probability based on the length
        sent_prob = max(sent_prob_dynamic, args.sent_prob)  # combine dynamic probability with a fixed one
        if random.random() < sent_prob:  # 30% probability to add noise
            target_words = target.split()
            noisy_target = target.split()
            for i in range(len(noisy_target)):
                if random.random() < args.tok_prob:  # 15% probability to replace with random token

                    noisy_target[i] = random.choice(target_words)
            noisy_pairs.append((source, ' '.join(noisy_target)))
        else:
            clean_pairs.append((source, target))

    return clean_pairs + noisy_pairs


def process(args):
    set_seed(args.seed)
    src_file, tgt_file = f"{args.in_prefix}.{args.src_lang}", f"{args.in_prefix}.{args.tgt_lang}"
    out_src_file, out_tgt_file = f"{args.out_prefix}.{args.src_lang}", f"{args.out_prefix}.{args.tgt_lang}"
    pairs = read_text_pair(src_file, tgt_file)
    text_pair_ls = []
    for epoch in tqdm(range(args.epoch)):
        aug_pairs = target_denoising_finetune(pairs, args)
        text_pair_ls.extend(aug_pairs)

    write_text_pair(text_pair_ls, out_src_file, out_tgt_file)


if __name__ == '__main__':
    args = get_args()
    process(args)
