import chromadb
from chromadb.config import Settings

# Verbinde dich mit der ChromaDB
# client = chromadb.Client(Settings(chroma_api_impl="local", chroma_api_port=8000))
client = chromadb.HttpClient(host='localhost', port=8000)

# Definiere den Namen der Collection
collection_name = "vier"

# Hole die Collection
collection = client.get_or_create_collection(name=collection_name)

# Lösche alle Elemente in der Collection
# Methode: Löschen der gesamten Collection und neu erstellen
client.delete_collection(name=collection_name)
collection = client.get_or_create_collection(name=collection_name)

print(f"Alle Elemente in der Collection '{collection_name}' wurden gelöscht.")

