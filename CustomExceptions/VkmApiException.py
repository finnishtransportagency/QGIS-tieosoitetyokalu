class VkmApiException(Exception):
    def __init__(self, url, message='VKM-rajapintaan ei saada yhteyttä.'):
        self.message = message
        self.url = url


    def __str__(self):
        return f'{self.message} VKM-URL: {self.url}'   
