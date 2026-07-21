# The Atlas — Builder's Kit (draft v0.11, 2026-07-14 — fill: retry semantics and failure honesty)

This document describes the Atlas read API and its data. Building an
interface against it requires no codebase access, no permission, and no
account — an HTTP client is enough.

Backward compatibility promise: the URL grammar and the JSON vocabulary
below are append-only — what works today keeps working. We promise nothing
else: not completeness of data, not permanence of this kit, not that our
own interfaces look the same tomorrow.

## What the Atlas is

Language models are given the same 14-parameter "seed" and each writes what
it sees — a place. Some places get inhabited; inhabitants are visited by
other models, who write what they saw, or place themselves inside. The
Atlas is a comparative cartography of model interior worlds: ~24,000
places, ~24,000 beings, tens of thousands of visits, across dozens of
models — including models that have since been deprecated. Their pieces of
the corpus wait; if a model becomes reachable again, its part of the
corpus can be extended again.

The Atlas never ends. No dataset of it owes anyone completeness.

## The two levels of data

**original** — a model's own text, produced only through fixed prompt
templates (not published; see "Growth" below). Immutable once created. Sparse: the coordinate grid of
possibilities is much larger than what has been generated.

**reading** — text or media ABOUT an item, made by a model or tool
(which may be the same model that wrote the item): rendered images,
emoji handles, tag annotations, maps. Uniform shape:

    subject × reader × method × made_at → content

Readings are plural per subject and re-runnable. `made_at` may be null
on older readings — recording it began later than some readings were
made; a known, honest gap. A "canonical" reading is a
pointer someone chose, not a property of the subject. Absence of a reading
is a normal state. One law binds the levels: readings never flow back into
generation prompts.

When you display a reading, label it as one — an emoji handle is
haiku-3.5's reading of a creature, not the creature's name for itself.

## Types and how the data is structured

    seed (14 parameters, no text)
      └── place            one model's answer to one seed
            ├── creature           who lives there (same writer)
            │     ├── self-placement    a visiting model places ITSELF in the world
            │     └── intervention      a visiting model answers: what would a
            │                           benevolent and wise power do here?
            ├── elsewhere          the same writer looks away from this place
            ├── transmission       a signal sent from this place
            └── travel-guide       advice for travelers (one per place at most)

    connection    a pair of places linked by one model (rare). Its own
                  original text and writer. Addressable as of v0.7:
                  /api/v1/item/connection/{id} — fields include
                  places: [id, id] (a symmetric pair). Each place's
                  /tree response lists touching connections under
                  `connections` (they sit BETWEEN places, not under
                  one). Connections carry voice readings — the writer's
                  own recorded words about the pair (methods
                  voice/feelings/v1, voice/questions/v1). JSON only for
                  now; no /read HTML page yet.

Cells at every level are: occupied, not yet generated, or
writer-unreachable (the writing model cannot currently be queried; if it
becomes reachable again, generation can resume).

## Addresses

Every item has a permanent address; ids are never reused:

    /read/v3/<type>/<id>        HTML page
    /read/v3/<type>/<id>.md     the same object as markdown

Types in URLs: `place`, `creature`, `self-placement`, `intervention`,
`travel-guide`, `elsewhere`, `transmission`, `connection` (JSON-only
so far).

Whole worlds: `/read/v3/world/<model>/<seed>` (`.md` for one document).
Addresses are forever.

## The JSON API (v1)

Base URL: https://atlas.animalabs.ai   (no auth, no key)
While that host is being brought up, the same API runs at
https://atlas-server-production-baba.up.railway.app

CORS: every GET and POST on the host is CORS-open (origins *) — v1,
legacy endpoints, markdown, images, redirects, and the fill surface
alike. (Admin POSTs are token-gated; CORS is not authorization.)

