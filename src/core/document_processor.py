from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredImageLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
import tempfile
import os
import sys
import importlib.util
from PIL import Image
from langchain.docstore.document import Document

# Add the project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.api.ollama_api import get_available_models
import base64
from io import BytesIO
import shutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

def is_package_installed(package_name):
    return importlib.util.find_spec(package_name) is not None

@dataclass
class ProcessedFile:
    name: str
    size: int
    type: str
    collection_name: str

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with Chroma DB"""
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        
        # Initialize Chroma settings
        self.chroma_settings = Settings(
            persist_directory="./chroma_db",
            anonymized_telemetry=False
        )
        
        # Create Chroma client
        self.client = chromadb.Client(self.chroma_settings)
        
        # Initialize processed files list
        self.processed_files: List[ProcessedFile] = []
        
        # Text splitter for documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Create persistent directory if it doesn't exist
        if not os.path.exists("./chroma_db"):
            os.makedirs("./chroma_db")

    def process_file(self, uploaded_file) -> None:
        """Process an uploaded file and store it in Chroma DB"""
        try:
            # Create temporary file to process
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                file_path = tmp_file.name

            # Determine file type and load accordingly
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                loader = PyPDFLoader(file_path)
            elif file_type.startswith("image/"):
                loader = UnstructuredImageLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            # Load and split documents
            documents = loader.load()
            splits = self.text_splitter.split_documents(documents)

            # Create collection name from file name
            collection_name = f"collection_{uploaded_file.name.replace('.', '_')}"

            # Create or get collection
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_functions.OllamaEmbeddingFunction(
                    model_name="nomic-embed-text",
                    base_url="http://localhost:11434"
                )
            )

            # Create Chroma vectorstore
            vectorstore = Chroma(
                client=self.client,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )

            # Add documents to vectorstore
            vectorstore.add_documents(splits)

            # Store file info
            processed_file = ProcessedFile(
                name=uploaded_file.name,
                size=len(uploaded_file.getvalue()),
                type=file_type,
                collection_name=collection_name
            )
            self.processed_files.append(processed_file)

            # Cleanup temporary file
            os.unlink(file_path)

        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

    def get_processed_files(self) -> List[Dict]:
        """Get list of processed files"""
        return [
            {"name": f.name, "size": f.size, "type": f.type}
            for f in self.processed_files
        ]

    def remove_file(self, file_name: str) -> None:
        """Remove a file from the processor and its collection from Chroma"""
        try:
            # Find the file in processed files
            file_to_remove = next(
                (f for f in self.processed_files if f.name == file_name),
                None
            )
            
            if file_to_remove:
                # Delete collection from Chroma
                self.client.delete_collection(file_to_remove.collection_name)
                
                # Remove from processed files list
                self.processed_files = [
                    f for f in self.processed_files if f.name != file_name
                ]
            else:
                raise ValueError(f"File {file_name} not found")

        except Exception as e:
            raise Exception(f"Error removing file: {str(e)}")

    def search_documents(self, query: str, k: int = 3) -> List[Dict]:
        """Search across all collections for relevant documents"""
        results = []
        for processed_file in self.processed_files:
            collection = self.client.get_collection(processed_file.collection_name)
            query_results = collection.query(
                query_texts=[query],
                n_results=k
            )
            results.extend(query_results['documents'][0])
        return results

    def reset_state(self) -> None:
        """Reset the processor state and clear all collections"""
        try:
            # Delete all collections
            for processed_file in self.processed_files:
                self.client.delete_collection(processed_file.collection_name)
            
            # Clear processed files list
            self.processed_files.clear()
            
            # Delete persistence directory
            if os.path.exists("./chroma_db"):
                import shutil
                shutil.rmtree("./chroma_db")
                os.makedirs("./chroma_db")

        except Exception as e:
            raise Exception(f"Error resetting state: {str(e)}")

    def _clear_vector_store(self):
        """Safely clear the vector store and its directory"""
        try:
            if hasattr(self, 'vector_store') and self.vector_store is not None:
                try:
                    self.vector_store.delete_collection()
                except:
                    pass
            if os.path.exists("./chroma_db"):
                # Force remove readonly files
                def handle_error(func, path, exc_info):
                    import stat
                    if not os.access(path, os.W_OK):
                        os.chmod(path, stat.S_IWUSR)
                        func(path)
                shutil.rmtree("./chroma_db", onerror=handle_error)
        except Exception as e:
            print(f"Warning: Could not clear vector store: {str(e)}")

    def _load_processed_files(self):
        """Load processed files from vector store metadata"""
        if self.vector_store is None:
            return {}
        
        processed_files = {}
        try:
            # Get all documents from the collection
            docs = self.vector_store.get()
            if docs and docs['metadatas']:
                for metadata in docs['metadatas']:
                    if metadata and 'source' in metadata:
                        processed_files[metadata['source']] = {
                            'name': metadata['source'],
                            'type': metadata.get('type', 'document'),
                            'size': metadata.get('size', 0)
                        }
        except Exception as e:
            print(f"Warning: Failed to load processed files: {str(e)}")
        return processed_files

    def get_relevant_context(self, query, k=3):
        """Get relevant context from documents with enhanced debug logging."""
        if self.vector_store is None:
            print("Warning: Vector store is not initialized")
            return ""
        
        if not self.processed_files:
            print("No documents have been processed yet")
            return ""
        
        try:
            print(f"Searching for: {query}")
            print(f"Available documents: {list(self.processed_files.keys())}")
            
            # Search for relevant documents with distance score
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)
            
            if not docs_and_scores:
                print("No relevant documents found")
                return ""
            
            print(f"Found {len(docs_and_scores)} relevant documents")
            
            # Format documents with metadata and relevance info
            formatted_contexts = []
            for doc, score in docs_and_scores:
                source = doc.metadata.get('source', 'Unknown')
                doc_type = doc.metadata.get('type', 'document')
                relevance = round((1 - score) * 100, 2)
                
                print(f"Document: {source}, Type: {doc_type}, Score: {relevance}%")
                print(f"Content length: {len(doc.page_content)} characters")
                
                context = f"Source: {source} (Type: {doc_type}, Relevance: {relevance}%)"
                if doc_type == 'image':
                    context += f"\nImage Analysis:\n{doc.page_content}"
                else:
                    context += f"\nContent: {doc.page_content}"
                formatted_contexts.append(context)
            
            return "\n\n---\n\n".join(formatted_contexts)
            
        except Exception as e:
            print(f"Error during document search: {str(e)}")
            return f"Error searching documents: {str(e)}"

    def cleanup(self):
        """Clean up resources and delete stored data"""
        try:
            if self.vector_store is not None:
                try:
                    self.vector_store.delete_collection()
                except Exception as e:
                    print(f"Warning: Failed to delete collection: {str(e)}")
                finally:
                    self.vector_store = None
            
            self._clear_vector_store()
            self.processed_files = []
            print("Cleanup completed successfully")
            
        except Exception as e:
            print(f"Warning: Failed to cleanup: {str(e)}")
            # Try force cleanup
            try:
                if os.path.exists("./chroma_db"):
                    shutil.rmtree("./chroma_db", ignore_errors=True)
            except:
                pass