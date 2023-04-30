import io
import re
import pytesseract as pt
import pdf2image
from docx import Document

from Model.Exceptions import FileConvertError

class FileConverter:
    @staticmethod
    def from_pdf(file: bytes) -> str:
        languages = ['eng', 'rus']
        text = ""

        try:
            pages = pdf2image.convert_from_bytes(file, dpi=200)
            for i in range(len(pages)):
                text += pt.image_to_string(pages[i], lang='+'.join(languages))

            text = re.sub(r'\b\w\b', '', text)
            text = re.sub(r'[^\w\s]', '', text)
        except:
            raise FileConvertError("pdf")

        return text
    
    @staticmethod
    def from_docx(file: bytes) -> str:
        try:
            doc_bytes = io.BytesIO(file)
            doc = Document(doc_bytes)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
        except:
            raise FileConvertError("docx")

        full_text = '\n'.join(text)
        return full_text
    
    @staticmethod
    def from_txt(file: bytes) -> str:
        return file.decode("utf-8")


'''
with open("das.docx", "rb") as file:
    bytes = file.read()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(bytes)
        subprocess.run(['start', '', f.name], shell=True)
'''