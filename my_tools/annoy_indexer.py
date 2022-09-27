'''
usage:  Build annoy indexer, and  quickly find similar words.
'''
import os
import sys
import pickle
import logging
import numpy as np
from tqdm import tqdm
from annoy import AnnoyIndex

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    stream=sys.stdout,
)
logger = logging.getLogger("AnnoyIndexer")

class AnnoyIndexer(object):
    """This class allows the use of `Annoy <https://github.com/spotify/annoy>`_ for fast (approximate)
    vector retrieval in `most_similar()` calls of
    """
    def __init__(self,tokens=None ,vectors=None,num_trees=10):
        '''
        Parameters:
            tokens: tokens list
            vectors: numpy arrary
            num_trees: int,  Number of trees for Annoy indexer.
        '''
        self.vocab_tokens = tokens
        self.vocab2indices = {}
        self.vocab_vectors = vectors
        self.vocab_size  = None
        self.features_dim = None
        self.num_trees = num_trees
        self.indexer = None

        if (tokens is not None) and (vectors is not None):
            self._init_params(tokens,vectors,num_trees)

    def _init_params(self,tokens,vectors,num_trees):
        self.vocab_tokens = tokens
        for idx,token in enumerate(self.vocab_tokens):
            self.vocab2indices[token] = idx
        if not isinstance(vectors,np.ndarray) and isinstance(vectors,list):
            self.vocab_vectors = np.array(vectors)
        else:
            self.vocab_vectors = vectors
        self.vocab_size = len(self.vocab_tokens)
        self.features_dim = self.vocab_vectors.shape[1]
        self.num_trees = num_trees

    def __len__(self):
        return self.vocab_size

    def update_vocab(self,tokens ,vectors):
        print("Updating vocab...")
        if not isinstance(vectors,np.ndarray): vectors = np.array(vectors)
        # tokens: list, vectors: numpy array
        cur_indices = 0
        dedup_vectors = []
        for token,vector in tqdm(zip(tokens,vectors)):
            idx = self.vocab2indices.get(token,None)
            if idx is None: # new token
                self.vocab_tokens.append(token)
                dedup_vectors.append(vector)
                self.vocab2indices[token] = self.vocab_size + cur_indices
                cur_indices += 1

        # update vocab
        old_size  = self.vocab_size
        self.vocab_vectors = np.vstack([self.vocab_vectors,*dedup_vectors])
        self.vocab_size = len(self.vocab_tokens)
        logger.info(f"Origin vocab size: {old_size}, Current vocab size: {self.vocab_size}")


    def build_indexer(self):
        logger.info("Building annoy indexer...")
        indexer = AnnoyIndex(self.features_dim, 'angular')
        for idx, vec in tqdm(enumerate(self.vocab_vectors)):
            indexer.add_item(idx, vec)
        indexer.build(self.num_trees)

        self.indexer = indexer
        logger.info("Indexer has been created.")

    def save(self,path):
        # path/vocab.ann path/vocab.info
        if not os.path.exists(path): os.makedirs(path)
        ann_path = os.path.join(path,"vocab.ann")
        info_path = os.path.join(path,"vocab.info")
        info = {
                "vocab_tokens": self.vocab_tokens,
                "vocab_vectors": self.vocab_vectors,
                "num_trees": self.num_trees
        }
        self.indexer.save(ann_path)
        with open(info_path,"wb") as fout:
            pickle.dump(info,fout)
        logger.info(f"Saved to {path} success.")

    def load(self,path):
        assert os.path.exists(path),f"Path {path} not exists. "
        ann_path = os.path.join(path, "vocab.ann")
        info_path = os.path.join(path, "vocab.info")
        with open(info_path,"rb") as fin:
            info = pickle.load(fin)
        self._init_params(tokens=info["vocab_tokens"],vectors=info["vocab_vectors"],num_trees=info["num_trees"])
        self.indexer = AnnoyIndex(self.features_dim, 'angular')
        self.indexer.load(ann_path)  # super fast, will just mmap the file

    def most_similar(self, vector, topk):
        """Find `num_neighbors` most similar items.
        Parameters
        ----------
        vector : numpy.array
            Vector for word/document.
        topk : int
            Number of most similar items
        Returns
        -------
        list of (str, float)
            List of most similar items in format [(`item`, `cosine_distance`), ... ]
        """
        ids, distances = self.indexer.get_nns_by_vector(
            vector, topk, include_distances=True)

        return ids, distances

    def idx2token(self,idx):
        return self.vocab_tokens[idx]

    def token2idx(self,token):
        idx = self.vocab2indices.get(token,-1)
        return idx

    def search_vector(self,token):
        idx = self.token2idx(token)
        vec = self.vocab_vectors[idx]
        return vec

if __name__ == '__main__':
    # 1.get weight
    from paddlenlp.embeddings import TokenEmbedding
    token_embedding = TokenEmbedding(embedding_name="w2v.baidu_encyclopedia.target.word-word.dim300")
    weight = token_embedding.weight.numpy()

    # 2.build ann tree
    vocab_size = len(token_embedding.vocab)
    indices = list(range(vocab_size))
    tokens= token_embedding.vocab.to_tokens(indices)
    print(tokens[:10])

    print("build annoy indexer...")
    indexer = AnnoyIndexer(tokens,weight,num_trees=10)
    indexer.build_indexer()

    # 3. save params
    print("save annoy indexer...")
    indexer.save(path="save")

    # 4.load indexer
    print("load annoy indexer...")
    indexer_new = AnnoyIndexer()
    indexer_new.load(path="save")
    print(indexer_new)
    print(len(indexer_new))

    # 5.search sim word
    print("search sim words ...")
    word = "电影"
    # word = "国王"

    # idx = indexer_new.token2idx(word)
    vec = indexer_new.search_vector(word)
    topk=5
    ids, distances = indexer_new.most_similar(vec,topk)
    nearest_tokens = [indexer_new.idx2token(idx) for idx in ids]
    print(f"{word}'s {topk} nearest_tokens",nearest_tokens)
    # 电影's 5 nearest_tokens ['电影', '影片', '电视剧', '影视作品', '导演']
    # 国王's 5 nearest_tokens ['国王', '雅赫摩斯', '雨果·卡佩', '塞利姆', '法王路易']
