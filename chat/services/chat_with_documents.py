import os
import hashlib
import time
import sys
import uuid
from utils.utils import obtiene_db_path, get_current_timestamp
import sqlite3
from dotenv import load_dotenv
import openai
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import MessagesPlaceholder, ChatPromptTemplate
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from pinecone import Pinecone
from langchain_core.messages import HumanMessage, AIMessage
from documents.models import Document
from chat.models import Chat_history, Chat_assistant, Chat_assistant_documents
from .chat_tools import ChatWithModels, PineconeRelevantDocs
import markdown

load_dotenv()


class document_chat:

    def __init__(
        self,
        temperature=0.0,
        llm_model="",
        asistant=None,
        pdf_id_document=None,
        pdf_document=None,
        conversation_hash=None,
    ):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.help_file = ""
        self.embeddings = OpenAIEmbeddings(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model="text-embedding-3-large",
            dimensions=3072,
        )
        self.query_vector = PineconeVectorStore.from_existing_index(
            index_name="agora", embedding=self.embeddings
        )
        self.vector_store = PineconeVectorStore.from_existing_index(
            index_name="agora", embedding=self.embeddings
        )

        self.asistant = asistant
        self.pdf_id_document = pdf_id_document
        self.pdf_document = pdf_document
        self.conversation_hash = conversation_hash

    def assistant_chat(self, id_assistant, query):
        # rescatamos de la tabla assistant
        print("Obteniendo asistente...")
        # verificamos que exista el asistente con id_assistant
        try:
            chat_assistant = Chat_assistant.objects.get(id_chat_assistant=id_assistant)
            # obtenemos el modelo, rol y temperatura
            llm_model = chat_assistant.llm_model
            temperature = chat_assistant.temperature
            role = chat_assistant.role
            namespace = chat_assistant.company_id
            print(f"Modelo: {llm_model} Temperatura: {temperature} Rol: {role}")
        except Chat_assistant.DoesNotExist:
            print(f"No se encontró el asistente con id: {id_assistant}")
            return f"No se encontró el asistente con id: {id_assistant}"

        # Obtenemos todos los documentos del asistente usando related_name
        print("Obteniendo documentos del asistente...")
        document_ids = [
            str(doc_id)
            for doc_id in chat_assistant.assistant_documents.values_list(
                "id_document__id_document", flat=True
            )
        ]
        print(f"Documentos del asistente: {document_ids}")
        # Obtenemos los documentos relevantes de Pinecone
        print("Obteniendo documentos relevantes desde Pinecone...")
        RelevantDocsObject = PineconeRelevantDocs(query, 5)
        Relevant_docs = RelevantDocsObject.HashIDFilterSearch(document_ids, namespace)

        # Concatenamos los documentos relevantes a role
        role = f"""{role} /n Basa tu respuesta en estos documentos: /n {Relevant_docs['relevant_docs']}"""

        # Hacemos la consulta a OpenAI
        print("Haciendo consulta a OpenAI...")
        chat = ChatWithModels(llm_model, temperature)
        model_response = chat.OpenAI_Chat(query, role)
        final_response = self.GetWrapedResponse(model_response, Relevant_docs)

        # Reemplazar saltos de línea por <br/>
        model_response_con_breaks = final_response.replace("\n", "<br/>")
        message = self.ProcesarRespuestaMarkdown(model_response_con_breaks)

        print(f"La respuesta final es: {message}")
        return {
            "content": message,
            "id_chat_history": 0,
        }

    def ChatSingleDoc(self, id_document, query):
        # Obtenemos el id_vdb del documento
        print("ChatSingleDoc Obteniendo id de base vectorial...")
        hash_ID = [str(id_document)]
        # Obtenemos el company_id del documento
        document = Document.objects.get(id_document=id_document)
        namespace = document.company_id

        # Consultamos el documento en Pinecone
        print(f"Consultando documento {hash_ID} en Pinecone...")
        RelevantDocsObject = PineconeRelevantDocs(query, 5)
        Relevant_docs = RelevantDocsObject.HashIDFilterSearch(hash_ID, namespace)

        # Concatenamos los documentos relevantes a role
        role = f""" /n Basa tu respuesta en estos documentos: /n {Relevant_docs['relevant_docs']}"""
        # Hacemos la consulta a OpenAI
        print("Haciendo consulta a OpenAI...")
        chat = ChatWithModels()
        model_response = chat.OpenAI_Chat(query, role)
        final_response = self.GetWrapedResponse(model_response, Relevant_docs)

        # Reemplazar saltos de línea por <br/>
        model_response_con_breaks = final_response.replace("\n", "<br/>")
        message = self.ProcesarRespuestaMarkdown(model_response_con_breaks)

        print(f"La respuesta final es: {message}")
        return {"content": message, "id_chat_history": 0}

    def GetWrapedResponse(self, model_response, relevant_docs):
        final_response = f"{model_response} <br/><br/>**Fuentes:** <br/><br/>- {relevant_docs['sources']}"
        return final_response

    def ProcesarRespuestaMarkdown(self, respuesta):
        # Convertir el texto de Markdown a HTML
        html = markdown.markdown(respuesta)
        return html

    def evaluate_answer(self, useful, id_chat_history):
        try:
            # En el chat history seteamos el campo useful a lo que venga como parametro
            chat_history = Chat_history.objects.get(id_chat_history=id_chat_history)
            chat_history.useful = useful
            chat_history.save()
            if useful:
                return "Gracias por tu valoracion, tendremos en cuenta que esta respuesta te ha sido util!"
            else:
                return "Gracias por tu valoracion, lo tendremos en cuenta para mejorar!"

        except Chat_history.DoesNotExist:
            return False
