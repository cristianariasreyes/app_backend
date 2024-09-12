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

load_dotenv()


class document:
    def __init__(self,document):
        self.data = document.POST.copy() #We made a copy of the data in the request object so we can modify it
        self.file = document.FILES
        try:
            read_document = PdfReader(self.file)
            content = ""
            self.name = self.file.filename
            for page in range(len(read_document.pages)):
                pageObj = read_document.pages[page]
                content += pageObj.extract_text()
                
            #We add the content of the PDF to the data dictionary
            self.data['content'] = content
            
            #Creamos un UUID
            self.UUID = str(uuid.uuid4())
        except Exception as e:
            raise Exception(f"There was an error reading PDF File: {e}")

    def __str__(self) -> str:
        return f""" Document: {self.data['name']}\n
                    Asunto: {self.data['name']}\n
                    Dueño: {self.data['name']}\n
                    Categoria: {self.data['category']}\n
                    Identificador: {self.data['name']}\n      
                    Company: {self.data['Company']}\n
                    Content : {self.content}\n
                    UUID: {self.UUID}
                    """


    #Inserta un documento en la base de datos de pinecone
    def SaveDocument(self):
        #Guardamos los datos del documento en la base de datos
        #Guardamos el archivo PDF
        #Guardamos el registro en pinecone
        pass

    def SavePineconeDocument(self):
        try:
            print("Dividiendo el texto en chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000, chunk_overlap=200, length_function=len
            )
            chunks = text_splitter.split_text(self.data['content'])
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
                    "name":self.data['name'],
                    "subject":self.data['subject'],
                    "category":self.data['category'],
                    "owner":self.data['owner'],
                    "identifier":self.data['identifier'],
                    "company":self.data['company'],
                    "department":self.data['department'],
                    "UUID":self.data['content']
                    }))       
                print(f"Chunk {i} se guardó correctamente. ")
                i+=1
            PineconeVectorStore.from_documents(documento,embeddings,index_name="agorachat",namespace="agorachat")
            print("Documento guardado completamente.")
            return self.UUID
        except Exception as e:
            raise Exception(f"Se produjo un error guardando el documento: {e}")
            
    def SavePDFDocument(self):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        s3_file_path = f"{settings.ENVIRONMENT_CUSTOM}/{self.file.name}"
        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_file_path}"

        try:
            s3_client.upload_fileobj(self.file, settings.AWS_STORAGE_BUCKET_NAME, s3_file_path)
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


# resultado =document.list_documents("documento")
# print(f"Resultado: {metadata}")
# print(type(resultado))
# documento = document('108969278611.txt','transcription','cristian arias','108969278611','plataforma group','Alerta de guerra','Mesa de ayuda','transcription')
# documento.insert_in_database()
