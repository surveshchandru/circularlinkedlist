from flask import Flask, jsonify, request
from flask_cors import CORS
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from music_playlist import (
    CircularLinkedList, Song, Stack, Queue,
    Searching, Sorting, SAMPLE_DATA
)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Global state (single playlist session)
playlist   = CircularLinkedList()
undo_stack = Stack(capacity=30)
req_queue  = Queue(capacity=15)
_current   = [None]

def song_to_dict(s, idx=None):
    if s is None:
        return None
    return {
        "idx":      idx,
        "title":    s.title,
        "artist":   s.artist,
        "genre":    s.genre,
        "duration": s.duration,
    }

def get_songs_list():
    return [song_to_dict(s, i+1) for i, s in enumerate(playlist.to_list())]

def get_queue_items():
    items = []
    idx = req_queue._front
    while idx != req_queue._rear:
        items.append(req_queue._data[idx])
        idx = (idx + 1) % req_queue._cap
    return items

def get_cll_pointer_info(action_name="current"):
    if _current[0] is None:
        return None
    curr = _current[0]
    is_head = (curr == playlist.head)
    is_tail = (curr == playlist.tail) if playlist.tail else (curr.next == playlist.head)
    next_title = curr.next.title if curr.next else None

    # Find prev title in CLL
    prev_title = None
    if playlist.size > 1:
        p = playlist.head
        while p.next != curr:
            p = p.next
        prev_title = p.title
    elif playlist.size == 1:
        prev_title = curr.title

    wrap_around = is_head and (action_name == "next")
    wrap_prev   = is_tail and (action_name == "prev")

    return {
        "current": song_to_dict(curr),
        "is_head": is_head,
        "is_tail": is_tail,
        "prev_title": prev_title,
        "next_title": next_title,
        "action": action_name,
        "wrap_around": wrap_around or wrap_prev,
        "pointer_expr": f"Node('{prev_title}') <-- [ Node('{curr.title}') ] --> Node('{next_title}')",
        "tail_to_head": f"tail.next == head ('{playlist.tail.title if playlist.tail else ''}' --> '{playlist.head.title if playlist.head else ''}')"
    }

# ── Load sample data at startup ──────────────────────────────────
for t, a, g, d in SAMPLE_DATA:
    s = Song(t, a, g, d)
    playlist.insert_end(s)
_current[0] = playlist.head

# Pre-seed queue with 2 songs so queue is active on launch
if len(SAMPLE_DATA) > 2:
    req_queue.enqueue(SAMPLE_DATA[1][0])
    req_queue.enqueue(SAMPLE_DATA[2][0])


# ── PLAYLIST ROUTES ──────────────────────────────────────────────

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/playlist')
def get_playlist():
    return jsonify({
        "songs":    get_songs_list(),
        "total":    playlist.size,
        "duration": round(playlist.total_duration(), 2),
        "cll":      get_cll_pointer_info("sync")
    })

@app.route('/api/add', methods=['POST'])
def add_song():
    d = request.json or {}
    title    = d.get('title', '').strip()
    artist   = d.get('artist', '').strip()
    genre    = d.get('genre', '').strip() or 'General'
    duration = float(d.get('duration', 3.5))
    position = d.get('position', None)

    if not title:
        return jsonify({"error": "Song title is required"}), 400
    if not artist:
        return jsonify({"error": "Artist name is required"}), 400

    song = Song(title, artist, genre, duration)

    if position is None:
        playlist.insert_end(song)
        pos_desc = "At End (Tail)"
        pointer_desc = f"tail.next = Node('{title}'); Node('{title}').next = head; tail = Node('{title}')"
        time_comp = "O(1) with Tail pointer"
        msg = f"ADD END: '{title}'"
    elif position == 0:
        playlist.insert_beginning(song)
        pos_desc = "At Beginning (Head)"
        pointer_desc = f"Node('{title}').next = head; tail.next = Node('{title}'); head = Node('{title}')"
        time_comp = "O(1) with Tail pointer"
        msg = f"ADD BEGINNING: '{title}'"
    else:
        pos_num = int(position)
        playlist.insert_at_position(song, pos_num)
        pos_desc = f"At Position {pos_num}"
        pointer_desc = f"Traversed {pos_num-1} nodes; prev.next = Node('{title}'); Node('{title}').next = curr"
        time_comp = f"O({pos_num}) Traversal"
        msg = f"ADD POS {pos_num}: '{title}'"

    undo_stack.push(("ADD", title, msg))
    if _current[0] is None:
        _current[0] = playlist.head

    return jsonify({
        "message": f"Successfully inserted '{title}' into Circular Linked List",
        "songs": get_songs_list(),
        "total": playlist.size,
        "cll": get_cll_pointer_info("insert"),
        "ds_reaction": {
            "structure": "Circular Linked List",
            "operation": f"Insert {pos_desc}",
            "pointers": pointer_desc,
            "complexity": time_comp,
            "undo_pushed": f"Undo Stack updated: Size {undo_stack.size()}"
        }
    })

