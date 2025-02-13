from fastapi import FastAPI
from pydantic import BaseModel
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

app = FastAPI()

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

class EmailRequest(BaseModel):
    destinatario: str
    assunto: str
    mensagem: str

def obter_credenciais():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

@app.post("/enviar_email")
def enviar_email(request: EmailRequest):
    creds = obter_credenciais()
    service = build("gmail", "v1", credentials=creds)

    email_msg = f"Subject: {request.assunto}\nTo: {request.destinatario}\n\n{request.mensagem}"
    raw_msg = base64.urlsafe_b64encode(email_msg.encode()).decode()

    try:
        service.users().messages().send(
            userId="me",
            body={"raw": raw_msg}
        ).execute()
        return {"status": "sucesso", "mensagem": "E-mail enviado com sucesso!"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}