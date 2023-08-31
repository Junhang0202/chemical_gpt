import Chemical_material
import pandas as pd
import os
import openai
import logging

data = pd.DataFrame(columns=['entity','IUPACname','solid','soluble','filter'])
df = pd.read_csv(os.getcwd()+'/experiment_data/gpt4_entity.csv')

data['filter']=0
# Set up logging
logging.basicConfig(filename='gpt4_api_errors_gpt4_entity.log', level=logging.ERROR)

def test_agent(task):
    try:
        chem_model = Chemical_material.Chembot(model="gpt-4", temp=0.1, max_iterations=2)
        return chem_model.run_sc(task)
    except openai.error.APIError as e:
        error_message = f"Caught an Error: {e}. Skipping this {task} task."
        print(error_message)
        logging.error(error_message)  # Log the error
        return None

try:
    for i in range(len(df)):
        chemical_materials = df['entity'][i]
        if isinstance(chemical_materials, str):
            chemical_materials = chemical_materials.split(',')
        for chemical_material in chemical_materials:
            print("Entity:", chemical_material.strip())
            filtered_chemical_material = []
            logging.info(f"正在处理:\n {chemical_material}") 
            task1 = f"Is {chemical_material} solid?"
            task2 = f"Is {chemical_material} soluble?"
            result1 = test_agent(task1)
            result2 = test_agent(task2)
            print("Result1内容为:\n",result1)
            print("Result2内容为:\n",result2)
            if result1 is None or result2 is None:
                skip_message = f"并没有找到 {chemical_material}."
                data.loc[len(data)] = {'entity':str(chemical_material),'IUPACname':str(df['IUPACname'][i]),'solid':'None','soluble':'None','filter':0}
                logging.error(skip_message)  # Log the skip
                continue
            if result1 == "Yes" and result2 == "No":
                filtered_chemical_material.append(chemical_material)
                data.loc[len(data)] = {'entity':str(chemical_material),'IUPACname':str(df['IUPACname'][i]),'solid':str(result1),'soluble':str(result2),'filter':1}
            else:
                data.loc[len(data)] = {'entity':str(chemical_material),'IUPACname':str(df['IUPACname'][i]),'solid':str(result1),'soluble':str(result2),'filter':0}
except Exception as e:
    logging.error(f"An error occurred: {e}. Last processed chemical material was {chemical_material}")
finally:
    data.to_csv('gpt4_entity.csv', index=False)
