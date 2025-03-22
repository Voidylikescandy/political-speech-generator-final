import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DB_PATH

# Connect to LanceDB
db = lancedb.connect(DB_PATH)

# Set up embedding model
model = get_registry().get("sentence-transformers").create(
    name="BAAI/bge-small-en-v1.5", device="cuda"
)

# Define text splitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)

# Define LanceDB Schema
class Words(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    source_id: str

# Create or open table
if "words" not in db.table_names():
    table = db.create_table("words", schema=Words)
else:
    table = db.open_table("words")

def insert_text_into_db(text_dict):
    total_chunks = 0
    for source_id, text in text_dict.items():
        chunks = splitter.split_text(text)
        records = [{"text": chunk, "source_id": source_id} for chunk in chunks]
        table.add(records)
        total_chunks += len(records)
    print(f"Inserted {total_chunks} chunks into DB.")