@app.route('/api/remove', methods=['POST'])
def remove_song():
    d = request.json or {}
    title = d.get('title', '').strip()
    if not title:
        return jsonify({"error": "Please specify a song title"}), 400

    # Search case-insensitively in playlist
    songs = playlist.to_list()
    exact_title = None
    for s in songs:
        if s.title.lower() == title.lower() or title.lower() in s.title.lower():
            exact_title = s.title
            break

    target = exact_title if exact_title else title
    deleted = playlist.delete_by_title(target)
    if deleted:
        undo_stack.push(("DELETE", deleted, f"DELETE: '{target}'"))
        if _current[0] and _current[0].title.lower() == target.lower():
            _current[0] = playlist.head

        return jsonify({
            "message": f"Unlinked and removed '{target}' from Circular Linked List",
            "songs": get_songs_list(),
            "total": playlist.size,
            "cll": get_cll_pointer_info("remove"),
            "ds_reaction": {
                "structure": "Circular Linked List & LIFO Stack",
                "operation": "Delete Node & Push to Undo Stack",
                "pointers": f"prev.next = Node('{target}').next; Node('{target}').next = None",
                "complexity": "O(n) Search + O(1) Unlink",
                "undo_pushed": f"Pushed '{target}' to Undo Stack (Top of Stack, Size: {undo_stack.size()})"
            }
        })
    return jsonify({"error": f"'{title}' was not found in playlist"}), 404

@app.route('/api/undo', methods=['POST'])
def undo():
    action = undo_stack.pop()
    if action is None:
        return jsonify({"error": "Undo Stack is empty! Nothing to restore."}), 400

    op = action[0]
    if op == "ADD":
        playlist.delete_by_title(action[1])
        msg = f"Undone addition: removed '{action[1]}'"
        pointers = "Popped ADD action from Stack; unlinked node from CLL"
    else:
        s = action[1]
        s.next = None
        playlist.insert_end(s)
        msg = f"Undone deletion: restored '{s.title}' to Circular List"
        pointers = f"Popped '{s.title}' from Undo Stack; relinked at Tail: tail.next = Node('{s.title}')"

    _current[0] = playlist.head
    return jsonify({
        "message": msg,
        "songs": get_songs_list(),
        "total": playlist.size,
        "cll": get_cll_pointer_info("undo"),
        "ds_reaction": {
            "structure": "LIFO Stack (Undo Buffer)",
            "operation": f"Stack Pop (LIFO) -> {op}",
            "pointers": pointers,
            "complexity": "O(1) Pop",
            "stack_remaining": undo_stack.size()
        }
    })

# ── PLAYBACK ROUTES ──────────────────────────────────────────────

@app.route('/api/now-playing')
def now_playing():
    if _current[0] is None:
        return jsonify({"error": "Playlist is empty"}), 404
    info = get_cll_pointer_info("current")
    res = song_to_dict(_current[0])
    res["cll"] = info
    return jsonify(res)

@app.route('/api/next', methods=['GET', 'POST'])
def next_song():
    if _current[0] is None:
        return jsonify({"error": "Playlist empty"}), 404
    
    was_tail = (_current[0] == playlist.tail) or (_current[0].next == playlist.head)
    _current[0] = _current[0].next
    info = get_cll_pointer_info("next")
    
    res = song_to_dict(_current[0])
    res["cll"] = info
    res["ds_reaction"] = {
        "structure": "Circular Linked List",
        "operation": "Traverse Forward (current = current.next)",
        "pointers": f"Advanced pointer to '{_current[0].title}'",
        "circular_wrap": "🔄 WRAP-AROUND! Traversed from Tail back to Head (tail.next == head)" if was_tail else "Linear forward traversal within loop",
        "complexity": "O(1) Pointer advance"
    }
    return jsonify(res)

