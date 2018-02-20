from django.contrib.auth.middleware import RemoteUserMiddleware

class UMRemoteUserMiddleware(RemoteUserMiddleware):
    header = "HTTP_REMOTE_USER"
    
    def process_request(self, request):
        return super(UMRemoteUserMiddleware, self).process_request(request)