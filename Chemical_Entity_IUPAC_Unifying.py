import os
import numpy as np
import pandas as pd
import pubchempy as pcp

data = pd.read_csv(os.getcwd()+'\experiment_data\SimpleChemical_stanza_result.csv')

data['IUPACname'] = ''
data['cid'] = 0

for i in range(0,len(data)):
    compound_entity= data['entity'][i]    
    compounds = pcp.get_compounds(compound_entity, 'name')
    if compounds:
        data['IUPACname'][i] = compounds[0].iupac_name
        data['cid'][i] = compounds[0].cid
    else:
        data['IUPACname'][i] = 'None'

data.to_csv(os.getcwd()+'\experiment_result\SimpleChemical_stanza_result_Iupacname.csv',index=False)