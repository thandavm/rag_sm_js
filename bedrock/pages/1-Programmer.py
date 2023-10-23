import csv
import json
import boto3
import streamlit as st

## get the boto3 client
bedrock = boto3.client('bedrock')
bedrock_runtime = boto3.client('bedrock-runtime')

## 
st.title('Programmer')
prog_lang = st.selectbox('Programming Language', ('Python', 'JavaScript', 'C++', "SQL"))


## Set up prompt
prompt_data = f"""


Human: You have a CSV, with columns:
- date (YYYY-MM-DD)
- product_id
- price
- units_sold

Create a {prog_lang} program to analyze the sales data from a CSV file. The program should be able to read the data, and determine below:

- Total revenue for the year
- The product with the highest revenue
- The date with the highest revenue
- Visualize monthly sales using a bar chart

Ensure the code is syntactically correct, bug-free, optimized, not span multiple lines unnecessarily, and prefer to use standard libraries. Return only code without any surrounding text, explanation or context.


Assistant:
"""
#input = st.text_area(label = 'Enter your instructions here', value=prompt_data)
input = st.text_area(label = "Enter your instructions here", value=prompt_data)

run_btn = st.button('Run', key="run_btn", type="primary")

## Set up the input for the model
body = json.dumps({
                    "prompt": input,
                    "max_tokens_to_sample":4096,
                    "temperature":0.5,
                    "top_k":250,
                    "top_p":0.5,
                    "stop_sequences": ["\n\nHuman:"]
                  }) 

## Invoke Model
if run_btn:

  modelId = 'anthropic.claude-v2' # change this to use a different version from the model provider
  accept = 'application/json'
  contentType = 'application/json'

  response = bedrock_runtime.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
  response_body = json.loads(response.get('body').read())

  st.code(response_body.get('completion'))