@app.route('/api/prev', methods=['GET', 'POST'])
def prev_song():
    if _current[0] is None:
        return jsonify({"error": "Playlist empty"}), 404
    
    was_head = (_current[0] == playlist.head)
    cur = _current[0]
    for _ in range(playlist.size - 1):
        cur = cur.next
    _current[0] = cur
    info = get_cll_pointer_info("prev")

    res = song_to_dict(_current[0])
    res["cll"] = info
    res["ds_reaction"] = {
        "structure": "Circular Linked List",
        "operation": "Traverse Backward (loop n-1 steps)",
        "pointers": f"Pointer now at '{_current[0].title}'",
        "circular_wrap": "🔄 WRAP-AROUND! Reversed from Head to Tail via loop" if was_head else "Backward traversal via CLL cycle",
        "complexity": "O(n) in singly Circular Linked List"
    }
    return jsonify(res)

@app.route('/api/select', methods=['POST'])
def select_song():
    d = request.json or {}
    title = d.get('title', '').strip()
    songs = playlist.to_list()
    found = None
    for s in songs:
        if s.title.lower() == title.lower() or title.lower() in s.title.lower():
            found = s
            break
    if found:
        _current[0] = found
        res = song_to_dict(found)
        res["cll"] = get_cll_pointer_info("select")
        res["ds_reaction"] = {
            "structure": "Circular Linked List",
            "operation": f"Direct Node Selection ('{found.title}')",
            "pointers": f"Current pointer set directly to Node('{found.title}')",
            "complexity": "O(1) pointer assignment"
        }
        return jsonify(res)
    return jsonify({"error": "Song not found"}), 404

# ── SEARCH ROUTES ────────────────────────────────────────────────

@app.route('/api/search')
def search():
    query  = request.args.get('q', '').strip()
    stype  = request.args.get('type', 'smart')
    songs  = playlist.to_list()

    if not query:
        return jsonify({
            "results": [song_to_dict(s) for s in songs],
            "comparisons": 0,
            "method": "All Songs",
            "ds_reaction": {
                "structure": "Playlist Array Export",
                "operation": "Full List Retrieval",
                "complexity": "O(n)"
            }
        })

    results = []
    comps   = 0

    if stype == 'smart':
        q_l = query.lower()
        for s in songs:
            comps += 1
            if q_l in s.title.lower() or q_l in s.artist.lower() or q_l in s.genre.lower():
                results.append(song_to_dict(s))
        method = "Smart Search (Title / Artist / Genre)"
        comp_formula = f"Examined {comps} of {len(songs)} nodes"
        complexity = f"O(n) [n={len(songs)}]"

    elif stype == 'linear_title':
        q_l = query.lower()
        for s in songs:
            comps += 1
            if q_l in s.title.lower():
                results.append(song_to_dict(s))
        method = "Linear Search (Title)"
        comp_formula = f"{comps} sequential string comparisons"
        complexity = f"O(n)"

    elif stype == 'binary_title':
        ss, _, _ = Sorting.bubble_sort_by_title(songs)
        lo, hi = 0, len(ss) - 1
        found = None
        q_l = query.lower()
        while lo <= hi:
            comps += 1
            mid = (lo + hi) // 2
            mid_t = ss[mid].title.lower()
            if mid_t == q_l or mid_t.startswith(q_l):
                found = ss[mid]
                break
            elif mid_t < q_l:
                lo = mid + 1
            else:
                hi = mid - 1
        if found:
            results = [song_to_dict(found)]
        else:
            for s in ss:
                comps += 1
                if q_l in s.title.lower():
                    results.append(song_to_dict(s))
        method = "Binary Search (Title O(log n))"
        comp_formula = f"{comps} divide-and-conquer comparisons on sorted array"
        complexity = f"O(log n) [log2({len(songs)}) ≈ 3-4]"

    elif stype == 'artist':
        q_l = query.lower()
        for s in songs:
            comps += 1
            if q_l in s.artist.lower():
                results.append(song_to_dict(s))
        method = "Linear Search (Artist)"
        comp_formula = f"{comps} comparisons"
        complexity = "O(n)"

    elif stype == 'genre':
        results_raw, comps = Searching.linear_search_by_genre(songs, query)
        if not results_raw:
            q_l = query.lower()
            for s in songs:
                if q_l in s.genre.lower():
                    results_raw.append(s)
        results = [song_to_dict(s) for s in results_raw]
        method  = "Linear Search (Genre)"
        comp_formula = f"{comps} genre checks"
        complexity = "O(n)"

    elif stype == 'binary_duration':
        try:
            dur = float(query)
            ds, _, _ = Sorting.insertion_sort_by_duration(songs)
            for s in ds:
                comps += 1
                if abs(s.duration - dur) <= 0.5:
                    results.append(song_to_dict(s))
            method = f"Duration Search (~{dur}m)"
            comp_formula = f"Scanned sorted durations around {dur}m"
            complexity = "O(log n) + O(k)"
        except ValueError:
            return jsonify({"error": "Duration search expects a number (e.g. 4.0)"}), 400
    else:
        return jsonify({"error": "Unknown search type"}), 400

    return jsonify({
        "results": results,
        "comparisons": comps,
        "method": method,
        "ds_reaction": {
            "structure": "Searching Algorithm Engine",
            "operation": method,
            "matches": len(results),
            "comparisons": comps,
            "formula": comp_formula,
            "complexity": complexity
        }
    })

