import json
import chromadb
from chromadb.config import Settings
from transformers import AutoTokenizer, AutoModel
import torch
import csv

# Initialisiere ChromaDB-Client
client = chromadb.HttpClient(host='localhost', port=8000)

# Definiere den Namen der Collection
collection_name = "vier"

# Hole oder erstelle die Collection
collection = client.get_or_create_collection(name=collection_name)

# Lade ein vortrainiertes Modell und Tokenizer von Hugging Face
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Definiere eine Einbettungsfunktion
def embed_text(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        embeddings = model(**inputs)
    return embeddings.last_hidden_state.mean(dim=1).numpy()

# Pfad zur JSON-Datei
json_file_path = 'wpdata.json'

# Lade die JSON-Daten aus der Datei
with open(json_file_path, 'r', encoding='utf-8') as f:
    articles = json.load(f)

# Extrahiere Inhalte und IDs für Einbettungen
texts = [article["content"] for article in articles]
ids = [str(article["ID"]) for article in articles]

# Vektorisierung der Texte
embeddings = embed_text(texts)

results_dict = {}


def generate_html_links(data):
    ids = data["ids"][0]
    distances = data["distances"][0]
    metadatas = data["metadatas"][0]
    documents = data["documents"][0]
    
    html_output = ""
    
    for i in range(len(ids)):
        id_value = ids[i]
        distance_value = distances[i]
        title = metadatas[i]["title"]
        permalink = metadatas[i]["permalink"]
        document = documents[i]
        first_20_words = ' '.join(document.split()[:20])
        
        #html_output += f'<a href="{permalink}" id={id_value}" distance="{distance_value}">{title}</a>\n' # <!-- {first_20_words} --><br>\n'
        html_output += f'<a href="{permalink}" id={id_value}" distance="{distance_value}">{title}</a><br> <!-- {first_20_words} --><br>\n'
    
    return html_output



for i, (doc_id, doc_embedding) in enumerate(zip(ids, embeddings)):
    # Abfrage nach ähnlichen Vektoren
    results = collection.query(
        query_embeddings=[doc_embedding.tolist()],
        n_results=6  # top_k=6, da der eigene Satz dabei sein wird
    )

    print(f"<hr>Zur ID {doc_id} wurde folgendes gefunden:<br>")
    print(generate_html_links(results))


