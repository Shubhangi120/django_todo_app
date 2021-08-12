from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView,FormView
from django.urls import reverse_lazy
from .models import Task
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login #since we do not want the user to login too after registering
# Create your views here.

class OurLogin(LoginView):
    template_name= 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterUser(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):  #user is logged in as soon as it registers
        user = form.save()  #form.save() will return the value as user since it is a user creation form
        if user is not None:
            login(self.request, user)
        return super(RegisterUser, self).form_valid(form)

    def get(self, *args, **kwargs):  #already logged in user should not be able to get to or see register page
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterUser, self).get(*args, **kwargs)

class TaskList(LoginRequiredMixin, ListView):
    model=Task
    context_object_name = 'Tasks'
    
    # overriding the method since we need to modify or customize it as it originally just returns the data we pass through it but we need to ensure a user sees only his data and not others

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #inheriting the original data from superclass
        context['Tasks'] = context['Tasks'].filter(user = self.request.user) #filtering out only that data from the original list that belongs to  the requested user
        context['count'] = context['Tasks'].filter(complete = False).count()
        search_input = self.request.GET.get('search-item') or ''
        if search_input:
            context['Tasks'] = context['Tasks'].filter(title__startswith = search_input)
        context['search_input'] = search_input    #to throw our search input to our template so that we can keep the value in the search box as the search input even after searching an item
        return context

    


class TaskDetail(LoginRequiredMixin,DetailView):
    model=Task
    context_object_name = 'Details'


class TaskCreate(LoginRequiredMixin,CreateView):
    model=Task
    fields= ['title','description','complete']
    success_url = reverse_lazy('tasks')
    
    #modifying the CreateView built-in methos form_valid such that only the requested user's data can be modified
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    
class TaskUpdate(LoginRequiredMixin,UpdateView):
    model=Task
    fields= ['title','description','complete']
    success_url = reverse_lazy('tasks')

class TaskDelete(LoginRequiredMixin, DeleteView):
    model=Task
    context_object_name = 'Tasks'
    success_url = reverse_lazy('tasks')