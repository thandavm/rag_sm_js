# Lab 1:  RAG application using FAISS as a Vector Store

## Part 1. is focussed on getting the required models deployed - Embedding Model and Generation Model.  

Embedding Model:  GPT-J 6B model
Generation Model:  Falcon 7B model

## Part 2. is focussed on building a RAG application using FAISS + 

1. Notebook to be used: https://github.com/thandavm/rag_sm_js/blob/main/notebooks/01-aws-question-answering-rag.ipynb
2. Use the Endpoints created in part 1 of this Lab and update the notebook accordingly
3. Run the notebook

# Lab 2: RAG application using Kendra as a Knowlege Base

## Part 1: Build an Index in the Kendra Knowledge Base

1. Use the following documentation to create the index - https://github.com/thandavm/rag_sm_js/blob/main/docs/Index%20data%20in%20Kendra.pdf
2. Use the notebook - https://github.com/thandavm/rag_sm_js/blob/main/notebooks/02-aws-qna-kendra-rag.ipynb
3. Update the Kendra Index ID and Generation Model information in the notebook
4. Run the Notebook

## Part 2: RAG application with a Streamlit app on top of Kendra

1. Go to Studio -> New -> Terminal and install the requirements.txt using "pip install -r requirements.txt"
2. Now run the app.py using the command "streamlit run app.py"
3. You can now access the streamlit app using the following - https://<<domainid>>.studio.us-east-1.sagemaker.aws/jupyter/default/proxy/8501/

# Lab 3: RAG application using Amazon OpenSearch as a Knowledge Base

1. Using the lab info -  https://catalog.workshops.aws/semantic-search/en-US/setup/using-own-account
2. launch the Stack
3. Once launched, we will run the RAG application from here - https://catalog.workshops.aws/semantic-search/en-US/module-7-retrieval-augmented-generation