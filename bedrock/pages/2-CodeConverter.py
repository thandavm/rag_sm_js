import streamlit as st
from bs4 import BeautifulSoup
import json
import boto3

# Setting page title and header
st.set_page_config(page_title="Code Converter", page_icon=":robot_face:")

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# Model Information
anthropic_model = 'anthropic.claude-v1'

## get the boto3 client
bedrock = boto3.client('bedrock')
bedrock_runtime = boto3.client('bedrock-runtime')

# Streamlit code
st.title('Code Conversion')

col1, col2 = st.columns(2)
with col1:
    source = st.selectbox("Souce: ", ["Python", "Java Script", "Cobol", "Java"])
with col2:
    target = st.selectbox("Target: ", ["Java Script", "Python", "Cobol", "Java"])

source_code = st.text_area("Source Code", key="source_code", placeholder= "Enter Source Code...")
    
convert = st.button("Convert", type= "primary")

# set prompt template
prompt = f"""

Human:  Convert the following code snippet written in {source} language to {target} language : \n {source_code}.  Please put your rewrite in <rewrite></rewrite> tags.

Assistant:
"""

if convert:
    body = json.dumps({"prompt": prompt, "max_tokens_to_sample": 250})
    
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock_runtime.invoke_model(body=body, modelId=anthropic_model, 
                                    accept=accept, 
                                    contentType=contentType)
    
    response_body = json.loads(response.get('body').read())
    soup = BeautifulSoup(response_body['completion'], 'html.parser')
    output = soup.find("rewrite").text.strip()
    target_code = st.code(output, language=target)
