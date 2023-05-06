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

    def create_db(self) -> None:
        if not self.dataStorage.is_exist:
            self.dataStorage.create(self.config.get_data()["database"], self.DUMP_PATH)
    
    def set_current_eml(self, email_path: str) -> int:
        self.current_eml = Email(Path(email_path))
        return len(self.current_eml.msgs)
    
    def search(self, fields: list[str], filters: list[str], 
               timefrom: str, timeto: str, isTimeSearch: bool,
               keywordsSubject: list[str], keywordsText: list[str], keywordsFiles: list[str],
               logic_operator: str) -> list[Mail]:
        def check_condition(func):
            def wrapper(*args, **kwargs):
                if len(args[0]) == 0 and logic_operator == "AND":
                    return self.dataStorage.get_all_mails()
                elif len(args[0]) == 0 and logic_operator == "OR":
                    return []
                else:
                    return func(*args, **kwargs)
            return wrapper
        
        @check_condition
        def simple_search(fields, filters):
            return self.dataStorage.simple_search(fields, filters, logic_operator)

        @check_condition
        def fulltext_search(keywords, field):
            return self.dataStorage.fulltext_search(keywords, field)

        @check_condition
        def fulltext_search_files(keywords):
            return self.dataStorage.fulltext_search_files(keywords)
        
        set1 = set(simple_search(fields, filters))
        if isTimeSearch:
            set2 = set(self.dataStorage.time_search(timefrom, timeto))
        else:
            if logic_operator == "AND":
                set2 = set(self.dataStorage.get_all_mails())
            elif logic_operator == "OR":
                set2 = set([])
        set3 = set(fulltext_search(keywordsSubject, "subject"))
        set4 = set(fulltext_search(keywordsText, "body"))
        set5 = set(fulltext_search_files(keywordsFiles))
        
        if logic_operator == "AND":
            return list(set1 & set2 & set3 & set4 & set5)
        elif logic_operator == "OR":
            return list(set1 | set2 | set3 | set4 | set5)

    def add_mails(self):
        i = 1
        for filename, mail in self.current_eml.get_mails():
            try:
                self.dataStorage.add_mail(mail)
                yield f"Письмо '{filename}' успешно добавлено", i
            except Exception as error:
                yield str(error) + f': "{filename}"', i
            i += 1

    def export_csv(self, mails: list[Mail], filename: str) -> None:
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                dict_mail_list = [mail.get_export_dict() for mail in mails]
                writer = csv.DictWriter(csvfile, fieldnames=dict_mail_list[0].keys())
                writer.writeheader()
                for row in dict_mail_list:
                    writer.writerow(row)
        except:
            raise Exception("Ошибка при экспорте csv")
    
    def export_txt(self, mails: list[Mail], path: str) -> None:
        try:
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
        except:
            raise Exception("Ошибка при экспорте txt")
    
    def export_json(self, mails: list[Mail], filename: str) -> None:
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as jsonfile:
                json.dump([mail.get_export_dict() for mail in mails], jsonfile, ensure_ascii=False, indent=4)
        except:
            raise Exception("Ошибка при экспорте json")