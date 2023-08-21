# ChemAssistant-An advanced chemical bot based on GPT 4.0

Note: Please note that use LINUX system.

## 1. Before run the code

---

You need to apply for a [ *GPT-4* API account](https://openai.com/blog/gpt-4-api-general-availability)
. Based on our tests, the performance of *GPT-4* is far superior to *GPT-3.5*.
   
> **Note:** All *GPT-3.5* model does not currently support in this code. We will add relevant code in next version.

## 2. Quick Start

To quickly run the code, follow the steps below:

1. Clone the repository to your local machine:

   ```
   git clone https://github.com/Junhang0202/chemical_gpt.git
   ```

2. Import your OPENAI_API_KEY and SERP_API_KEY:

   ```
    vim ~/.bashrc

    #Openai_api_key
    export OPENAI_API_KEY="sk-xxxxx"

    #SERP_API
    export SERP_API_KEY="your own SERP_API_KEYxxxx"
   ```
> **Note:**[ More detail about SERP_API_KEY](https://serpapi.com/)

3. Install the required dependencies:

   ```
   conda env create -f environment.yml
   ```


4. Using ChemAssistant:

   ```
   cd  xxx\chemical_material_gpt
   nohup python test_chembot.py >chembot_output.txt 2>&1 &echo $! > chembot_output_id.txt
   ```

You should now be able to run the code successfully. 
If you encounter any issues, please refer to open an issue on the repository for further assistance.
