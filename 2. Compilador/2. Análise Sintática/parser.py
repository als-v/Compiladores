import pandas as pd
table = []

with open('saida.txt', 'r') as file:
    for idx, line in enumerate(file):
        
        formatedLine = line.replace('LexToken(', '')
        formatedData = formatedLine.split(',')
        data = []

        if formatedLine[0:7] == 'VIRGULA':
            data.append([formatedData[0], ',', formatedData[len(formatedData)-2] formatedData[len(formatedData)-1].replace(')', '')])
        else:
            formatedData[1] = formatedData[1].replace("'", '')
            formatedData[3] = formatedData[3].replace(')\n', '')
            data.append(formatedData)
