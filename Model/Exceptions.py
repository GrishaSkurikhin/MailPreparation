class FileConvertError(Exception):
    def __init__(self, file_type: str) -> None:
        self.file_type = file_type
    
    def __str__(self) -> str:
        return "Ошибка при обработке вложения - " + self.file_type

class GetFilesError(Exception):
    pass

class ParseAddressError(Exception):
    pass

class ParseDateError(Exception):
    pass

class ParseBodyError(Exception):
    pass

class ParseHTMLError(Exception):
    pass

class DSConnectionError(Exception):
    def __str__(self) -> str:
        return "Ошибка при подключении к базе данных. Проверьте параметры подключения."

class DSInternalError(Exception):
    def __str__(self) -> str:
        return "Ошибка на стороне сервера базы данных"

class QueryError(Exception):
    def __init__(self, add_info: str) -> None:
        self.add_info = add_info

    def __str__(self) -> str:
        return "Ошибка в выполнении запроса к базе данных: " + self.add_info

class UniqueError(Exception):
    def __init__(self, object: str) -> None:
        self.object = object

    def __str__(self) -> str:
        if self.object == "mail":
            return "Такое письмо уже существует"
        elif self.object == "company":
            return "Такая компания уже существует"
        elif self.object == "domain":
            return "Домен с таким именем для данной компании уже существует"

class UndefinedError(Exception):
    def __init__(self, action: str) -> None:
        self.action = action

    def __str__(self) -> str:
        return "Неизвестная ошибка при: " + self.action