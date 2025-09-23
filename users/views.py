from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .models import User

# class RegisterView(APIView):
#     def post(self, request):
#         serializer = UserRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({
#                 'message': 'User registered successfully.',
#                 'token': token.key,
#                 'username': user.username,
#                 'role': user.role
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'  # or 'id'

class UserUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

class UserDeleteView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

class LoginView(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'role': user.role
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)