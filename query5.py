import chromadb
from chromadb.config import Settings
from transformers import AutoTokenizer, AutoModel
import torch
import json

import sys

if len(sys.argv) < 2:
    print("Bitte geben Sie einen Parameter ein.")
    exit() 
    
parameter = sys.argv[1]
print(f"Der übergebene Parameter ist: {parameter}")


# Verbinde dich mit der ChromaDB
client = chromadb.HttpClient(host='localhost', port=8000)

# Definiere den Namen der Collection
collection_name = "vier"

# Hole oder erstelle die Collection
collection = client.get_or_create_collection(name=collection_name)

print("Elements:",collection.count()) # returns the number of items in the collection

# Lade ein vortrainiertes Modell und Tokenizer von Hugging Face
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Definiere eine Einbettungsfunktion
def embed_text(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        embeddings = model(**inputs)
    return embeddings.last_hidden_state.mean(dim=1).numpy()


# Führe eine Query aus
query_text = [parameter]
query_embeddings = embed_text(query_text)
results = collection.query(
    query_embeddings=query_embeddings.tolist(),  # Nutze die Einbettungen für die Abfrage
    n_results=5
)

# print("-----RESULTS-----");

# print(results);

# Formatiert ausgeben
# formatted_data = json.dumps(results, indent=4, ensure_ascii=False)
# print(formatted_data)

## Zeige die Ergebnisse an
#for result in results:
##    print(result)

# Ausgabe der Dokumente
# documents = results.get("documents", [])
# for document in documents:
#    for doc in document:
#        print("-----------------------------------------------------------")
#        print(doc)





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
        
        #html_output += f'<a href="{permalink}" id={id_value}" distance="{distance_value}">{title}</a><br>\n' # <!-- {first_20_words} --><br>\n'
        html_output += f'<a href="{permalink}" id={id_value}" distance="{distance_value}">{title}</a><br> <!-- {first_20_words} --><br>\n'
    
    return html_output


# HTML-Links generieren
html_links = generate_html_links(results)
print(html_links)

