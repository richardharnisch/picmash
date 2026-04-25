# Image ELO Ranking System — Description

## Overview

A web application where visitors rank a fixed set of images by repeatedly choosing their favourite between two images shown side-by-side. Each comparison updates both images' ELO ratings so the full collection is sorted into a crowd-sourced leaderboard over time.

---

## Core Concept

The system maintains a pool of images. Every page load picks two images and asks the visitor "which do you prefer?". The visitor clicks one image; the result is recorded as a win/loss and both images' ELO ratings are recalculated. No account or login is required. Votes accumulate from all visitors, gradually producing a stable ranking.

---

## Data Model

### Image Entry

Each item in the pool has:

| Field   | Type             | Notes                                      |
|---------|------------------|--------------------------------------------|
| `name`  | short string     | Display label shown below the image        |
| `image` | stored file/URL  | The actual image asset                     |
| `rating`| floating-point   | ELO rating, initialised at **1500**        |

A legacy integer `score` field (raw win count) may optionally be kept but is not used for ranking.

---

## Pages / Routes

| Route          | Purpose                                                                 |
|----------------|-------------------------------------------------------------------------|
| `/`            | **Voting page** — shows two images; visitor clicks one to vote          |
| `/vote/`       | **Vote handler** — accepts a POST with winner/loser IDs, updates ELO, redirects to `/` |
| `/leaderboard/`| **Leaderboard** — table of all images sorted by ELO descending          |
| `/faq/`        | **FAQ** — static explanatory page                                        |

---

## Voting Page Behaviour

1. Load all image entries from the database.
2. If fewer than two entries exist, show an error/notice page.
3. Pick **one image at random** from the full pool (`img1`).
4. From the remaining images, pick the one **closest in ELO rating** to `img1` (`img2`).
5. Render both images side-by-side, each wrapped in a separate form. Each form encodes:
   - `winner_id` — the ID of the image in that form (the one the user is about to vote for)
   - `loser_id`  — the ID of the other image
6. Submitting either form sends a POST to the vote handler.

---

## ELO Update Algorithm

Parameters:
- **K-factor**: 32 (controls how much a single result moves the ratings)
- **Scale factor**: 400 (controls the steepness of the expected-score curve)
- **Default rating**: 1500

Given a winner with rating `Rw` and a loser with rating `Rl`:

```
E_winner = 1 / (1 + 10^((Rl - Rw) / 400))
E_loser  = 1 / (1 + 10^((Rw - Rl) / 400))

new_Rw = Rw + K * (1 - E_winner)
new_Rl = Rl + K * (0 - E_loser)
```

Both updated values are persisted immediately after each vote.

---

## Leaderboard Page Behaviour

- Fetches all image entries ordered by `rating` descending, with `name` as a tiebreaker.
- Displays a ranked table: rank number, thumbnail, name, ELO rating (rounded to integer).
- Links back to the voting page.

---

## Image Management

Images are loaded into the system through an **admin interface** (back-office CRUD). Each entry requires a name and an image file upload. The admin panel also exposes the current rating for each entry (the raw legacy `score` field is read-only there). There is no public-facing upload form; the image pool is curated by the site operator.

---

## Access Control / Anti-Abuse

- No authentication is required to vote.
- No per-visitor deduplication is enforced at this time (the system relies on good-faith voting).
- CSRF protection is applied to the POST vote endpoint.

---

## UI / UX Notes

- Dark-themed interface (dark background, light text).
- On wide/landscape screens the two images are displayed **side-by-side**.
- On narrow/portrait screens (≤ 600 px wide or aspect ratio ≤ 1:1) the layout **stacks vertically**, each image taking up half the viewport height.
- Images scale to fill their container while preserving aspect ratio (`object-fit: contain`).
- A persistent **?** help icon is fixed to the bottom-right corner and links to the FAQ.
- Each pick immediately redirects back to the voting page with a new pair.

---

## Summary of Key Design Decisions

1. **Pair selection** is semi-random: one image is chosen randomly, the other is the closest-rated peer. This ensures comparisons are informative (similar-strength opponents) while still introducing variety.
2. **ELO with K=32** provides moderate sensitivity — a single upset moves ratings by at most 32 points.
3. The image pool is **static** (operator-managed); the site is not designed for user uploads.
4. **No user sessions or accounts** are needed; the product is intentionally lightweight.
5. The leaderboard is **live** — it always reflects the current state of all ratings.
