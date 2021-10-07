import re

# abrir o arquivo
arq = open('e-mails.txt', 'r')

# lista com os e-mails
emails = []

# para cada linha do arquivo, a expressão irá pegar epans o e-mail
for email in arq:
       emails.append(re.findall(r'(?<=<)(.*?)(?=>)', email))

# abro um arquivo de resultados
arq = open('result.txt', 'w')

# printo os e-mails formatados
for email in emails:
    email = str(email).split("'")[1]
    print(email)