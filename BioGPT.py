from time import gmtime, strftime
import numpy as np
import pandas as pd
import torch
from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, BioGptModel
import os

model = BioGptModel.from_pretrained("microsoft/BioGPT-Large")
tokenizer = AutoTokenizer.from_pretrained("microsoft/BioGPT-Large")

data = pd.read_csv(os.getcwd()+'\experiment_result\SimpleChemical_stanza_result_Iupacname.csv')

data['similarity'] = 0.0
w = 'adsorption'
for i in range(len(data)):
    word = data['IUPACname'][i]
    input_ids = torch.tensor(tokenizer.encode(word, add_special_tokens=False)).unsqueeze(0)
    with torch.no_grad():
        outputs = model(input_ids=input_ids)
        embeddings = outputs[0][:, -1, :]  # use the last hidden state
    w_input_ids = torch.tensor(tokenizer.encode(w, add_special_tokens=False)).unsqueeze(0)
    similarities = {}
    with torch.no_grad():
        w_outputs = model(input_ids=w_input_ids)
        w_embeddings = w_outputs[0][:, -1, :]  # use the last hidden state
    cos_sim = torch.nn.functional.cosine_similarity(embeddings, w_embeddings).item()
    data['similarity'][i] = cos_sim

data.to_csv(os.getcwd()+'\experiment_result\BioGPT_CosineSimilarity.csv')