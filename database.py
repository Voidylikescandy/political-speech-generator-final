import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DB_PATH

# Connect to LanceDB
db = lancedb.connect(DB_PATH)

# Set up embedding model
model = get_registry().get("sentence-transformers").create(name="BAAI/bge-small-en-v1.5", device="cuda")

# Define text splitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)

# Define LanceDB Schema
class Words(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    source_id: str

# Create or open table
table_name = "words"
if table_name not in db.table_names():
    # print("Data does not exist...")
    table = db.create_table(table_name, schema=Words)
else:
    table = db.open_table(table_name)

def insert_text_into_db(text_dict):
    """
    Takes a dictionary of source_id -> text mappings,
    splits the text into chunks and inserts each chunk into the vector database.
    """
    total_chunks = 0
    
    for source_id, text in text_dict.items():
        chunks = splitter.split_text(text)
        records = [{"text": chunk, "source_id": source_id} for chunk in chunks]
        table.add(records)
        total_chunks += len(records)
        # print(f"Inserted {len(records)} chunks into the database with source_id: {source_id}")
    # print(f"Total: Inserted {total_chunks} chunks from {len(text_dict)} sources into the database.")
