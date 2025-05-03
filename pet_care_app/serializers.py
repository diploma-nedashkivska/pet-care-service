import uuid
import boto3
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'hash_password']


class SignUpSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True)
    photo = serializers.ImageField(required=False)

    def create(self, validated_data):
        photo = validated_data.pop("photo", None)
        user = User(
            full_name=validated_data["full_name"],
            email=validated_data["email"]
        )
        user.set_password(validated_data["password"])

        if photo:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            key = f"user_profile/{uuid.uuid4().hex}.jpg"
            s3.upload_fileobj(
                photo.file,
                settings.AWS_STORAGE_BUCKET_NAME,
                key
            )
            user.photo_url = (
                f"https://{settings.AWS_STORAGE_BUCKET_NAME}"
                f".s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{key}"
            )
        user.save()
        return user
