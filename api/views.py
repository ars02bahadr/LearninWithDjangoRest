from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.models import UserType, UserRole, Profile
from api.serializers import UserRoleSerializer, UserTypeSerializer, RegisterSerializer, ProfileSerializer, ProfileFormSerializer
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            }
        ),
        responses={200: 'Returns token and user data'}
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username is None or password is None:
            return Response({
                'error': 'Lütfen kullanıcı adı ve şifre giriniz'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'error': 'Geçersiz kullanıcı adı veya şifre'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        token, _ = Token.objects.get_or_create(user=user)
        
        try:
            profile = Profile.objects.select_related('user', 'user_type').prefetch_related('user_roles').get(user=user)
            profile_serializer = ProfileSerializer(profile)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'profile': profile_serializer.data
            })
        except Profile.DoesNotExist:
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'profile': None
            })


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: 'Returns user data'}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'message': 'Kayıt başarılı'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        responses={200: ProfileSerializer(many=True)}
    )
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        profiles = Profile.objects.select_related('user', 'user_type').prefetch_related('user_roles').all()
        result_page = paginator.paginate_queryset(profiles, request)
        serializer = self.serializer_class(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


    @swagger_auto_schema(
        operation_description="Create a new profile with image upload support",
        request_body=ProfileFormSerializer,
        responses={201: ProfileSerializer}
    )
    def post(self, request):
        serializer = ProfileFormSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response({
                'message': 'Profil başarıyla oluşturuldu',
                'data': ProfileSerializer(profile).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'error': 'Geçersiz veri',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        responses={200: ProfileSerializer}
    )
    def get(self, request, pk):
        try:
            profile = Profile.objects.select_related('user', 'user_type').prefetch_related('user_roles').get(pk=pk)
            serializer = self.serializer_class(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profil bulunamadı'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Update a profile with image upload support",
        request_body=ProfileFormSerializer,
        responses={200: ProfileSerializer}
    )
    def put(self, request, pk):
        try:
            profile = Profile.objects.select_related('user', 'user_type').prefetch_related('user_roles').get(pk=pk)
            serializer = ProfileFormSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                profile = serializer.save()
                return Response({
                    'message': 'Profil başarıyla güncellendi',
                    'data': ProfileSerializer(profile).data
                })
            return Response({
                'error': 'Geçersiz veri',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Güncellenecek profil bulunamadı'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        responses={204: "Profile deleted"}
    )
    def delete(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
            user = profile.user
            profile.delete()
            user.delete()
            return Response({
                'message': 'Profil ve kullanıcı başarıyla silindi'
            }, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Silinecek profil bulunamadı'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UserTypeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserTypeSerializer(many=True)}
    )
    def get(self, request, pk=None):
        if pk:
            try:
                user_type = UserType.objects.get(pk=pk)
                serializer = UserTypeSerializer(user_type)
                return Response(serializer.data)
            except UserType.DoesNotExist:
                return Response(
                    {'error': 'Kullanıcı tipi bulunamadı'},
                    status=status.HTTP_404_NOT_FOUND
                )
        user_types = UserType.objects.all()
        serializer = UserTypeSerializer(user_types, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=UserTypeSerializer,
        responses={201: UserTypeSerializer}
    )
    def post(self, request):
        serializer = UserTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Kullanıcı tipi başarıyla oluşturuldu',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="User Type ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=UserTypeSerializer,
        responses={200: UserTypeSerializer}
    )
    def put(self, request, pk):
        try:
            user_type = UserType.objects.get(pk=pk)
            serializer = UserTypeSerializer(user_type, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Kullanıcı tipi başarıyla güncellendi',
                    'data': serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserType.DoesNotExist:
            return Response(
                {'error': 'Güncellenecek kullanıcı tipi bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="User Type ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={204: 'User Type deleted'}
    )
    def delete(self, request, pk):
        try:
            user_type = UserType.objects.get(pk=pk)
            user_type.delete()
            return Response({
                'message': 'Kullanıcı tipi başarıyla silindi'
            }, status=status.HTTP_200_OK)
        except UserType.DoesNotExist:
            return Response(
                {'error': 'Silinecek kullanıcı tipi bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserTypeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserTypeSerializer}
    )
    def get(self, request, pk):
        try:
            user_type = UserType.objects.get(pk=pk)
            serializer = UserTypeSerializer(user_type)
            return Response(serializer.data)
        except UserType.DoesNotExist:
            return Response(
                {'error': 'Kullanıcı tipi bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        request_body=UserTypeSerializer,
        responses={200: UserTypeSerializer}
    )
    def put(self, request, pk):
        try:
            user_type = UserType.objects.get(pk=pk)
            serializer = UserTypeSerializer(user_type, data=request.data)
            if serializer.is_valid():
                user_type = serializer.save()
                return Response({
                    'message': 'Kullanıcı tipi başarıyla güncellendi',
                    'data': UserTypeSerializer(user_type).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserType.DoesNotExist:
            return Response(
                {'error': 'Güncellenecek kullanıcı tipi bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        responses={204: "User type deleted"}
    )
    def delete(self, request, pk):
        try:
            user_type = UserType.objects.get(pk=pk)
            user_type.delete()
            return Response({
                'message': 'Kullanıcı tipi başarıyla silindi'
            }, status=status.HTTP_200_OK)
        except UserType.DoesNotExist:
            return Response(
                {'error': 'Silinecek kullanıcı tipi bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserRoleSerializer(many=True)}
    )
    def get(self, request, pk=None):
        if pk:
            try:
                user_role = UserRole.objects.get(pk=pk)
                serializer = UserRoleSerializer(user_role)
                return Response(serializer.data)
            except UserRole.DoesNotExist:
                return Response(
                    {'error': 'Kullanıcı rolü bulunamadı'},
                    status=status.HTTP_404_NOT_FOUND
                )
        user_roles = UserRole.objects.all()
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=UserRoleSerializer,
        responses={201: UserRoleSerializer}
    )
    def post(self, request):
        serializer = UserRoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Kullanıcı rolü başarıyla oluşturuldu',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="User Role ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=UserRoleSerializer,
        responses={200: UserRoleSerializer}
    )
    def put(self, request, pk):
        try:
            user_role = UserRole.objects.get(pk=pk)
            serializer = UserRoleSerializer(user_role, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Kullanıcı rolü başarıyla güncellendi',
                    'data': serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Güncellenecek kullanıcı rolü bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="User Role ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={204: 'User Role deleted'}
    )
    def delete(self, request, pk):
        try:
            user_role = UserRole.objects.get(pk=pk)
            user_role.delete()
            return Response({
                'message': 'Kullanıcı rolü başarıyla silindi'
            }, status=status.HTTP_200_OK)
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Silinecek kullanıcı rolü bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserRoleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserRoleSerializer}
    )
    def get(self, request, pk):
        try:
            user_role = UserRole.objects.get(pk=pk)
            serializer = UserRoleSerializer(user_role)
            return Response(serializer.data)
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Kullanıcı rolü bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        request_body=UserRoleSerializer,
        responses={200: UserRoleSerializer}
    )
    def put(self, request, pk):
        try:
            user_role = UserRole.objects.get(pk=pk)
            serializer = UserRoleSerializer(user_role, data=request.data)
            if serializer.is_valid():
                user_role = serializer.save()
                return Response({
                    'message': 'Kullanıcı rolü başarıyla güncellendi',
                    'data': UserRoleSerializer(user_role).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Güncellenecek kullanıcı rolü bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        responses={204: "User role deleted"}
    )
    def delete(self, request, pk):
        try:
            user_role = UserRole.objects.get(pk=pk)
            user_role.delete()
            return Response({
                'message': 'Kullanıcı rolü başarıyla silindi'
            }, status=status.HTTP_200_OK)
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Silinecek kullanıcı rolü bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )
