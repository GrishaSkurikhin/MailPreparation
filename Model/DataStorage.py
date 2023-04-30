import psycopg2
from pathlib import Path

from Model.Exceptions import DSConnectionError, DSInternalError, QueryError, UniqueError, UndefinedError
from Model.Mail import *


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
         except psycopg2.OperationalError:
             raise DSConnectionError()
         except (psycopg2.InternalError, psycopg2.DatabaseError):
             raise DSInternalError()
         except Exception:
             return False
         return result[0] == 1
    
    def create(self, connection_settings: dict, dump_path: Path) -> None:
        try:
            connection = psycopg2.connect(host=connection_settings["host"], 
                                          port=connection_settings["port"], 
                                          user=connection_settings["user"], 
                                          password=connection_settings["password"])
            cursor = connection.cursor()
            cursor.execute("CREATE database {}".format(self.db_name))
            with open(dump_path, 'r') as f:
                sql = f.read()
            cursor.execute(sql)
            cursor.close()
            connection.close()
        except psycopg2.OperationalError:
            raise DSConnectionError()
        except psycopg2.ProgrammingError:
            raise QueryError("база данных уже существует или файл dump неисправен")
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
        
    def add_mail(self, mail: Mail) -> None:
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
                cursor = self.connection.cursor()

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

                self.connection.commit()

            except psycopg2.errors.UniqueViolation:
                 self.connection.rollback()
                 raise UniqueError("mail")
            except psycopg2.ProgrammingError:
                self.connection.rollback()
                raise QueryError("при вставке письма")
            except Exception as error:
                 self.connection.rollback()
                 raise UndefinedError("вставка письма " + str(error))
            finally:
                 cursor.close()
                 

    def add_company(self, name: str, type: str) -> None:
        try:
            cursor = self.connection.cursor()
            query = f"INSERT INTO {self.t_companies} (name, type) VALUES (%s, %s)"
            cursor.execute(query, (name, type,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            raise UniqueError("company")
        finally:
            cursor.close()
        
    def add_domain(self, domain: str, company_id: str) -> None:
        try:
            cursor = self.connection.cursor()
            query = f"INSERT INTO {self.t_domains} (domain, company_id) VALUES (%s, %s)"
            cursor.execute(query, (domain, company_id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            raise UniqueError("domain")
        finally:
            cursor.close()
    
    def del_mail(self, id: str) -> None:
         cursor = self.connection.cursor()
         query = f"DELETE FROM {self.t_messages} WHERE id = %s"
         cursor.execute(query, (id,))
         self.connection.commit()
         cursor.close()

    def del_company(self, id: str) -> None:
         cursor = self.connection.cursor()
         query = f"DELETE FROM {self.t_companies} WHERE id = %s"
         cursor.execute(query, (id,))
         self.connection.commit()
         cursor.close()

    def del_domain(self, id: str) -> None:
         cursor = self.connection.cursor()
         query = f"DELETE FROM {self.t_domains} WHERE id = %s"
         cursor.execute(query, (id,))
         self.connection.commit()
         cursor.close()

    def get_users(self) -> list[dict]:
         cursor = self.connection.cursor()
         query = f"SELECT address, name FROM {self.t_adresses}"
         cursor.execute(query)
         rows = cursor.fetchall()
         cursor.close()

         rows = [{"email": address, "name": name} for address, name in rows]
         return rows

    def get_companies(self) -> list[dict]:
         cursor = self.connection.cursor()
         query = f"SELECT name, type FROM {self.t_companies}"
         cursor.execute(query)
         rows = cursor.fetchall()
         cursor.close()
         rows = [{"name": name, "type": type} for name, type in rows]
         return rows
    
    def get_companies_domains(self) -> list[dict]:
         cursor = self.connection.cursor()
         query = f"SELECT * FROM {self.v_companies_domains}"
         cursor.execute(query)
         rows = cursor.fetchall()
         cursor.close()

         rows = [{"id": id, "name": name, "type": type, "domains": domains} for id, name, type, domains in rows]
         return rows

    def get_file_by_id(self, id: str) -> bytes:
        cursor = self.connection.cursor()
        query = f"SELECT bytes FROM {self.t_files} WHERE id = %s"
        cursor.execute(query, (id,))
        row = cursor.fetchall()
        cursor.close()
        return bytes(row[0][0])
    
    def __convert_to_mail(self, rows_mails: list[tuple], rows_files: list[tuple]) -> list[Mail]:
        mail_list = []
        viewed_mails = [] # при объединении отправителей уже просмотренные письма исключаются
        for i in range(len(rows_mails)):
            if rows_mails[i][0] in viewed_mails:
                continue
            # объединяем отправителей
            recievers = [{"name": rows_mails[i][4], "email": rows_mails[i][5], "type": rows_mails[i][6]}]
            for j in range(len(rows_mails)):
                if rows_mails[i][0] == rows_mails[j][0] and i != j:
                    recievers.append({"name": rows_mails[j][4], "email": rows_mails[j][5], "type": rows_mails[j][6]})
                    viewed_mails.append(rows_mails[j][0])
            
            # Добавляем файлы
            files = []
            for row_file in rows_files:
                if row_file[3] == rows_mails[i][0]:
                    files.append({"id": row_file[0], "filename": row_file[1], "text": row_file[2], "bytes": None})

            mail_list.append(Mail(rows_mails[i][0], rows_mails[i][1], {"name":rows_mails[i][2], "email": rows_mails[i][3]}, recievers, rows_mails[i][7], rows_mails[i][8], str(rows_mails[i][9]), rows_mails[i][10], files))

        return mail_list
    
    def get_all_mails(self) -> list[Mail]:
         get_mails_query = f'''SELECT id, reply_id, sender_name, sender_address, reciever_name, reciever_address, reciever_type, subject, body, datetime, priority
                               FROM {self.v_mails_info}'''
         get_files_query = f'''SELECT id, name, text, message_id FROM {self.t_files}'''
         cursor = self.connection.cursor()

         cursor.execute(get_mails_query)
         rows_mails = cursor.fetchall()

         cursor.execute(get_files_query)
         rows_files = cursor.fetchall()

         cursor.close()
         return self.__convert_to_mail(rows_mails, rows_files)

    def simple_search(self, fields: list, filters: list, logic_operator: str) -> list[Mail]:
        # Поиск по одному фильтру: адресу получателя, отправителя, компании, типу компании, приоритету
        fields_list = [f"{field} = %s" for field in fields]
        get_mails_query = f'''SELECT id, reply_id, sender_name, sender_address, reciever_name, reciever_address, reciever_type, subject, body, datetime, priority
                              FROM {self.v_mails_info} WHERE {f" {logic_operator} ".join(fields_list)}'''
        get_files_query = f'''SELECT id, name, text, message_id FROM {self.t_files}'''
        cursor = self.connection.cursor()

        cursor.execute(get_mails_query, filters)
        rows_mails = cursor.fetchall()

        cursor.execute(get_files_query)
        rows_files = cursor.fetchall()

        cursor.close()
        return self.__convert_to_mail(rows_mails, rows_files)

    def time_search(self, timefrom: str, timeto: str) -> list[Mail]:
        # Поиск по времени
        get_mails_query = f"SELECT * FROM {self.v_mails_info} WHERE datetime > %s AND datetime < %s"
        get_files_query = f'''SELECT id, name, text, message_id FROM {self.t_files}'''
        cursor = self.connection.cursor()

        cursor.execute(get_mails_query, [timefrom, timeto])
        rows_mails = cursor.fetchall()


        cursor.execute(get_files_query)
        rows_files = cursor.fetchall()

        cursor.close()
        return self.__convert_to_mail(rows_mails, rows_files)
    
    def fulltext_search(self, field: str, search_words: list, type: str) -> list[Mail]:
        # Полнотекстовый поиск по ключевым словам: по теме или тексту письма (вложений)
        query = "SELECT * FROM {} WHERE to_tsvector('russian', {}) @@ to_tsquery('russian', %s)".format(self.view_name, field)
        self.cursor.execute(query, (' & '.join(search_words),))
        rows = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

    def close(self):
        self.connection.close()