from .models import Room

def active_room(request):
    if request.user.is_authenticated:
        if request.user.active_room_id:
            room = Room.objects.get(pk=request.user.active_room_id)

            return {'active_room': room }

    return {'active_room': None}