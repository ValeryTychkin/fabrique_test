import uuid


class AddClientId:
    """
    Если клиент анон без id ('hashcode_id') в куки файле,
        то происходит генерация и добавление id (UUID) в куки файл клиента
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.user.is_authenticated and not request.COOKIES.get('hashcode_id'):
            response.set_cookie('hashcode_id', str(uuid.uuid4().hex))
        return response
