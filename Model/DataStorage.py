import functools
import psycopg2
from pathlib import Path

from Model.Exceptions import DSConnectionError, DSInternalError, QueryError, UniqueError, UndefinedError
from Model.Mail import *

def operation_handler(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.connection is None:
                raise DSConnectionError()
            cursor = self.connection.cursor()
            try:
                result = func(self, cursor, *args, **kwargs)
                return result
            except psycopg2.OperationalError:
                raise DSConnectionError()
            except psycopg2.ProgrammingError:
                self.connection.rollback()
                raise QueryError()
            except UniqueError as error:
                 self.connection.rollback()
                 raise error
            except (psycopg2.InternalError, psycopg2.DatabaseError):
                raise DSInternalError()
            except Exception:
                self.connection.rollback()
                raise UndefinedError()
            finally:
                self.connection.commit()
                cursor.close()
        return wrapper

class DataStorage:
    def __init__(self):
        self.db_name = "MailAnalyze"
        self.t_recievers = 'public."recievers"'
        self.t_messages = 'public."messages"'
        self.t_adresses = 'public."email_addresses"'
        self.t_files = 'public."files"'
        self.t_companies = 'public."companies"'
        self.t_domains = 'public."domains"'
        self.v_companies_domains = 'public."v_companies_domains"'
        self.v_mails_info = 'public."v_mails_info"'

        self.connection = None
    
    def is_exist(self, connection_settings: dict) -> bool:
        try:
            connection = psycopg2.connect(host=connection_settings["host"], 
                                           port=connection_settings["port"], 
                                           user=connection_settings["user"], 
                                           password=connection_settings["password"])
            cursor = connection.cursor()
            cursor.execute(f"SELECT exists(SELECT 1 from pg_catalog.pg_database where datname = '{self.db_name}')")
            res = cursor.fetchone()[0]
            cursor.close()
            connection.close()
        except psycopg2.OperationalError:
            raise DSConnectionError()
        except (psycopg2.InternalError, psycopg2.DatabaseError):
            raise DSInternalError()
        except Exception:
            return False
        return res
    
    def check_connection(self, connection_settings: dict) -> bool:
         try:
             connection = psycopg2.connect(host=connection_settings["host"], 
                                           port=connection_settings["port"], 
                                           dbname=self.db_name, 
                                           user=connection_settings["user"], 
                                           password=connection_settings["password"])
             cursor = connection.cursor()
             cursor.execute("SELECT 1")
             result = cursor.fetchone()
             cursor.close()
             connection.close()
         except Exception as error:
             return False
         return result[0] == 1
    
    def create(self, connection_settings: dict, dump_path: Path) -> None:
        try:
            connection = psycopg2.connect(host=connection_settings["host"], 
                                          port=connection_settings["port"], 
                                          user=connection_settings["user"], 
                                          password=connection_settings["password"])
            cursor = connection.cursor()
            with open(dump_path, 'r') as f:
                sql = f.read()
            cursor.execute(sql)
            cursor.close()
            connection.close()
        except psycopg2.OperationalError:
            raise DSConnectionError()
        except psycopg2.ProgrammingError:
            raise QueryError()
        except (psycopg2.InternalError, psycopg2.DatabaseError):
            raise DSInternalError()

    def connect(self, connection_settings: dict) -> None:
        try:
            self.connection = psycopg2.connect(host=connection_settings["host"], 
                                               port=connection_settings["port"], 
                                               dbname=self.db_name, 
                                               user=connection_settings["user"], 
                                               password=connection_settings["password"])
        except psycopg2.OperationalError:
            raise DSConnectionError()
        except (psycopg2.InternalError, psycopg2.DatabaseError):
            raise DSInternalError()
        
    @operation_handler
    def add_mail(self, cursor, mail: Mail) -> None:
            insert_adress_query = f'''INSERT INTO {self.t_adresses} (address, name)
                                      VALUES (%s, %s)
                                      ON CONFLICT (address) DO UPDATE SET address = EXCLUDED.address
                                      RETURNING id'''
            insert_reciever_query = f'''INSERT INTO {self.t_recievers} (message_id, address_id, type) 
                                        VALUES (%s, %s, %s)'''
            insert_message_query = f'''INSERT INTO {self.t_messages} (id, subject, sender_id, datetime, priority, body, reply_id)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            insert_file_query = f'''INSERT INTO {self.t_files} (name, text, bytes, message_id)
                                    VALUES (%s, %s, %s, %s)'''

            try:
                # вставка отправителя
                if mail.sender["name"] is None and mail.sender["email"] is None:
                    sender_adress_id = None
                else:
                    cursor.execute(insert_adress_query, (mail.sender["email"], mail.sender["name"],))
                    sender_adress_id = cursor.fetchall()[0][0]

                # вставка письма
                cursor.execute(insert_message_query, (mail.id, mail.subject, sender_adress_id, mail.date, mail.priority, mail.body, mail.in_reply_to,))

                # вставка получателей
                for reciever in mail.recievers:
                    cursor.execute(insert_adress_query, (reciever["email"], reciever["name"],))
                    reciever_adress_id = cursor.fetchall()
                    cursor.execute(insert_reciever_query, (mail.id, reciever_adress_id[0][0], reciever["type"],))
                # вставка вложений
                for file in mail.files:
                    cursor.execute(insert_file_query, (file["filename"], file["text"], file["bytes"], mail.id,))
            except psycopg2.errors.UniqueViolation:
                raise UniqueError("mail")
                 
    @operation_handler
    def add_company(self, cursor, name: str, type: str) -> None:
        try:
            cursor = self.connection.cursor()
            query = f"INSERT INTO {self.t_companies} (name, type) VALUES (%s, %s)"
            cursor.execute(query, (name, type,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            raise UniqueError("company")
    
    @operation_handler
    def add_domain(self, cursor, domain: str, company_id: str) -> None:
        try:
            cursor = self.connection.cursor()
            query = f"INSERT INTO {self.t_domains} (domain, company_id) VALUES (%s, %s)"
            cursor.execute(query, (domain, company_id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            raise UniqueError("domain")
    
    @operation_handler
    def del_mail(self, cursor, id: str) -> None:
        query = f"DELETE FROM {self.t_messages} WHERE id = %s"
        cursor.execute(query, (id,))

    @operation_handler
    def del_company(self, cursor, id: str) -> None:
         query = f"DELETE FROM {self.t_companies} WHERE id = %s"
         cursor.execute(query, (id,))

    @operation_handler
    def del_domain(self, cursor, id: str) -> None:
         query = f"DELETE FROM {self.t_domains} WHERE id = %s"
         cursor.execute(query, (id,))

    @operation_handler
    def get_users(self, cursor) -> list[dict]:
         query = f"SELECT address, name FROM {self.t_adresses}"
         cursor.execute(query)
         return [{"email": address, "name": name} for address, name in cursor.fetchall()]

    @operation_handler
    def get_companies(self, cursor) -> list[dict]:
         query = f"SELECT name, type FROM {self.t_companies}"
         cursor.execute(query)
         return [{"name": name, "type": type} for name, type in cursor.fetchall()]
    
    @operation_handler
    def get_companies_domains(self, cursor) -> list[dict]:
         query = f'''SELECT company_id, company_name, company_type, array_agg(ARRAY[domain_id::text, domain]) AS domains
                     FROM {self.v_companies_domains}
                     GROUP BY company_id, company_name, company_type;'''
         cursor.execute(query)
         return [{"id": id, "name": name, "type": type, "domains": domains} for id, name, type, domains in cursor.fetchall()]

    @operation_handler
    def get_file_by_id(self, cursor, id: str) -> bytes:
        query = f"SELECT bytes FROM {self.t_files} WHERE id = %s"
        cursor.execute(query, (id,))
        row = cursor.fetchall()

        return bytes(row[0][0])
    
    def __convert_to_mail(self, rows_mails: list[tuple], rows_files: list[tuple]) -> list[Mail]:
        mail_list = []
        viewed_mails = [] # при объединении отправителей уже просмотренные письма исключаются
        for i in range(len(rows_mails)):
            if rows_mails[i][0] in viewed_mails:
                continue
            # объединяем отправителей
            recievers = [{"name": rows_mails[i][6], "email": rows_mails[i][7], "type": rows_mails[i][8], "company_name": rows_mails[i][9], "company_type": rows_mails[i][10]}]
            for j in range(len(rows_mails)):
                if rows_mails[i][0] == rows_mails[j][0] and i != j:
                    recievers.append({"name": rows_mails[i][6], "email": rows_mails[j][7], "type": rows_mails[j][8], "company_name": rows_mails[j][9], "company_type": rows_mails[j][10]})
                    viewed_mails.append(rows_mails[j][0])
            
            # Добавляем файлы
            files = []
            for row_file in rows_files:
                if row_file[3] == rows_mails[i][0]:
                    files.append({"id": row_file[0], "filename": row_file[1], "text": row_file[2], "bytes": None})

            mail_list.append(Mail(rows_mails[i][0], rows_mails[i][1], 
                                  {"name":rows_mails[i][2], "email": rows_mails[i][3], "company_name": rows_mails[i][4], "company_type": rows_mails[i][5]}, 
                                  recievers, rows_mails[i][11], rows_mails[i][12], str(rows_mails[i][13]), rows_mails[i][14], files))

        return mail_list
    
    @operation_handler
    def get_all_mails(self, cursor) -> list[Mail]:
         get_mails_query = f'''SELECT id, reply_id, 
                               sender_name, sender_address, sender_company_name, sender_company_type, 
                               reciever_name, reciever_address, reciever_type, reciever_company_name, reciever_company_type, 
                               subject, body, datetime, priority
                               FROM {self.v_mails_info}'''
         get_files_query = f'''SELECT id, name, text, message_id FROM {self.t_files}'''

         cursor.execute(get_mails_query)
         rows_mails = cursor.fetchall()

         cursor.execute(get_files_query)
         rows_files = cursor.fetchall()

         return self.__convert_to_mail(rows_mails, rows_files)

    @operation_handler
    def simple_search(self, cursor, fields: list, filters: list, logic_operator: str) -> list[Mail]:
        # Поиск по одному фильтру: адресу получателя, отправителя, компании, типу компании, приоритету
        fields_list = [f"{field} = %s" for field in fields]
        get_mails_query = f'''SELECT id, reply_id, 
                               sender_name, sender_address, sender_company_name, sender_company_type, 
                               reciever_name, reciever_address, reciever_type, reciever_company_name, reciever_company_type, 
                               subject, body, datetime, priority
                              FROM {self.v_mails_info} WHERE {f" {logic_operator} ".join(fields_list)}'''
        get_files_query = f'''SELECT id, name, text, message_id FROM {self.t_files}'''

        cursor.execute(get_mails_query, filters)
        rows_mails = cursor.fetchall()

        cursor.execute(get_files_query)
        rows_files = cursor.fetchall()

        return self.__convert_to_mail(rows_mails, rows_files)

    @operation_handler
    def time_search(self, cursor, timefrom: str, timeto: str) -> list[Mail]:
        # Поиск по времени
        get_mails_query = f'''SELECT id, reply_id, 
                               sender_name, sender_address, sender_company_name, sender_company_type, 
                               reciever_name, reciever_address, reciever_type, reciever_company_name, reciever_company_type, 
                               subject, body, datetime, priority
                            FROM {self.v_mails_info} WHERE datetime > %s AND datetime < %s'''
        get_files_query = f'''SELECT id, name, text, message_id FROM {self.t_files}'''

        cursor.execute(get_mails_query, [timefrom, timeto])
        rows_mails = cursor.fetchall()

        cursor.execute(get_files_query)
        rows_files = cursor.fetchall()

        return self.__convert_to_mail(rows_mails, rows_files)
    
    @operation_handler
    def fulltext_search(self, cursor, search_words: list, field: str) -> list[Mail]:
        # Полнотекстовый поиск по ключевым словам: по теме или тексту письма
        query = f'''SELECT id, reply_id, 
                               sender_name, sender_address, sender_company_name, sender_company_type, 
                               reciever_name, reciever_address, reciever_type, reciever_company_name, reciever_company_type, 
                               subject, body, datetime, priority
                FROM {self.v_mails_info} WHERE to_tsvector('russian', {field}) @@ to_tsquery('russian', %s)'''
        get_files_query = f'''SELECT id, name, text, message_id FROM {self.t_files}'''

        cursor.execute(query, (' & '.join(search_words),))
        rows_mails = cursor.fetchall()
        
        cursor.execute(get_files_query)
        rows_files = cursor.fetchall()

        return self.__convert_to_mail(rows_mails, rows_files)

    @operation_handler
    def fulltext_search_files(self, cursor, search_words: list) -> list[Mail]:
         # Полнотекстовый поиск по ключевым словам во вложениях
         query = f'''SELECT id, reply_id, 
                               sender_name, sender_address, sender_company_name, sender_company_type, 
                               reciever_name, reciever_address, reciever_type, reciever_company_name, reciever_company_type, 
                               subject, body, datetime, priority
                     FROM {self.v_mails_info}'''
         get_files_query = f'''SELECT id, name, text, message_id FROM {self.t_files}
                                WHERE to_tsvector('russian', text) @@ to_tsquery('russian', %s)'''
        
         cursor.execute(query)
         rows_mails = cursor.fetchall()

         cursor.execute(get_files_query, (' & '.join(search_words),))
         rows_files = cursor.fetchall()

         mails_list = self.__convert_to_mail(rows_mails, rows_files)
         new_mail_list = []
         for mail in mails_list:
             if len(mail.files) != 0:
                 new_mail_list.append(mail)

         return new_mail_list

    def close(self):
        if self.connection is not None:
            self.connection.close()
        