import matplotlib.pyplot as plt
import pandas as pd
import mpld3
import os
import math

from flask import Flask,request
from flask import render_template
from flask import send_file


pd.set_option('display.max_columns', None)

app = Flask(__name__)
hostname = "localhost"
port = "3000"

@app.route('/', methods=['GET'])
def listFiles():
    
    data = {}
    data['baseUrl'] = "http://" + hostname + ":" + port + "/showData?filename="
    nodes = os.listdir('./static/Data')
    
    data['nodes'] = {}
    for dir in nodes:
        files = os.listdir('./static/Data/'+dir)
        csvs=[]
        for fileName in files:
            if fileName.endswith(".csv"):
                csvs.append(fileName)
        data['nodes'].update({dir:csvs})
        data['nodes']= dict(sorted(data['nodes'].items()))
    return render_template('showFiles.html', data=data)

@app.route('/getcsv', methods=['POST'])
def plot_csv():
    path = './static/Data/' + request.form['filepath']
    # return path
    return send_file(path,
                     mimetype='text/csv',
                     attachment_filename='data.csv',
                     as_attachment=True)


def calc(value):
    a = 0
    if (value > 8191):
        a = (value - 16384) / (4096 / 9.80665)
    else:
        a = (value) / (4096 / 9.80665)
    return (math.floor(a * 1000)) / 1000

def avg(list1):
    if len(list1)>0:
        return sum(list1)/len(list1)
    else:
        return 0

def plotGraph(filepath):
    # Load data
    data = pd.read_csv('./static/Data/' + filepath, header=None)
    data.columns = ['date', 'time', 'x', 'y', 'z']

    #Creating output data file
    dataCor = pd.DataFrame()
    dataCor['Time'] = data['time']
    dataCor['AccX'] = data['x'].apply(calc)
    dataCor['AccY'] = data['y'].apply(calc)
    dataCor['AccZ'] = data['z'].apply(calc)
    

    accx = dataCor.plot(x ='Time', y='AccX', kind = 'line', figsize=(10,4), title='Acceleration Data - Local X-direction',lw=0.5, grid=True, color='Red',label="Acc X - m/s^2").get_figure()
    accy = dataCor.plot(x ='Time', y='AccY', kind = 'line', figsize=(10,4), title='Acceleration Data - Local Y-direction',lw=0.5, grid=True, color='Green',label="Acc Y - m/s^2").get_figure()
    accz = dataCor.plot(x ='Time', y='AccZ', kind = 'line', figsize=(10,4), title='Acceleration Data - Local Z-direction',lw=0.5, grid=True, color='Blue',label="Acc Z - m/s^2").get_figure()

    #DataSummary
    threesecx=[]
    threesecy=[]
    threesecz=[]
    tensecx=[]
    tensecy=[]
    tensecz=[]
    onesecx=[]
    onesecy=[]
    onesecz=[]
    count=len(dataCor)
    xval=0
    yval=0
    zval=0
    xl=[]
    yl=[]
    zl=[]

    xl = dataCor['AccX']
    yl = dataCor['AccY']
    zl = dataCor['AccZ']

    if(count>0):
        xlavg=sum(xl)/count
        ylavg=sum(yl)/count
        zlavg=sum(zl)/count
    else:
        xlavg=0
        ylavg=0
        zlavg=0

    xl=list(map(lambda x:(x)**2,xl))
    yl=list(map(lambda y:(y)**2,yl))
    zl=list(map(lambda z:(z)**2,zl))

    if count>100:

        for i in range(count//100):
            tempx=xl[i:(i+1)*100]
            tempy=yl[i:(i+1)*100]
            tempz=zl[i:(i+1)*100]

            onesecx.append((sum(tempx)/len(tempx))**0.5)
            onesecy.append((sum(tempy)/len(tempy))**0.5)
            onesecz.append((sum(tempz)/len(tempz))**0.5)

    if count>300:

        for i in range(count//300):
            tempx=xl[i:(i+1)*300]
            tempy=yl[i:(i+1)*300]
            tempz=zl[i:(i+1)*300]

            threesecx.append((sum(tempx)/len(tempx))**0.5)
            threesecy.append((sum(tempy)/len(tempy))**0.5)
            threesecz.append((sum(tempz)/len(tempz))**0.5)

    if count>1000:

        for i in range(count//1000):
            tempx=xl[i:(i+1)*1000]
            tempy=yl[i:(i+1)*1000]
            tempz=zl[i:(i+1)*1000]

            tensecx.append((sum(tempx)/len(tempx))**0.5)
            tensecy.append((sum(tempy)/len(tempy))**0.5)
            tensecz.append((sum(tempz)/len(tempz))**0.5)


    xval=sum(xl)
    yval=sum(yl)
    zval=sum(zl)
    
    if(count>0):
        xval/=count
        yval/=count
        zval/=count

    xval=xval**0.5
    yval=yval**0.5
    zval=zval**0.5

    Headers=["Start Time","Avg_x(1 sec)","Avg_y(1 sec)","Avg_z(1 sec)","Avg_x(3 sec)","Avg_y(3 sec)","Avg_z(3 sec)","Avg_x(10 sec)","Avg_y(10 sec)","Avg_z(10 sec)","Avg_x","Avg_y","Avg_z"]
    Values=[dataCor.iloc[0:1,0:1],round(avg(onesecx),4),round(avg(onesecy),4),round(avg(onesecz),4),round(avg(threesecx),4),round(avg(threesecy),4),round(avg(threesecz),4),round(avg(tensecx),4),round(avg(tensecy),4),round(avg(tensecz),4),round(xval,4),round(yval,4),round(zval,4)]        

    html0 = "<form method='post' action='http://" + hostname + ":" + port + "/getcsv'>"
    html0 += """
            <input type="hidden" name="filepath" value=""" + filepath + """>
            <input type="submit" value="Download Data File" />
            </form>"""

            
    html1 = mpld3.fig_to_html(accx)
    html2 = mpld3.fig_to_html(accy)
    html3 = mpld3.fig_to_html(accz)

    header_html = "<tr>"
    for title in Headers:
        header_html += "<th style='border: 1px solid black;'>" + str(title) + "</th>"
    header_html += "</tr>"

    data_html = "<tr>"
    for value in Values:
        data_html += "<td style='border: 1px solid black;'>" + str(value) + "</td>"
    data_html += "</tr>"

    table_html = "<table style='border: 1px solid black;' cellspacing='2px;'>"
    table_html += header_html + data_html
    table_html += "</table>"


    f = open("./templates/plot.html", "w")
    f.write(html0 + html1 + html2 + html3 + table_html)
    f.close()
    return

@app.route('/showData', methods=['GET'])
def plot():
    filename = request.args.get('filename')
    plotGraph(filename)
    return render_template('plot.html')
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000,debug=True)