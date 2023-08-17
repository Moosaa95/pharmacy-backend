from rest_framework import serializers
from accounts.models import State, UserBase, Profile
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserBase
        fields = [
            'id',
            'user_name',
            'email',

        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type':'password'}, write_only=True, validators=[validate_password], required=True)
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True, required=True)
    state  = serializers.CharField(max_length=100, required=False, allow_blank=True)


    class Meta:
        model = UserBase
        fields = [
            'user_name',
            'email',
            'usertype',
            'password',
            'password2',
            'state'
            # 'business_name'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password":"password fields does not match"})
        
        if UserBase.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email address already exists"})
        if UserBase.objects.filter(user_name=attrs['user_name']).exists():
            raise serializers.ValidationError({"user_name": "Username already exists"})
        
        return attrs
    
    def create(self, validated_data):
        print('validated')
        print(validated_data)
        # business_name = validated_data.pop('business_name', '')
        state_id = validated_data["state"]
        state = State.objects.get(id=state_id)
        print('this is the state', state)
        user = UserBase.objects.create(
            user_name = validated_data['user_name'],
            email = validated_data['email'],
            usertype = validated_data.get('usertype', 'user'),
            # business_name = validated_data['business_name'],
            state = state,
            # lga = validated_data["lga"],

        )
        user.set_password(validated_data['password'])
        user.save()



        profile = Profile.objects.create(
            userbase=user,
            # business_name=user.business_name if user.usertype == "pharmacy" else "",  # Set the extracted business_name value here
            state=user.state, 
            lga=user.lga
        )

        return user 


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        print('poppppp')
        token = super().get_token(user)
        token['first_name'] = user.profile.first_name
        token['last_name'] = user.profile.last_name
        token['user_name'] = user.user_name
        token['email'] = user.email
        token['usertype'] = user.usertype
        token['verified'] = user.profile.verified
        token['image'] = str(user.profile.image)

        return token



