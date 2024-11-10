import os
from dotenv import load_dotenv
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.together import TogetherEmbedding
from llama_index.llms.together import TogetherLLM
from llama_index.core.query_engine import NLSQLTableQueryEngine

from llama_index.core import Settings
from llama_index.core import SQLDatabase
from sqlalchemy import create_engine

load_dotenv(dotenv_path="/home/user/.ssh/.env")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini

engine = create_engine("sqlite:///mock_programs.db")
# metadata_obj = MetaData()
table_name = "mock_programs"
sql_database = SQLDatabase(engine, include_tables=[table_name])

# embeddings and llm
embed_model = TogetherEmbedding(
    model_name="togethercomputer/m2-bert-80M-8k-retrieval", api_key=TOGETHER_API_KEY
)

llm = TogetherLLM(
    model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", api_key=TOGETHER_API_KEY
)
#llm = TogetherLLM(
#    model="meta-llama/Llama-3.2-3B-Instruct-Turbo", api_key=TOGETHER_API_KEY
#)

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=[table_name], llm=llm, embed_model=embed_model
)
# query_str = "Show up to 5 programs in San Francisco"
def run_query(query_str):
    response = query_engine.query(query_str)
    return response

query_str = "Show up to 5 programs near me " + "Bay area " + "show complete information"
response = run_query(query_str)
print(response)
