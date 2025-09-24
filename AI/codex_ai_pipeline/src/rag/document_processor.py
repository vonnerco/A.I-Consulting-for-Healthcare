from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import chromadb

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("documents")
    
    def process_documents(self, file_paths: list):
        documents = []
        for path in file_paths:
            loader = PyPDFLoader(path)
            docs = loader.load()
            documents.extend(docs)
        
        chunks = self.text_splitter.split_documents(documents)
        return chunks
    
    def store_embeddings(self, chunks):
        ids = [f"doc_{i}" for i in range(len(chunks))]
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
