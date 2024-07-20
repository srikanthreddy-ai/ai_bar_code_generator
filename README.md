# ai_bar_code_generator
convert the list of barcode into defined barcode in A4 paper

1. Install dependencies listed in requirements.txt:
   pip install -r requirements.txt
2. Execute run.py:
   python run.py
3. Access the API endpoints (e.g., method: POST http://localhost:5000/api/qr_code_generator) to interact with the API.

4. Ex: curl --location 'http://127.0.0.1:5000/api/qr_code_generator' \
--form 'pdf_file=@"/D:/FreeLAnce/input3.pdf"' \
--form 'pageSize="[ 210, 200 ]"' \
--form 'billWidth="38"' \
--form 'billHeight="20"' \
--form 'billRows="8"' \
--form 'billColumns="4"'
