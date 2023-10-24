import streamlit as st
import boto3
import json
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
from langchain.embeddings import BedrockEmbeddings


### configs
REGION_NAME = 'us-east-1'
KENDRA_INDEX = 'b52d1029-70a1-4e81-8cd7-2082e5dc0e9b'
AOSS_INDEX_NAME = 'aws_index'
AOSS_VECTOR_FIELD = 'vectors'
AOSS_HOST = '042wcys1zj5zx51an9u1.us-east-1.aoss.amazonaws.com'
AOSS_SERVICE = 'aoss'

### Models
TEXT_GENERATION_MODEL_ENDPOINT_NAME = 'jumpstart-dft-hf-llm-falcon-7b-instruct-bf16'
anthropic_model = 'anthropic.claude-v1'
titan_embeddings = 'amazon.titan-embed-g1-text-02'

### clients
sagemaker_runtime_client = boto3.client('runtime.sagemaker')
kendra_client = boto3.client('kendra')
bedrock_runtime = boto3.client('bedrock-runtime')
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-g1-text-02", client=bedrock_runtime)

### Streamlit code
AI_ICON = "../images/logo.png"
header = f"An AI App powered by Amazon Kendra and Generative AI!"
st.write(f"<h3 class='main-header'>{header}</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    model = st.selectbox("Select Model to use:", ["Sagemaker JumpStart", "Bedrock"])
with col2:
    kbase = st.selectbox("Select Model to use:", ["Kendra", "OpenSearch"])
    
query = st.text_input("You are talking to an AI, ask any question.", key="input")

### Functions to read query data from knowledge base
def get_kendra_results(query):
    result = ''
    context = []

    response = kendra_client.query(QueryText= query, IndexId=KENDRA_INDEX)

    first_result_type = ''
    if response['TotalNumberOfResults']!=0:
        first_result_type = response['ResultItems'][0]['Type']
        
    if first_result_type == 'QUESTION_ANSWER' or first_result_type == 'ANSWER':
        result = response['ResultItems'][0]['DocumentExcerpt']['Text']
    
    elif first_result_type == 'DOCUMENT':
        for query_result in response["ResultItems"]:
            if query_result["Type"]=="DOCUMENT":
                answer_text = query_result["DocumentExcerpt"]["Text"]
                context.append(answer_text)
            
            for text in context:
                result += text
    
    return result

def get_opensearch_results(query):
    
    credentials = boto3.Session().get_credentials()

    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                   REGION_NAME, AOSS_SERVICE, session_token=credentials.token)
    
    aoss_client = OpenSearch(
        hosts=[{'host': AOSS_HOST, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        ssl_assert_hostname = False,
        ssl_show_warn = False,
        connection_class=RequestsHttpConnection,
        timeout=300
    )
    
    query_embedding = embeddings.embed_query(query)

    query_qna = {
        "size": 3,
        "query": {
            "knn": {
            "vectors": {
                "vector": query_embedding,
                "k": 3
                }
            }
        }
    }

    # OpenSearch API call
    relevant_documents = aoss_client.search(
        body = query_qna,
        index = AOSS_INDEX_NAME
    )
    
    context = ""
    for r in relevant_documents['hits']['hits']:
        s = r['_source']
        context += f"{s['text']}\n"
    return context

### Execution Code 
if query:
    if kbase == "Kendra":
        context = get_kendra_results(query)
    elif kbase == "OpenSearch":
        context = get_opensearch_results(query)

    if model == "Sagemaker Jumpstart":
        template = """
            You are a helpful, polite, fact-based agent.
            If you don't know the answer, just say that you don't know.
            Please answer the following question using the context provided. 

            CONTEXT: 
            {context}
            =========
            QUESTION: {question} 
            ANSWER: """
            
        prompt = template.format(context=context, question=query)

        response_model = sagemaker_runtime_client.invoke_endpoint(
                            EndpointName=TEXT_GENERATION_MODEL_ENDPOINT_NAME,
                            Body=json.dumps(
                            {"inputs": prompt, "parameters": {"max_new_tokens": 500}}),
                            ContentType="application/json",
                        )
        response = json.loads(response_model["Body"].read())
        
        st.write(response[0]["generated_text"])
    elif model == "Bedrock":
        template = f"""Human: You are a helpful, polite, fact-based agent.
        If you don't know the answer, just say that you don't know.
        Please answer the following question using the context provided. 

        CONTEXT: 
        {context}
        =========
        QUESTION: {query} 
        
        Assistant: """

        prompt = template.format(context=context, question=query)  
        body = json.dumps({"prompt": prompt, "max_tokens_to_sample": 250})
        
        accept = 'application/json'
        contentType = 'application/json'

        response = bedrock_runtime.invoke_model(body=body, modelId=anthropic_model, 
                                        accept=accept, 
                                        contentType=contentType)
        
        response_body = json.loads(response.get('body').read())
        
        st.write(response_body['completion'])