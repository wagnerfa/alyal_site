import smtplib
from email.mime.text import MIMEText

msg = MIMEText('This is a test email.')
msg['Subject'] = 'Test Email'
msg['From'] = 'contato@alyal.com.br'
msg['To'] = 'wagnerandrade.dev@gmail.com'
email = 'wagnerandrade.dev@gmail.com'

with smtplib.SMTP('email-ssl.com.br', 587) as server:
    server.starttls()
    server.login('contato@alyal.com.br', 'Castiell@750')
    server.sendmail('contato@alyal.com.br', email, msg.as_string())

