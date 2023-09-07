import streamlit as st
import uuid
import sys
import boto3
import json

KENDRA_INDEX = 'b892de24-c1cd-47d2-afec-5ba905065502'
TEXT_GENERATION_MODEL_ENDPOINT_NAME = 'jumpstart-dft-hf-llm-falcon-7b-instruct-bf16'
AI_ICON = "../images/logo.png"

sagemaker_runtime_client = boto3.client('runtime.sagemaker')
kendra_client = boto3.client('kendra')

header = f"An AI App powered by Amazon Kendra and Generative AI!"
st.write(f"<h3 class='main-header'>{header}</h3>", unsafe_allow_html=True)
    
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

st.markdown('---')
query = st.text_input("You are talking to an AI, ask any question.", key="input")

if query:
    context = get_kendra_results(query)
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