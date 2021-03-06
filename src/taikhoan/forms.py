import datetime
from django import forms
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import ThanhVien, NhanVienBoPhan, Khach, TV_GIOITINH_CHOICES

class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = ThanhVien
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        taikhoan = super(UserAdminCreationForm, self).save(commit=False)
        taikhoan.set_password(self.cleaned_data["password1"])
        if commit:
            taikhoan.save()
        return taikhoan


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = ThanhVien
        fields = ('email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class NhanVienBoPhanForm(forms.ModelForm):
    class Meta:
        model = NhanVienBoPhan
        fields = ('thanhvien', 'bophan')

class KhachForm(forms.ModelForm):
    email = forms.EmailField(
        label   ='',
        widget  = forms.EmailInput(
            attrs = {
                "class": "input100",
                "placeholder": "Email",
            }
        )
    )
    class Meta:
        model = Khach
        fields = ['email']

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(KhachForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        # Save the provided password in hashed format
        obj = super(KhachForm, self).save(commit=False)
        if commit:
            obj.save()
            request = self.request
            request.session['id_khach'] = obj.id
        return obj

class LoginForm(forms.Form):
    email = forms.EmailField(
        label   ='',
        widget  = forms.TextInput(
            attrs = {
                "class": "input100",
                "placeholder": "Email",
                "value": "admin@ryan.com",
                "label": "Email"
            }            
        )
    )
    password = forms.CharField(
        label   ='',
        widget  = forms.PasswordInput(
            attrs = {
                "class": "input100",
                "placeholder": "Password",
                "value": "q01225507883",
                "label": 'Mật khẩu'
            }
        )
    )

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email  = data.get("email")
        password  = data.get("password")
        # qs = ThanhVien.objects.filter(email=email)
        # if qs.exists():
            # user email is registered, check active/
            # not_active = qs.filter(is_active=False)
            # if not_active.exists():
                ## not active, check email activation
                # link = reverse("account:resend-activation")
                # reconfirm_msg = """yêu cầu <a href='{resend_link}'> gửi lại email xác nhận</a>.
                # """.format(resend_link = link)
                # confirm_email = EmailActivation.objects.filter(email=email)
                # is_confirmable = confirm_email.confirmable().exists()
                # if is_confirmable:
                    # msg1 = "Vui lòng kiểm tra email để xác nhận tài khoản hoặc " + reconfirm_msg.lower()
                    # raise forms.ValidationError(mark_safe(msg1))
                # email_confirm_exists = EmailActivation.objects.email_exists(email).exists()
                # if email_confirm_exists:
                    # msg2 = "Email chưa được xác nhận. " + reconfirm_msg
                    # raise forms.ValidationError(mark_safe(msg2))
                # if not is_confirmable and not email_confirm_exists:
                    # raise forms.ValidationError("Tài khoản không hoạt động.")


        taikhoan = authenticate(request, username=email, password=password)
        if taikhoan is None:
            raise forms.ValidationError("Email hoặc mậ khẩu sai")
        login(request, taikhoan)
        self.taikhoan = taikhoan
        return data

    # def form_valid(self, form):
    #     request = self.request
    #     next_ = request.GET.get('next')
    #     next_post = request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #     email  = form.cleaned_data.get("email")
    #     password  = form.cleaned_data.get("password")
        
    #     print(user)
    #     if user is not None:
    #         if not user.is_active:
    #             print('inactive user..')
    #             messages.success(request, "This user is inactive")
    #             return super(LoginView, self).form_invalid(form)
    #         login(request, user)
    #         user_logged_in.send(user.__class__, instance=user, request=request)
    #         try:
    #             del request.session['guest_email_id']
    #         except:
    #             pass
    #         if is_safe_url(redirect_path, request.get_host()):
    #             return redirect(redirect_path)
    #         else:
    #             return redirect("/")
    #     return super(LoginView, self).form_invalid(form)

class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    email = forms.EmailField(
        label   ='Email',
        widget  = forms.TextInput(
            attrs = {
                "class": "input100",
            }
        )
    )
    full_name = forms.CharField(
        label   ='Họ tên',
        widget  = forms.TextInput(
            attrs = {
                "class": "input100",
            }
        )
    )
    ngaysinh = forms.DateField(
        label   ='Ngày sinh',
        input_formats=["%d/%m/%Y"],
        widget  = forms.DateInput(
            format=('%d/%m/%Y'),
            attrs = {
                "class": "input100",
            }
        )
    )
    gioitinh = forms.ChoiceField(
        label   = 'Giới tính',
        choices = TV_GIOITINH_CHOICES,
        widget  = forms.Select( 
            attrs = {
                "class": "input100",
            }
        )
    )
    sdt = forms.CharField(
        label   ='Số điện thoại',
        widget  = forms.NumberInput(
            attrs = {
                "class": "input100",
            }
        )
    )
    password1 = forms.CharField(
        label   ='Mật khẩu',
        widget  = forms.PasswordInput(
            attrs = {
                "class": "input100",
                "placeholder": "Password",
                # "value": "q01225507883"
            }
        )
    )
    password2 = forms.CharField(
        label   ='Xác nhận mật khẩu',
        widget  = forms.PasswordInput(
            attrs = {
                "class": "input100",
                "placeholder": "Re-password",
                # "value": "q01225507883"
            }
        )
    )

    class Meta:
        model = ThanhVien
        fields = ('full_name', 'email', 'ngaysinh', 'gioitinh', 'sdt')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = ThanhVien.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email


    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        taikhoan = super(RegisterForm, self).save(commit=False)
        taikhoan.set_password(self.cleaned_data["password1"])
        taikhoan.is_active = True # send confirmation email via signals
        # obj = EmailActivation.objects.create(user=user)
        # obj.send_activation_email()
        if commit:
            taikhoan.save()
        return taikhoan

