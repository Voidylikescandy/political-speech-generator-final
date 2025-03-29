import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DB_PATH
from logger import logger

# Connect to LanceDB
try:
    logger.info("Connecting to LanceDB...")
    db = lancedb.connect(DB_PATH)
    logger.info("Connected to LanceDB successfully")
except Exception as e:
    error_msg = f"Failed to connect to LanceDB: {str(e)}"
    logger.error(error_msg)
    raise Exception(error_msg)

# Set up embedding model
try:
    logger.info("Setting up embedding model...")
    model = get_registry().get("sentence-transformers").create(name="BAAI/bge-small-en-v1.5", device="cuda")
    logger.info("Embedding model initialized successfully")
except Exception as e:
    error_msg = f"Failed to initialize embedding model: {str(e)}"
    logger.error(error_msg)
    raise Exception(error_msg)

# Define text splitter
try:
    logger.info("Initializing text splitter...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
    logger.info("Text splitter initialized successfully")
except Exception as e:
    error_msg = f"Failed to initialize text splitter: {str(e)}"
    logger.error(error_msg)
    raise Exception(error_msg)

# Define LanceDB Schema
class Words(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    source_id: str

# Create or open table
table_name = "words"
try:
    if table_name not in db.table_names():
        # print("Data does not exist...")
        logger.info(f"Table '{table_name}' does not exist. Creating new table...")
        table = db.create_table(table_name, schema=Words)
        logger.info("Table created successfully")
    else:
        logger.info(f"Opening existing table '{table_name}'...")
        table = db.open_table(table_name)
        logger.info("Table opened successfully")
except Exception as e:
    error_msg = f"Failed to create or open table '{table_name}': {str(e)}"
    logger.error(error_msg)
    raise Exception(error_msg)

def insert_text_into_db(text_dict):
    """
    Takes a dictionary of source_id -> text mappings,
    splits the text into chunks and inserts each chunk into the vector database.
    """
    total_chunks = 0
    logger.info("Starting text insertion process...")
    
    try:
        if not isinstance(text_dict, dict):
            error_msg = "Input must be a dictionary mapping source_id to text"
            logger.error(error_msg)
            raise TypeError(error_msg)
            
        for source_id, text in text_dict.items():
            try:
                logger.info(f"Processing text for source_id: {source_id}")
                if not isinstance(text, str):
                    error_msg = f"Text for source_id {source_id} must be a string"
                    logger.error(error_msg)
                    raise TypeError(error_msg)
                    
                chunks = splitter.split_text(text)
                records = [{"text": chunk, "source_id": source_id} for chunk in chunks]
                table.add(records)
                total_chunks += len(records)
                logger.info(f"Inserted {len(records)} chunks into the database for source_id: {source_id}")
                # print(f"Inserted {len(records)} chunks into the database with source_id: {source_id}")
            except Exception as e:
                error_msg = f"Failed to process text for source_id {source_id}: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        logger.info(f"Total: Inserted {total_chunks} chunks from {len(text_dict)} sources into the database.")
        # print(f"Total: Inserted {total_chunks} chunks from {len(text_dict)} sources into the database.")
    except Exception as e:
        if not isinstance(e, TypeError):
            error_msg = f"Failed during text insertion process: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        else:
            raise
