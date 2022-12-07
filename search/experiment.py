import re
from bsbi import BSBIIndex
from compression import VBEPostings
import math

######## >>>>> 3 IR metrics: RBP p = 0.8, DCG, dan AP

def rbp(ranking, p = 0.8):
  """ menghitung search effectiveness metric score dengan 
      Rank Biased Precision (RBP)

      Parameters
      ----------
      ranking: List[int]
         vektor biner seperti [1, 0, 1, 1, 1, 0]
         gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
         Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                 di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                 di rank-6 tidak relevan
        
      Returns
      -------
      Float
        score RBP
  """
  score = 0.
  for i in range(1, len(ranking) + 1):
    pos = i - 1
    score += ranking[pos] * (p ** (i - 1))
  return (1 - p) * score

def dcg(ranking):
  """ menghitung search effectiveness metric score dengan 
      Discounted Cumulative Gain

      Parameters
      ----------
      ranking: List[int]
         vektor biner seperti [1, 0, 1, 1, 1, 0]
         gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
         Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                 di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                 di rank-6 tidak relevan
        
      Returns
      -------
      Float
        score DCG
  """
  # TODO
  # catatan: DCG = sigma(rel_i / log_2(i + 1)); i = rank mulai dari 1
  res = 0
  for i in range(len(ranking)):
    tmp = ranking[i] / math.log(i + 2, 2)
    res += tmp
  return res

def ap(ranking):
  """ menghitung search effectiveness metric score dengan 
      Average Precision

      Parameters
      ----------
      ranking: List[int]
         vektor biner seperti [1, 0, 1, 1, 1, 0]
         gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
         Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                 di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                 di rank-6 tidak relevan
        
      Returns
      -------
      Float
        score AP
  """
  # TODO
  # catatan:  ap = sigma(prec@i(rel) / R); 1 <= i <= K
  #           prec@K = 1/K * (jumlah yg relevan)
  #           R = jumlah yg relevan di <ranking>
  R = sum(ranking)
  prec = 0
  for i in range(len(ranking)):
    if (ranking[i]) == 1:
      prec += sum(ranking[:i])/(i+1)
  return prec / R

######## >>>>> memuat qrels

def load_qrels(qrel_file = "qrels.txt", max_q_id = 30, max_doc_id = 1033):
  """ memuat query relevance judgment (qrels) 
      dalam format dictionary of dictionary
      qrels[query id][document id]

      dimana, misal, qrels["Q3"][12] = 1 artinya Doc 12
      relevan dengan Q3; dan qrels["Q3"][10] = 0 artinya
      Doc 10 tidak relevan dengan Q3.

  """
  qrels = {"Q" + str(i) : {i:0 for i in range(1, max_doc_id + 1)} \
                 for i in range(1, max_q_id + 1)}
  with open(qrel_file) as file:
    for line in file:
      parts = line.strip().split()
      qid = parts[0]
      did = int(parts[1])
      qrels[qid][did] = 1
  return qrels

######## >>>>> EVALUASI !

def eval(qrels, query_file = "queries.txt", k = 1000):
  """ 
    loop ke semua 30 query, hitung score di setiap query,
    lalu hitung MEAN SCORE over those 30 queries.
    untuk setiap query, kembalikan top-1000 documents
  """
  BSBI_instance = BSBIIndex(data_dir = 'collection', \
                          postings_encoding = VBEPostings, \
                          output_dir = 'index')

  with open(query_file) as file:
    rbp_scores = []
    dcg_scores = []
    ap_scores = []
    for qline in file:
      parts = qline.strip().split()
      qid = parts[0]
      query = " ".join(parts[1:])

      # HATI-HATI, doc id saat indexing bisa jadi berbeda dengan doc id
      # yang tertera di qrels
      ranking = []
      for (score, doc) in BSBI_instance.retrieve_tfidf(query, k = k):
          did = int(re.search(r'.*\\(.*)\.txt', doc).group(1)) 
          ranking.append(qrels[qid][did])
      rbp_scores.append(rbp(ranking))
      dcg_scores.append(dcg(ranking))
      ap_scores.append(ap(ranking))

  print("Hasil evaluasi TF-IDF terhadap 30 queries")
  print("RBP score =", sum(rbp_scores) / len(rbp_scores))
  print("DCG score =", sum(dcg_scores) / len(dcg_scores))
  print("AP score  =", sum(ap_scores) / len(ap_scores))
  print()

def eval_bm25(qrels, query_file = "queries.txt", k = 1000, k1 = 2, b = 0.5):
  """ 
    loop ke semua 30 query, hitung score di setiap query,
    lalu hitung MEAN SCORE over those 30 queries.
    untuk setiap query, kembalikan top-1000 documents
  """
  BSBI_instance = BSBIIndex(data_dir = 'collection', \
                          postings_encoding = VBEPostings, \
                          output_dir = 'index')

  with open(query_file) as file:

    rbp_scores_bm25 = []
    dcg_scores_bm25 = []
    ap_scores_bm25 = []
    for qline in file:
      parts = qline.strip().split()
      qid = parts[0]
      query = " ".join(parts[1:])

      # HATI-HATI, doc id saat indexing bisa jadi berbeda dengan doc id
      # yang tertera di qrels

      ranking = []
      for (score, doc) in BSBI_instance.retrieve_bm25(query, k = k, k1 = k1, b = b):
          did = int(re.search(r'.*\\(.*)\.txt', doc).group(1)) 
          ranking.append(qrels[qid][did])
      rbp_scores_bm25.append(rbp(ranking))
      dcg_scores_bm25.append(dcg(ranking))
      ap_scores_bm25.append(ap(ranking))
  
  print(f"Hasil evaluasi BM25 terhadap 30 queries dengan k1={k1} dan b={b}")
  print("RBP score =", sum(rbp_scores_bm25) / len(rbp_scores_bm25))
  print("DCG score =", sum(dcg_scores_bm25) / len(dcg_scores_bm25))
  print("AP score  =", sum(ap_scores_bm25) / len(ap_scores_bm25))
  print()

if __name__ == '__main__':
  qrels = load_qrels()

  assert qrels["Q1"][166] == 1, "qrels salah"
  assert qrels["Q1"][300] == 0, "qrels salah"

  eval(qrels)
  eval_bm25(qrels, b=0.2)
  eval_bm25(qrels)
  eval_bm25(qrels, b=0.8)
  eval_bm25(qrels, k1=1)
  eval_bm25(qrels, k1=1, b=0.8)
  eval_bm25(qrels, k1=5)
  eval_bm25(qrels, k1=5, b=0.8)