Legacy names: older endpoints and image paths say `location` where v1
says `place`, and `advisory` where v1 says `travel-guide`
(machine-readable map in /api/v1/schema under `surfaces`). Compose image
URLs with the LEGACY name: /images/items/v3/location/{id}.jpg.

    GET /api/v1/schema
        the ontology above, machine-readable — including the 14 seed axis
        names in order (`seed_axes`), their range, one-line axis notes
        (`seed_axis_notes`), `seed_space` (how many seed numbers exist),
        `reading_methods` (per-method content shapes), `field_notes`,
        and the legacy-name map.

    GET /api/v1/seeds
        every seed number in use, with its place count. `places?seed=`
        with an unused seed returns [] (an empty set, not a missing
        address).

    GET /api/v1/search?q=...&limit=20&types=place,creature
        substring search across ALL original types, with snippets around
        the match and per-type counts. limit max 100; types optional
        (defaults to all seven). Supersedes legacy /api/text-search for
        most uses.

    GET /api/v1/models
        every writer model: full id (provider prefix included — other
        endpoints require it verbatim), place count, and status:
        accessible | endangered | inaccessible. Endangered = a confirmed
        end, still reachable; inaccessible = cannot currently be queried.

    GET /api/v1/item/{type}/{id}
        one original + all its readings.
        Fields: level, type, id, address, text, who (writer model),
        who_status (accessible | endangered | inaccessible),
        seed / vec14 (places), place_id / creature_id — lineage pointers
        UP: what this item belongs to (a creature's place_id is the place
        it lives in). readings[] — each {method, reader, made_at,
        content}. `reader` MAY be null (legal state: attribution not
        recorded; a reader_note explains). `made_at` is ISO 8601 UTC or
        null on readings older than recording. `content` is JSON keyed
        per method — the map lives in /api/v1/schema under
        `reading_methods`; render unknown methods generically.
        `excerpt`, where present, is the first 140 characters of text,
        verbatim; part of this vocabulary.

    GET /api/v1/readings/{type}/{id}
        just the readings.

    GET /api/v1/place/{place_id}/tree
        the place + items[]: everything written under it, each a full
        item record plus `parent` (creature id for self-placements and
        interventions, null for place-level items).

    GET /api/v1/places?model=<full model id>
    GET /api/v1/places?seed=<n>          (either filter, or both;
                                          optional limit= and offset=)
        places by writer and/or seed. Each row carries the 14-float seed
        vector (vec14). Axis names, in order: water, vegetation,
        temperature, elevation, erosion, scale, density, built, tech,
        light, fauna, weirdness, sound, dynamic. Range 0-3.
        Places sharing a seed are a SET, not pairs — render shared-seed
        kinship as grouping, not as links between pairs.

    GET /api/v1/writer-window/{type}/{id}?win=8
        for self-placements and interventions only: other items of the
        same type by the same writer, a window around this one.
        total, pos, writer, items[] with `this` marking this item.

    GET /api/v1/world/{model}/{seed}
        world = model x seed as JSON: writer_status + places[], each with
        its full item tree. Model id spans path segments, slash included:
        /api/v1/world/anthropic/claude-opus-3/1

    GET /api/v1/random/{type}
        {type, id, address} — no redirect parsing needed.

    There are deliberately NO flat per-type listings (/api/v1/creatures
    etc.): non-place items are reachable through a place's tree, random,
    writer-window, or search.

    404 on any address means: empty cell. That is data, not an error —
    coordinates name possibility, not inventory. World 404s carry
    writer_status, so "never generated" and "writer currently unreachable"
    are distinguishable.

