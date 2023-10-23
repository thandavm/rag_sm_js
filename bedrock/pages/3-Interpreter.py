import boto3
import json
import streamlit as st

from langchain.llms.bedrock import Bedrock
from langchain import PromptTemplate

## 
st.title('Interpreter')
prog_lang = st.selectbox('Programming Language', ('Python', 'JavaScript', 'C++', "SQL"))


sample_code = st.text_area('Sample Code', key = 'sample_code')
btn_interpret = st.button('Interpret', type="primary")

# Create a prompt template that has multiple input variables
multi_var_prompt = PromptTemplate(
    input_variables=["code", "programmingLanguage"], 
    template="""

Human: You will be acting as an expert software developer in {programmingLanguage}. 
You will explain the below code and highlight if there are any red flags or where best practices are not being followed.
<code>
{code}
</code>

Assistant:"""
)

# Pass in values to the input variables
prompt = multi_var_prompt.format(code=sample_code, programmingLanguage=prog_lang)

inference_modifier = {'max_tokens_to_sample':4096, 
                      "temperature":0.5,
                      "top_k":250,
                      "top_p":1,
                      "stop_sequences": ["\n\nHuman"]
                     }

textgen_llm = Bedrock(model_id = "anthropic.claude-v2",
                    model_kwargs = inference_modifier 
                    )

if btn_interpret:
    response = textgen_llm(prompt)
    code_explanation = response[response.index('\n')+1:]
    st.write(code_explanation)