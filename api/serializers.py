from rest_framework import serializers
from api.models import UserType, UserRole, Profile
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserType
        fields='__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserRole
        fields='__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)
        extra_kwargs = {
            'username': {'required': False}  # Make username optional
        }


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    user_type = UserTypeSerializer(read_only=True)
    user_roles = UserRoleSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    user_type_id = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.all(),
        write_only=True,
        required=True,
        source='user_type'
    )
    user_role_ids = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all(),
        write_only=True,
        required=True,
        many=True,
        source='user_roles'
    )

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password', None)
        user_roles = validated_data.pop('user_roles')
        
        # Create user
        user = User.objects.create(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        if password:
            user.set_password(password)
        user.save()

        # Create profile
        profile = Profile.objects.create(
            user=user,
            **validated_data
        )
        
        # Add user roles
        profile.user_roles.set(user_roles)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        password = validated_data.pop('password', None)
        user_roles = validated_data.pop('user_roles', None)
        
        # Update user data if provided
        if user_data:
            user = instance.user
            # Don't update username
            user_data.pop('username', None)
            for attr, value in user_data.items():
                setattr(user, attr, value)
            if password:
                user.set_password(password)
            user.save()

        # Update user roles if provided
        if user_roles:
            instance.user_roles.set(user_roles)

        # Update profile data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class ProfileFormSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    user_type_id = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.all(),
        write_only=True,
        required=True,
        source='user_type'
    )
    user_role_ids = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all(),
        write_only=True,
        required=True,
        many=True,
        source='user_roles'
    )
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 
                 'phone_number', 'user_type_id', 'user_role_ids', 'profile_picture')

    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', '')
        }
        password = validated_data.pop('password', None)
        user_roles = validated_data.pop('user_roles')

        # Check if user exists
        try:
            user = User.objects.get(username=user_data['username'])
            # Update existing user
            user.email = user_data['email']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            if password:
                user.set_password(password)
            user.save()

            # Check if profile exists
            try:
                profile = Profile.objects.get(user=user)
                # Update existing profile
                for attr, value in validated_data.items():
                    setattr(profile, attr, value)
                profile.save()
                profile.user_roles.set(user_roles)
                return profile
            except Profile.DoesNotExist:
                # Create new profile for existing user
                profile = Profile.objects.create(
                    user=user,
                    **validated_data
                )
                profile.user_roles.set(user_roles)
                return profile

        except User.DoesNotExist:
            # Create new user and profile
            user = User.objects.create(**user_data)
            if password:
                user.set_password(password)
            user.save()

            profile = Profile.objects.create(
                user=user,
                **validated_data
            )
            profile.user_roles.set(user_roles)
            return profile

    def update(self, instance, validated_data):
        user = instance.user
        if 'email' in validated_data:
            user.email = validated_data.pop('email')
        if 'first_name' in validated_data:
            user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user.last_name = validated_data.pop('last_name')
        if 'password' in validated_data:
            user.set_password(validated_data.pop('password'))
        user.save()

        if 'user_roles' in validated_data:
            instance.user_roles.set(validated_data.pop('user_roles'))
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor"})
        return attrs

    def create(self, validated_data):
        password2 = validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user