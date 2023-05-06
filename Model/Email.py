from email import policy
from email.header import Header
from email.message import Message
from email.parser import BytesParser
from email.utils import parseaddr
from bs4 import BeautifulSoup
from dateutil import parser
from pathlib import Path
import os

from Model.Mail import *
from Model.FileConverter import *
from Model.Exceptions import GetFilesError, ParseBodyError, ParseDateError, ParseAddressError, ParseHTMLError

class Email:
    def __init__(self, path: Path) -> None:
        try:
            eml_files = list(path.glob('*.eml'))
        except PermissionError:
            raise Exception("Нет прав доступа для чтения файлов в директории")

        if len(eml_files) == 0:
            raise Exception("В директории не найдены файлы с расширением .eml")
        
        self.msgs = [] 
        for file in eml_files:
            try:
                with open(file, 'rb') as fp:
                    name = os.path.basename(fp.name)
                    try:
                        msg = BytesParser(policy=policy.default).parse(fp)
                    except:
                        raise Exception("Ошибка при обработке файла: " + name)
                    self.msgs.append((name, msg))
            except:
                raise Exception("Ошибка при чтении файла")
        
    
    def get_mails(self):
        for name, msg in self.msgs:
            try:
                mail = Mail(
                        id=msg.get('Message-ID'),
                        in_reply_to=msg.get('In-Reply-To'),
                        sender=self.__parse_address(msg.get('From'))[0],
                        recievers=self.__get_all_recievers(msg),
                        subject=msg.get('Subject'),
                        body=self.__parse_body(msg),
                        date=self.__parse_date(msg.get('Date')),
                        priority=msg.get('X-Priority'),
                        files=self.__get_files(msg)
                    )
                yield (name, mail)

            except (GetFilesError, ParseBodyError, ParseAddressError, ParseDateError) as error:
                yield Exception(error)
            except Exception:
                yield Exception("Ошибка при получении данных")
            
    def __get_files(self, msg: Message) -> list[dict]:
        attachments = []
        for part in msg.walk():
            try:
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    content_type = part.get_content_type()
                    content = part.get_payload(decode=True)
                    if content_type == 'text/plain' and filename.endswith('.txt'):
                        text = FileConverter.from_txt(content)
                    elif content_type == 'application/pdf' and filename.endswith('.pdf'):
                        text = FileConverter.from_pdf(content)
                    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' and filename.endswith('.docx'):
                        text = FileConverter.from_docx(content)
                    else:
                        continue
                    attachments.append({"id": None, "filename": filename, "text": text, "bytes": content})
            except FileConvertError as error:
                raise GetFilesError(error)
            except UnicodeDecodeError:
                raise GetFilesError("Ошибка при декодировании вложения")
            except Exception:
                raise GetFilesError("Ошибка при получении вложения")

        return attachments
                
    def __parse_address(self, address: Header) -> list[dict]:
        if address is None:
            return [{"name": None, "email": None}]
        try:
            address_list = list(map(parseaddr, address.split(',')))
            return [{"name": address[0], "email": address[1].lower()} for address in address_list]
        except Exception:
            raise ParseAddressError("Ошибка при получении адреса почты")

    def __parse_date(self, date: Header) -> str:
        try:
            date = parser.parse(date)
            return str(date.strftime("%Y-%m-%d %H:%M:%S %Z"))
        except ValueError:
            raise ParseDateError("Ошибка при получении времени отправки: неверный формат")
        except Exception:
            raise ParseDateError("Ошибка при получении времени отправки")

    def __parse_body(self, msg: Message) -> str:
        try:
            body = msg.get_body(preferencelist=('plain'))
            if body is None:
                body = msg.get_body(preferencelist=('html'))
                if body is None:
                    return ""
                return self.__parse_html(body.get_content())
            else:
                return '\n'.join([line for line in body.get_content().split('\n') if not line.startswith('>')])
        except ParseHTMLError as error:
            raise ParseBodyError(error)
        except Exception:
            raise ParseBodyError("Ошибка при получении текста")
    
    def __parse_html(self, html: str) -> str:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            if soup.find():
                for script in soup(["script", "style"]):
                    script.extract() 
                return soup.get_text(separator='\n', strip=True)
            else:
                return ""
        except (TypeError, ValueError):
            raise ParseHTMLError("Ошибка при парсинге html: некорректный формат")
        except Exception:
            raise ParseHTMLError("Ошибка при парсинге html")
    
    def __get_all_recievers(self, msg: Message) -> list[dict]:
        recievers = []
        for reciever in self.__parse_address(msg.get("To")):
            if reciever["name"] is not None or reciever["email"] is not None:
                recievers.append({"name": reciever["name"], "email": reciever["email"], "type": "standart"})
        
        for reciever in self.__parse_address(msg.get("Cc")):
            if reciever["name"] is not None or reciever["email"] is not None:
                recievers.append({"name": reciever["name"], "email": reciever["email"], "type": "cc"})
        
        for reciever in self.__parse_address(msg.get("Bcc")):
            if reciever["name"] is not None or reciever["email"] is not None:
                recievers.append({"name": reciever["name"], "email": reciever["email"], "type": "bcc"})
        
        return recievers