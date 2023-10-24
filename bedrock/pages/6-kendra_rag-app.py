import streamlit as st
import uuid
import sys
import boto3
import json

KENDRA_INDEX = 'b892de24-c1cd-47d2-afec-5ba905065502'
TEXT_GENERATION_MODEL_ENDPOINT_NAME = 'jumpstart-dft-hf-llm-falcon-7b-instruct-bf16'
AI_ICON = "../images/logo.png"
anthropic_model = 'anthropic.claude-v1'

sagemaker_runtime_client = boto3.client('runtime.sagemaker')
kendra_client = boto3.client('kendra')
bedrock_runtime = boto3.client('bedrock-runtime')

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
model = st.selectbox("Select Model to use:", ["Sagemaker JumpStart", "Bedrock"])
query = st.text_input("You are talking to an AI, ask any question.", key="input")


if query:
    context = get_kendra_results(query)

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