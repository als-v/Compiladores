import pandas as pd

def searchDataLine(data, line):
    return data.loc[data['linha'] == line]

def searchTokenLineData(data, line, token):
    lineData = searchDataLine(data, line)
    lineDataToken = lineData.loc[lineData['token'] == token]
   
    return len(lineDataToken) > 0
    
data = []

with open('saida.txt', 'r') as file:
    for idx, line in enumerate(file):
        
        formatedLine = line.replace('LexToken(', '')
        formatedData = formatedLine.split(',')

        if formatedLine[0:7] == 'VIRGULA':
            data.append([formatedData[0], ',', int(formatedData[len(formatedData)-2]), int(formatedData[len(formatedData)-1].replace(')\n', '').replace(')', ''))])
        else:
            data.append([formatedData[0], formatedData[1].replace("'", ''), int(formatedData[2]), int(formatedData[3].replace(')\n', '').replace(')', ''))])

dataPD = pd.DataFrame(data, columns = ['token', 'valor', 'linha', 'coluna'])

lineStart = dataPD['linha'].min()
lineEnd = dataPD['linha'].max()
print(lineStart, lineEnd)

for line in range(lineStart, lineEnd+1):
    dataLine = searchDataLine(dataPD, line)
    # print(dataLine, '\n\n')

    if len(dataLine) > 0:

        if ((searchTokenLineData(dataPD, line, 'ABRE_PARENTESE')) and (not searchTokenLineData(dataPD, line, 'ATRIBUICAO'))):
            lineIDs = dataLine.loc[dataLine['token'] == 'ID']
       
            if len(lineIDs) != 0:

                if len(lineIDs) > 1:
                    function = lineIDs.iloc[0]
                else:
                    function = lineIDs

                print(function, '\n', lineIDs, '\n\n')
                # print('É uma função:', function['valor'])