import datetime
import string
import uuid
from secrets import choice

import jwt
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from macaroonApp.authentication import PreSignupAuth, DummyAuthentication
from macaroonApp.models import Profile, RefreshToken
from macaroonApp.serializers import ProfileSerializer
from macaroonApp.utils import verify_token
from macaroonBackend.settings import JWT_SECRET, JWT_VALIDITY_IN_DAYS

from Cryptodome.Hash import SHA512

User = get_user_model()


class MoneyForm(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request: Request):
        print(request.data, flush=True)
        publickey = request.data.get('public_key')
        amount = request.data.get('amount')

        return Response(request.data)


class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    authentication_classes = [BasicAuthentication, DummyAuthentication, PreSignupAuth]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Profile.objects.all()
        else:
            return Profile.objects.filter(user=user)

    def perform_create(self, serializer):
        id_ = str(uuid.uuid4().hex)
        serializer.save(user=self.request.user,
                        id=id_)


class AddContactAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        profile: Profile = request.user.profile
        contact_email = request.data.get('email')
        try:
            profile.contacts.add(Profile.objects.get(user__email=contact_email))
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)


class ListContactsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        profile: Profile = request.user.profile
        contacts = profile.contacts.all().prefetch_related('user')
        serializer = ProfileSerializer(contacts, many=True)
        return Response(serializer.data)


class RandomUsername:
    """
    using firstname & lastname
    create a random username (all lower case)
    that doesnt already exist in db
    """
    num_of_random_letters = 3
    num_of_random_numbers = 2
    user_model = get_user_model()

    def get_username(self, slug: str = None):
        username = ''
        if slug:
            username = slug

        while True:
            random_letters = string.ascii_lowercase
            random_numbers = string.digits
            username += self.get_random_char(
                random_letters, self.num_of_random_letters
            )
            username += self.get_random_char(
                random_numbers, self.num_of_random_numbers
            )
            if self.username_exist_in_db(username) is False:
                return username

    def username_exist_in_db(self, username):
        """
        :return: True if username already exist in db
            else False
        """
        q = self.user_model.objects.filter(username=username)
        return q.exists()

    def get_random_char(self, ip_str, n):
        return (''.join(
            choice(ip_str)
            for _ in range(n)
        ))


class OAuthCallback(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request: Request):

        email, picture = verify_token(request.data.get("jwt"))
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                username = RandomUsername().get_username(slug=email.split("@")[0])
                user = User.objects.create_user(
                    username=username, email=email, first_name=picture)
            prev_tokens = Token.objects.filter(user=user).order_by("-created")
            for i in range(3, prev_tokens.count()):
                prev_tokens[i].delete()
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            refresh_token = RefreshToken.objects.create(token=token)
            hasher = SHA512.new(truncate="256")
            hasher.update(refresh_token.token.key.encode('utf-8'))
            jwt_payload = {"email": email, "hash": hasher.hexdigest(),
                           "exp": datetime.datetime.now() + datetime.timedelta(
                               days=JWT_VALIDITY_IN_DAYS)}
            return JsonResponse(
                {"access_token": jwt.encode(payload=jwt_payload,
                                            key=JWT_SECRET,
                                            algorithm="HS256"),
                 "refresh_token": refresh_token.token.key})

        else:
            return JsonResponse(data={}, status=status.HTTP_401_UNAUTHORIZED)


class RefreshJWT(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request: Request, JWT_VALIDITY_IN_DAYS=None):
        refresh_token_by_user = request.POST.get("refresh_token")
        access_token = request.POST.get("access_token")
        if refresh_token_by_user and access_token:
            jwt_payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
            hasher = SHA512.new(truncate="256")
            token = RefreshToken.objects.get(token__key=refresh_token_by_user)
            hasher.update(token.token.key.encode('utf-8'))

            if jwt_payload.get(
                    "hash") == hasher.hexdigest() and \
                    token.token.key == refresh_token_by_user \
                    and datetime.datetime.now() < datetime.datetime.fromtimestamp(token.expiry):
                jwt_payload = {"email": jwt_payload.get("email"),
                               "hash": hasher.hexdigest(),
                               "exp": datetime.datetime.now() + datetime.timedelta(
                                   days=JWT_VALIDITY_IN_DAYS)}
                return JsonResponse({"access_token": jwt.encode(
                    payload=jwt_payload, key=JWT_SECRET, algorithm="HS256")})
            else:
                return JsonResponse({}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
