import json
import os
import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import PyPDF2

# Define the folder containing PDF files
data_folder = os.path.join(os.path.dirname(__file__), "rag_data")

# Initialize lists to store text data and metadata
documents = []
chunk_metadata = []

# List of specific PDF files to process
pdf_files = [
    "30 Days To Internet Marketing Success.pdf",
    "60-Minute Brand Strategist. The Essential Brand Book for Marketing Professionals.pdf",
]

# Loop through the specified PDF files
for file_name in pdf_files:
    file_path = os.path.join(data_folder, file_name)
    
    if os.path.exists(file_path):
        print(f"Processing {file_name}...")
        
        # Extract text from PDF
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            
            # Append the extracted text as a single document
            documents.append(text)
    else:
        print(f"File {file_name} not found in {data_folder}")

# Check if any documents were processed
if not documents:
    print("❌ No documents were processed. Please check the PDF files and their locations.")
    exit(1)

# Split text into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = []

for i, doc in enumerate(documents):
    split_chunks = text_splitter.split_text(doc)
    chunks.extend(split_chunks)
    chunk_metadata.extend([{"doc_index": i, "source": pdf_files[i], "text": chunk} for chunk in split_chunks])

# Save chunk metadata for retrieval
metadata_path = os.path.join(data_folder, "chunk_metadata.json")
with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(chunk_metadata, f, indent=4)

# Convert text chunks into embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)

# Store embeddings in FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings, dtype=np.float32))

# Save the FAISS index
faiss_path = os.path.join(data_folder, "rag_data_index.faiss")
faiss.write_index(index, faiss_path)

print("✅ FAISS index created and saved successfully for the PDF files in rag_data!")