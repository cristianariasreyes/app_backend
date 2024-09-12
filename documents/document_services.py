import os
from pinecone import Pinecone
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
import hashlib
import uuid
import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError
from openai import OpenAI
from chat.services.chat_tools import ChatWithModels

load_dotenv()


class document:
    def __init__(self,document):
        self.data = document.POST.copy() #We made a copy of the data in the request object so we can modify it
        self.file = document.FILES
        self.uploaded_file = list(self.file.values())[0]
        self.uploaded_FileName = self.uploaded_file.name

    def __str__(self) -> str:
        return f""" 
                    Asunto: {self.data['subject']}\n
                    Dueño: {self.data['owner']}\n
                    Categoria: {self.data['category']}\n
                    Departamento: {self.data['department']}\n
                    """


    #Inserta un documento en la base de datos de pinecone
    def SaveDocument(self):
        try:
            self.data['document_name'] = self.uploaded_file.name
            self.data['company_id'] = "DemoPLG"
            self.data['id_document'] = self.CreateUUID()
            content = self.GetContent()
            self.data['resume'] = self.CreateResume(content)
            self.data['document_path'] = self.SavePDFDocument()
            self.SavePineconeDocument(content,self.data['company_id'])
        except Exception as e:
            raise Exception(f"Error al crear el documento: {e}")
        return self.data

   
    def SavePineconeDocument(self,content,namespace):
        try:
            print("Dividiendo el texto en chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000, chunk_overlap=200, length_function=len
            )
            chunks = text_splitter.split_text(content)
            print(f"Se dividió el texto en {len(chunks)} chunks")
            #Creamos los embeddings
            print("Creando los embeddings...")
            embeddings = OpenAIEmbeddings(
                api_key=os.environ.get("OPENAI_API_KEY"),
                model="text-embedding-3-large",
                dimensions=3072,
            )
            Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
            llm = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            print("Se crearon los embeddings")
            #Guardamos la metadata en el el vector de pinecone

            
            print("Guardando el documento y la metadata en el vector de pinecone...")
            documento = []
            i = 1
            for chunk in chunks:
                documento.append(Document(page_content=chunk,metadata={
                    "name":self.data['document_name'],
                    "subject":self.data['subject'],
                    "category":self.data['document_category_name'],
                    "owner":self.data['owner'],
                    "department":self.data['document_department_name'],
                    "id_document":self.data['id_document'],
                    "document_type":self.data['document_type_name'],
                    "resume":self.data['resume']
                    }))       
                print(f"Chunk {i} se guardó correctamente. ")
                i+=1
            PineconeVectorStore.from_documents(documento,embeddings,index_name="agorachat",namespace=namespace)
            print("Documento guardado completamente.")
             
        except Exception as e:
            raise Exception(f"Se produjo un error guardando el documento: {e}")
            
    def SavePDFDocument(self):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        
        s3_file_path = f"{settings.ENVIRONMENT_CUSTOM}/{self.uploaded_file.name}"  # Nombre del archivo
        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_file_path}"

        try:
            print(f"Subiendo el archivo a AWS S3 en la ruta: {s3_url}")
            s3_client.upload_fileobj(self.uploaded_file, settings.AWS_STORAGE_BUCKET_NAME, s3_file_path)  # Subir archivo
            print("El archivo se subió correctamente a AWS S3")
            return s3_url
        except NoCredentialsError:
            raise Exception("AWS credentials not available")
        except Exception as e:
            raise Exception(f"Error uploading file to AWS S3: {e}")
    
    def SavePostgresDocument(self):
        pass
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
        result = index.query(
            filter={"record_type": {"$eq": query}},
            vector=vector,
            include_metadata=True,
            top_k=100,
        )

        # Inicializar un diccionario para la metadata y un conjunto para los nombres ya procesados
        metadata_dict = {}
        processed_names = set()

        for match in result["matches"]:
            # Verificar si el nombre del documento ya ha sido procesado
            if match["metadata"]["name"] not in processed_names:
                metadata = {
                    "id": match["id"],
                    "name": match["metadata"]["name"],
                    "subject": match["metadata"].get("subject", ""),
                    "category": match["metadata"].get("category", ""),
                    "owner": match["metadata"].get("owner", ""),
                    "identifier": match["metadata"].get("identifier", ""),
                    "file_type": match["metadata"].get("file_type", ""),
                    "company": match["metadata"].get("company", ""),
                    "department": match["metadata"].get("department", ""),
                }
                metadata_dict[match["id"]] = metadata
                processed_names.add(match["metadata"]["name"])

        return metadata_dict

    def save_document_record(self, name):
        # escribimos en el archivo documentos_cargados.txt el nombre del archivo que se ha cargado
        # con un salto de linea al final
        with open("documentos_cargados.txt", "a") as file:
            file.write(name + "\n")

        return "El archivo se ha subido y procesado correctamente"

    def GetContent(self):
        try:
            print("Leyendo el contenido del documento PDF...")
            reader = PdfReader(self.uploaded_file)  # Leer el archivo PDF
            content = ""
            for page in reader.pages:
                content += page.extract_text()  # Extraer el texto de cada página
        except Exception as e:
            raise Exception(f"Error leyendo el archivo PDF: {e}")
        print(f"Contenido extraído: {content[:200]}...")  # Muestra un fragmento del contenido
        return content
    
    def CreateUUID(self):
        DOC_UUID =str(uuid.uuid4())
        print(f"UUID del documento: {DOC_UUID}")
        return DOC_UUID

    def CreateResume(self,content):
        role="""Eres un experto resumiendo documentos. Debes generar un resumen de no mas de 500 caracteres del documento
        completo que se te proporciona"""
        
        prompt = f"Documento completo: {content}"
        try:
            print("Creando el resumen del documento...")
            new_chat = ChatWithModels()
            resume = new_chat.OpenAI_Chat(prompt,role)
        except Exception as e:
            raise Exception(f"Error al generar el resumen del documento: {e}")
        print(f"Este es el resumen del documento: {resume}")
        return resume


