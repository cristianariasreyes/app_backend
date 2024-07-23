import os
import hashlib
import time
from utils.utils import obtiene_db_path, get_current_timestamp
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI
import random
import re

load_dotenv()

class assistant_coach():
    def __init__(self,id_ast_coach,id_ast_coach_chain=0,user_answer=None):
         
        #embeddings = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'))
        #self.vector_store = PineconeVectorStore.from_existing_index(index_name="agora",embedding=embeddings)

        #Assistant atributes:
        self.role = ""
        self.temperature= None
        self.llm_model = ""
        self.questions_per_chain = None
        self.evaluating_prompt = ""
        self.querying_prompt = ""
        self.id_ast_coach=id_ast_coach
        self.name = ""
        self.description = ""
        self.avatar = ""
        self.coach_name=""
        self.document_source = ""
        
        #chain atributes:
        self.current_question = ""
        self.user_answer = user_answer
        self.id_ast_coach_chain = id_ast_coach_chain
        self.id_current_question = None

        #General atributtes:
        self.db_path = obtiene_db_path()
        
        
        #obtenemos las caracteristicas del asistente
        try:
            self._get_asistant_features()

            #Si viene una chain, obtenemos la pregunta actual
            if self.id_ast_coach_chain is not None:
                print(f"La cadena de coachin no es vacia, obteniendo pregunta actual, es {self.id_ast_coach_chain}...")
                current_question_ = self.get_current_question(self.id_ast_coach_chain)
                self.id_current_question = current_question_['id_ast_coach_question']
                self.current_question = current_question_['question']
            else:
                print("La cadena de coaching  es vacia")

        except Exception as e:
            print("Error al iniciar el asistente de coaching", e)
            raise Exception( f"Error al iniciar el asistente de coaching {e}")
                    

    def get_coach_presentation(self):
        try:
            print("Obteniendo presentación del asistente...")
            coach_presentation=f"""
                                    {self.description} <br><br>
                                    Estoy configurado una temperatura de {self.temperature} y 
                                    usando el modelo de lenguaje {self.llm_model}.<br>
                                    Mis jefes me han pedido que hagamos una ronda de 
                                    {self.questions_per_chain} preguntas para entrenar!.<br>"""
            coach_title=f"¡Hola, soy {self.coach_name}! "
            
            return {'coach_presentation':coach_presentation,
                    'coach_title':coach_title,
                    'coach_avatar':self.avatar}
        except Exception as e:
            
            print("Error al obtener la presentación del asistente", e)
            return None
                        
    def _get_asistant_features(self):
        #Obtenemos datos del asistente
        try:
            print("Obteniendo features del asistente...")
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                query = """SELECT 
                                    role, 
                                    temperature,
                                    llm_model,
                                    evaluating_prompt,
                                    querying_prompt,
                                    questions_per_chain,
                                    name,
                                    description,
                                    avatar,
                                    coach_name,
                                    document_source
                                FROM 
                                    asistant a inner join ast_coach ac on 
                                    a.id_assistant = ac.id_assistant                                
                                  WHERE 
                                    ac.id_ast_coach = ?
                                    """
                cursor.execute(query,(self.id_ast_coach,))
                asistant_features = cursor.fetchone()
                
                if asistant_features is None:
                    raise Exception("No se pudieron obtener las características del asistente")
                else:
                    self.role = asistant_features[0]
                    self.temperature = asistant_features[1]
                    self.llm_model = asistant_features[2]
                    self.evaluating_prompt = asistant_features[3]
                    self.querying_prompt = asistant_features[4]
                    self.questions_per_chain = asistant_features[5]
                    self.name = asistant_features[6]
                    self.description = asistant_features[7]
                    self.avatar = asistant_features[8]
                    self.coach_name = asistant_features[9]
                    self.document_source = asistant_features[10]
                
                print("Features del asistente cargadas correctamente...")
                print("temperature:",self.temperature)
                print("llm_model:",self.llm_model)
                print("questions_per_chain:",self.questions_per_chain)
        except Exception as e:
            print("Error al obtener las características del asistente", e)
            raise Exception( f"Error al obtener las características del asistente {e}")

    def begin_coaching_chain(self):
        try:
            #Creamos una nueva cadena de coaching
            new_coach_chain = self.add_new_coach_chain(self.id_ast_coach)
            id_ast_coach_chain = new_coach_chain['id_ast_coach_chain']
            
            get_questions = self.get_next_question(id_ast_coach_chain)
            if get_questions is None:
                raise Exception("No se pudieron obtener las preguntas porque aparentemente no quedan")
            new_question = get_questions['question']
            id_ast_coach_qa = get_questions['id_ast_coach_qa']
            
            id_ast_coach_question = self._add_new_question(id_ast_coach_chain,id_ast_coach_qa,new_question)
            welcome_prompt = f"""
            Un usuario ha iniciado una rutina de coaching de {self.questions_per_chain} preguntas
            contigo. 
            Por favor envia un mensaje de bienvenida y animo para empezar la rutina. El mensaje debe ser
            breve pero poderoso, de no mas de 150 caracteres.          
            """
            
            welcome_role = f"""
            Eres {self.coach_name}, {self.description} 

            """
            welcome_message = self.openai_chat(welcome_role,welcome_prompt)
            
            output = {
                'result':True,
                'id_ast_coach_chain':id_ast_coach_chain,
                'id_ast_coach_question':id_ast_coach_question,
                'current_question':new_question,
                'welcome_message':welcome_message,
                'avatar':self.avatar,
                'error_message':''
            }
            print ("Cadena de coaching iniciada con exito")
            print(output)
            return output
        except Exception as e:
            print("Error al iniciar la cadena de coaching", e)
            raise Exception( f"Error al iniciar la cadena de coaching {e}")

    def add_new_coach_chain(self,id_ast_coach):
        try:
            print("Iniciando nueva cadena de coaching...")
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                current_date = get_current_timestamp()
                # Insertamos un nuevo registro en la tabla y obtenemos el ID creado
                cursor.execute("""INSERT INTO ast_coach_chain (
                                        chain_status, 
                                        user,
                                        chain_date,
                                        id_ast_coach) 
                               VALUES ('1','',?,?)""",(current_date,id_ast_coach))
                id_ast_coach_chain = cursor.lastrowid
                db.commit()
                print("Regitro creado con exito. id_ast_coach_chain:", id_ast_coach_chain)
                return {
                    'result':True,
                    'id_ast_coach_chain':id_ast_coach_chain,
                    'error_message':''}

        except Exception as e:
            print("Error al crear una nueva cadena de coaching", e)
            return {
                'result':False,
                'id_ast_coach_chain':'',
                'error_message':f'Hubo un error al crear una nueva cadena de coaching: {str(e)}'
            }
                
    def _set_initial_QA(self,id_ast_coach):
        #Este método se encarga de obtener las preguntas iniciales del coach y guardarlas 
        #en la tabla de preguntas
        try:
            initial_questions = self.get_document_questions(self.questions_per_chain)
            
            #evaluamos si se obtuvieron las preguntas. De lo contrario intentamos nuevamente
            #hasta un total de 3 veces:
            if initial_questions['result'] == False:
                print("No se obtuvieron las preguntas, intentando nuevamente...")
                for i in range(3):
                    initial_questions = self.get_document_questions(self.questions_per_chain)
                    if initial_questions['result'] == True:
                        break
                if initial_questions['result'] == False:
                    raise Exception("No se pudieron obtener las preguntas iniciales")
            
            questions_array = initial_questions['questions']

            #Ahora obtenemos el diccionario con preguntas y respuestas
            QA_array = self.get_answers(questions_array)

            #Iteramos la lista de preguntas y respuestas y las guardamos en la base de datos
            for QA in QA_array:
                id_question = self.add_coach_qa(self.id_ast_coach,QA['question'],QA['answer'])
                print("agregando id_current_question:",id_question)
                
        except Exception as e:
            print("Error seteando preguntas iniciales", e)
            raise Exception( f"Error seteando preguntas iniciales {e}")
                        
    def add_coach_qa(self,id_ast_coach,question,answer):
        try:
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                qa_entry_date=get_current_timestamp()
                cursor.execute("INSERT INTO ast_coach_qa (id_ast_coach,qa_question,qa_answer,qa_entry_date) VALUES (?,?,?,?)",(id_ast_coach,question,answer,qa_entry_date))
                id_current_qa = cursor.lastrowid
                db.commit()
                print(f"Pregunta agregada con exito. id_current_qa:{id_current_qa}, pregunta:{question}, respuesta:{answer}")
                return id_current_qa
        except Exception as e:
            print("Error al agregar una pregunta al coaching", e)
            return None

    def _add_new_question(self,id_ast_coach_chain,id_ast_coach_qa,question):
        try:
            print("Agregando nueva pregunta...")
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                current_date = get_current_timestamp()
                cursor.execute("""INSERT INTO ast_coach_question (
                                    id_ast_coach_chain,
                                    id_ast_coach_qa,
                                    question,
                                    question_status)
                               VALUES (?,?,?,?)""",(id_ast_coach_chain,id_ast_coach_qa,question,'delivered'))
                db.commit()
                #retornamos el id de la pregunta creada
                id_ast_coach_question = cursor.lastrowid
                print(f"Pregunta agregada con exito a la cadena de coaching id_ast_coach_question:{id_ast_coach_question}")
                return id_ast_coach_question
        except Exception as e:
            print("Error al agregar una pregunta al coaching", e)
            return None

    def get_coach_comment(self,id_ast_coach_question,is_correct,user_answer):
        try:
            print("Obteniendo comentario del coach...")
            question_answer = self.get_right_answer(id_ast_coach_question)
            question = question_answer[0]
            right_answer = question_answer[1]
            
            iscorrect_verbose = ""
            if is_correct == 0:
                answer_evaluation = "La respuesta es incorrecta"
            if is_correct == 1:
                answer_evaluation = "La respuesta es correcta"
            if is_correct == 2:
                answer_evaluation = "Respuesta no tiene relacion con la pregunta"
            if is_correct == 3:
                answer_evaluation = "El alumno no sabe o no recuerda pero pide ayuda"
                
            comment_role =f"""
            {self.role}
            
            El alumno acaba de responder una pregunta.Se ha evaluado la respuesta del usuario de la
            siguiente forma: {iscorrect_verbose}.
            
            Debes hacer un comentario al respecto basandote la materia del curso que se te 
            proporciona.
            Si la respuesta es correcta, felicitalo y de ser necesario complementa su respuesta
            con lo que pudiera haberle faltado. 
            
            Si la respuesta es incorrecta, indicale en que se equivoco, guialo sobre la respuesta 
            correcta y animalo. No le preguntes si quiere intentarlo denuevo pues ya ha sido evaluado
            y se pasará a la siguiente pregunta.
            
            Si la respuesta no tiene relacion alguna con la pregunta o con la materia del curso,
            indicale que debe responder sobre lo que se le ha preguntado. 
            Puedes hacer un comentario ameno para romper el hielo y decirle que lo intente denuevo.
            
            Si el alumno no sabe o no recuerda pero pide ayudas o pistas, dale alguna pista que lo 
            ayude a encontrar la repuesta por si mismo, nunca le des la respuesta directamente. Dile
            luego que con esas pistas deberia poder encontrar la respuesta, que lo intente denuevo.
                        
            Cosas que nunca debes incluir en tus comentarios:
             -Nunca le preguntes al alumno si quiere responder otra pregunta.
             -No le preguntes en que mas puedes ayudarlo, eres un profesor no un asistente de soporte.

            - Esta fué la pregunta: {question}
            - Esta fué la respuesta del alumno: {user_answer}
            - Materia del curso que contiene la respuesta correcta: {right_answer}
            """
            answer_evaluation = self.openai_chat(comment_role,user_answer)
            return answer_evaluation
        except Exception as e:
            print("Error al obtener el comentario del coach", e)
            return None       
            
    def evaluate_answer(self,id_ast_coach_question,user_answer):
        try:
            print("Evaluando respuesta del usuario...")
            question_answer = self.get_right_answer(id_ast_coach_question)
            question = question_answer[0]
            right_answer = question_answer[1]

            
            
            evaluation_role =f"""
            {self.role}
            
            Debes dar una evaluacion de la respuesta del usuario segun lo que se te proporciona
            en el texto fuente.
            La evaluacion solo puede ser uno de estos numeros: 0,1,2,3. 
            El criterio para decidir el numero a entregar es el siguiente:
           
            se califica con un 0:
             - La respuesta es incorrecta o el alumno no quiere seguir participando.
             - La respuesta no tiene que ver ni con la pregunta ni con la respuesta 
            correcta pero se manifiesta cansancio o la intencion de parar.
             - El alumno no sabe o no quiere responder y no pide ayuda.
            --------------------------------
            se califica con un 1:
            - Si la respuesta es correcta en un alto porcentaje de su contenido. 
            - Si la respuesta es parcialmente correcta, es decir, tiene elementos de la respuesta 
              pero faltan otros, evaluala con un 1, es decir, considerala correcta pero indicale 
              al alumno la parte faltante en la respuesta.
            --------------------------------
            se califica con un 2:
              -La respuesta no tiene ninguna relacion alguna con con la  pregunta realizada.
            --------------------------------
            Se califica con un 3:
             - El al alumno pide ayuda o pistas sobre la pregunta que se le ha hecho.
                         
            - Esta fué la pregunta: {question}
            - Materia del curso: {right_answer}
            
            El formato de salida de tu respuesta debe ser solo el numero de la evaluacion y NADA MAS.
            """
            
            #print(f"Prompt de evaluación: {system_role}")

            print("Obteniendo is_correct...")
            is_correct = self.openai_chat(evaluation_role,user_answer)
            
            # Verificamos si is_correct es una cadena o un entero y lo convertimos a entero si es necesario
            if isinstance(is_correct, str):
                if is_correct.isdigit():
                    is_correct = int(is_correct)
                else:
                    print("is_correct es una cadena pero no contiene un número válido")
            else:
                # Si no es una cadena, asumimos que es un entero u otro tipo no válido
                try:
                    is_correct = int(is_correct)
                except ValueError:
                    print("is_correct no es un entero ni una cadena válida")

            # Comprobamos si is_correct es 0, 1 o 2
            if is_correct not in [0, 1, 2]:
                print("is_correct no es un 0, 1 o 2, intentando buscar un 1 en la cadena...")
                if "1" in str(is_correct):
                    is_correct = 1
                elif "0" in str(is_correct):
                    is_correct = 0
                elif "2" in str(is_correct):
                    is_correct = 2
            else:
                print("is_correct es un 0, 1 o 2")

            # Debugging output
            print(f"Valor final de is_correct: {is_correct} (tipo: {type(is_correct)})")
            return is_correct
        except Exception as e:
            print("Error al evaluar la respuesta del usuario", e)
            return None
        
    def _get_documentation(self):
        try:
            print("Obteniendo documentación...")    
            #leemos y cargamos el archivo de texto principito.txt
            with open(self.document_source, 'r',encoding='utf-8') as file:
                documentation = file.read()
                print("Documentación cargada con exito")
            return documentation
        except Exception as e:
            print("Error al obtener la documentación", e)
            raise Exception(f"Eror al obtener la documentación: {e}") 
                    
    def add_coaching_conversation(self,human_answer,coach_entry):
        try:
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                cursor.execute("""INSERT INTO coaching_assistant_conversation 
                               (id_current_question,human_answer,coach_entry)
                               VALUES (?,?,?)""",(self.id_current_question,human_answer,coach_entry))
                db.commit()
                print("Conversación agregada con exito")
        except Exception as e:
            print("Error al agregar una conversación al coaching", e)
            return None
    
    def get_right_answer(self,id_ast_coach_question):
        try:
            print(f"Obteniendo respuesta correcta para pregunta{id_ast_coach_question} ...")
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT 
                                    qa_question,
                                    qa_answer
                                  FROM 
                                    ast_coach_qa
                                  WHERE 
                                    id_ast_coach_qa = (SELECT id_ast_coach_qa FROM ast_coach_question WHERE id_ast_coach_question = ?)
                                    """,(id_ast_coach_question,))
                right_answer = cursor.fetchone()
                print(f"Respuesta correcta obtenida con exito: {right_answer}")
                return right_answer
        except Exception as e:
            print("Error al obtener la respuesta correcta", e)
            return None
        
    def get_comment_and_evaluation(self,id_ast_coach_question,user_answer):
        
        try:
            #Obtenemos la evaluacion
            is_correct = self.evaluate_answer(id_ast_coach_question,user_answer)
            #Obtenemos un comentario de la evaluacion
            coach_comment = self.get_coach_comment(id_ast_coach_question,is_correct,user_answer)
            
            final_evaluation = {
                'is_correct':is_correct,
                'answer_evaluation':coach_comment,
                'avatar':self.avatar
            }
            return final_evaluation
        except Exception as e:
            print("Error al evaluar la respuesta del usuario", e)
            return None
  
    def get_document_questions(self,number_of_questions):
        # Este metodo entrega instrucciones y pide al LLm que genere la cantidad de preguntas
        # definidas en el el asistente. Finalmente verifica que se hayan generado la cantidad de 
        # preguntas correctas y las retorna en un array.

        try:
            documentation = self._get_documentation()
            system_role =f"""
            {self.role}
            
            Debes devolver una lista SIN ENUMERAR de {number_of_questions} preguntas diferentes relacionadas a la 
            documentación que se te proporciona. Separa cada pregunta con un salto de línea. 
            Jamas entregues el formato de respuesta de otra forma.
            Documentacion para las preguntas:
            {documentation}       
            """
            user_content = ""
            print(f"Obteniendo {self.questions_per_chain} preguntas del coach...")
            coach_questions = self.openai_chat(system_role,user_content)
            
            #construimos un array con las preguntas
            questions_array = coach_questions.split("\n")
            
            #verificamos que el array tenga exactamente el número de preguntas que se requieren
            if len(questions_array) == self.questions_per_chain:
                print(f"Se obtuvieron exitosamente {self.questions_per_chain} preguntas")
                return {'result':True, 
                        'questions':questions_array}
            else:
                raise Exception(f"Se obtuvieron {len(questions_array)} preguntas, se esperaban {self.questions_per_chain}")
        except Exception as e:
            print("Error al obtener las preguntas del coach", e)
            raise Exception( f"Error al obtener las preguntas del coach {e}")

    def get_remained_questions(self,id_ast_coach_chain,id_ast_coach_qa):
        try:
            # Todas las preguntas posibles estan en la tabla ast_coach_qa y todas las preguntas hechas
            # en esta sesion estan en la tabla ast_coach_question. Por lo tanto, para obtener 
            # las preguntas que quedan por hacer, debemos hacer un left join entre ambas tablas
            # y obtener las preguntas que no estan en la tabla ast_coach_question
            print("Obteniendo preguntas restantes...")
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                cursor.execute("""
                               SELECT 
                                    id_ast_coach_qa,
                                    qa_question
                                  FROM 
                                    ast_coach_qa
                                  WHERE 
                                    id_ast_coach = ? AND
                                    id_ast_coach_qa NOT IN (SELECT id_ast_coach_qa FROM ast_coach_question WHERE id_ast_coach_chain = ?)
                                    """,(id_ast_coach_qa,id_ast_coach_chain))
                remained_questions = cursor.fetchall()
                print(f"Preguntas restantes obtenidas con exito:")
                #Si no quedan preguntas retornamos None,  de lo contrario armamos una lista donde cada
                #elemento es un diccionario con los campos recogiidos en el cursor
                if len(remained_questions) == 0:
                    return None
                else:
                    for i in range(len(remained_questions)):
                        remained_questions[i] = {
                            'id_ast_coach_qa' : remained_questions[i][0],
                            'question':remained_questions[i][1]
                        }
                return remained_questions
        except Exception as e:
            print("Error al obtener las preguntas restantes", e)
            return None

    def get_question_history(self):
        try:
            print("Obteniendo historial de preguntas...")
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT 
                                    human_answer,
                                    coach_entry
                                  FROM 
                                    coaching_assistant_conversation
                                  WHERE 
                                    id_current_question = ? AND
                                    question_status = 'evaluated'
                                    
                                    """,(self.id_current_question,))
                question_history = cursor.fetchall()
                #recorremos el cursor y armamos un string con el historial
                question_history = ""
                for row in cursor:
                    question_history += f"Alumno: {row[0]}\Coach: {row[1]}\n"
                
                return question_history
        except Exception as e:
            print("Error al obtener el historial de preguntas", e)
            return None

    def get_current_question(self,id_ast_coach_chain):
        try:
            print(f"Obteniendo pregunta actual de la chain: {id_ast_coach_chain}...")
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT 
                                    id_ast_coach_question,
                                    question
                                  FROM 
                                    ast_coach_question
                                  WHERE 
                                    id_ast_coach_chain = ? AND
                                    question_status = 'delivered'
                                    """,(id_ast_coach_chain,))
                current_question = cursor.fetchone()
                output = {
                        'id_ast_coach_question':current_question[0],
                        'question':current_question[1]}
                return output
        except Exception as e:
            print("Error al obtener la pregunta ", e)
            return None
        
    def get_next_question(self,id_ast_coach_chain):
        try:
            print(f"Obteniendo siguiente pregunta de la chain: {id_ast_coach_chain}...")
            #Obtiene el set de preguntas no hechas.
            
            remained_questions = self.get_remained_questions(id_ast_coach_chain,self.id_ast_coach)
            
            #Con verificamos que hayan respuestas restantes, si las hay elegimos un id al azar
            #y obtenemos los datos del diccionario almacenado en la posición correspondiente
            print("Aun quedan preguntas por hacer, eligiendo una al azar...")
            if remained_questions is not None:
                print(f"Aun quedan {len(remained_questions)} preguntas por hacer. Obteniendo una al azar...")
                random_question = random.choice(remained_questions)
                output = {
                        'id_ast_coach_qa':random_question['id_ast_coach_qa'],
                        'question':random_question['question'],
                        'avatar':self.avatar,
                        'goodbye':False}
                print(f"Siguiente pregunta obtenida de forma aleatoria con exito: {output}")
            else:
                print("No quedan preguntas por hacer, devolvemos el mensaje de despedida del asistente...")
                goodbye_request="Genera un mensaje de despedida porque no quedan mas preguntas por hacer. Animalo por haber llegado hasta el final"
                goodbye_role="Eres un profesor que ha terminado de evaluar a un alumno."
                goodbye_messege=self.openai_chat(goodbye_role,goodbye_request)

                output = {
                        'id_ast_coach_qa':0,
                        'question':goodbye_messege,
                        'avatar':self.avatar,
                        'goodbye':True}
            
            return output    
        except Exception as e:
            print("Error al obtener la siguiente pregunta", e)
            return None

    def get_answers(self,questions_array):
        
        #recibe las preguntas generadas y devuelve un diccionario con las preguntas y las respuestas
        try:
            print("Obteniendo respuestas a las preguntas...")
            QA_array = []
            documentation = self._get_documentation()
            i=0
            for question in questions_array:
                prompt = f"""
                Eres un asistente que responde preguntas basadas en un texto que se te proporciona.
                Debes dar la respuesta mas detallada y con mayor contexto posible.
                ------------------------------
                Texto para obtener respuesta:
                {documentation}
                 ------------------------------
                Respuesta:               
                """
                
                answer = self.openai_chat(prompt,question)
                QA_array.append({"question": question, "answer": answer})
            print(f"Respuestas obtenidas con exito: {QA_array}")
            return QA_array
        except Exception as e:
            print("Error al obtener las respuestas correctas", e)
            return None

    def evaluate_if_next_question(self):
        #dejamos que el asistente decida si segun el numero de respuestas se debe ir a la siguiente 
        # pregunta o continuar discutiendo la actual
        
        print("Evaluando si se debe ir a la siguiente pregunta...")
        prompt=f"""
        {self.role}
        
        Tienes la siguiente tarea: El usuario ha respondido erroneamente a la pregunta actual.
        Segun este historial debes decidir si el usuario queire pasar a la sigueinte pregunta o 
        continuar discutiendo la actual. responde solamente con la palabra "siguiente" o "continuar"
        
        Historial:
        {self.get_question_history()}       
        
        """        
        respuesta = self.openai_chat(prompt,"")
        print(f"La respuesta del asistente fue: {respuesta}")
        return respuesta

    def save_evaluation(self,id_ast_coach_question,is_correct):

        try:
            print(f"Guardando evaluación para la pregunta {id_ast_coach_question} ...")
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE ast_coach_question
                                SET question_status = 'evaluated', is_correct = ?
                                WHERE id_ast_coach_question = ?""",(is_correct,id_ast_coach_question))
                db.commit()
                print(f"Evaluación guardada con exito con un {is_correct}")
        except Exception as e:
            print("Error al guardar la evaluación", e)
            return None

        

                                            
    def openai_chat(self,role,content):
        try:
            print("Conversando con openai...")
            client = OpenAI()
            respuesta = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": content}
                ],
                temperature=self.temperature
            )
            print(respuesta.choices[0].message)
            return respuesta.choices[0].message.content
        except Exception as e:
            print("Error intentando conversar con openai", e)
            return None
    

