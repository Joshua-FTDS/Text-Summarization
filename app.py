import os
import io
import openai
import tempfile
import PyPDF2
import streamlit as st
import pytesseract
from fpdf import FPDF
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from openai import OpenAI
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

# os.environ["OPENAI_API_KEY"] =
# client = OpenAI()

os.environ["OPENAI_API_KEY"] = os.getenv("text_api")
client = OpenAI()

def ringkasan(teks):
    messages = [
        {"role": "user", "content": f"Ringkas teks berikut:\n\n{teks}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message

def simpan_pdf(ringkasan_teks, filename="ringkasan.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, ringkasan_teks)
    c.save()

def baca_file_pdf(uploaded_file):
    # Simpan file sementara
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    reader = PyPDF2.PdfReader(temp_file_path)
    teks = ""

    for i, page in enumerate(reader.pages):
        # Mengambil teks dari halaman
        page_teks = page.extract_text()
        if page_teks:
            teks += page_teks + "\n"
        else:
            # Jika tidak ada teks, konversi halaman menjadi gambar
            img = convert_from_path(temp_file_path, first_page=i + 1, last_page=i + 1)[0]
            # Atur konfigurasi Tesseract
            custom_config = r'--oem 3 --psm 6'
            teks += pytesseract.image_to_string(img, config=custom_config) + "\n"

    return teks

def main():
    st.title("Alat Ringkas Teks")
    
    uploaded_file = st.file_uploader("Upload file PDF", type="pdf")
    
    if uploaded_file is not None:
        teks = baca_file_pdf(uploaded_file)
        
        if teks:
            st.subheader("Teks yang diambil dari file:")
            st.write(teks)
            
            if st.button("Ringkas"):
                hasil_ringkasan = ringkasan(teks)
                st.subheader("Ringkasan:")
                st.write(hasil_ringkasan)

                # Simpan ringkasan ke file PDF
                simpan_pdf(hasil_ringkasan)
                st.success("Ringkasan disimpan dalam file: ringkasan.pdf")
        else:
            st.warning("Tidak ada teks yang dapat diekstrak dari file.")
    
if __name__ == "__main__":
    main()