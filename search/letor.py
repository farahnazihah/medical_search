"""
perhitungan topK documents pada file ini dilakukan dengan memanfaatkan kode dari
Tugas Pemrograman 2. Asumsi file letor.py ini berada di dalam folder yang sama
dengan bsbi.py dan compression.py dari TP2.

TP2
├── collection/
├── nfscorpus/
├── bsbi.py
├── compression.py
├── index.py
├── search.py
...
...
└── letor.py


"""

import lightgbm as lgb
import numpy as np
import random

from gensim.models import TfidfModel
from gensim.models import LsiModel
from gensim.corpora import Dictionary
from scipy.spatial.distance import cosine
from bsbi import BSBIIndex
from compression import VBEPostings


def dataset_training():
    documents = dict()
    with open("./nfcorpus/train.docs") as file:
        for line in file:
            doc_id, content = line.split("\t")
            documents[doc_id] = content.split()

    queries = dict()
    with open("./nfcorpus/train.vid-desc.queries", encoding='utf8') as file:
        for line in file:
            q_id, content = line.split("\t")
            queries[q_id] = content.split()

    NUM_NEGATIVES = 1
    q_docs_rel = {}  # grouping by q_id terlebih dahulu
    with open("nfcorpus/train.3-2-1.qrel") as file:
        for line in file:
            q_id, _, doc_id, rel = line.split("\t")
            if (q_id in queries) and (doc_id in documents):
                if q_id not in q_docs_rel:
                    q_docs_rel[q_id] = []
                q_docs_rel[q_id].append((doc_id, int(rel)))

    # group_qid_count untuk model LGBMRanker
    group_qid_count = []
    dataset = []
    for q_id in q_docs_rel:
        docs_rels = q_docs_rel[q_id]
        group_qid_count.append(len(docs_rels) + NUM_NEGATIVES)
        for doc_id, rel in docs_rels:
            dataset.append((queries[q_id], documents[doc_id], rel))
        # tambahkan satu negative (random sampling saja dari documents)
        dataset.append(
            (queries[q_id], random.choice(list(documents.values())), 0))

    # test
    print("number of Q-D pairs:", len(dataset))
    assert sum(group_qid_count) == len(dataset), "ada yang salah"

    return documents, queries, q_docs_rel, group_qid_count, dataset


# build LSI/LSA model
def vector_rep(text, model, dictionary):
    NUM_LATENT_TOPICS = 200
    rep = [topic_value for (_, topic_value) in model[dictionary.doc2bow(text)]]
    return rep if len(rep) == NUM_LATENT_TOPICS else [0.] * NUM_LATENT_TOPICS


def features(query, doc, model, dictionary):
    v_q = vector_rep(query, model, dictionary)
    v_d = vector_rep(doc, model, dictionary)
    q = set(query)
    d = set(doc)
    cosine_dist = cosine(v_q, v_d)
    jaccard = len(q & d) / len(q | d)
    return v_q + v_d + [jaccard] + [cosine_dist]


def build_model(dataset):
    # bentuk dictionary, bag-of-words corpus, dan kemudian Latent Semantic Indexing
    # dari kumpulan 3612 dokumen.
    NUM_LATENT_TOPICS = 200

    dictionary = Dictionary()
    bow_corpus = [dictionary.doc2bow(doc, allow_update=True)
                  for doc in documents.values()]
    model = LsiModel(bow_corpus, num_topics=NUM_LATENT_TOPICS)

    X = []
    Y = []
    for (query, doc, rel) in dataset:
        X.append(features(query, doc, model, dictionary))
        Y.append(rel)

    # ubah X dan Y ke format numpy array
    X = np.array(X)
    Y = np.array(Y)

    return X, Y, model, dictionary


def train_ranker(X, Y):
    ranker = lgb.LGBMRanker(
        objective="lambdarank",
        boosting_type="gbdt",
        n_estimators=100,
        importance_type="gain",
        metric="ndcg",
        num_leaves=40,
        learning_rate=0.02,
        max_depth=-1)

    # di contoh kali ini, kita tidak menggunakan validation set
    # jika ada yang ingin menggunakan validation set, silakan saja
    ranker.fit(X, Y,
               group=group_qid_count,
               verbose=10)

    return ranker


def get_topK_documents(query, k):
    BSBI_instance = BSBIIndex(data_dir='collection',
                              postings_encoding=VBEPostings,
                              output_dir='index')

    BSBI_instance.index()

    topk = []
    for (score, doc) in BSBI_instance.retrieve_bm25(query, k=k):
        print(f"{doc:30} {score:>.3f}")
        topk.append(doc)

    return topk


if __name__ == '__main__':
    documents, queries, q_docs_rel, group_qid_count, dataset = dataset_training()
    X, Y, model, dictionary = build_model(dataset)
    ranker = train_ranker(X, Y)

    query = "lipid metabolism in toxemia and normal pregnancy"
    topk_doc = get_topK_documents(query, 10)

    docs = []
    for doc in topk_doc:
        print(doc)
        with open("collection\\" + doc) as file:
            docs.append((doc, " ".join(line.strip() for line in file)))

    # bentuk ke format numpy array
    X_unseen = []
    for doc_id, doc in docs:
        X_unseen.append(
            features(query.split(), doc.split(), model, dictionary))

    X_unseen = np.array(X_unseen)

    scores = ranker.predict(X_unseen)

    did_scores = [x for x in zip([did for (did, _) in docs], scores)]
    sorted_did_scores = sorted(
        did_scores, key=lambda tup: tup[1], reverse=True)

    print("query        :", query)
    print("SERP/Ranking :")
    for (did, score) in sorted_did_scores:
        print(f"{did:30} {score:>.2f}")
