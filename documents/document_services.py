import os
from pinecone import Pinecone
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
import hashlib

from openai import OpenAI

load_dotenv()


class document:
    def __init__(
        self,
        document_file,
        category,
        owner,
        identifier,
        company,
        subject,
        department,
        record_type,
    ):
        self.content = ""
        if record_type == "documento":
            self.file_type = document_file.filename.split(".")[-1]
        if record_type == "transcription":
            self.file_type = "txt"
        self.subject = ""
        self.name = ""
        self.category = category
        self.owner = owner
        self.identifier = identifier
        self.company = company
        self.document_file = document_file
        self.subject = subject
        self.department = department
        self.record_type = record_type
        self.metadata_field_info = ""
        # cargamos el documento
        read_document = None
        self.hash_ID = ""

        try:
            if self.file_type == "pdf":
                read_document = PdfReader(self.document_file)

                content = ""
                self.name = self.document_file.filename
                for page in range(len(read_document.pages)):
                    pageObj = read_document.pages[page]
                    content += pageObj.extract_text()

            if self.file_type == "txt":
                try:
                    # abrimos y leemos el archivo que tiene nombre document_file que esta en el directorio transcripciones
                    with open(
                        "transcripciones/borradores/" + self.document_file, "r"
                    ) as file:
                        content = file.read()
                        self.name = self.document_file
                        # cerramos el archivo
                        file.close()
                        # una vez leido el archivo, lo pasamos a la carpeta transcripciones
                        os.rename(
                            self.document_file, f"transcripciones/{self.document_file}"
                        )

                except Exception as e:
                    raise Exception(f"Se produjo un error cargando el documento: {e}")
            self.content = content
            print("creando un hash ID del documento...")
            self.hash_ID = hashlib.md5(self.content.encode()).hexdigest()
            print(f"Hash ID del documento: {self.hash_ID}")

        except Exception as e:
            raise Exception(f"Se produjo un error cargando el documento: {e}")

    def __str__(self) -> str:
        return f""" Nombre: {self.name}\n
                    Extension del archivo: {self.file_type}\n
                    Asunto: {self.subject}\n
                    Dueño: {self.owner}\n
                    Categoria: {self.category}\n
                    identificador: {self.identifier}
                    company: {self.company}
                """

    # Inserta un documento en la base de datos de pinecone
    def save_document(self):
        print(f"content:{self.content}")

        # preparamos el metadata para insertarlo al documento
        doc_metadata = f"""<metadata>
                            record_type:{self.record_type},
                            name:{self.name},
                            subject:{self.subject},
                            category:{self.category},
                            owner:{self.owner},
                            identifier:{self.identifier},
                            file_type:{self.file_type},
                            company:{self.company},
                            department:{self.department},
                            hash_ID:{self.hash_ID},
                        </metadata>"""
        self.content = doc_metadata + self.content
        try:
            print("Dividiendo el texto en chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000, chunk_overlap=200, length_function=len
            )
            chunks = text_splitter.split_text(self.content)
            print(f"Se dividió el texto en {len(chunks)} chunks")
            # Creamos los embeddings
            # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
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
            documento = []
            i = 1
            for chunk in chunks:
                documento.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "record_type": self.record_type,
                            "name": self.name,
                            "subject": self.subject,
                            "category": self.category,
                            "owner": self.owner,
                            "identifier": self.identifier,
                            "file_type": self.file_type,
                            "company": self.company,
                            "department": self.department,
                            "hash_ID": self.hash_ID,
                        },
                    )
                )

                print(f"Chunk {i} se guardó correctamente. ")
                i += 1
            PineconeVectorStore.from_documents(
                documento, embeddings, index_name="agora"
            )
            print("Documento guardado completamente.")
            self.save_document_record(self.name)
        except Exception as e:
            raise Exception(f"Se produjo un error guardando el documento: {e}")

    # def delete_document(id_document):

    @classmethod
    def list_documents(cls, query):
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        index = pc.Index("agora")
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


# resultado =document.list_documents("documento")
# print(f"Resultado: {metadata}")
# print(type(resultado))
# documento = document('108969278611.txt','transcription','cristian arias','108969278611','plataforma group','Alerta de guerra','Mesa de ayuda','transcription')
# documento.insert_in_database()
