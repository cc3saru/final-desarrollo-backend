from django.db.transaction import atomic

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from api.models import User
from api.serializers import UserListSerializer, UserCreateSerializer, UserMeSerializer
from api.utils import send_email, encode_token, decode_token

from app.settings import (
    FRONTEND_URL,
    TOKEN_TYPE_CONFIRM_EMAIL,
    TOKEN_TYPE_RESET_PASSWORD,
    RESET_PASSWORD_TEMPLATE_ID,
    WELCOME_TEMPLATE_ID,
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    def get_permissions(self):
        if self.action in ['get_all_users', 'get_me', 'list']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['create_user', 'confirm_email', 'forgot_password', 'change_password', 'verify_token']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer
    
    @action(detail=False, methods=['get'])
    def get_all_users(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_me(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @atomic
    @action(detail=False, methods=['post'])
    def create_user(self, request):
        serializer = UserCreateSerializer(data=request.data)
        
        email = request.data['email']
        try:
            user = User.objects.get(email=email)
            if user.email_confirmed: return Response(status=status.HTTP_409_CONFLICT)
        except User.DoesNotExist: pass

        if serializer.is_valid():
            serializer.save()

            # Crear token
            token = encode_token(serializer.instance, TOKEN_TYPE_CONFIRM_EMAIL)

            # Enviar correo electrónico
            send_email(
                to=[serializer.data['email']],
                template=WELCOME_TEMPLATE_ID,
                variables={
                    'subject': 'Confirmar correo electrónico',
                    'link': FRONTEND_URL + '/confirm-email?token=' + token,
                }
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def confirm_email(self, request):
        token = request.data['token']
        decoded_token = decode_token(token)
        user_id = decoded_token['user_id']
        type = decoded_token['type']

        try: user = User.objects.get(id=user_id)
        except User.DoesNotExist: return Response(status=status.HTTP_404_NOT_FOUND)

        if user.email_confirmed: return Response(status=status.HTTP_200_OK)
    
        if type == int(TOKEN_TYPE_CONFIRM_EMAIL):
            user.email_confirmed = True
            user.save()
            return Response(status=status.HTTP_200_OK)  
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        email = request.data['email']
        
        try:
            user = User.objects.get(email=email)

            # Crear token
            token = encode_token(user, TOKEN_TYPE_RESET_PASSWORD)

            # Enviar correo electrónico
            send_email(
                to=[email],
                template=RESET_PASSWORD_TEMPLATE_ID,
                variables={
                    'subject': 'Restablecer contraseña',
                    'link': FRONTEND_URL + '/change-password?token=' + token,
                }
            )

            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print(error)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        token = request.data['token']
        decoded_token = decode_token(token)
        user_id = decoded_token['user_id']
        type = decoded_token['type']

        if type == int(TOKEN_TYPE_RESET_PASSWORD):
            user = User.objects.get(id=user_id)
            user.set_password(request.data['password'])
            user.save()
            return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def verify_token(self, request):
        token = request.data['token']
        decoded_token = decode_token(token)
        type = decoded_token['type']

        if type == int(TOKEN_TYPE_RESET_PASSWORD):
            return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)