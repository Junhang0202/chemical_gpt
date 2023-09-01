from langchain import OpenAI
from multiprocessing import BoundedSemaphore
import json
import csv
import string
import os
import json
from metapub import PubMedFetcher
from Bio import Entrez
import re
from tqdm import tqdm
import requests
import pandas as pd
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
llm = OpenAI(model_name="gpt-4", temperature = 0)


def preprocess_and_download(keyword, suffix_list):
    keyword_list=[]
    for suffix in suffix_list:
        keyword_list.append(keyword+" "+suffix)
    out = []
    # Get PMID by request and BeautifulSoup
    for i in range(len(keyword_list)):
        search_urls = ['https://pubmed.ncbi.nlm.nih.gov/?term='+keyword_list[i]+'&format=pmid&size=200']
        for search_url in search_urls:
            print(search_url)
            response = requests.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            pmid_list = str(soup.find_all('pre')).split('\r\n')
            pmid_list[0] = pmid_list[0][-8:]
            pmid_list[-1] = pmid_list[-1][:-7]
            out.append(pmid_list)
            
    data = pd.DataFrame(columns=['key','value'])
    data['key'] = keyword_list
    data = data.set_index('key')
    data['value'] = out
    data['value'] = data['value'].apply(lambda x: str(x)[1:-1])
    data.to_json('PMID.json',orient='columns')

    # Download the abstracts
    Entrez.email = 'xxxxxxxx'
    with open("PMID.json") as f:
        validpmid = json.load(f)
        validpmid=validpmid["value"]
        vals1 = validpmid.values()
        vals1 = str(vals1)
        vals1 = vals1.translate(str.maketrans('', '', string.punctuation))
        vals1 = vals1.split()
    vals=list(set(vals1))
    def exabs():
        title_list = []

        abstract_list = []
        Entrez.api_key='xxxxxxxxxx'

        fetch = PubMedFetcher()
        count = 0
        maxcons = 10
        pool_sema = BoundedSemaphore(value=maxcons)
        success=0
        not_exist=0
        error=0
        
        for pmid in tqdm(vals):
            if (os.path.exists("Abstract_Text/" + pmid + '_abstract.txt')):
                print(pmid + ' exists')
                continue
            try:
                pmid = re.findall(r'\d+', pmid)[0]
                article = fetch.article_by_pmid(pmid)
                
                abstract1 = article.abstract # str
                title = article.title
                dictionary={}
                if(abstract1):
                    dictionary['Abstract']=abstract1
                if(title):
                    dictionary['title']= title
                
                if len(dictionary)==0:
                    not_exist+=1
                else:
                    with open("Abstract_Text/" + pmid + '_abstract.txt', 'w') as f:
                        f.write("title: " + dictionary['title']+ "\n")
                        f.write("Abstract: " + dictionary['Abstract']+ "\n")
                    success+=1
                print(f"success:{success}\tnot_exist:{not_exist}\terror:{error}")
            except:
                error+=1
                print(f"success:{success}\tnot_exist:{not_exist}\terror:{error}")
    exabs()

def query_llm(keyword, related_concept, Prompt_Template):
    # preprocess_and_download(keyword, related_concept)
    dir_name = "Abstract_Text/"
    with open("Database.txt", "w") as f_write:
        for filename in os.listdir(dir_name):
            with open(dir_name + filename, "r") as f_read:
                content = f_read.readlines()
                for line in content:
                    f_write.write(f"Paper unique ID: {filename[:-13]}\n")
                    f_write.write(line)
                    f_write.write("\n\n")
    loader = TextLoader("Database.txt")
    documents = loader.load()

    # split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # create the open-source embedding function
    embedding_function = OpenAIEmbeddings()

    # load it into Chroma
    docsearch = Chroma.from_documents(docs, embedding_function)
    retriever = docsearch.as_retriever(search_type="mmr", search_kwargs={'fetch_k': 100})
    
    llm = OpenAI(model_name="gpt-4", temperature = 0)
    
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever,return_source_documents=True)
    result = qa({"query": Prompt_Template})
    return result['result']
    
if __name__ == '__main__':
    keyword = "uric acid"
    related_concept = ["adsorption", "detection", "sensing", "determination", "sensor", "remove", "degradation", "oxidation"]
    Prompt_Template = f"List chemical materials that are related to {keyword} {related_concept[0]}"
    
    # preprocess_and_download(keyword, related_concept)
    answer = query_llm(keyword, related_concept, Prompt_Template)
    with open("answer.txt", "w") as f_write:
        f_write.write(answer)