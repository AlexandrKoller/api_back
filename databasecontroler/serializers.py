from rest_framework import serializers
from databasecontroler.models import UserFile
from django.contrib.auth import get_user_model
User=get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    
                                           
class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = '__all__'
        read_only_fields = ['FileOwner']
