import json
import chromadb
from chromadb.config import Settings
from transformers import AutoTokenizer, AutoModel
import torch
import re
import spacy
import language_tool_python
import csv

# Verbinde dich mit der ChromaDB
#client = chromadb.Client(Settings(chroma_api_impl="local", chroma_api_port=8000))
client = chromadb.HttpClient(host='localhost', port=8000)


# Laden des SpaCy-Modells zur Lemmatisierung
nlp = spacy.load('de_core_news_sm')

# Laden des LanguageTool-Tools zur Rechtschreibkorrektur
tool = language_tool_python.LanguageTool('de')


# Funktion zur Vorverarbeitung des Textes
def preprocess_text(text):
    # Rechtschreibkorrektur
    text = tool.correct(text)
    # Kleinbuchstaben
    text = text.lower()
    # Satzzeichen handhaben: Entfernen nur der unnötigen Satzzeichen
    text = re.sub(r'[^a-zA-Zäöüß0-9\s]', '', text)
    # Text in SpaCy-Dokument konvertieren
    doc = nlp(text)
    # Lemmatisierung
    processed_text = ' '.join([token.lemma_ for token in doc])
    return processed_text




# Definiere den Namen der neuen Collection
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

# Extrahiere Inhalte für Einbettungen
texts = []
for article in articles:
    content = article["title"]+"\n"+article["title"]+"\n\n "+article["content"]
    print("-----------------------------------------------")
    print(content)
    content = preprocess_text(content)
    print("---------------------->>>>---------------------")
    print(content)
    print("-----------------------------------------------")
    texts.append(content)

## Extrahiere Inhalte für Einbettungen
#texts = [article["content"] for article in articles]

# Berechne Einbettungen für die Texte
embeddings = embed_text(texts)

# IDs und Metadaten erstellen
ids = [str(article["ID"]) for article in articles]
# metadatas = [{"title": article["title"]} for article in articles]
metadatas = [{"title": article["title"], "permalink": article["permalink"]} for article in articles]


# Füge die Daten in die Collection ein
response = collection.add(
    documents=texts,
    embeddings=embeddings.tolist(),
    metadatas=metadatas,
    ids=ids
)


# Gebe die Antwort aus, um zu sehen, welche Informationen zurückgegeben werden
print("done")


