# contest/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import ImageEntry
import random

def index(request):
    # Fetch all ImageEntry objects
    entries = list(ImageEntry.objects.all())
    if len(entries) < 2:
        return render(request, 'contest/not_enough.html')

    # 1) Pick one image at random
    img1 = random.choice(entries)

    # 2) Build a list of the remaining entries
    others = [e for e in entries if e.id != img1.id]

    # 3) Find the one with the closest rating to img1.rating
    img2 = min(others, key=lambda e: abs(e.rating - img1.rating))

    return render(request, 'contest/index.html', {
        'img1': img1,
        'img2': img2,
    })


def vote(request):
    if request.method == 'POST':
        winner_id = request.POST.get('winner_id')
        loser_id  = request.POST.get('loser_id')
        if winner_id and loser_id:
            winner = get_object_or_404(ImageEntry, id=winner_id)
            loser  = get_object_or_404(ImageEntry, id=loser_id)

            # --- Elo parameters ---
            K = 32  # K‐factor (you can adjust to taste)

            # Current ratings
            Rw = winner.rating
            Rl = loser.rating

            # Calculate expected scores
            # E_winner = 1 / (1 + 10^((Rl - Rw)/400))
            # E_loser  = 1 / (1 + 10^((Rw - Rl)/400))
            E_winner = 1 / (1 + 10 ** ((Rl - Rw) / 400))
            E_loser  = 1 / (1 + 10 ** ((Rw - Rl) / 400))

            # Actual scores: winner gets 1, loser gets 0
            S_winner = 1
            S_loser  = 0

            # New ratings
            new_Rw = Rw + K * (S_winner - E_winner)
            new_Rl = Rl + K * (S_loser  - E_loser)

            # Update and save
            winner.rating = new_Rw
            loser.rating  = new_Rl
            winner.save()
            loser.save()

            # (Optional) If you still want to track "raw wins," you can also do:
            # winner.score += 1
            # winner.save()

    return redirect('contest:index')


def leaderboard(request):
    # Sort by descending rating (highest Elo first). Tie‐break by name.
    entries = ImageEntry.objects.order_by('-rating', 'name')
    return render(request, 'contest/leaderboard.html', {
        'entries': entries,
    })

def faq_view(request):
    return render(request, 'contest/faq.html')
