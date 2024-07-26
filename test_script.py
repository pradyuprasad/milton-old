import numpy as np
from gensim.models import Word2Vec
import faiss

# Test numpy
print("NumPy version:", np.__version__)
array = np.array([1, 2, 3])
print("NumPy array:", array)

# Test gensim
sentences = [["hello", "world"], ["goodbye", "world"]]
model = Word2Vec(sentences, vector_size=10, window=5, min_count=1, workers=4)
print("Gensim word vector for 'hello':", model.wv["hello"])

# Test faiss
d = 10  # dimension
index = faiss.IndexFlatL2(d)  # build the index
print("FAISS index is trained:", index.is_trained)
