import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DB_PATH
from logger import logger

# Connect to LanceDB
logger.info("Connecting to LanceDB...")
db = lancedb.connect(DB_PATH)
logger.info("Connected to LanceDB successfully")

# Set up embedding model
logger.info("Setting up embedding model...")
model = get_registry().get("sentence-transformers").create(name="BAAI/bge-small-en-v1.5", device="cuda")
logger.info("Embedding model initialized successfully")

# Define text splitter
logger.info("Initializing text splitter...")
splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
logger.info("Text splitter initialized successfully")

# Define LanceDB Schema
class Words(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    source_id: str

# Create or open table
table_name = "words"
if table_name not in db.table_names():
    # print("Data does not exist...")
    logger.info(f"Table '{table_name}' does not exist. Creating new table...")
    table = db.create_table(table_name, schema=Words)
    logger.info("Table created successfully")
else:
    logger.info(f"Opening existing table '{table_name}'...")
    table = db.open_table(table_name)
    logger.info("Table opened successfully")

def insert_text_into_db(text_dict):
    """
    Takes a dictionary of source_id -> text mappings,
    splits the text into chunks and inserts each chunk into the vector database.
    """
    total_chunks = 0
    logger.info("Starting text insertion process...")
    
    for source_id, text in text_dict.items():
        logger.info(f"Processing text for source_id: {source_id}")
        chunks = splitter.split_text(text)
        records = [{"text": chunk, "source_id": source_id} for chunk in chunks]
        table.add(records)
        total_chunks += len(records)
        logger.info(f"Inserted {len(records)} chunks into the database for source_id: {source_id}")
        # print(f"Inserted {len(records)} chunks into the database with source_id: {source_id}")
    logger.info(f"Total: Inserted {total_chunks} chunks from {len(text_dict)} sources into the database.")
    # print(f"Total: Inserted {total_chunks} chunks from {len(text_dict)} sources into the database.")