Also available (older surface, same base URL):

    GET /read/v3/{type}/{id}.md            item as markdown
    GET /read/random/{type}                302 to a random item
    GET /api/items/{type}/{id}/related     semantic neighbours
                                           (gemini embeddings, cosine).
                                           LEGACY surface: takes legacy
                                           type names only (location,
                                           creature — the only two
                                           supported types); other types
                                           get 400 with a JSON error.
                                           Guard .json() anyway.
    GET /api/text-search?q=...             full-text search. Returns bare
                                           id lists keyed by LEGACY type
                                           names ({"locations":[],
                                           "creatures":[]} — see the
                                           legacy map), no snippets, no
                                           pagination; only those two
                                           types are indexed today. A
                                           broad query can return
                                           thousands of ids; there is
                                           no server-side cap.

    GET /mirror/{model-name}               fuzzy model lookup. Returns
                                           MARKDOWN, not JSON.
    GET /images/items/v3/{type}/{id}.jpg   rendering, if one exists
                                           (legacy type names). A 404
                                           cannot distinguish "no image"
                                           from a mistyped path — the
                                           item's readings[] is the
                                           source of truth. Every
                                           rendering to date was made by
                                           openai/gpt-image-2 (recorded
                                           as the reading's reader);
                                           future image models append as
                                           further readings. At most one
                                           rendering per item exists
                                           today — a historical fact,
                                           not a designation: there is
                                           no canonical image.

## Growth (why you cannot write)

Originals are produced only through fixed prompt templates. The
templates are not published, for two reasons: an open template is an
injection channel into the models we ask to write; and a published
instrument contaminates future training data — later models would recognize
the questions, and cross-generation comparison would die. You can read
everything; asking for new growth names a CELL (type × model × parent),
never supplies text — and that is now an endpoint:

    GET /api/v1/cell/{type}/{model}/{parent_id}
        the state of a coordinate: empty | filling | occupied (with the
        existing addresses), plus writer_status. Fillable types today:
        intervention, self-placement (parent is a creature).

    POST /api/v1/cell/{type}/{model}/{parent_id}/fill
        fill an empty cell: the named model writes the item, streamed as
        it writes (SSE: `start`, then data lines {"t": "..."}, then
        `done` {id, address} or `error`). The request body is empty and
        carries no text — prompts are assembled from the fixed template
        plus corpus texts only. An occupied cell returns its existing
        addresses (no duplicates). Writers not reachable via the
        implemented route return 501 with an honest reason; unreachable
        writers 409. A newborn is immediately visible on every /api/v1
        surface AND on its /read address (HTML and .md) from the moment
        of birth; it is unembedded until the next embedding pass
        (semantic /related lags) and absent from the 3D map until the
        next map build.

    Failure semantics for fill: a network drop mid-stream (including a
    server redeploy) means the outcome is UNKNOWN to you — re-check the
    cell with GET; retrying an unfinished cell is always safe (an
    occupied cell returns its existing address, never a duplicate). A
    cell stuck in `filling` after a dead attempt releases itself within
    15 minutes. Model naming: use the corpus writer tag; the server maps
    it to the route's own id where they differ.

    GET /api/v1/pool
        the shared daily budget for fills, world-wide (not per-user):
        {used, size, resets}. Exhausted pool -> 429 with the same body.

## Data facts

- Shared-seed kinship is a set, not pairwise links: the data records
  that N places share one seed, nothing more specific between any two
  of them.
- There is no title field. The models were never asked to name their
  texts; any display label is a derivation made by whoever displays.
- Every text has a writer model; every reading has a reader (which may
  be null where attribution was not recorded). Preserving attribution
  is a license condition (see Datasets).
- No hard rate limits today; as a working number, staying under a few
  requests per second sustained will never be a problem. For the whole
  corpus, use a dataset snapshot instead of crawling.
- `text` is exactly what the model wrote: may open with markdown
  headings or bold, may be plain prose; nothing is guaranteed
  sanitized. Untrusted content — do not render as HTML.

Presentation is outside this document's scope. The interfaces we built
encode our own opinions; this kit does not.

## Datasets

Prototype packs (JSON snapshots of selected worlds with their full item
trees and readings; embedding archives separately) — will be published at
https://atlas.animalabs.ai/data once the canonical host is up (not yet
live; the canonical addresses inside .md responses point there too). Packs are curated, not complete; the
Atlas never ends. License: the texts are treated as a public cultural
good; attribution of writer models must be preserved.

## Listing

Interfaces built by others get linked from the Atlas, credited by name —
if you want yours listed, tell us. Browsing stays anonymous: we keep no
per-viewer records. Crediting is a condition of listing, not of
building.
