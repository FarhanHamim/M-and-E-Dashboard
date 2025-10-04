from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Project, Indicator, IndicatorValue, Cluster


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with additional fields"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    organization = forms.CharField(max_length=200, required=False)
    position = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes
        for field_name, field in self.fields.items():
            placeholder_text = field.label.lower() if field.label else field_name.replace('_', ' ')
            field.widget.attrs.update({
                'class': 'form-input',
                'placeholder': f'Enter {placeholder_text}'
            })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                role='project_user',  # Default role
                phone_number=self.cleaned_data.get('phone_number'),
                organization=self.cleaned_data.get('organization'),
                position=self.cleaned_data.get('position')
            )
        
        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['role', 'phone_number', 'organization', 'position']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'organization': forms.TextInput(attrs={'class': 'form-input'}),
            'position': forms.TextInput(attrs={'class': 'form-input'}),
        }


class ProjectForm(forms.ModelForm):
    """Form for creating/editing projects"""
    
    class Meta:
        model = Project
        fields = [
            'name', 'code', 'description', 'cluster', 'status',
            'start_date', 'end_date', 'budget', 'assigned_users'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'cluster': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'budget': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'assigned_users': forms.CheckboxSelectMultiple(),
        }


class IndicatorForm(forms.ModelForm):
    """Form for creating/editing indicators"""
    
    class Meta:
        model = Indicator
        fields = [
            'name', 'code', 'description', 'indicator_type', 'measurement_unit',
            'target_value', 'frequency', 'projects', 'responsible_user'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'indicator_type': forms.Select(attrs={'class': 'form-select'}),
            'measurement_unit': forms.Select(attrs={'class': 'form-select'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'projects': forms.CheckboxSelectMultiple(),
            'responsible_user': forms.Select(attrs={'class': 'form-select'}),
        }


class IndicatorValueForm(forms.ModelForm):
    """Form for submitting indicator values"""
    
    class Meta:
        model = IndicatorValue
        fields = [
            'indicator', 'project', 'reported_value', 'target_value',
            'reporting_period_start', 'reporting_period_end', 'notes'
        ]
        widgets = {
            'indicator': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'reported_value': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'reporting_period_start': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'reporting_period_end': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter projects and indicators based on user role
        if user:
            if user.profile.is_admin:
                # Admins can see all projects and indicators
                pass
            else:
                # Project users can only see their own projects and indicators
                user_projects = Project.objects.filter(created_by=user, is_active=True)
                self.fields['project'].queryset = user_projects
                
                # Filter indicators based on user's projects
                user_indicators = Indicator.objects.filter(
                    projects__in=user_projects, is_active=True
                ).distinct()
                self.fields['indicator'].queryset = user_indicators


class ProjectUserIndicatorEntryForm(forms.Form):
    """Per-indicator entry form for project users with validation"""
    indicator_id = forms.IntegerField(widget=forms.HiddenInput())
    reported_value = forms.DecimalField(min_value=0, decimal_places=2, max_digits=15)
    target_value = forms.DecimalField(min_value=0, decimal_places=2, max_digits=15, required=False)
    reporting_period_start = forms.DateField()
    reporting_period_end = forms.DateField()
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, indicator: Indicator, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indicator = indicator
        self.user = user
        # UI classes
        self.fields['reported_value'].widget.attrs.update({'class': 'form-input', 'step': '0.01'})
        self.fields['target_value'].widget.attrs.update({'class': 'form-input', 'step': '0.01'})
        self.fields['reporting_period_start'].widget.attrs.update({'class': 'form-input', 'type': 'date'})
        self.fields['reporting_period_end'].widget.attrs.update({'class': 'form-input', 'type': 'date'})
        self.fields['notes'].widget.attrs.update({'class': 'form-textarea'})
        self.fields['indicator_id'].initial = indicator.id

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('reporting_period_start')
        end = cleaned.get('reporting_period_end')
        if start and end and start > end:
            raise forms.ValidationError('Reporting period start cannot be after end date.')
        return cleaned


class ClusterForm(forms.ModelForm):
    """Form for creating/editing clusters"""
    
    class Meta:
        model = Cluster
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class UserEditForm(forms.ModelForm):
    """Form for editing user basic information"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }


class PasswordChangeForm(forms.Form):
    """Form for changing password"""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label='Current Password'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label='Confirm New Password'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        
        return password2
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Your old password was entered incorrectly.')
        return old_password
    
    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
