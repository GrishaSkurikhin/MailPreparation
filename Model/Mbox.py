from dateutil import parser
from bs4 import BeautifulSoup
import email
import mailbox
import re
import chardet

from Data import Mail


class Mbox(mailbox.mbox):
    def __init__(self, filename, factory=None, create=True) -> None:
        super().__init__(filename, factory=factory, create=create)
        mails = [] # list[Mail]
        a = self.items()[0][1]
        decoded_header = email.header.decode_header(a.get("Subject"))[0][0]
        if isinstance(decoded_header, bytes):
            detected_encoding = chardet.detect(decoded_header)['encoding']
            decoded_header = decoded_header.decode(detected_encoding)
            print(detected_encoding)
            print(decoded_header)
        #self.decode_header(self[0].get("Subject"))

    def decode_header(self, header: str):
        header = email.header.decode_header(header)[0]
        header = header[0]
        if isinstance(header, bytes):
            header = header.decode('utf-8', errors='replace')
        print('header:', header)

mbox = Mbox("tmp.mbox")


'''
class Mbox():
    def __init__(self, mbox_path: StrPath) -> None:
        try:
            mbox = mailbox.mbox(mbox_path)
        except:
            raise Exception("Ошибка при создании объекта Mbox")
        mbox.
        self.id_map = {}
        for message in mbox:
            self.id_map[message['Message-ID']] = message
        self.mails_count = len(self.id_map)

    def get_data(self):
        for id, message in self.id_map.items():
            try:
                To = self.GetAdresses(message, "To")
                Cc = self.GetAdresses(message, "Cc")
                Bcc = self.GetAdresses(message, "Bcc")
                Sender = self.GetAdresses(message, "From")[0]
                Subject = self.DecodeHeader(message['Subject'])
                Body = self.GetBody(message)
                Recievers = [(reciever[0], reciever[1], "standart") for reciever in To]
                Recievers += [(reciever[0], reciever[1], "copy") for reciever in Cc]
                Recievers += [(reciever[0], reciever[1], "blind copy") for reciever in Bcc]
                Date = self.GetDate(message)
                In_reply_to = message['In-Reply-To']
                Priority = message.get('X-Priority')
                yield [id, Recievers, Sender, Subject, Date, Priority, Body, In_reply_to]
            except Exception as error:
                yield Exception(error)

    def DecodeHeader(self, header):
        try:
            decoded_header = email.header.decode_header(header)[0][0]
            if isinstance(decoded_header, bytes):
                detected_encoding = chardet.detect(decoded_header)['encoding']
                decoded_header = decoded_header.decode(detected_encoding)
            return decoded_header
        except:
            raise Exception("Ошибка при получении заголовка")

    def GetDate(self, message):
        date = message['Date']
        date = parser.parse(date)
        return str(date.strftime("%Y-%m-%d %H:%M:%S %Z"))

    def GetAdresses(self, message, header_type):
        try:
            header = message.get(header_type)
            if not isinstance(header, str):
                return []
            adresses = list(map(email.utils.parseaddr, header.split(',')))
            for i in range(len(adresses)):
                adresses[i] = (self.DecodeHeader(adresses[i][0]), adresses[i][1].lower())
            return adresses
        except:
            raise Exception("Ошибка при получении адреса email")

    def GetBody(self, message):
        try:
            if message.is_multipart():
                for part in message.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            body = part.get_payload(decode=True)
                            break
            else:
                body = message.get_payload(decode=True)

            detected_encoding = chardet.detect(body)['encoding']
            body_decoded = body.decode(detected_encoding)
            pattern = re.compile(r'^>.*\n', re.MULTILINE)
            clean_body = pattern.sub('', body_decoded)

            soup = BeautifulSoup(clean_body, 'html.parser')
            if soup.find():
                for script in soup(["script", "style"]):
                    script.extract() 
                return soup.get_text(separator='\n', strip=True)
            
            clean_body = re.sub(r'\n\s*\n', '\n', clean_body)
            return clean_body
        except Exception as error:
            raise Exception("Ошибка при получении текста сообщения: " + error)
'''