# ── SORT ROUTES ──────────────────────────────────────────────────

@app.route('/api/sort', methods=['POST'])
def sort_playlist():
    d = request.json or {}
    by = d.get('by', 'title')
    songs = playlist.to_list()

    if by == 'title':
        s, swaps, comps = Sorting.bubble_sort_by_title(songs)
        method = "Bubble Sort (Alphabetical by Title)"
        comp_desc = f"{comps} comparisons, {swaps} adjacent element swaps"
        complexity = "O(n²) Time | O(1) Auxiliary Space"
    elif by == 'duration':
        s, swaps, comps = Sorting.insertion_sort_by_duration(songs)
        method = "Insertion Sort (Duration Ascending)"
        comp_desc = f"{comps} comparisons, {swaps} shift insertions"
        complexity = "O(n²) Worst / O(n) Best | In-place"
    elif by == 'artist':
        s, swaps, comps = Sorting.selection_sort_by_artist(songs)
        method = "Selection Sort (Artist Name)"
        comp_desc = f"{comps} comparisons, {swaps} minimum swaps"
        complexity = "O(n²) Time | O(1) Space"
    else:
        return jsonify({"error": "Unknown sort key"}), 400

    playlist.rebuild_from_list(s)
    _current[0] = playlist.head
    return jsonify({
        "message": f"Successfully sorted Circular Playlist by {by} via {method}",
        "comparisons": comps,
        "swaps": swaps,
        "songs": get_songs_list(),
        "cll": get_cll_pointer_info("sort"),
        "ds_reaction": {
            "structure": "Sorting Algorithm & Circular Linked List Rebuild",
            "algorithm": method,
            "stats": comp_desc,
            "rebuild": "Pointers sequentially rebuilt: node[i].next = node[i+1]; tail.next = head (Circular invariant restored!)",
            "complexity": complexity
        }
    })

# ── QUEUE ROUTES ─────────────────────────────────────────────────