#id_ast_coach_chain=None
#id_question=None
#respuesta="""el  titulo de anticuerpos fue mas alto en estos individuos  en comparacion 
#individuos solo vacunados."""

#coaching = assistant_coach(3)
#coaching._set_initial_QA(3)    
#
#if id_ast_coach_chain is None:
#    begin_coaching = coaching.begin_coaching_chain()
#else:
#    coach_evaluation = coaching.get_comment_and_evaluation(id_question,respuesta)
 


#    if coach_evaluation['is_correct'] in [0,1]:
#        coaching.save_evaluation(id_question,coach_evaluation['is_correct'])
#        next_question = coaching.get_next_question(id_ast_coach_chain)
#        if next_question is None:
#            #pedimos a openai que de un mensaje de despedida porque no hay mas preguntas
#            goodbye_request="Genera un mensaje de despedida porque no quedan mas preguntas por hacer. Animalo por haber llegado hasta el final"
#            goodbye_role="Eres un profesor que ha terminado de evaluar a un alumno."
#            goodbye_messege=coaching.openai_chat(goodbye_role,goodbye_request)
#            print(goodbye_messege)
#        else:
#            question=next_question['question']
#            id_ast_coach_qa = next_question['id_ast_coach_qa']
#            coaching._add_new_question(id_ast_coach_chain,id_ast_coach_qa,question)



