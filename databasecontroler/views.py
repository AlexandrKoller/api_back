from rest_framework.viewsets import ModelViewSet
from django.utils import timezone
from rest_framework.response import Response
from django.http import FileResponse
from django.contrib.auth import get_user_model
from .permissions import AdminOrUserPermissions, AdminOrUserForUserViewSetPermissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from databasecontroler.serializers import UserSerializer, UserFileSerializer
from .models import UserFile
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework import status
import mimetypes
from django.core.files.storage import FileSystemStorage
import os
from dotenv import load_dotenv

load_dotenv()
User=get_user_model()

# Create your views here.
class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [AdminOrUserForUserViewSetPermissions, IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff == False:
            return User.objects.filter(username=user)
        return User.objects.all()
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    

class UserFileViewSet(ModelViewSet):
    serializer_class = UserFileSerializer
    permission_classes = [AdminOrUserPermissions, IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_queryset(self):
        user = self.request.user
        if self.action == 'memberfiles':
            pk = self.kwargs['pk']
            return UserFile.objects.filter(FileOwner=pk)
        if user.is_staff == False:
            return UserFile.objects.filter(FileOwner=user)
        if self.action == 'download_anon' or user.is_staff:
            return UserFile.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(FileOwner=self.request.user)
        
    def get_permissions(self):
        if self.action == 'download_anon':
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        if int(request.user.SizeStorage + request.FILES['File'].size) > int(os.getenv("MAX_SIZE_USER_STORAGE")):
            data = {'message': 'yours storage is full'}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    @action(methods=['get'], detail=True)
    def memberfiles(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserFileSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  
    
    @action(methods=['get'], detail=True)
    def download(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        file_handle = instance.File.open()
        response = FileResponse(file_handle, as_attachment=True, filename=instance.Name, content_type=mimetypes.guess_type(instance.File.path)[0])
        instance.DateLastDownLoad = timezone.now()
        instance.save()
        return response
    
    @action(methods=['post'], detail=False)   
    def download_anon(self, request, pk=None, *args, **kwargs):
        instance = get_object_or_404(UserFile, loadcode=request.data.get('loadcode'))
        if request.data.get('info'):
            serializer = UserFileSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)  
        file_handle = instance.File.open()
        response = FileResponse(file_handle, as_attachment=True, filename=instance.Name, content_type=mimetypes.guess_type(instance.File.path)[0], status=status.HTTP_200_OK)
        instance.DateLastDownLoad = timezone.now()
        instance.save()
        return response


