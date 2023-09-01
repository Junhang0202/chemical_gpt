import stanza
import numpy as np
import pandas as pd
import os
import time
from time import strftime,gmtime
import torch

torch.cuda.is_available()
start_time = time.perf_counter()

# Run the following code if you use at first time.
# stanza.download('en',package='mimic', processors={'ner': 'BioNLP13CG'})

nlp = stanza.Pipeline('en',package='mimic', processors={'ner': 'BioNLP13CG'},download_method=None) 

data = pd.DataFrame(columns=['pmid','entity','domain'])
result = pd.read_csv(os.getcwd()+'\experiment_data\Scopus_data.csv')
for i in range(len(result)):
    pmid = result['id'][i]
    title = result['title'][i]
    abstract = result['abstract'][i]         
    doc = nlp(title+abstract)
    for j in range(len(doc.entities)):
        entity = doc.entities[j].text
        domain = doc.entities[j].type
        data.loc[len(data)] = {'pmid':str(pmid),'entity':str(entity),'domain':str(domain)}

data.to_csv(os.getcwd()+'experiment_result\stanza_result_uric_acid.csv',index=False)
end_time = time.perf_counter()
using_time = strftime("%H:%M:%S", gmtime(end_time - start_time))
print("Time:{}".format(using_time))