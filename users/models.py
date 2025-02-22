from django.db import models

# Create your models here.

class User(models.Model):
    ROLE_CHOICES = [
    ('CUSTOMER', 'Customer'),
    ('PARTNER', 'Partner'),
    ('ADMIN', 'Admin'),
]

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    password = models.CharField(max_length=128, null=True, blank=True)  # Store the plain password here
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        managed = False,
        db_table = 'users'


class LoanApplication(models.Model):

    LOAN_STATUS_CHOICES = [
    ('IN-PROGRESS', 'In Progress'),
    ('ACTIVE', 'Active'),
    ('REJECTED', 'Rejected'),
]
  
    application_id = models.AutoField(primary_key=True)
    applicant_name = models.CharField(max_length=255,null=False)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    martial_status = models.CharField(max_length=20)
    email = models.EmailField(max_length=255,null=False)
    phone_number = models.CharField(max_length=15,null=False)
    alternate_phone_number = models.CharField(max_length=15)
    alternate_email = models.EmailField(max_length=255)
    pan_number = models.CharField(max_length=10)
    aadhar_number = models.CharField(max_length=12)
    PA_address = models.CharField(max_length=255)
    PA_pincode = models.CharField(max_length=6)
    PA_state = models.CharField(max_length=50)
    PA_city = models.CharField(max_length=50)
    CA_address = models.CharField(max_length=255)
    CA_pincode = models.CharField(max_length=6)
    CA_state = models.CharField(max_length=50)
    CA_city = models.CharField(max_length=50)
    type_of_employment = models.CharField(max_length=50)
    employer_type = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    EA_address = models.CharField(max_length=255)
    EA_pincode = models.CharField(max_length=6)
    EA_state = models.CharField(max_length=50)
    EA_city = models.CharField(max_length=50)
    official_mail_id = models.EmailField(max_length=255,null=True)
    work_experience = models.CharField(max_length=50,null=True)
    monthly_income = models.IntegerField(null=True)
    existing_emis = models.IntegerField(null=True)
    annual_income = models.IntegerField(null=True)
    annual_profit = models.IntegerField(null=True)
    loan_product = models.CharField(max_length=50,null=True)
    loan_amount = models.IntegerField( null=True)
    loan_tenure = models.IntegerField(null=True)
    property_identification = models.CharField(max_length=50,null=True)
    project_name = models.CharField(max_length=255)
    developer_name = models.CharField(max_length=255)
    booking_date = models.DateField(null=True)
    typology = models.CharField(max_length=50)
    stage_of_construction = models.CharField(max_length=50)
    property_value = models.IntegerField(null=True)
    property_address = models.CharField(max_length=255)
    property_pincode = models.CharField(max_length=6)   
    property_state = models.CharField(max_length=50)
    property_city = models.CharField(max_length=50)
    name_of_closing_agent = models.CharField(max_length=255)
    loan_status = models.CharField(
        max_length=50,
        choices=LOAN_STATUS_CHOICES,
    )
    disbursement_date = models.DateField(null=True)
    disbursed_amount = models.IntegerField(null=True)
    loan_emis = models.IntegerField(null=True)
    loan_interest_rate = models.IntegerField(null=True)
    loan_processing_fee = models.IntegerField(null=True)
    loan_sanctioned_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications_creation')
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications_modification',null=True)
    aadhar = models.FileField(upload_to='', blank=True, null=True)
    pan_card = models.FileField(upload_to='', blank=True, null=True)
    bank_statement = models.FileField(upload_to='', blank=True, null=True)
    itr = models.FileField(upload_to='', blank=True, null=True)
    salary_slips = models.JSONField(blank=True, null=True)  
    flat_no = models.CharField(max_length=50,null=True)
    block_no = models.CharField(max_length=50,null=True)
    payout_percentage = models.IntegerField(null=True)
    
    class Meta:
        managed = False,
        db_table = 'loan_applications'

class CorporateProjectDetails(models.Model):
    corporate_name = models.CharField(max_length=255, null=False)
    company_name = models.CharField(max_length=255, null=False)
    gstin = models.CharField(max_length=15, unique=True, null=False)
    company_address = models.TextField(null=False)
    pincode = models.CharField(max_length=6, null=False)
    state = models.CharField(max_length=50, null=False)
    city = models.CharField(max_length=50, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by= models.ForeignKey(User, on_delete=models.CASCADE, related_name='corporate_project_creation')

    class Meta:
        db_table = 'corporate_project_details'
       