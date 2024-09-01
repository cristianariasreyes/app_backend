import os
from pinecone import Pinecone
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
import uuid

from openai import OpenAI

load_dotenv()

class document:
    def __init__(self, document_file, category, owner,identifier,company,subject,department):
        self.content = ""  
        self.subject = ""
        self.name = ""
        self.category = category
        self.owner = owner
        self.identifier = identifier
        self.company = company
        self.document_file = document_file
        self.subject = subject
        self.department = department
        self.metadata_field_info = ""
        #cargamos el documento
        read_document = None
        self.UUID = ""
        
        try:
            read_document = PdfReader(self.document_file)
            content = ""
            self.name = self.document_file.filename
            for page in range(len(read_document.pages)):
                pageObj = read_document.pages[page]
                content += pageObj.extract_text()
            self.content = content
            #Creamos un UUID
            self.UUID = str(uuid.uuid4())
        except Exception as e:
            raise Exception(f"Se produjo un error cargando el documento: {e}")
       

    def __str__(self) -> str:
        return f""" Nombre: {self.name}\n
                    Asunto: {self.subject}\n
                    Dueño: {self.owner}\n
                    Categoria: {self.category}\n
                    Identificador: {self.identifier}\n      
                    Company: {self.company}\n
                    Content : {self.content}\n
                    UUID: {self.UUID}
                    """
    #Inserta un documento en la base de datos de pinecone
    def save_document(self):
        print(f"content:{self.content}")
        
        #preparamos el metadata para insertarlo al documento
        doc_metadata=f"""<metadata>
                            name:{self.name},
                            subject:{self.subject},
                            category:{self.category},
                            owner:{self.owner},
                            identifier:{self.identifier},
                            company:{self.company},
                            department:{self.department},
                            UUID:{self.UUID},
                        </metadata>"""
        self.content = doc_metadata + self.content
        try:
            print("Dividiendo el texto en chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len
            )        
            chunks = text_splitter.split_text(self.content)        
            print(f"Se dividió el texto en {len(chunks)} chunks")
            #Creamos los embeddings
            print("Creando los embeddings...")
            embeddings = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"),
                                          model='text-embedding-3-large', dimensions=3072)
            Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
            llm=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            print("Se crearon los embeddings")
            #Guardamos la metadata en el el vector de pinecone

            
            print("Guardando el documento y la metadata en el vector de pinecone...")
            documento=[]
            i=1
            for chunk in chunks:
                documento.append(Document(page_content=chunk,metadata={
                    "name":self.name,
                    "subject":self.subject,
                    "category":self.category,
                    "owner":self.owner,
                    "identifier":self.identifier,
                    "company":self.company,
                    "department":self.department,
                    "UUID":self.UUID
                    }))       
                print(f"Chunk {i} se guardó correctamente. ")
                i+=1
            PineconeVectorStore.from_documents(documento,embeddings,index_name="agorachat",namespace="agorachat")
            print("Documento guardado completamente.")
            return self.UUID
        except Exception as e:
            raise Exception(f"Se produjo un error guardando el documento: {e}")
         
    #def delete_document(id_document):
    def delete_document(self,UUID):
        try:
            pc = Pinecone(api_key="PINECONE_API_KEY")
            index = pc.Index("agorachat")
            index.delete(
                filter={
                    "UUID": {"$eq": UUID}
                }
            )          
        except Exception as e:
            raise Exception(f"Se produjo un error eliminando el documento: {e}")
        return 'El documento se ha eliminado correctamente'
      
    @classmethod
    def list_documents(cls, query):
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        index = pc.Index("agorachat")
        embeddings = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"),model='text-embedding-3-large', dimensions=3072)
        vector = OpenAIEmbeddings.embed_query(embeddings, query)
        result = index.query(filter={'record_type': {'$eq': query}}, vector=vector, include_metadata=True, top_k=100)

        # Inicializar un diccionario para la metadata y un conjunto para los nombres ya procesados
        metadata_dict = {}
        processed_names = set()

        for match in result['matches']:
            # Verificar si el nombre del documento ya ha sido procesado
            if match['metadata']['name'] not in processed_names:
                metadata = {
                    "id": match['id'],
                    "name": match['metadata']['name'],
                    "subject": match['metadata'].get('subject', ''),
                    "category": match['metadata'].get('category', ''),
                    "owner": match['metadata'].get('owner', ''),
                    "identifier": match['metadata'].get('identifier', ''),
                    "file_type": match['metadata'].get('file_type', ''),
                    "company": match['metadata'].get('company', ''),
                    "department": match['metadata'].get('department', '')  
                }
                metadata_dict[match['id']] = metadata
                processed_names.add(match['metadata']['name'])

        return metadata_dict

    
        
    def save_document_record(self,name):
        #escribimos en el archivo documentos_cargados.txt el nombre del archivo que se ha cargado  
        #con un salto de linea al final
        with open("documentos_cargados.txt", "a") as file:
            file.write(name + "\n")
        
        return 'El archivo se ha subido y procesado correctamente'


#resultado =document.list_documents("documento")
#print(f"Resultado: {metadata}")
#print(type(resultado))
#documento = document('108969278611.txt','transcription','cristian arias','108969278611','plataforma group','Alerta de guerra','Mesa de ayuda','transcription')
#documento.insert_in_database()

