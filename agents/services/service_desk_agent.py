from dotenv import load_dotenv
from chat.services import chat_tools


class ServiceDeskAgent:
    def __init__(self,ticket_subject, ticket_body):
        self.ticket_subject = ticket_subject
        self.ticket_body = ticket_body
        pass
    def __str__(self):
        return "ServiceDeskAgent"
    
    #Acording ticket_subject and ticket_body, the agent returns the sentiment of the ticket.
    def GetTicketSentiment(self):
        pass
    
    def GetTicketCategory(self,categories):
        pass    
    