from flask import jsonify, request, render_template, send_file
from app import app
from app.models import Book
from app.controllers import create_qr_codes
import os

books = [
    Book(id=1, title="Book 1", author="Author 1"),
    Book(id=2, title="Book 2", author="Author 2"),
]


# @app.route('/')
# # def upload_form():
# #     return render_template('upload_form.html')

@app.route('/api/qr_code_generator', methods=['POST'])
def get_qr_codes():
    if 'pdf_file' not in request.files:
        return 'No file part in the request', 400
    pagesize = request.form.get('pageSize')
    billwidth = request.form.get('billWidth')
    billheight = request.form.get('billHeight')
    billrows = request.form.get('billRows')
    billcolumns = request.form.get('billColumns')
    file = request.files['pdf_file']
    if file.filename == '':
        return 'No selected file', 400
    if file and file.filename.endswith('.pdf'):
        file_path = create_qr_codes(file, pagesize, billwidth, billheight, billrows, billcolumns)
        return send_file(f"{os.getcwd()}/{file_path}", as_attachment=True)

@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify([book.to_dict() for book in books])

# Define more routes as needed
