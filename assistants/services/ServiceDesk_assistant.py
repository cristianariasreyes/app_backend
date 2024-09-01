import os
import hashlib
import time
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


class Servicetonic_assistant:
    def __init__(self, assistant) -> None:
        self.assistant = assistant

    def get_servicetonic_categories(self):

        query = """
                WITH RecursiveCTE AS (
                    -- CTE para obtener los niveles iniciales
                    SELECT
                        dr.ID_DEPENDENCE_RULE,
                        dr.ID_LIST_VALUE,
                        dr.ID_DR_PARENT,
                        lv.CODE_VALUE AS ListValue,
                        CAST(lv.CODE_VALUE AS VARCHAR(MAX)) AS DependencyPath,
                        0 AS Level
                    FROM
                        DEPENDENCE_RULE dr
                    INNER JOIN
                        LIST_VALUES lv ON dr.ID_LIST_VALUE = lv.ID_LIST_VALUE
                    WHERE
                        dr.ID_DR_PARENT IS NULL -- Empezar con los nodos raíz (sin padre)
                        and ID_DG = 24

                    UNION ALL

                    -- CTE recursiva para obtener todos los niveles
                    SELECT
                        dr.ID_DEPENDENCE_RULE,
                        dr.ID_LIST_VALUE,
                        dr.ID_DR_PARENT,
                        lv.CODE_VALUE AS ListValue,
                        CAST(rcte.DependencyPath + '##' + lv.CODE_VALUE AS VARCHAR(MAX)) AS DependencyPath,
                        Level + 1
                    FROM
                        DEPENDENCE_RULE dr
                    INNER JOIN
                        LIST_VALUES lv ON dr.ID_LIST_VALUE = lv.ID_LIST_VALUE
                    INNER JOIN
                        RecursiveCTE rcte ON dr.ID_DR_PARENT = rcte.ID_DEPENDENCE_RULE

                        where  ID_DG = 24
                )

                -- Seleccionar el resultado final ordenado por nivel de profundidad
                SELECT
                    --ID_DEPENDENCE_RULE,
                    --ID_LIST_VALUE,
                    --ID_DR_PARENT,
                    --ListValue,
                    --Level
                    DependencyPath
                FROM
                    RecursiveCTE
        """
        with connect_servicetonic_demo_database() as cnxn:
            cursor = cnxn.cursor()

            if cursor:
                print("Conexión exitosa")

            cursor.execute(query)
            rows = cursor.fetchall()

        categories = ""
        i = 1
        # recorremos los resultados
        for row in rows:
            categories += f"{i}. {row[0]}\n"
            i += 1
        print(categories)
        return categories

    def ServiceTonic_assistant(self, description):

        categories = Servicetonic_assistant(
            "servicetonic"
        ).get_servicetonic_categories()

        system_role = """Eres un agente de mesa de ayuda que lee la peticion del usuario y la
        clasifica en una de la lista de categorias. Las categorias estan separadas por el separador
        ##. Dentro de las categorias candidatas, debes elegir siempre la categoria que tenga
        # mas elementos separados por ##.
        La descripcion llega por correo y muchas veces se adjunta la firma del usuario. Debes ignorar
        aquel texto que parezca ser parte de la firma del correo.
        La respuesta a la consulta del usuario debe ser literalmente el nombre de la categoria que
        describa mejor la peticion del usuario dentro de las categorias disponibles tal
        y cual estan escritas y nada mas.
        Jamas entregues una respuesta que no este en la lista de categorias."""

        prompt = f"""
        Consulta del usuario: {description}
        Categorias disponibles:
        {categories}
        """

        client = OpenAI()
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ],
        )
        print(respuesta.choices[0].message)
        return respuesta.choices[0].message.content

    def get_servicetonic_ticket_description(self, ID_INCIDENT_PROJECT):

        try:
            with connect_servicetonic_demo_database() as cnxn:
                cursor = cnxn.cursor()
                if cursor:
                    print("Conexión exitosa")

                cursor.execute(
                    "select DESCRIPTION FROM incident where ID_PROJECT = 25 AND ID_INCIDENT_PROJECT  = ? ",
                    (ID_INCIDENT_PROJECT,),
                )
                rows = cursor.fetchall()
                description = rows[0]
            return description
        except Exception as e:
            print(
                f"Error al obtener la descripcion del ticket {ID_INCIDENT_PROJECT}: {e}"
            )
            return None

    def get_ticket_sentiment(self, user_message):

        system_role = """Eres un experto en evaluar el sentimiento de un mensaje del usuario de una
        mesa de ayuda.Segun la descripcion del correo enviado por el usuario debes evaluar el
        sentimiento del mensaje en las siguientes categorias: Positivo, Negativo, Neutral.

        Debes diferenciar el tono del mensaje del contenido del mensaje. Lo mas importante es evaluar
        el sentimiento por el contenido del mensaje ya que el tono puede ser amable pero el mensaje
        puede ser negativo.

        Califica como positivo solo aquellos que tengan claramente marcado un sentimiento positivo
        en el mensaje y en el tono.

        Califica como negativo si el mensaje es negativo aunquie el tono sea amable.

        Califica como neutral si el mensaje no tiene un sentimiento claro o si el mensaje es
        informativo y no tiene un sentimiento claro.

        Responde solo con el nombre de la categoria que describa mejor el sentimiento del mensaje."""

        prompt = f"""
        correo enviado por usuario: {user_message}
        """

        client = OpenAI()
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ],
        )
        # print(respuesta.choices[0].message)
        return respuesta.choices[0].message.content

    def update_servicetonic_ticket_with_category(self, ID_INCIDENT_PROJECT):

        description = self.get_servicetonic_ticket_description(ID_INCIDENT_PROJECT)
        print(f"La descripcion del ticket {ID_INCIDENT_PROJECT} es: {description[0]}")

        categoria_completa = self.self_classify_servicetonic_ticket(description[0])
        print(f"La categoria del ticket {ID_INCIDENT_PROJECT} es: {categoria_completa}")

        categoria_dividida = categoria_completa.split("##")

        if len(categoria_dividida) == 1:
            tipo_ticket = categoria_dividida[0]
            categoria = ""
            sub_categoria = ""
            detalle = ""
        if len(categoria_dividida) == 2:
            tipo_ticket = categoria_dividida[0]
            categoria = categoria_dividida[1]
            sub_categoria = ""
            detalle = ""
        if len(categoria_dividida) == 3:
            tipo_ticket = categoria_dividida[0]
            categoria = categoria_dividida[1]
            sub_categoria = categoria_dividida[2]
            detalle = ""
        if len(categoria_dividida) == 4:
            tipo_ticket = categoria_dividida[0]
            categoria = categoria_dividida[1]
            sub_categoria = categoria_dividida[2]
            detalle = categoria_dividida[3]

        ticket_sentiment = self.get_ticket_sentiment(description)

        print(
            f"La categoria del ticket luego de separar los valores es:{tipo_ticket}##{categoria}##{sub_categoria}##{detalle} El largo de la categoria es {len(categoria)}"
        )
        chat = document_chat(description[0], 0, "gpt-3.5-turbo")
        agora_response = chat.basic_chat(0.2)
        print(f"Respuesta de agora: {agora_response}")
        with connect_servicetonic_demo_database() as cnxn:
            cursor = cnxn.cursor()

            if cursor:
                print("Conexión exitosa")

            consulta = "UPDATE incident_0025 set TICKET_SENTIMENT=?, AGORA_RESPONSE = ?, TIPO_TICKET = ?, CATEGORIA = ?, SUB_CATEGORIA = ?, DETALLE = ? where ID_INCIDENT = (SELECT ID_INCIDENT FROM incident where ID_INCIDENT_PROJECT=?)"
            cursor.execute(
                consulta,
                (
                    ticket_sentiment,
                    agora_response,
                    tipo_ticket,
                    categoria,
                    sub_categoria,
                    detalle,
                    ID_INCIDENT_PROJECT,
                ),
            )
            cnxn.commit()
            # print(consulta)
            # print(f"Ticket {ID_INCIDENT_PROJECT} actualizado con éxito. La categoria es {tipo_ticket}##{categoria}##{sub_categoria}##{detalle}")
        return {
            "user_sentiment": ticket_sentiment,
            "agora_response": agora_response,
            "categoria": categoria,
            "sub_categoria": sub_categoria,
            "detalle": detalle,
        }


ticket = Servicetonic_assistant("servicetonic")
# categorias = ticket.get_servicetonic_categories()
# descripcion = ticket.get_servicetonic_ticket_description(6177)
# print(descripcion)
# respuesta=ticket.self_classify_servicetonic_ticket(descripcion)
# ticket.update_servicetonic_ticket_with_category(6192)

# ticket.get_ticket_sentiment(6178)
