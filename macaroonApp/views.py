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
from macaroonApp.models import Profile, RefreshToken, CustomGroup, Transaction, FinalPayment
from macaroonApp.serializers import ProfileSerializer, CustomGroupSerializer, TransactionSerializer, FinalPaymentSerializer
from macaroonApp.utils import verify_token
from macaroonBackend.settings import JWT_SECRET, JWT_VALIDITY_IN_DAYS

from Cryptodome.Hash import SHA512

User = get_user_model()


class MoneyForm(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request: Request):
        print(request.data, flush=True)
        data = request.data
        try:
            data["addressTo"] = User.objects.get(email=data["addressTo"]).profile.public_key
        except User.DoesNotExist:
            pass

        try:
            markedFor = CustomGroup.objects.get(slug=data["markedFor"]).members.all()
            data["markedFor"] = []
            for member in markedFor:
                data["markedFor"].append(member.public_key)
        except CustomGroup.DoesNotExist:
            try:
                data["markedFor"] = [User.objects.get(email=data["addressTo"]).profile.public_key]
            except User.DoesNotExist:
                pass

        return Response(data)


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


class CustomGroupViewSet(viewsets.ModelViewSet):
    serializer_class = CustomGroupSerializer
    queryset = CustomGroup.objects.all().prefetch_related("members")


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


class TransactionsSent(APIView):
    def get(self, request: Request):
        transactions = Transaction.objects.filter(sender=request.user.profile)
        response = TransactionSerializer(transactions, many=True).data
        for transaction in response:
            transaction["sender_email"] = Profile.objects.get(id=transaction["sender"]).user.email
            transaction["destination_email"] = []
            for destination in transaction["destination"]:
                destination_obj = Profile.objects.get(id=destination)
                transaction["destination_email"].append(destination_obj.user.email)
        return Response(response)


class TransactionsReceivedAsIntermediary(APIView):
    def get(self, request: Request):
        transactions = Transaction.objects.filter(intermediary=request.user.profile)
        response = TransactionSerializer(transactions, many=True).data
        for transaction in response:
            transaction["destination_email"] = []
            transaction["sender_email"] = Profile.objects.get(id=transaction["sender"]).user.email
            for destination in transaction["destination"]:
                destination_obj = Profile.objects.get(id=destination)
                transaction["destination_email"].append(destination_obj.user.email)
        return Response(response)


class SaveTransaction(APIView):
    def post(self, request: Request):
        data: dict = request.data
        data["sender"] = request.user.profile.id
        moneyReceiver_public_key = data["intermediary_public_key"]
        data.pop("intermediary_public_key")
        data["intermediary"] = Profile.objects.get(public_key=moneyReceiver_public_key).id


        destination_public_keys = data["destination_public_keys"]
        data.pop("destination_public_keys")
        data["destination"] = []
        for destination_public_key in destination_public_keys:
            data["destination"].append(Profile.objects.get(public_key=destination_public_key).id)
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FinalPaymentsSent(APIView):
    def get(self, request: Request):
        transactions = FinalPayment.objects.filter(moneySender=request.user.profile)
        response = FinalPaymentSerializer(transactions, many=True).data
        for transaction in response:
            transaction["moneySender_email"] = Profile.objects.get(id=transaction["moneySender"]).user.email
        return Response(response)


class FinalPaymentsReceived(APIView):
    def get(self, request: Request):
        transactions = FinalPayment.objects.filter(moneyReceiver=request.user.profile)
        response = FinalPaymentSerializer(transactions, many=True).data
        for transaction in response:
            transaction["moneySender_email"] = Profile.objects.get(id=transaction["moneySender"]).user.email
        return Response(response)


class SaveFinalPayment(APIView):
    def post(self, request: Request):
        data: dict = request.data
        data["moneySender"] = request.user.profile.id
        intermediary_public_key = data["moneyReceiver_public_key"]
        data.pop("moneyReceiver_public_key")
        data["moneyReceiver"] = Profile.objects.get(public_key=intermediary_public_key).id
        serializer = FinalPaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
