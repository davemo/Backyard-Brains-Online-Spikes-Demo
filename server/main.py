import wave, sys, struct, json, os

from flask import Flask, redirect, url_for, render_template
from werkzeug import secure_filename

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['wav','wave'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def main_page():
    return redirect('/analyze.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    from jinja2 import FileSystemLoader
    app.jinja_loader = FileSystemLoader(
        os.path.join(os.path.dirname(__file__), '..'))


    soundfile = request.files['spikes_file']
    if soundfile and allowed_file(soundfile.filename):
        filename = secure_filename(soundfile.filename)
        soundfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('analyze.html',
                               sampleData= provide_json_of_wav(filename))
    else:
        return "Invalid file"

def provide_json_of_wav(filename):
    w = wave.open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb')
    if w:
        pcm_list = []
        for i in range(w.getnframes()):
            frame = w.readframes(1)
            pcm_list.append(struct.unpack("h", frame)[0])
        return json.dumps(pcm_list)
    else:
        return "Oops!, couldn't read" + \
                os.path.join(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    if app.config['DEBUG']:
        from werkzeug import SharedDataMiddleware
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/': os.path.join(os.path.dirname(__file__), '..')
            })
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
