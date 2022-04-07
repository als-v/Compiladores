import pandas as pd
data = []

with open('saida.txt', 'r') as file:
    for idx, line in enumerate(file):
        
        formatedLine = line.replace('LexToken(', '')
        formatedData = formatedLine.split(',')

        if formatedLine[0:7] == 'VIRGULA':
            data.append([formatedData[0], ',', formatedData[len(formatedData)-2], formatedData[len(formatedData)-1].replace(')\n', '').replace(')', '')])
        else:
            data.append([formatedData[0], formatedData[1].replace("'", ''),formatedData[2], formatedData[3].replace(')\n', '').replace(')', '')])

dataPD = pd.DataFrame(data, columns = ['token', 'valor', 'linha', 'coluna'])
print(dataPD)