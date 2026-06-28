from rest_framework import serializers
from .models import User , VendorProfile


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ["first_name","last_name","email","password"]
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class VendorRegistrationSerializer(serializers.Serializer):
    #user fields
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    #vendor fields
    company_name = serializers.CharField()
    phone_no = serializers.CharField()
    gst_number = serializers.CharField()
    pan_number = serializers.CharField()
    annual_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    def create(self,validated_data):
            #create user
            user = User.objects.create_user(
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'],
                password=validated_data['password'],
                role='vendor',
            )
            #create vendor profile
            vendor_profile = VendorProfile.objects.create(
                user=user,
                company_name = validated_data['company_name'],
                phone_no = validated_data['phone_no'],
                gst_number = validated_data['gst_number'],
                pan_number = validated_data['pan_number'],
                annual_revenue=validated_data['annual_revenue'],
            )
            return user
        