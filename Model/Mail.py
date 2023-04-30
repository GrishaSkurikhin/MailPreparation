class Mail:
    def __init__(self, id: str, 
                 in_reply_to: str, 
                 sender: dict,
                 recievers: list[dict], 
                 subject: str, body: str,
                 date: str, 
                 priority: str, 
                 files: list[dict]
                 ) -> None:
        self.id, self.in_reply_to, self.sender = id, in_reply_to, sender
        self.recievers, self.subject, self.body = recievers, subject, body
        self.date, self.priority, self.files = date, priority, files
    
    def get_export_dict(self) -> dict:
        return {"subject": self.subject,
                "date": self.date,
                "priority": self.priority,
                "sender": self.sender,
                "recievers": self.recievers,
                "body": self.body,
                "files": [{"filename": file["filename"], "text": file["text"]} for file in self.files]}