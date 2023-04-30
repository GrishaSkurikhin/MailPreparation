import configparser

class Config:
    def __init__(self, path):
        f = open(path)
        f.close()
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(path)
    
    def set_data(self, data: dict) -> None:
        for field, info in data.items():
            self.config.set('database', field, info)
        
        with open(self.path, 'w') as f:
            self.config.write(f)
    
    def get_data(self) -> dict:
        return self.config.__dict__['_sections'].copy()