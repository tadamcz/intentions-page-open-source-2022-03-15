from intentions_page.forms import IntentionEditForm, NoteEditForm
from intentions_page.models import Intention, Note
import django.utils.timezone as timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse
from intentions_page.models import get_working_day_date


def home(request):
    if request.user.is_authenticated:
        working_day_date = get_working_day_date()

        context = {
            'content_by_date': create_day_range(working_day_date, working_day_date, request.user)
        }

        return render(request, 'pages/home.html', context)
    else:
        return render(request, 'pages/welcome.html')


@login_required
def history(request):
    intentions = Intention.objects.filter(creator=request.user)
    notes = Note.objects.filter(creator=request.user)

    end_date = get_working_day_date()

    start_date_candidates = [end_date]
    if intentions:
        start_date_candidates.append(intentions.last().date)
    if notes:
        start_date_candidates.append(notes.last().date)

    start_date = min(start_date_candidates)

    day_range = create_day_range(start_date, end_date, request.user)

    context = {
        'content_by_date': day_range
    }

    return render(request, 'pages/history.html', context)

def create_day(date, user):

    intentions = Intention.objects.filter(creator=user, date=date)

    for i in intentions:
        i.edit_form = IntentionEditForm(instance=i)

    note = Note.objects.filter(creator=user, date=date).first()
    if not note:
        note = Note(creator=user, date=date)
        note.save()

    note.edit_form = NoteEditForm(instance=note)

    return {'intentions': intentions, 'note': note}

def create_day_range(start,end,user):
    day_range = {}

    num_days = (end - start).days + 1

    date_range = (end - timezone.timedelta(days=x) for x in range(num_days))

    for date in date_range:
        day_range[date] = create_day(date, user)

    return day_range

@login_required
def create(request):
    if request.method == 'POST':
        intentions = request.POST['list'].splitlines()
        intentions.reverse()
        for i in intentions:
            if not i.isspace() and not i == "":
                Intention.objects.create(title=i, creator=request.user)

    return redirect('home')


@login_required
def edit(request, primary_key):
    intention = Intention.objects.get(id=primary_key)

    if intention.creator != get_user(request):
        raise PermissionDenied

    if request.method == 'POST':
        form = IntentionEditForm(request.POST, instance=intention)
        form.save()

    return redirect(request.headers.get('Referer', 'home'))


@login_required
def append(request, primary_key):
    if request.method == 'POST':
        intention = Intention.objects.get(id=primary_key)

        if intention.creator != get_user(request):
            raise PermissionDenied

        intention.title += ' ' + request.POST['append']
        intention.save()

    return redirect(request.headers.get('Referer', 'home'))

@login_required
def note(request, primary_key):
    if request.method == 'POST':
        note = Note.objects.get(id=primary_key)
        if note.creator != get_user(request):
            raise PermissionDenied
        if note.version < int(request.POST['version']):
            note.content = request.POST['content']
            note.version = request.POST['version']
            note.save()
            print('saved!')
        return HttpResponse(status=200)

def feedback(request):
    email = request.POST.get("email")
    message = request.POST.get("message")
    message = message.replace('\n', '<br>')
    path = request.path

    html = f"<html>" \
           f"<br><b>path: </b>{path}" \
           f"<br><b>email: </b>{email}" \
           f"<br><b>message: </b>{message}" \
           f"</html>"

    result = send_mail("Feedback on intentions.page", message, recipient_list=['tmkadamcz@gmail.com'], html_message=html, from_email=email)

    if result is 1:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)

def privacy_policy(request):
    return render(request, "privacy-policy.html")