@app.route('/api/queue/request', methods=['POST'])
def request_song():
    d = request.json or {}
    title = d.get('title', '').strip()
    if not title:
        return jsonify({"error": "Please provide a song title to queue"}), 400

    songs = playlist.to_list()
    found = None
    for s in songs:
        if s.title.lower() == title.lower():
            found = s
            break
    if not found:
        for s in songs:
            if title.lower() in s.title.lower() or title.lower() in s.artist.lower():
                found = s
                break

    resolved_title = found.title if found else title
    old_rear = req_queue._rear

    if req_queue.enqueue(resolved_title):
        new_rear = req_queue._rear
        return jsonify({
            "message": f"Enqueued '{resolved_title}' into FIFO Request Queue",
            "queue": get_queue_items(),
            "queue_size": req_queue.size(),
            "ds_reaction": {
                "structure": "Circular Array Queue (FIFO)",
                "operation": f"Enqueue ('{resolved_title}')",
                "pointers": f"rear = (rear + 1) % cap  -> ({old_rear} + 1) % {req_queue._cap} = {new_rear}",
                "front_idx": req_queue._front,
                "rear_idx": new_rear,
                "capacity": req_queue._cap - 1,
                "complexity": "O(1) Time | O(1) Space"
            }
        })
    return jsonify({"error": "Queue is full (capacity 15)"}), 400

@app.route('/api/queue/play-next', methods=['GET', 'POST'])
def play_next_requested():
    old_front = req_queue._front
    title = req_queue.dequeue()

    if title is None:
        if _current[0]:
            _current[0] = _current[0].next
        return jsonify({
            "message": "Queue was empty! Advanced to next song in Circular Playlist instead.",
            "song": song_to_dict(_current[0]) if _current[0] else None,
            "queue": get_queue_items(),
            "cll": get_cll_pointer_info("next"),
            "ds_reaction": {
                "structure": "Queue Empty Fallback",
                "operation": "Default CLL Traversal",
                "complexity": "O(1)"
            }
        })

    new_front = req_queue._front
    songs = playlist.to_list()
    found = None
    for s in songs:
        if s.title.lower() == title.lower() or title.lower() in s.title.lower():
            found = s
            break

    if found:
        _current[0] = found
        target_song = song_to_dict(found)
    else:
        target_song = {"title": title, "artist": "Requested Guest", "genre": "Custom", "duration": 3.2, "idx": None}

    return jsonify({
        "message": f"Dequeued '{title}' from FIFO Queue -> Now Playing in Circular Linked List!",
        "song": target_song,
        "queue": get_queue_items(),
        "cll": get_cll_pointer_info("queue_play"),
        "ds_reaction": {
            "structure": "FIFO Queue -> Circular Linked List Handover",
            "operation": f"Dequeue (FIFO): '{title}'",
            "pointers": f"front = (front + 1) % cap  -> ({old_front} + 1) % {req_queue._cap} = {new_front}",
            "handover": f"Connected Workflow: Dequeued from FIFO Queue -> Set CLL current pointer to Node('{title}')",
            "complexity": "O(1) Dequeue + O(1) Playback Pointer Update"
        }
    })

@app.route('/api/queue')
def get_queue():
    return jsonify({
        "queue": get_queue_items(),
        "size": req_queue.size(),
        "capacity": req_queue._cap - 1,
        "front": req_queue._front,
        "rear": req_queue._rear
    })

# ── STATS ROUTE ──────────────────────────────────────────────────

@app.route('/api/stats')
def stats():
    songs = playlist.to_list()
    if not songs:
        return jsonify({"error": "Playlist empty"}), 404

    total   = sum(s.duration for s in songs)
    avg     = total / len(songs)
    longest = max(songs, key=lambda s: s.duration)
    shortest= min(songs, key=lambda s: s.duration)
    genres  = {}
    for s in songs:
        genres[s.genre] = genres.get(s.genre, 0) + 1

    return jsonify({
        "total_songs":    playlist.size,
        "total_duration": round(total, 2),
        "avg_duration":   round(avg, 2),
        "longest":        song_to_dict(longest),
        "shortest":       song_to_dict(shortest),
        "undo_size":      undo_stack.size(),
        "queue_size":     req_queue.size(),
        "genres":         genres,
        "cll_head":       playlist.head.title if playlist.head else None,
        "cll_tail":       playlist.tail.title if playlist.tail else None,
        "tail_loops_to_head": True if (playlist.tail and playlist.tail.next == playlist.head) else False
    })

@app.route('/api/history')
def history():
    items = [item[2] for item in reversed(undo_stack._data)]
    return jsonify({
        "history": items,
        "stack_size": undo_stack.size(),
        "capacity": undo_stack._cap
    })

if __name__ == '__main__':
    print("\n  Music Playlist API running at http://127.0.0.1:5000")
    print("  Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)
