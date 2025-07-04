from flask import Flask, render_template, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from src.prompt import prompt_template
import os

app = Flask(__name__)
load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.environ.get('PINECONE_API_ENV')

embeddings = download_hugging_face_embeddings()

# Initialize Pinecone client properly with environment
pc = PineconeClient(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

index_name = "medbot"

pinecone_index = pc.Index(index_name)

# IMPORTANT: Pass text_key argument here!
docsearch = Pinecone(pinecone_index, embeddings, text_key="text")

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
chain_type_kwargs = {"prompt": PROMPT}

llm = CTransformers(
    model="model/llama-2-7b-chat.ggmlv3.q4_0.bin",
    model_type="llama",
    config={'max_new_tokens': 512, 'temperature': 0.8}
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=docsearch.as_retriever(search_kwargs={'k': 2}),
    return_source_documents=True,
    chain_type_kwargs=chain_type_kwargs
)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form.get("msg")
    print("User Query:", msg)
    result = qa({"query": msg})
    print("Response:", result["result"])
    return str(result["result"])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
