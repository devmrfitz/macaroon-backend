
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class MoneyForm(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request: Request):
        print(request.data, flush=True)
        return Response(request.data)
