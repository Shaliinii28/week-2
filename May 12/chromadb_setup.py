import chromadb
import uuid

def initialize_chromadb(document_content=None):
    try:
        # Initialize ChromaDB client with persistent storage
        client = chromadb.PersistentClient(path="./chroma_data")
        
        # Create or get a collection named 'sample_collection'
        collection = client.get_or_create_collection(name="sample_collection")
        
        # Use provided document content or default
        if document_content is None:
            document_content = "This is a sample document about artificial intelligence and machine learning."
            metadata = {"author": "Sample Author", "category": "Technology"}
        else:
            metadata = {"author": "Internet", "category": "Fiction"}
        
        # Sample document data
        document_id = str(uuid.uuid4())
        
        # Add the document to the collection
        collection.add(
            documents=[document_content],
            metadatas=[metadata],
            ids=[document_id]
        )
        
        print(f"Successfully added document with ID: {document_id}")
        print("Document content:", document_content)
        print("Metadata:", metadata)
        
        return client, collection
    
    except Exception as e:
        print(f"Error initializing ChromaDB or storing document: {str(e)}")
        raise

def list_all_documents(collection):
    """
    List all documents in the collection.
    
    Args:
        collection: ChromaDB collection object
    """
    try:
        # Query all documents (using a generic query to retrieve everything)
        results = collection.query(query_texts=[""], n_results=collection.count())
        print("\nAll Documents in Collection:")
        for i, (doc, meta, doc_id) in enumerate(zip(results["documents"], results["metadatas"], results["ids"])):
            print(f"Document {i+1} (ID: {doc_id}):")
            print(f"Content: {doc}")
            print(f"Metadata: {meta}")
            print("-" * 50)
    except Exception as e:
        print(f"Error listing documents: {str(e)}")

if __name__ == "__main__":
    try:
        # Example document (replace with your content or set to None for default)
        custom_document = (
            "They had always called it the green river. It made sense. The river was green. "
            "The river likely had a different official name, but to everyone in town, it was and "
            "had always been the green river. So it was with great surprise that on this day the "
            "green river was a fluorescent pink."
        )
        
        # Initialize ChromaDB and store document
        client, collection = initialize_chromadb(document_content=custom_document)
        
        # Query the collection to verify the document
        query_text = "green river"  # Adjusted to match the document
        results = collection.query(query_texts=[query_text], n_results=1)
        print("\nQuery Results:")
        print(f"Query: {query_text}")
        print("Retrieved document:", results["documents"])
        print("Metadata:", results["metadatas"])
        
        # List all documents in the collection
        list_all_documents(collection)
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")