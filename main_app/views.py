from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Art, Photo

import uuid  # for generating random strings (what we name our photos)
import boto3  # sdk to interact with aws bucket

# Add these "constants" below the imports
S3_BASE_URL = 'https://s3-us-east-2.amazonaws.com/'
BUCKET = 'start-streetart'


class ArtCreate(LoginRequiredMixin, CreateView):
    model = Art
    fields = ['name', 'artist', 'description']

    # When valid art is added, assign a user as its owner.
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ArtDelete(DeleteView):
    model = Art
    success_url = '/art/'

class ArtUpdate(UpdateView):
    model = Art
    fields = '__all__'
    success_url = '/art/'

def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


@login_required
def art_index(request):
    art = Art.objects.all()
    return render(request, 'art/index.html', {'art': art})


@login_required
def art_detail(request, art_id):
    oneArt = Art.objects.get(id=art_id)
    return render(request, 'art/detail.html', {'oneArt': oneArt})


@login_required
def add_photo(request, art_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + \
            photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            # build the full url string
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # we can assign to art_id or at (if you have an art object)
            photo = Photo(url=url, art_id=art_id)
            photo.save()
        except:
            print('An error occurred uploading file to S3')
    return redirect('art_detail', art_id=art_id)


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('art_index')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)