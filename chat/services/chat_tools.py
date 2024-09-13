from openai import OpenAI
from dotenv import load_dotenv
from pinecone import Pinecone
import os

load_dotenv()


class ChatWithModels:
    def __init__(self, model="gpt-4o-mini", temperature=0.5):
        self.model = model
        self.temperature = temperature

    def OpenAI_Chat(self, query, role):
        # Generar una respuesta usando OpenAI
        try:
            print(f"chateando con estos parametros: modelo: {self.model}, temperatura: {self.temperature}")
            client = OpenAI()
            respuesta = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": query}
                ],
                temperature=self.temperature
            )
            print(respuesta.choices[0].message.content)
            return respuesta.choices[0].message.content
        except Exception as e:
            print(e)
            return f"error: No se pudo conectar con OpenAI: {e}"
class PineconeRelevantDocs:
    def __init__(self, query, top_k=5):
        self.top_k = top_k
        self.query = query

    def HashIDFilterSearch(self, hash_IDs,namespace):
        try:
            print("generando la instancia de OpenAi")
            cliente = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            print(f"HashID a consultar:{hash_IDs}")
            response = cliente.embeddings.create(
                input=self.query, model="text-embedding-3-large", dimensions=3072
            )
            relevant_vectors = response.data[0].embedding
            pc = Pinecone(
                api_key=os.environ.get("PINECONE_API_KEY"),
            )
            index = pc.Index(name="agorachat")
            respuesta = index.query(
                namespace=namespace,
                vector=relevant_vectors,
                top_k=5,
                include_metadata=True,
                filter={"id_document": {"$in": hash_IDs}},
            )
        except Exception as e:
            print(e)
            return {"error": "No se pudo conectar con Pinecone"}
        # Poblamos una estructura que tiene todos los hash_ID, el nombre del documento y el texto


        relevant_docs = ""
        original_source = []
        i = 1
        for docs in respuesta["matches"]:
            relevant_docs += f"Documento {i}: {docs['metadata']['text']} /n"
            # añadimos la source si no esta repetida
            if docs["metadata"]["name"] not in original_source:
                original_source.append(docs["metadata"]["name"])

            i += 1
        response = {"relevant_docs": relevant_docs, "sources": original_source}
        print(original_source)
        return response
