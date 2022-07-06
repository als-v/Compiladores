import re

# abrir o arquivo
arq = open('emails.txt', 'r')

# lista com os e-mails
emails = []

# para cada linha do arquivo, a expressão irá pegar apenas o e-mail
for email in arq:
       emails.append(re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', email))

# abro um arquivo de resultados
arq = open('result.txt', 'w')

# printo os e-mails formatados
for email in emails:
    email = str(email).split("'")[1]
    print(email)