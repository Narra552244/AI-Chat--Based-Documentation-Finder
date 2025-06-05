import os
from typing import List, Dict
from PyPDF2 import PdfReader
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, documents_dir: str = "data/documents"):
        self.documents_dir = documents_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def process_pdf(self, file_path: str) -> List[str]:
        """Extract text from PDF and split into chunks."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return self.text_splitter.split_text(text)
        except Exception as e:
            raise Exception(f"Error processing PDF {file_path}: {str(e)}")

    def process_text(self, file_path: str) -> List[str]:
        """Process text file and split into chunks."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return self.text_splitter.split_text(text)
        except Exception as e:
            raise Exception(f"Error processing text file {file_path}: {str(e)}")

    def get_document_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks."""
        try:
            embeddings = []
            for chunk in text_chunks:
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=chunk
                )
                embeddings.append(response.data[0].embedding)
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")

    def process_document(self, file_path: str, file_type: str) -> Dict:
        """Process document and return chunks and embeddings."""
        if file_type.lower() == 'pdf':
            chunks = self.process_pdf(file_path)
        else:
            chunks = self.process_text(file_path)
        
        embeddings = self.get_document_embeddings(chunks)
        
        return {
            'chunks': chunks,
            'embeddings': embeddings,
            'metadata': {
                'file_name': os.path.basename(file_path),
                'file_type': file_type,
                'chunk_count': len(chunks)
            }
        } 