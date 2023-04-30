import csv
import json
import os
from Model.Email import *
from Model.DataStorage import *
from Model.Config import *


class Model:
    def __init__(self) -> None:
        self.DUMP_PATH = Path("Model/dump.sql")
        self.current_eml = None
        self.dataStorage = DataStorage()
        self.config = Config("config.ini")
        self.dataStorage.connect(self.config.get_data()["database"])
    
    def create_db(self) -> None:
        if not self.dataStorage.is_exist:
            self.dataStorage.create(self.config.get_data(), self.DUMP_PATH)
    
    def set_current_eml(self, email_path: str) -> int:
        self.current_eml = Email(Path(email_path))
        return len(self.current_eml.msgs)
    
    def Search(self, fields, filters, timefrom, timeto, keywordsSubject, keywordsText, logic_operator):
        return []
        '''
        def joinLists(list1, list2):
            if logic_operator == "AND":
                intersection = [d1 for d1 in list1 for d2 in list2 if d1['id'] == d2['id']]
                return intersection
            elif logic_operator == "OR":
                set1 = set(d['id'] for d in list1)
                union = [d for d in list1]
                for d in list2:
                    if d['id'] not in set1:
                        union.append(d)
                return union
        
        list1 = self.dataStorage.simple_search(fields, filters, logic_operator) if len(fields) != 0 else []
        list2 = self.dataStorage.time_search(timefrom, timeto)
        list3 = self.dataStorage.fulltext_search("subject", keywordsSubject) if len(keywordsSubject) != 0 else []
        list4 = self.dataStorage.fulltext_search("body", keywordsText) if len(keywordsText) != 0 else []
        join_list = joinLists(list1, joinLists(list2, joinLists(list3, list4)))
        return join_list
        '''
        
    def add_mails(self):
        i = 1
        for filename, mail in self.current_eml.get_mails():
            if isinstance(mail, Exception):
                yield mail, i
            else:
                try:
                    self.dataStorage.add_mail(mail)
                    yield f"Письмо '{filename}' успешно добавлено", i
                except Exception as error:
                    yield error, i
            i += 1

    def export_csv(self, mails: list[Mail], filename: str) -> None:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            dict_mail_list = [mail.get_export_dict() for mail in mails]
            writer = csv.DictWriter(csvfile, fieldnames=dict_mail_list[0].keys())
            writer.writeheader()
            for row in dict_mail_list:
                writer.writerow(row)
    
    def export_txt(self, mails: list[Mail], path: str) -> None:
        i = 1
        for mail in mails:
            files_text = ""
            for file in mail.files:
                files_text += file["text"] + "\n"
            if mail.body.isspace() and files_text.isspace():
                continue
            with open(os.path.join(path, str(i) + ".txt"), 'w', newline='', encoding='utf-8') as txtfile:
                txtfile.write(mail.body + "\n" + files_text)
            i += 1
    
    def export_json(self, mails: list[Mail], filename: str) -> None:
        with open(filename, 'w', newline='', encoding='utf-8') as jsonfile:
            json.dump([mail.get_export_dict() for mail in mails], jsonfile, ensure_ascii=False, indent=4)