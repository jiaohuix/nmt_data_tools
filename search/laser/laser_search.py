'''
功能：从向量库database搜索与query相近的topk的距离dist和索引idx (database和query都是laser编码的二值文件)
eg: python laser_search.py -d valid.en.bin -q test.en.bin -o test.en  -k 2 -b 512  --index FLAT --nlist 100
'''
import sys
import os
import numpy as np
import faiss
import argparse
import time
from tqdm import tqdm
import logging

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger("laser_sim_search")

def vec_sim_parser():
    parser = argparse.ArgumentParser("Vec Sim.")
    parser.add_argument(
        "-d",
        "--database",
        default="",
        type=str,
        required=True,
        help="Corpus database, from which to search for samples similar to the query (laser-encoded binary files).",
    )

    parser.add_argument(
        "-q",
        "--query",
        default="",
        type=str,
        required=True,
        help="Query vector, for each sample, find similar topk samples  from the database.(laser-encoded binary files).",
    )

    parser.add_argument(
        "--index",
        default="FLAT",
        type=str,
        choices=["FLAT","IVF"],
        help="bin.",
    )

    parser.add_argument(
        "-n",
        "--nlist",
        default=100,
        type=int,
        help="nlist of IVFFLAT.",
    )

    parser.add_argument(
        "-k",
        "--topk",
        default=1,
        type=int,
        help="topk.",
    )

    parser.add_argument(
        "-b",
        "--bsz",
        default=256,
        type=int,
        help="batch size.",
    )

    parser.add_argument(
        "-o",
        "--outprefix",
        default="",
        required=True,
        help="out prefix, output: outprefix.score outprefix.idx",
    )

    parser.add_argument("--gpu", action="store_true",help="weather to use gpu.")

    return parser


def load_laser_vec(vec_file):
    dim = 1024
    X = np.fromfile(vec_file, dtype=np.float32, count=-1)
    X.resize(X.shape[0] // dim, dim)  # [bsz,dim]
    return X

def build_indexer(args, vectors): # 还要试试IVF的
    # faiss: https://github.com/facebookresearch/faiss/blob/main/tutorial/python/4-GPU.py
    dims = vectors.shape[-1]
    indexer = faiss.IndexFlatL2(dims)  # build a flat (CPU) index
    if args.index == "IVF":
        logger.info("use    IndexIVFFlat...")
        indexer = faiss.IndexIVFFlat(indexer, dims, args.nlist, faiss.METRIC_L2)
    if args.gpu:
        logger.info("move index to gpu...")
        res = faiss.StandardGpuResources()
        indexer = faiss.index_cpu_to_gpu(res, 0, indexer)
    if args.index == "IVF":
        indexer.train(vectors)
    indexer.add(vectors)  # add vectors to the index
    return indexer


def batch_search(args, indexer, vec_query):
    num_quries = vec_query.shape[0]
    steps = num_quries // args.bsz
    num_chunk = steps + int(num_quries % args.bsz != 0)
    vec_query_ls = np.array_split(vec_query, num_chunk, axis=0)
    Dist_ls, idx_ls = [], []
    for query in tqdm(vec_query_ls):
        D, I = indexer.search(query, args.topk)
        Dist_ls.append(D.reshape([-1,args.topk]))
        idx_ls.append(I.reshape([-1,args.topk]))
    D = np.vstack(Dist_ls)
    I = np.vstack(idx_ls)
    return D, I


if __name__ == '__main__':
    parser = vec_sim_parser()
    args = parser.parse_args()

    vec_database = load_laser_vec(args.database)
    vec_query = load_laser_vec(args.query)
    indexer = build_indexer(args,vec_database)

    # search
    D,I = batch_search(args, indexer, vec_query)

    # save
    np.savetxt(args.outprefix+".dist", D,fmt='%.3f', delimiter='\t')
    np.savetxt(args.outprefix+".idx", I,fmt='%d', delimiter='\t')
