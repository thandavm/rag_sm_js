import streamlit as st
from langchain.llms import Bedrock
import os
import boto3
import json
from io import StringIO
from langchain.agents import create_csv_agent
from langchain.agents.agent_types import AgentType

bedrock = boto3.client('bedrock-runtime')
model_id = "anthropic.claude-instant-v1"
accept = 'application/json'
contentType = 'application/json'

##langchain bedrock
inference_modifier = {'max_tokens_to_sample':4096, 
                      "temperature":0.5,
                      "top_k":250,
                      "top_p":1,
                      "stop_sequences": ["\n\nHuman"]
                     }

instant_llm = Bedrock(model_id = "anthropic.claude-instant-v1")

st.title("👨‍💻 Work with Files")
st.write("Please upload your File.")
data_file = st.file_uploader("Upload a File")

#meta_data = create_query_string("../data/sample.sql")
#query = 'Write a SQL query that fetches all the patients who were prescribed more than 5 different medications on 2023-04-01'

query = st.text_input("Enter your query: ", key="query")
btn_generate = st.button("Generate", key = "generate", type="primary")

if data_file:
    file_path = os.path.join("/tmp", data_file.name)

    if data_file.name.split(".")[-1] == "sql":
        stringio = StringIO(data_file.getvalue().decode("utf-8"))
        meta_data = stringio.read()
    elif data_file.name.split(".")[-1] == "csv":
        # Save the uploaded file to disk
        with open(file_path, "wb") as f:
            f.write(data_file.getbuffer())

        agent = create_csv_agent(
                        instant_llm,
                        file_path,
                        verbose=True,
                        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    )
                            

if btn_generate and data_file.name.split(".")[-1] == "sql":
    prompt_sql_data = f"""Human: You're provided with a database schema representing any hospital's patient management system.
    The system holds records about patients, their prescriptions, doctors, and the medications prescribed.  
    Provide just the SQL Code.  Do not add additional information.

    Here's the schema: {meta_data}
    \n
    
    Please answer this question based on the Schema: {query}


    Assistant:
    """

    body = json.dumps({
                        "prompt": prompt_sql_data,
                        "max_tokens_to_sample":4096,
                        "temperature":0.5,
                        "top_k":250,
                        "top_p":0.5,
                        "stop_sequences": ["\n\nHuman:"]
                    })

    #st.write(body)
    response = bedrock.invoke_model(body=body, modelId=model_id, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())

    st.code(response_body.get('completion'))
    
if btn_generate and data_file.name.split(".")[-1] == "csv":
    answer = agent.run(query)
    st.write(answer)
    
    
#### Sample Questions

# query = 'Write a SQL query that fetches all the patients who were prescribed more than 5 different medications on 2023-04-01'

# how many rows are there?
# How many males
# is Meena one of the survivors