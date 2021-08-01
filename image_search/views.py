from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

import base64
import io
import json
import logging

from torchvision import models
from torchvision import transforms
from PIL import Image

import spotipy

from .forms import ImageUploadForm

from spotify.views import session_cache_path 

logger = logging.getLogger(__name__)

# load pretrained DenseNet and go straight to evaluation mode for inference
# load as global variable here, to avoid expensive reloads with each request
model = models.densenet121(pretrained=True)
model.eval()

# load mapping of ImageNet index to human-readable label
json_path = f'{settings.IMAGE_CLASSIFICATION_JSON}/imagenet_class_index.json'
imagenet_mapping = json.load(open(json_path))


def transform_image(image_bytes):
    
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)

def get_prediction(image_bytes):
    
    tensor = transform_image(image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    class_name, human_label = imagenet_mapping[predicted_idx]
    return human_label


@login_required
def image_search(request):
    image_uri = None
    predicted_label = None

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            image_bytes = image.file.read()
            # convert and pass the image as base64 string to avoid storing in DB or filesystem
            encoded_img = base64.b64encode(image_bytes).decode('ascii')
            image_uri = 'data:%s;base64,%s' % ('image/jpeg', encoded_img)

            # get predicted label
            try:
                predicted_label = get_prediction(image_bytes)
                results = search(request, predicted_label)
            except RuntimeError as re:
                logger.error("Prediction Error = %s", re) 
    else:
        form = ImageUploadForm()

    context = {
        'form': form,
        'image_uri': image_uri,
        'predicted_label': predicted_label,
        'results': results,
    }
    return render(request, 'image_search.html', context)

def search(request, query):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    search_results = spotify.search(query, limit=10, offset=0, type='track', market=None)

    list_of_suggestions = []
    for track in search_results["tracks"]["items"]:
        list_of_suggestions.append(f'{track["name"]} * {track["artists"][0]["name"]} * {track["album"]["name"]}')
        
    return list_of_suggestions
