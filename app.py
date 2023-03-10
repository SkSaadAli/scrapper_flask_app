import subprocess
import time
from flask import Flask, Response, render_template_string,render_template,request,redirect,send_file,after_this_request
import os
import uuid

app = Flask(__name__)


filename = str(uuid.uuid4()) + '.csv'
dic={1:False,2:False,3:False}
max_retries=3
max_sites=40
def generate_output():
    cmd = ["python","-u", "/final_test.py", str(dic), str(max_retries),str(max_sites),filename]
    yield str.encode('--Connection Established--\n')
    if dic[1] or dic[2] or dic[3]:
        yield str.encode('--Connection Established--\n')
        try:
            process = subprocess.Popen(
            
                cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                yield line + b'\n'
                time.sleep(0.08)
        except Exception as error:
            yield str.encode(f'{error}')
    else:
        yield 'No Site Selected You Shouldn\'t be here\n'
    
    


@app.route('/download_output/<filename>')
def download_output(filename):
    # Call the generate_output() function here
    # ...
    # After the script finishes running:
    # df.to_csv('output.csv', index=False)
    
    # Return a response object with the CSV file attachment
    file_path = 'scrapper/' + filename
    # @after_this_request
    # def remove_file(response):
    #     try:
    #         os.remove(file_path)
    #     except Exception as error:
    #         app.logger.error("Error deleting file from disk: %s", error)
    #     return response
    # remove_file()
    return send_file(filename,
                     mimetype='text/csv',
                     attachment_filename='output.csv',
                     as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        global dic,max_sites,max_retries

        dic[1]=bool(request.form.get('checkboxOne'))
        dic[2]=bool(request.form.get('checkboxTwo'))
        dic[3]=bool(request.form.get('checkboxThree'))

        max_retries=request.form.get('retry')
        max_sites= request.form.get('max_site')

        return redirect('/logs')
        
    return render_template('index.html')

@app.route('/logs')
def log():
    return render_template('log.html',filename=filename)


@app.route('/output')
def output():

    return Response(generate_output(), mimetype='text/html')

if __name__ == '__main__':
    app.run()