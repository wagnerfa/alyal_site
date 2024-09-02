import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
import os


def envio_email(email, titulo, nome, treinamento):
    msg = EmailMessage()
    msg['From'] = 'contato@alyal.com.br'
    msg['To'] = email
    msg['Subject'] = titulo

    # Adicionando a imagem de assinatura
    image_cid = make_msgid(domain='example.com')
    assinatura_path = os.path.join(os.path.dirname(__file__), 'static', 'assinaturaWagnerAlyal.png')

    with open(assinatura_path, 'rb') as img:
        img_data = img.read()
        img_name = 'assinatura.png'

    # Construindo a mensagem HTML com a imagem
    mensagem_html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Confirmação de Pré-inscrição</title>
    </head>
    <body>
        <p>Parabéns <strong>{nome}</strong>!</p>
        <p>Sua pré-inscrição em nosso treinamento <strong>{treinamento}</strong> foi realizada com sucesso.</p>
        <p>Estamos entusiasmados com sua decisão de aprimorar seus conhecimentos e habilidades nessa área inovadora. Nossa equipe entrará em contato com você o mais breve possível para confirmar seus dados e finalizar sua inscrição</p>
        <p>Seja bem-vindo à nossa comunidade de aprendizagem! Estamos ansiosos para ajudá-lo a alcançar seus objetivos</p>
        <br>
        <br>

        <img src="cid:{image_cid[1:-1]}" alt="Assinatura-WA">
    </body>
    </html>
    """

    # Adicionando o corpo da mensagem como 'alternative'
    msg.add_alternative(mensagem_html, subtype='html')

    # Adicionando a imagem como 'related'
    msg.get_payload()[0].add_related(img_data, maintype='image', subtype='png', cid=image_cid, filename=img_name)

    # Enviando o email
    with smtplib.SMTP('email-ssl.com.br', 587) as server:
        server.starttls()
        server.login('contato@alyal.com.br', 'Castiell@750')
        server.send_message(msg)


