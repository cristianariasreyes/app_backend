import os
import hashlib
import time
import sys
from utils.utils import obtiene_db_path, get_current_timestamp
import sqlite3
from dotenv import load_dotenv
import openai
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import MessagesPlaceholder,ChatPromptTemplate
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
load_dotenv()

class document_chat:
    
    def __init__(self, temperature=0.0,llm_model="",asistant=None,pdf_id_document=None,pdf_document=None,conversation_hash=None):
        self.llm=ChatOpenAI(model=llm_model,temperature=temperature)
        self.help_file=""
        self.embeddings = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"),model='text-embedding-3-large', dimensions=3072)
        self.query_vector = PineconeVectorStore.from_existing_index(index_name="agora",embedding=self.embeddings)
        self.vector_store = PineconeVectorStore.from_existing_index(index_name="agora",embedding=self.embeddings)
        self.prompt = ""
        self.chat_history = []
        self.history_string=""
        self.asistant = asistant
        self.pdf_id_document = pdf_id_document
        self.pdf_document = pdf_document
        self.conversation_hash = conversation_hash
        
    def get_prompt(self,query):
        print("Armando el prompt...")
        try:
            
            system_prompt ="""Esta es una conversacion amistosa entre un humano y una IA. 
            El humano hace preguntas y la IA responde.
            La IA responde solo basado en los documentos que tiene disponibles.
            La IA tiene memoria, para ello tiene a su disposicion un historial de conversacion reciente que
            puede solo en estos casos:
            1. Para ampliar el contexto de la pregunta actual.
            2. En caso el humano pregunte especificamente por conversaciones recientes.
            como base de la respuesta. Si la pregunta no tiene nada que ver con el historial debe decir
            simplemente que no tiene informacion suficiente para responder.
            
            Pregunta actual del humano: {query}
            """
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human","{query}"),
                MessagesPlaceholder(variable_name="chat_history")
            ])
            return prompt_template
        

            #prompt = PromptTemplate(
            #    input_variables={"documents", "query", "history"},
            #    template=template)
            #respuesta = prompt.format(documents=documents,query=query,history=history)
            
            #print("Prompt: "+respuesta) 
        except Exception as e:
            print(f"Se produjo un error generando el prompt: {e}")
    def get_metadata(self):
        print("Obteniendo metadata...")
        return [
            AttributeInfo(
                name="name",
                description="Nombre del archivo subido",
                type="string"
            ),
            AttributeInfo(
                name="subject",
                description="Breve resumen de lo que trata el documento",
                type="string"
            ),
            AttributeInfo(
                name="category",
                description="""Nos dice que tipo de informacion cotiene el documento. Debemos usar 
                esta metadata para entender mejor el contenido del documento y poder hacer busquedas 
                mas precisas.""",
                type="string"
            ),
            AttributeInfo(
                name="owner",
                description="El usuario que ha subido el documento o quien tiene privilegios sobre el documento",
                type="string"
            ),
            AttributeInfo(
                name="identifier",
                description="""Identificador. Usar este campo para agrupar documentos que refieren 
                a un unico identificador como podria ser un DNI, un rol, etc.""",
                type="string"
            ),
            AttributeInfo(
                name="file_type",
                description="extension del archivo subido",
                type="string"
            ),
            AttributeInfo(
                name="company",
                description="A que organizacion pertenece el documento",
                type="string"
            ),
            AttributeInfo(
                name="department",
                description="""Departamento al que pertenece el documento. Usar esta metadata para
                relacionar el contenido con un departamento especifico de la empresa.""",
                type="string"
            )
        ]   
    def basic_chat_with_memory(self):
        print("Creando un vector store...")
        vector_store = PineconeVectorStore.from_existing_index(index_name="agora",embedding=self.embeddings)

        #Obtenemos el historial de chat
        memory_chat = []
        memory_chat = self.get_db_history_chat()
        if memory_chat==[]:
            memory_chat.append(("",""))        
        #Invocamos el prompt
        self.prompt = self.get_prompt(self.query)
        
        print("Obteniendo una respuesta con historial...")
        try:
            print("creando un retriever...")
            retriever = vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k":5,"score_threshold":0.74})
            print("Obteniendo respuesta con memoria...")
            qa = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True)

            memory_chat.append(HumanMessage(content="Humano: "+ self.query))
            result = qa({"question":self.prompt,"chat_history":memory_chat})
            #agregamos la respuesta al historial
            id_chat_history = self.add_entry_to_history(self.query,result["answer"])
            print(f"Historial:{memory_chat}")
            print(f"Respuesta: {result['answer']}")
            #enviamos la respuesta y el id_chat_history en un diccionario
            return {"result":result["answer"],"id_chat_history":id_chat_history}
        except Exception as e:
            print(f"Se produjo un error haciendo consulta por similitud: {e}")
            raise e
    def basic_chat(self,score_threshold):
        print("BASIC CHAT")

        print("Obteniendo una respuesta...")
        try:
            #Invocamos el prompt
            retriever = self.vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k":5,"score_threshold":score_threshold}, )
            qa = RetrievalQA.from_chain_type(
                llm=self.llm,
                retriever=retriever,
                return_source_documents=True
                
                )
            result = qa.invoke(self.query)
            
            print(result)
            return result["result"]
        except Exception as e:
            print(f"Se produjo un error haciendo consulta por similitud(basica): {e}")
            if hasattr(e, 'args') and len(e.args) > 0:
                error_message = e.args[0]
                # Extraer el mensaje del error
                if isinstance(error_message, dict) and 'error' in error_message:
                    print(f"Error: {error_message['error']['message']}")
                    return f"Error: {error_message['error']['message']}"
                else:
                    print(f"Error: {error_message}")
                    return f"Error: {error_message}"
            else:
                print("Ocurrió un error desconocido.")
                return "Ocurrió un error desconocido."
    def add_entry_to_history(self,question,answer):
        print("Agregando input al historial de la conversacion...")
        pass
    def get_db_history_chat(self,format=None):
        pass
    def GetDocumentsHashID(self,id_assistant,id_document):
        print("Entrando a la funcion que obtiene los hash_ID...")
        if id_document:
            # Caso donde se está chateando con un solo documento
            try:
                print("Intentando obtener documentos...")
                document = Document.objects.get(id=id_document)
                id_vdbs = [document.id_vdb]
            except Document.DoesNotExist:
                id_vdbs = []
        elif id_assistant:
            # Caso donde se está chateando con un asistente
            documentos = Chat_assistant_documents.objects.select_related('id_document').filter(id_chat_assistant=id_assistant)
            id_vdbs = list(documentos.values_list('id_document__id_vdb', flat=True))
        else:
            id_vdbs = []
        print(f"ID_VDBs: {id_vdbs}")
        return id_vdbs

    
    def assistant_chat(self,id_assistant,query):
        #rescatamos de la tabla assistant
        print("Obteniendo asistente...")
        chat_assistant = Chat_assistant.objects.get(id_chat_assistant=id_assistant)
        #obtenemos el modelo, rol y temperatura
        llm_model = chat_assistant.llm_model
        temperature = chat_assistant.temperature
        role = chat_assistant.role
        print(f"Modelo:{llm_model} Temperatura:{temperature} Rol:{role}")
        
        #Obtenemos todos los documentos del asistente
        print("Obteniendo documentos del asistente...")
        chat_assistant_documents = Chat_assistant_documents.objects.filter(id_chat_assistant=id_assistant)
        document_hashIDs = self.GetDocumentsHashID(id_assistant,None)

        #Obtenemos los documentos relevantes de Pinecone
        print("Obteniendo documentos relevantes desde Pinecone...")
        RelevantDocsObject = PineconeRelevantDocs(query,5)
        Relevant_docs=RelevantDocsObject.HashIDFilterSearch(document_hashIDs)
        
        #Concatenamos los documentos relevantes a role
        role = f"""{role} /n Basa tu respuesta en estos documentos: /n {Relevant_docs['relevant_docs']}"""
        #Hacemos la consulta a OpenAI
        print("Haciendo consulta a OpenAI...")
        chat = ChatWithModels(llm_model,temperature)
        model_response = chat.OpenAI_Chat(query,role)
        final_response = f"{model_response} /n Fuentes:/n {Relevant_docs['sources']}"
        print(f"La respuesta final es: {final_response}")
        return final_response
    
    def ChatSingleDoc(self,id_document,query):
        #Obtenemos el id_vdb del documento
        print("Obteniendo id de base vectorial...")
        hash_ID=self.GetDocumentsHashID(None,id_document)

        #Consultamos el documento en Pinecone
        print(f"Consultando documento {hash_ID} en Pinecone...")
        RelevantDocsObject = PineconeRelevantDocs(query,5)
        Relevant_docs=RelevantDocsObject.HashIDFilterSearch(hash_ID)
    
        #Concatenamos los documentos relevantes a role
        role = f""" /n Basa tu respuesta en estos documentos: /n {Relevant_docs['relevant_docs']}"""
        #Hacemos la consulta a OpenAI
        print("Haciendo consulta a OpenAI...")
        chat = ChatWithModels()
        model_response = chat.OpenAI_Chat(query,role)
        final_response = self.GetWrapedResponse(model_response,Relevant_docs)
        print(f"La respuesta final es: {final_response}")
        return final_response
    
    
    def GetWrapedResponse(self,model_response,relevant_docs):
        final_response = f"{model_response} /n Fuentes:/n {relevant_docs['sources']}"
        return final_response
        
    def get_relevant_documents(self):
        
        try:
            print("Obteniendo documentos relevantes...")
            embeddings = openai.embeddings.create(input=self.query, 
                                                model="text-embedding-3-large", 
                                                dimensions=3072)
            #print(embeddings.data[0].embedding)
            relevant_vectors = embeddings.data[0].embedding
            pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"),)
            index = pc.Index(name="agora")
            respuesta = index.query(
                vector=relevant_vectors,
                top_k=5,
                include_metadata=True,
                filter={'hash_ID': {'$in': ['cafa46e6cbf2e9579564e509417f704b','e20365773d7ebbe777b579332052cb93']}},
                )
            relevant_docs = ""
            i=1
            for docs in respuesta.matches:
                relevant_docs += f"Documento {i}: {docs.metadata['text']} /n"
                i+=1
            role = f"""Eres"" un asistente que responde las preguntas del usuario basado en documentos relevante. 
                      Estos son los documentos que tienes a disposicion: /n {relevant_docs}"""
                
            # Generar una respuesta usando OpenAI
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            client = OpenAI()
            respuesta = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": self.query}
                ],
                temperature=0.5
            )
            return respuesta.choices[0].message.content

        except Exception as e:
            print(f"Se produjo un error obteniendo documentos relevantes: {e}")
            return None
    @staticmethod   
    def evaluate_answer(useful,id_history_chat):
        print("Validando la respuesta...")
        conn= None
        try:
            db_path = obtiene_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            sql="""UPDATE chat_history SET useful = ? WHERE id_chat_history = ?"""
            cursor.execute(sql,(useful,id_history_chat))            
            conn.commit()
            print("Entrada validada.")
            return True
        except Exception as e:
            print(f"Error validando la respuesta: {e}")
            return f"Error validando la respuesta: {e}"
        finally:
            if conn:
                conn.close()





#chat=document_chat()
#respuesta = chat.assistant_chat(1,"Cual es el presupuesto de la licitacion de subrei para adquirir lansweeper?")
#print(respuesta)
#print (respuesta.matches[0])
#for match in respuesta.matches:
 #   print(f"Hash ID:{match.metadata['hash_ID']} Nombre:{match.metadata['name']}")
#,filter={"hash_ID":"cafa46e6cbf2e9579564e509417f704b"}






