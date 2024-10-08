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
from documents.models import Document_type, Document_department, Document_category
import tiktoken

load_dotenv()
enc = tiktoken.get_encoding("cl100k_base")


class document:
    def __init__(self, document, files):
        self.data = document  # We made a copy of the data in the request object so we can modify it
        self.file = files
        self.uploaded_file = list(self.file.values())[0]
        self.uploaded_FileName = self.uploaded_file.name

    def __str__(self) -> str:
        return f"""
                    Asunto: {self.data['subject']}\n
                    Dueño: {self.data['owner']}\n
                    Categoria: {self.data['id_document_category_id']}\n
                    Departamento: {self.data['id_document_department_id']}\n
                    """

    def querydict_to_dict(self, querydict):
        data = {}
        for key, value in querydict.lists():
            # Si el valor es una lista, toma el primer elemento
            data[key] = (
                value[0] if isinstance(value, list) and len(value) > 0 else value
            )
        return data

    # Inserta un documento en la base de datos de pinecone
    def SaveDocument(self):
        try:

            self.data["document_name"] = self.uploaded_file.name
            self.data["company_id"] = "DemoPLG"
            if not self.data.get("id_document"):
                self.data["id_document"] = self.CreateUUID()
            content = self.GetContent()
            self.data["resume"] = self.CreateResume(content)
            self.data["document_path"] = self.SavePDFDocument()
            self.SavePineconeDocument(content, self.data["company_id"])
        except Exception as e:
            raise Exception(f"Error al crear el documento: {e}")
        return self.data

    def count_tokens(self, text):
        return len(enc.encode(text))

    def SavePineconeDocument(self, content, namespace):
        try:
            print("Dividiendo el texto en chunks...")
            # Obtenemos el nombre de la categoria, el tipo de documento y el departamento
            category = (
                Document_category.objects.filter(
                    id_document_category=self.data["id_document_category"]
                )
                .values("description")
                .first()["description"]
            )
            department = (
                Document_department.objects.filter(
                    id_document_department=self.data["id_document_department"]
                )
                .values("description")
                .first()["description"]
            )
            document_type = (
                Document_type.objects.filter(
                    id_document_type=self.data["id_document_type"]
                )
                .values("description")
                .first()["description"]
            )

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=8000,  # Tamaño máximo de chunk en tokens
                chunk_overlap=200,  # Solapamiento en tokens entre chunks
                length_function=self.count_tokens,  # Usamos la función para contar tokens
            )
            chunks = text_splitter.split_text(content)
            print(f"Se dividió el texto en {len(chunks)} chunks")
            # Creamos los embeddings
            print("Creando los embeddings...")
            embeddings = OpenAIEmbeddings(
                api_key=os.environ.get("OPENAI_API_KEY"),
                model="text-embedding-3-large",
                dimensions=3072,
            )
            Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
            llm = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            print("Se crearon los embeddings")
            # Guardamos la metadata en el el vector de pinecone

            print("Guardando el documento y la metadata en el vector de pinecone...")
            print(
                f"La categoria y departamento son: {category} y {department} y el namespace es: {namespace}"
            )
            documento = []
            i = 1

            print("-------------------")
            print("self.data", self.data)
            print("-------------------")

            metadata = {
                "name": self.data["document_name"],
                "subject": self.data["subject"],
                "category": category,
                "owner": self.data["owner"],
                "department": department,
                "id_document": str(self.data["id_document"]),
                "document_type": document_type,
                "resume": self.data["resume"],
            }
            print("-------------------")
            print("metadata", metadata)
            print("-------------------")

            for chunk in chunks:
                documento.append(
                    Document(
                        page_content=chunk,
                        metadata=metadata,
                    )
                )
                print(f"Chunk {i} se guardó correctamente. ")
                i += 1
            PineconeVectorStore.from_documents(
                documento, embeddings, index_name="agorachat", namespace=namespace
            )
            print("Documento guardado completamente.")

        except Exception as e:
            print("error SavePineconeDocument ", e)
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
            s3_client.upload_fileobj(
                self.uploaded_file, settings.AWS_STORAGE_BUCKET_NAME, s3_file_path
            )  # Subir archivo
            print("El archivo se subió correctamente a AWS S3")
            return s3_url
        except NoCredentialsError:
            raise Exception("AWS credentials not available")
        except Exception as e:
            raise Exception(f"Error uploading file to AWS S3: {e}")

    def SavePostgresDocument(self):
        pass

    # def delete_document(id_document):
    def delete_document(self, UUID):
        try:
            pc = Pinecone(api_key="PINECONE_API_KEY")
            index = pc.Index("agorachat")
            index.delete(filter={"UUID": {"$eq": UUID}})
        except Exception as e:
            raise Exception(f"Se produjo un error eliminando el documento: {e}")
        return "El documento se ha eliminado correctamente"

    @classmethod
    def list_documents(cls, query):
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        index = pc.Index("agorachat")
        embeddings = OpenAIEmbeddings(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model="text-embedding-3-large",
            dimensions=3072,
        )
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
        print(
            f"Contenido extraído: {content[:200]}..."
        )  # Muestra un fragmento del contenido
        return content

    def CreateUUID(self):
        DOC_UUID = uuid.uuid1()
        print(f"UUID del documento: {DOC_UUID}")
        return DOC_UUID

    def CreateResume(self, content):
        role = """Eres un experto resumiendo documentos. Debes generar un resumen de no mas de 1000 caracteres del documento
        completo que se te proporciona"""

        prompt = f"Documento completo: {content}"
        try:
            print("Creando el resumen del documento...")
            new_chat = ChatWithModels()
            resume = new_chat.OpenAI_Chat(prompt, role)
        except Exception as e:
            raise Exception(f"Error al generar el resumen del documento: {e}")
        print(f"Este es el resumen del documento: {resume}")
        return resume
