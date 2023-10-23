import streamlit as st
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.llms import Bedrock

inference_modifier = {'max_tokens_to_sample':4096, 
                      "temperature":0.5,
                      "top_k":250,
                      "top_p":1,
                      "stop_sequences": ["\n\nHuman"]
                     }

textgen_llm = Bedrock(model_id = "anthropic.claude-instant-v1",
                    model_kwargs = inference_modifier 
                    )

st.title("👨‍💻 Work with Databases")

db = SQLDatabase.from_uri("sqlite:////Users/thandavm/work/thandavm-git/ga-bedrock/coderapp/data/Chinook.db")
toolkit = SQLDatabaseToolkit(db=db, llm=textgen_llm)

agent_executor = create_sql_agent(
    llm=textgen_llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

query = st.text_input("Ask the Chinook db:", key="query")
btn_execute = st.button("Execute", key = 'btn_execute', type="primary")

if btn_execute:
    output = agent_executor.run(query)
    st.write(output)