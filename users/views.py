from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from .models import User


from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import LoanApplication
from .serializers import LoanApplicationSerializer

import datetime
import jwt
import os
from django.conf import settings
import shutil
import base64
from django.db.models import Count

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CorporateProjectDetails

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os

from .models import LoanApplication, User
from .serializers import LoanApplicationSerializer


def check_user_token(request):
    try:
        # Extract the token from the Authorization header (Bearer <token>)
        token = request.headers.get('Authorization').split("Bearer ")[1]
    except Exception as err:
        # If any error occurs (e.g., missing token), return False
        return False

    try:
        # Decode the JWT token with the secret key and HS256 algorithm
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return False
    except jwt.InvalidTokenError:
        # Invalid token
        return False

@api_view(['POST'])
def register_user(request):
    data = request.data
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    password = data.get('password')
    role = data.get('role')  # Default role is customer

    if role not in ['customer', 'partner', 'admin']:
        return Response({'error': "Invalid role. Choose from 'customer', 'partner', or 'admin'.",
                        'success': False},
                        status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists','success':False}, status=status.HTTP_400_BAD_REQUEST)

    # Hash the password before saving it to the database
    hashed_password = make_password(password)

    # Create the user and save the hashed password
    user = User(email=email, first_name=first_name, last_name=last_name, role=role, password=hashed_password)
    user.save()
    return Response({'message': 'User registered successfully','success':True}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')
    role_from_frontend = data.get('role')  # Role received from frontend

    # Check if the user exists
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password', 'success': False}, status=status.HTTP_401_UNAUTHORIZED)

    # Verify the password using check_password
    if check_password(password, user.password):
        # Role validation: Ensure the role from frontend matches the database role
        if user.role != role_from_frontend:
            return Response({'error': 'Try to login from the correct page', 'success': False}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT token
        payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,  # Include role in token
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3),  # Token expiration
            'iat': datetime.datetime.utcnow(),  # Issued at time
        }

        # Create JWT token with custom secret and HS256 algorithm
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

        return Response({
            'access_token': token,
            'role': user.role,
            'success': True
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid email or password', 'success': False}, status=status.HTTP_401_UNAUTHORIZED)
       
@api_view(['POST'])
def change_password(request):
    payload = check_user_token(request)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        })
    user_id = payload['user_id']
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found','success':False}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Ensure that mandatory fields are present in the request
        mandatory_fields = ['current_password', 'new_password']
        for field in mandatory_fields:
            if field not in request.data:
                return Response({f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        # Verify the current password
        if not check_password(current_password, user.password):
            return Response({'error': 'Current password is incorrect','success':False}, status=status.HTTP_400_BAD_REQUEST)

        # Hash the new password and update the user
        hashed_new_password = make_password(new_password)
        user.password = hashed_new_password
        user.save()
        return Response({'message': 'Password updated successfully','success':True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e),'success':False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_loan_application(request):
    payload = check_user_token(request)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        })
    try:
        # Ensure that mandatory fields are present in the request
        mandatory_fields = ['fullName', 'email', 'mobile']
        for field in mandatory_fields:
            if field not in request.data:
                return Response({f'{field}': 'is required', 'success': False}, status=status.HTTP_400_BAD_REQUEST)
            
        user_id=payload['user_id']    

        try:
            created_by_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User with the provided ID does not exist','success':False}, status=status.HTTP_400_BAD_REQUEST)

        # Manually create and save the LoanApplication object
     
        loan_application =  LoanApplication(
        applicant_name = request.data.get("fullName"),
        gender = request.data.get("gender", ""),
        dob = request.data.get("dob", None),
        martial_status = request.data.get("maritalStatus", ""),
        email = request.data.get("email"),
        phone_number = request.data.get("mobile"),
        alternate_phone_number = request.data.get("altMobile", ""),
        pan_number = request.data.get("pan", ""),
        aadhar_number = request.data.get("aadhaar", ""),
        PA_address = request.data.get("permanentAddress", ""),
        PA_pincode = request.data.get("permanentPincode", ""),
        PA_state = request.data.get("permanentState", ""),
        PA_city = request.data.get("permanentCity", ""),
        CA_address = request.data.get("currentAddress", ""),
        CA_pincode = request.data.get("currentPincode", ""),
        CA_state = request.data.get("currentState", ""),
        CA_city = request.data.get("currentCity", ""),
        type_of_employment = request.data.get("employmentType", ""),
        company_name = request.data.get("companyName", ""),
        monthly_income = request.data.get("monthlyIncome", 0),
        official_mail_id = request.data.get("officialMail", ""),
        work_experience = request.data.get("workExperience", ""),
        existing_emis = request.data.get("existingEMIs", 0),
        annual_income = request.data.get("annualIncome", 0),
        annual_profit = request.data.get("annualProfit", 0),
        loan_product = request.data.get("loanProduct", ""),
        loan_amount = request.data.get("loanAmount", 0),
        loan_tenure = request.data.get("loanTenure", 0),
        project_name = request.data.get("projectName", ""),
        flat_no = request.data.get("flatNo", ""),
        block_no = request.data.get("blockNo", ""),
        loan_status = request.data.get("loan_status", "IN-PROGRESS"),
        created_by = created_by_user
        )
        
        # Save the object to the database
        loan_application.save()

        # Create a folder in the media path using the application_id
        application_folder = os.path.join(settings.MEDIA_ROOT, f'loan_applications/{loan_application.application_id}')
        os.makedirs(application_folder, exist_ok=True)

        def save_file(file, filename_prefix):
            file_extension = os.path.splitext(file.name)[1]  # Get original file extension
            filename = f"{filename_prefix}{file_extension}"  # Preserve original extension
            file_path = os.path.join(application_folder, filename)

            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            return f'loan_applications/{loan_application.application_id}/{filename}'

        # Save Aadhaar card file
        if 'aadhaarCardDoc' in request.FILES:
            loan_application.aadhar = save_file(request.FILES['aadhaarCardDoc'], 'aadhar')

        # Save PAN card file
        if 'panCardDoc' in request.FILES:
            loan_application.pan_card = save_file(request.FILES['panCardDoc'], 'pan_card')

        # Save Bank Statement file
        if 'bankStatements' in request.FILES:
            loan_application.bank_statement = save_file(request.FILES['bankStatements'], 'bank_statement')

        # Save ITR/Form16 file
        if 'form16' in request.FILES:
            loan_application.itr = save_file(request.FILES['form16'], 'itr')

        # Save multiple Salary Slips
        salary_slips = request.FILES.getlist('salarySlips')
        slip_paths = []
        for index, slip in enumerate(salary_slips, start=1):
            slip_path = save_file(slip, f'salary_slip_{index}')
            slip_paths.append(slip_path)

        # Save all salary slip paths as a JSON array
        loan_application.salary_slips = slip_paths

        # Save the updated loan application
        loan_application.save()
      
        return Response({"message": "Loan application successfully added!",'success':True}, status=status.HTTP_201_CREATED)    

    except Exception as e:  
        return Response({'error': str(e),'success':False}, status=status.HTTP_400_BAD_REQUEST)  

@api_view(['GET'])
def get_dashboard_data(request):
    """
    Get loan applications for a partner.
    Authenticate if the user is a partner, then filter applications created by them.
    """

    payload = check_user_token(request)
    print(payload)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        }, status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload['user_id']
    try:
            created_by_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
            return Response({'error': 'User with the provided ID does not exist','success':False}, status=status.HTTP_400_BAD_REQUEST)

    role = created_by_user.role

    if role == 'admin':
        loan_applications = LoanApplication.objects.all().values(
            'loan_status'
        ).annotate(count=Count('loan_status'))
    else :
        loan_applications = LoanApplication.objects.filter(created_by=created_by_user).values(
            'loan_status'
        ).annotate(count=Count('loan_status'))

    return Response({
        'success': True,
        'applications_summary': {
            status['loan_status']: status['count'] for status in loan_applications
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_corporate_project(request):
    """
    API to add a new corporate project.
    """
    payload = check_user_token(request)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        }, status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload['user_id']
    try:
        created_by_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User with the provided ID does not exist','success':False}, status=status.HTTP_400_BAD_REQUEST)

    role = created_by_user.role

    # if role != 'partner':
    #     return Response({'success': False, 'message': "Unauthorized access.Only Partner can access this Endpoint"}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Validate input data
        mandatory_fields = ['corporateName', 'companyPan', 'gstin', 'companyAddress', 'pincode', 'state', 'city']
        for field in mandatory_fields:
            if field not in request.data:
                return Response({f'{field}': 'is required', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

        # Check if GSTIN already exists
        if CorporateProjectDetails.objects.filter(gstin=request.data['gstin']).exists():
            return Response({'error': 'A project with this GSTIN already exists', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new corporate project record
        corporate_project = CorporateProjectDetails.objects.create(
            corporate_name=request.data['corporateName'],
            company_name=request.data['companyPan'],
            gstin=request.data['gstin'],
            company_address=request.data['companyAddress'],
            pincode=request.data['pincode'],
            state=request.data['state'],
            city=request.data['city'],
            created_by=created_by_user,
        )

        return Response({
            'success': True,
            'message': 'Corporate project added successfully!',
            'data': {
                'id': corporate_project.id,
                'corporate_name': corporate_project.corporate_name,
                'company_name': corporate_project.company_name,
                'gstin': corporate_project.gstin,
                'company_address': corporate_project.company_address,
                'pincode': corporate_project.pincode,
                'state': corporate_project.state,
                'city': corporate_project.city
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e), 'success': False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_corporate_project_detail(request):
    """
    API to retrieve all corporate projects.
    """
    payload = check_user_token(request)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        }, status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload['user_id']
    try:
        created_by_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User with the provided ID does not exist','success':False}, status=status.HTTP_400_BAD_REQUEST)

    role = created_by_user.role

    # if role != 'partner':
    #     return Response({'success': False, 'message': "Unauthorized access.Only Partner can access this Endpoint"}, status=status.HTTP_403_FORBIDDEN)

    try:
        data = CorporateProjectDetails.objects.get(created_by=created_by_user)
        
        data=model_to_dict(data)

        return Response({'success': True, 'data': data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e), 'success': False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_applications(request):
    """
    Get all loan applications for a user based on his role and display application's data.
    """

    payload = check_user_token(request)
    print(payload)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        }, status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload['user_id']
    try:
         created_by_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
            return Response({'error': 'User with the provided ID does not exist','success':False}, status=status.HTTP_400_BAD_REQUEST)

    role = created_by_user.role
    # Get loan applications based on user role
    if role == 'admin':
        loan_applications = LoanApplication.objects.all()
    else:
        loan_applications = LoanApplication.objects.filter(created_by=created_by_user)

    # Fetch user details for created_by field
    applications_summary = []
    for app in loan_applications:
        created_by_user = User.objects.get(id=app.created_by.id)  # Fetch user details

        applications_summary.append({
            'application_id': app.application_id,
            'applicant_name': app.applicant_name,
            'loan_product': app.loan_product,
            'loan_amount': app.loan_amount,
            'loan_status': app.loan_status,
            'developer_name': app.developer_name,
            'disbursed_amount': app.disbursed_amount,
            'project_name': app.project_name,
            'payout_percentage': app.payout_percentage,
            'created_at': app.created_at,
            'modified_at': app.modified_at,
            'created_by': {
                'id': created_by_user.id,
                'name': created_by_user.first_name,  # Adjust based on your user model
                'email': created_by_user.email,
                'role': created_by_user.role
            }
        })

    return Response({
        'success': True,
        'role': role,
        'applications_summary': applications_summary
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_application_by_id(request, application_id):
    """
    Get an application by its ID, including document paths as URLs.
    """

    payload = check_user_token(request)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        }, status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload['user_id']
    created_by_user = get_object_or_404(User, id=user_id)
    role = created_by_user.role

    # Fetch the loan application
    loan_application = get_object_or_404(LoanApplication, application_id=application_id)
    serializer = LoanApplicationSerializer(loan_application)

    # Helper function to generate file URLs
    def get_file_url(file_path):
        if file_path:
            # Ensure MEDIA_URL is not duplicated
            return request.build_absolute_uri(file_path) if file_path.startswith(settings.MEDIA_URL) \
                else request.build_absolute_uri(settings.MEDIA_URL + file_path.lstrip('/'))
        return None


    # Prepare document URLs
    documents = {
        "aadhar": get_file_url(serializer.data.get('aadhar')),
        "pan_card": get_file_url(serializer.data.get('pan_card')),
        "bank_statement": get_file_url(serializer.data.get('bank_statement')),
        "itr": get_file_url(serializer.data.get('itr')),
        "salary_slips": [get_file_url(slip_path) for slip_path in serializer.data.get('salary_slips', []) if slip_path]
    }

    return Response({
        'success': True,
        'role': role,
        'applications_data': serializer.data,
        'documents': documents
    }, status=status.HTTP_200_OK)



@api_view(['PUT'])
def update_loan_application(request, application_id):
    payload = check_user_token(request)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        })
    
    try:
        user_id = payload['user_id']

        # Check if the user exists
        try:
            created_by_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User with the provided ID does not exist', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the loan application exists
        try:
            loan_application = LoanApplication.objects.get(application_id=application_id)
        except LoanApplication.DoesNotExist:
            return Response({'error': 'Loan application not found', 'success': False}, status=status.HTTP_404_NOT_FOUND)

        # Mapping of request fields to database fields
        field_mapping = {
            "fullName": "applicant_name",
            "gender": "gender",
            "dob": "dob",
            "maritalStatus": "martial_status",
            "email": "email",
            "mobile": "phone_number",
            "altMobile": "alternate_phone_number",
            "pan": "pan_number",
            "aadhaar": "aadhar_number",
            "permanentAddress": "PA_address",
            "permanentPincode": "PA_pincode",
            "permanentState": "PA_state",
            "permanentCity": "PA_city",
            "currentAddress": "CA_address",
            "currentPincode": "CA_pincode",
            "currentState": "CA_state",
            "currentCity": "CA_city",
            "employmentType": "type_of_employment",
            "companyName": "company_name",
            "monthlyIncome": "monthly_income",
            "officialMail": "official_mail_id",
            "workExperience": "work_experience",
            "existingEMIs": "existing_emis",
            "annualIncome": "annual_income",
            "annualProfit": "annual_profit",
            "loanProduct": "loan_product",
            "loanAmount": "loan_amount",
            "loanTenure": "loan_tenure",
            "loan_status": "loan_status",
            "developer_name": "developer_name",
            "disbursed_amount": "disbursed_amount",
            "payout_percentage": "payout_percentage",
            "flatNo": "flat_no",
            "blockNo": "block_no",
            "project_name": "project_name",
        }

        # Update loan application fields based on mapping
        for request_key, model_field in field_mapping.items():
            if request_key in request.data:
                setattr(loan_application, model_field, request.data[request_key])

        # Save updated files if any
        application_folder = os.path.join(settings.MEDIA_ROOT, f'loan_applications/{loan_application.application_id}')
        os.makedirs(application_folder, exist_ok=True)

        def save_file(file, filename_prefix):
            file_extension = os.path.splitext(file.name)[1]  # Get original file extension
            filename = f"{filename_prefix}{file_extension}"  # Preserve original extension
            file_path = os.path.join(application_folder, filename)

            print(f"Saving file: {file.name} as {filename}")  # Debug print

            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            return f'loan_applications/{loan_application.application_id}/{filename}'

        # Save Aadhaar card file
        if 'aadhaarCardDoc' in request.FILES:
            loan_application.aadhar = save_file(request.FILES['aadhaarCardDoc'], 'aadhar')

        # Save PAN card file
        if 'panCardDoc' in request.FILES:
            loan_application.pan_card = save_file(request.FILES['panCardDoc'], 'pan_card')

        # Save Bank Statement file
        if 'bankStatements' in request.FILES:
            loan_application.bank_statement = save_file(request.FILES['bankStatements'], 'bank_statement')

        # Save ITR/Form16 file
        if 'form16' in request.FILES:
            loan_application.itr = save_file(request.FILES['form16'], 'itr')

        # Save multiple Salary Slips
        salary_slips = request.FILES.getlist('salarySlips')
        if salary_slips:
            slip_paths = []
            for index, slip in enumerate(salary_slips, start=1):
                slip_path = save_file(slip, f'salary_slip_{index}')
                slip_paths.append(slip_path)
            loan_application.salary_slips = slip_paths

        # Save the updated loan application
        loan_application.save()

        return Response({"message": "Loan application successfully updated!", 'success': True}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e), 'success': False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_loan_application(request, application_id):
    payload = check_user_token(request)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        })
    try:
        user_id = payload['user_id']

        # Check if the user exists
        try:
            created_by_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User with the provided ID does not exist', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the loan application exists
        try:
            loan_application = LoanApplication.objects.get(application_id=application_id)
        except LoanApplication.DoesNotExist:
            return Response({'error': 'Loan application not found', 'success': False}, status=status.HTTP_404_NOT_FOUND)

        # Delete the loan application
        loan_application.delete()

        # Delete the associated media folder
        application_folder = os.path.join(settings.MEDIA_ROOT, f'loan_applications/{application_id}')
        if os.path.exists(application_folder):
            shutil.rmtree(application_folder)

        return Response({"message": "Loan application successfully deleted!", 'success': True}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e), 'success': False}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def edit_corporate_project(request, project_id):
    """
    API to edit an existing corporate project.
    """
    payload = check_user_token(request)
    if not payload:
        return Response({
            'success': False,
            'message': "Try to login again"
        }, status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload['user_id']
    try:
        created_by_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User with the provided ID does not exist', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

    role = created_by_user.role

    try:
        # Fetch the existing project
        corporate_project = CorporateProjectDetails.objects.get(id=project_id)
    except CorporateProjectDetails.DoesNotExist:
        return Response({'error': 'Corporate project not found', 'success': False}, status=status.HTTP_404_NOT_FOUND)

    # Optional: Ensure only the creator or an admin can edit
    # if role != 'partner' and corporate_project.created_by != created_by_user:
    #     return Response({'success': False, 'message': "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    # Validate input fields
    allowed_fields = ['corporateName', 'companyPan', 'gstin', 'companyAddress', 'pincode', 'state', 'city']
    update_fields = {}
    
    for field in allowed_fields:
        if field in request.data:
            update_fields[field] = request.data[field]

    # Ensure at least one field is being updated
    if not update_fields:
        return Response({'error': 'No valid fields provided for update', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

    # Prevent GSTIN duplication
    if 'gstin' in update_fields and CorporateProjectDetails.objects.filter(gstin=update_fields['gstin']).exclude(id=project_id).exists():
        return Response({'error': 'A project with this GSTIN already exists', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

    # Update the corporate project details
    for key, value in update_fields.items():
        setattr(corporate_project, key.lower(), value)  # Ensuring correct field naming

    corporate_project.save()

    return Response({
        'success': True,
        'message': 'Corporate project updated successfully!',
        'data': {
            'id': corporate_project.id,
            'corporate_name': corporate_project.corporate_name,
            'company_name': corporate_project.company_name,
            'gstin': corporate_project.gstin,
            'company_address': corporate_project.company_address,
            'pincode': corporate_project.pincode,
            'state': corporate_project.state,
            'city': corporate_project.city
        }
    }, status=status.HTTP_200_OK)

