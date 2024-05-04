import base64
from django.shortcuts import render, redirect
from django.http import HttpResponse 
from .models import Task
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from To_do_list import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from . tokens import generate_token 
from rest_framework.views import APIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required



class TaskList(ListView):
    model = Task
    context_object_name = 'a'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # # user specific data
        context['a'] = context['a'].filter(user=self.request.user.id)
        context['tot_task'] = len(context['a'])
        context['count'] = context['a'].filter(complete=False).count()

        # For search specific input
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['a'] = context['a'].filter(
                title__istartswith=search_input
            )
            if len(context['a'])==1:
                context['search_flag']=True
            else:
                context['search_flag']=False
            print(context['search_flag'])

        # print(context['search_flag'])
        # To avoid refreshing of search bar
        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'b'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ('title','description','complete',)
    success_url = reverse_lazy('a')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ('title','description','complete')
    success_url = reverse_lazy('a')

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'b'
    success_url = reverse_lazy('a')



def signup(request):

    if request.method=="POST":

        uname = request.POST['uname']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        c_pass = request.POST['c_pass']

        # Required Conditions

        if User.objects.filter(username=uname):
            messages.error(request, "Username already taken.")
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already Registered.")
            return redirect('signup')

        if len(uname)>8:
            messages.error(request, "Username must be under 8 characters.")
            return redirect('signup')

        if pass1 != c_pass:
            messages.error(request, "Password didn't match")
            return redirect('signup')

        if not uname.isalnum():
            messages.error(request, "Username must be Alpha-Numerice")
            return redirect('signup')
        

        myuser = User.objects.create_user(username=uname,email=email,password=pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.email = email
        myuser.is_active = True
        myuser.save()
        # messages.success(request, "Your Account has been Successfully Created.")
        
        user = authenticate(username=uname, password=pass1)

        if user is not None:
            login(request, user)
            return redirect("a")
        else:
            return redirect('signup')
    
    return render(request, "task/signup.html")



def signin(request):

    if request.method=='POST':
        uname = request.POST['uname']
        pass1 = request.POST['pass1']

        user = authenticate(username=uname, password=pass1)

        if user is not None:
            login(request, user)

            return redirect('a')

        elif user is None:
            messages.error(request, "Invalid Inputs!!")
            return redirect('signin')

    return render(request, "task/signin.html")


def signout(request):
    logout(request)

    return redirect('a')


def forgot_password(request):
    if request.method=='POST':
        uname = request.POST['uname']

        try:
            if User.objects.filter(username=uname).first():

                user = User.objects.get(username=uname)
                uid =  urlsafe_base64_encode(force_bytes(user.pk))
                uid = uid + '=='
                token = generate_token.make_token(user)
        
                return render(request, "task/change_password_form.html", {'uid':uid, 'token':token})
            
            else:
                messages.error(request, 'Username not registered')
                return redirect("forgot_password")

        except Exception as e:
            print(e)
            
    return render(request, 'task/forgot_password.html')



def change_password_form(request, uidb64, token):
    if request.method=='POST':

        pass1 = request.POST['pass1']
        c_pass = request.POST['c_pass']

        try:

            if pass1 != c_pass:
                messages.error(request, "Password didn't match")
                return render(request, 'task/change_password_form.html', {'uid':uidb64, 'token':token})
            
            elif pass1 == c_pass:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                user.set_password(pass1)
                user.save()

                messages.success(request, "Password reset succesfully")
                return redirect('signin')

        except Exception as e:
            print(e)
    return render(request, 'task/change_password_form.html', {'uid':uidb64, 'token':token})