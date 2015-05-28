from flask import Flask, abort, send_from_directory, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.Text)
    length = db.Column(db.Integer)

class NoticeDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(db.Integer, db.ForeignKey('notice.id'))
    notice = db.relationship('Notice',
                    backref=db.backref('details', uselist=False))
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    buying_org = db.Column(db.Text)
    language_id = db.Column(db.Integer)

class NoticeDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(db.Integer, db.ForeignKey('notice.id'))
    notice = db.relationship('Notice',
                    backref=db.backref('documents', lazy='dynamic'))
    mimetype = db.Column(db.Text)
    file_id = db.Column(db.String(36))
    filename = db.Column(db.Text)
    title = db.Column(db.Text)

@app.route('/')
def front_page():
    return render_template('front.html')

@app.route('/contracts/')
def contracts():
    contracts = Notice.query.all()
    return render_template('contracts.html', contracts=contracts)

@app.route('/contract/<int:notice_id>/')
def contract(notice_id):
    contract = Notice.query.filter_by(id=notice_id).first_or_404()
    return render_template('contract.html', contract=contract)

@app.route('/search/')
def search():
    query = request.args.get('q')
    contracts = Notice.query.all()
    return render_template('contracts.html',
                           contracts=contracts,
                           query=query)

@app.route('/download/<int:notice_id>/<file_id>')
def download(notice_id, file_id):
    notice_id = str(notice_id)

    download_file = NoticeDocument.query.filter_by(file_id=file_id).first_or_404()
    
    directory = os.path.abspath(os.path.join(app.instance_path, 'documents', notice_id))
    filename = download_file.filename
    mimetype = download_file.mimetype

    return send_from_directory(directory,
                               file_id,
                               mimetype=mimetype,
                               as_attachment=True,
                               attachment_filename=filename)

if __name__ == '__main__':
    app.debug = True
    app.run()
