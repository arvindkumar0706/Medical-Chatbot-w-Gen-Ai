from src.helper import load_pdf, text_split, download_hugging_face_embeddings
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV')

extracted_data = load_pdf("Data/")
text_chunks = text_split(extracted_data)
embeddings = download_hugging_face_embeddings()

# Initialize Pinecone client
pc = PineconeClient(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)

index_name = "medbot"

# Create index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

# Get the Pinecone index instance
pinecone_index = pc.Index(index_name)

# Initialize LangChain Pinecone vectorstore from langchain_pinecone package
docsearch = Pinecone(
    pinecone_index,  # note: positional argument, no `client=` keyword
    embeddings,
    text_key="text"  # adjust if needed
)

# Add documents to Pinecone index
docsearch.add_documents(text_chunks)
