"""
=============================================================
  MUSIC PLAYLIST MANAGEMENT SYSTEM
  Data Structure: Circular Linked List
  Additional DSA:
    - Stack       -> Undo History (LIFO)
    - Queue       -> Song Request Queue (FIFO, circular array)
    - Linear Search  -> by title, by genre
    - Binary Search  -> by title, by duration
    - Bubble Sort    -> by title
    - Insertion Sort -> by duration
    - Selection Sort -> by artist
  CO1 – ADT & Linked Lists project
=============================================================
"""

import os
import sys


# =============================================================
#  SECTION 1 - ADT: Song Node (element of CLL)
# =============================================================

class Song:
    """
    Abstract Data Type – Song
    Fields : title, artist, genre, duration, next (CLL pointer)
    """

    def __init__(self, title, artist, genre, duration):
        self.title    = title
        self.artist   = artist
        self.genre    = genre
        self.duration = float(duration)   # in minutes
        self.next     = None              # CLL link

    def __str__(self):
        return (f"[{self.title}] by {self.artist} | "
                f"Genre: {self.genre} | Duration: {self.duration:.2f} min")


# =============================================================
#  SECTION 2 - CIRCULAR LINKED LIST (core data structure)
# =============================================================

class CircularLinkedList:
    """
    Circular Singly Linked List.
      head  ->  first node
      tail  ->  last node  (tail.next == head always)
    All structural invariants maintained after every operation.
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    # ----- INSERT operations -----

    def insert_end(self, song):
        """Insert at end. O(1) thanks to tail pointer."""
        if self.head is None:
            self.head = song
            self.tail = song
            song.next = song          # self-loop
        else:
            self.tail.next = song
            song.next      = self.head
            self.tail      = song
        self.size += 1

    def insert_beginning(self, song):
        """Insert at front. O(1)."""
        if self.head is None:
            self.insert_end(song)
        else:
            song.next      = self.head
            self.tail.next = song
            self.head      = song
            self.size     += 1

    def insert_at_position(self, song, pos):
        """Insert at 1-indexed position. O(n)."""
        if pos <= 1:
            self.insert_beginning(song)
            return
        if pos > self.size:
            self.insert_end(song)
            return
        cur = self.head
        for _ in range(pos - 2):
            cur = cur.next
        song.next = cur.next
        cur.next  = song
        self.size += 1

    # ----- DELETE operation -----

    def delete_by_title(self, title):
        """Delete first match by title. O(n). Returns deleted node or None."""
        if self.head is None:
            return None
        # only one node
        if self.size == 1 and self.head.title.lower() == title.lower():
            deleted   = self.head
            self.head = None
            self.tail = None
            self.size = 0
            return deleted
        # general case
        prev = self.tail
        cur  = self.head
        for _ in range(self.size):
            if cur.title.lower() == title.lower():
                prev.next = cur.next
                if cur == self.head:
                    self.head = cur.next
                if cur == self.tail:
                    self.tail = prev
                self.size -= 1
                return cur
            prev = cur
            cur  = cur.next
        return None   # not found

    # ----- DISPLAY -----

    def display(self):
        """Print formatted table of all songs. O(n)."""
        if self.head is None:
            print("  [!] Playlist is empty.")
            return
        cur = self.head
        print()
        print(f"  {'No.':<5} {'Title':<30} {'Artist':<22} {'Genre':<14} {'Duration':>10}")
        print("  " + "-" * 86)
        for i in range(self.size):
            print(f"  {i+1:<5} {cur.title:<30} {cur.artist:<22} {cur.genre:<14} {cur.duration:>8.2f} min")
            cur = cur.next
        print("  " + "-" * 86)
        print(f"  Total: {self.size} song(s)  |  {self.total_duration():.2f} min")
        print()

    # ----- HELPERS -----

    def to_list(self):
        """Return Python list of Song nodes (does not break CLL)."""
        result = []
        if self.head is None:
            return result
        cur = self.head
        for _ in range(self.size):
            result.append(cur)
            cur = cur.next
        return result

    def rebuild_from_list(self, songs):
        """Reconstruct CLL from a Python list of Song nodes."""
        self.head = None
        self.tail = None
        self.size = 0
        for s in songs:
            s.next = None
            self.insert_end(s)

    def total_duration(self):
        return sum(s.duration for s in self.to_list())


# =============================================================
#  SECTION 3 - STACK (Undo History — LIFO)
# =============================================================

class Stack:
    """
    Array-based Stack (Last-In First-Out).
    Stores tuples: (operation, data, description_string)
    Capacity: evicts oldest entry when full.
    """

    def __init__(self, capacity=50):
        self._data     = []
        self._capacity = capacity

    def push(self, item):
        if len(self._data) >= self._capacity:
            self._data.pop(0)   # remove oldest
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self._data.pop()

    def peek(self):
        return self._data[-1] if self._data else None

    def is_empty(self):
        return len(self._data) == 0

    def size(self):
        return len(self._data)

    def display(self):
        if self.is_empty():
            print("  [!] Undo stack is empty.")
            return
        print("\n  Undo History (top -> bottom):")
        for item in reversed(self._data):
            print(f"    <- {item[2]}")
        print()


# =============================================================
#  SECTION 4 - QUEUE (Song Request Queue — FIFO, circular array)
# =============================================================

class Queue:
    """
    Circular Array Queue (First-In First-Out).
    Fixed capacity; uses modular arithmetic for wrap-around.
    """

    def __init__(self, capacity=20):
        self._cap   = capacity + 1      # extra slot to distinguish full/empty
        self._data  = [None] * self._cap
        self._front = 0
        self._rear  = 0

    def enqueue(self, item):
        if self.is_full():
            print("  [!] Request queue is full!")
            return False
        self._data[self._rear] = item
        self._rear = (self._rear + 1) % self._cap
        return True

    def dequeue(self):
        if self.is_empty():
            return None
        item        = self._data[self._front]
        self._front = (self._front + 1) % self._cap
        return item

    def peek(self):
        return None if self.is_empty() else self._data[self._front]

    def is_empty(self):
        return self._front == self._rear

    def is_full(self):
        return (self._rear + 1) % self._cap == self._front

    def size(self):
        return (self._rear - self._front) % self._cap

    def display(self):
        if self.is_empty():
            print("  [!] Request queue is empty.")
            return
        print("\n  Song Request Queue (front -> rear):")
        idx = self._front
        pos = 1
        while idx != self._rear:
            print(f"    {pos}. {self._data[idx]}")
            idx = (idx + 1) % self._cap
            pos += 1
        print()


# =============================================================
#  SECTION 5 - SEARCHING ALGORITHMS
# =============================================================

class Searching:

    @staticmethod
    def linear_search_by_title(songs, title):
        """Linear Search O(n). Works on unsorted data."""
        comps = 0
        for song in songs:
            comps += 1
            if song.title.lower() == title.lower():
                return song, comps
        return None, comps

    @staticmethod
    def linear_search_by_genre(songs, genre):
        """Returns all songs matching genre. O(n)."""
        comps  = 0
        result = []
        for song in songs:
            comps += 1
            if song.genre.lower() == genre.lower():
                result.append(song)
        return result, comps

    @staticmethod
    def binary_search_by_title(songs, title):
        """Binary Search O(log n). Requires title-sorted list."""
        lo, hi = 0, len(songs) - 1
        comps  = 0
        while lo <= hi:
            mid   = (lo + hi) // 2
            comps += 1
            if songs[mid].title.lower() == title.lower():
                return songs[mid], comps
            elif songs[mid].title.lower() < title.lower():
                lo = mid + 1
            else:
                hi = mid - 1
        return None, comps

    @staticmethod
    def binary_search_by_duration(songs, duration):
        """Binary Search O(log n). Requires duration-sorted list."""
        lo, hi = 0, len(songs) - 1
        comps  = 0
        while lo <= hi:
            mid   = (lo + hi) // 2
            comps += 1
            if songs[mid].duration == duration:
                return songs[mid], comps
            elif songs[mid].duration < duration:
                lo = mid + 1
            else:
                hi = mid - 1
        return None, comps


# =============================================================
#  SECTION 6 - SORTING ALGORITHMS
# =============================================================

class Sorting:

    @staticmethod
    def bubble_sort_by_title(songs):
        """Bubble Sort O(n^2). Sorts alphabetically by title."""
        arr   = songs[:]
        n     = len(arr)
        swaps = 0
        comps = 0
        for i in range(n - 1):
            for j in range(n - i - 1):
                comps += 1
                if arr[j].title.lower() > arr[j + 1].title.lower():
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swaps += 1
        return arr, swaps, comps

    @staticmethod
    def insertion_sort_by_duration(songs):
        """Insertion Sort O(n^2) worst / O(n) best. Sorts by duration."""
        arr   = songs[:]
        swaps = 0
        comps = 0
        for i in range(1, len(arr)):
            key = arr[i]
            j   = i - 1
            while j >= 0:
                comps += 1
                if arr[j].duration > key.duration:
                    arr[j + 1] = arr[j]
                    j         -= 1
                    swaps     += 1
                else:
                    break
            arr[j + 1] = key
        return arr, swaps, comps

    @staticmethod
    def selection_sort_by_artist(songs):
        """Selection Sort O(n^2). Sorts alphabetically by artist."""
        arr   = songs[:]
        n     = len(arr)
        swaps = 0
        comps = 0
        for i in range(n):
            min_i = i
            for j in range(i + 1, n):
                comps += 1
                if arr[j].artist.lower() < arr[min_i].artist.lower():
                    min_i = j
            if min_i != i:
                arr[i], arr[min_i] = arr[min_i], arr[i]
                swaps += 1
        return arr, swaps, comps


# =============================================================
#  SECTION 7 - PLAYLIST CONTROLLER (orchestrator)
# =============================================================

class PlaylistController:
    """Ties together CLL, Stack, Queue, Searching, Sorting."""

    def __init__(self, name="My Playlist"):
        self.name       = name
        self.playlist   = CircularLinkedList()
        self.undo_stack = Stack(capacity=30)
        self.req_queue  = Queue(capacity=15)
        self._current   = None    # currently playing node

    # -- Add / Remove ------------------------------------------

    def add_song(self, title, artist, genre, duration, position=None):
        song = Song(title, artist, genre, duration)
        if position is None:
            self.playlist.insert_end(song)
            msg = f"ADD END: '{title}'"
        elif position == 0:
            self.playlist.insert_beginning(song)
            msg = f"ADD BEGINNING: '{title}'"
        else:
            self.playlist.insert_at_position(song, position)
            msg = f"ADD POS {position}: '{title}'"
        self.undo_stack.push(("ADD", title, msg))
        if self._current is None:
            self._current = self.playlist.head
        print(f"  [+] Added: {song}")

    def remove_song(self, title):
        deleted = self.playlist.delete_by_title(title)
        if deleted:
            self.undo_stack.push(("DELETE", deleted, f"DELETE: '{title}'"))
            print(f"  [-] Removed: {deleted}")
            self._current = self.playlist.head
        else:
            print(f"  [!] Song '{title}' not found.")

    def undo_last(self):
        action = self.undo_stack.pop()
        if action is None:
            print("  [!] Nothing to undo.")
            return
        op = action[0]
        if op == "ADD":
            self.playlist.delete_by_title(action[1])
            print(f"  [<] Undone ADD: removed '{action[1]}'.")
        elif op == "DELETE":
            s = action[1]; s.next = None
            self.playlist.insert_end(s)
            print(f"  [<] Undone DELETE: restored '{s.title}'.")

    # -- Playback ----------------------------------------------

    def now_playing(self):
        if self._current is None:
            print("  [!] Playlist is empty.")
        else:
            print(f"\n  [>] Now Playing: {self._current}")

    def next_song(self):
        if self._current is None:
            print("  [!] Playlist is empty.")
        else:
            self._current = self._current.next
            print(f"  [>>] Next: {self._current}")

    def prev_song(self):
        if self._current is None:
            print("  [!] Playlist is empty.")
        else:
            cur = self._current
            for _ in range(self.playlist.size - 1):
                cur = cur.next
            self._current = cur
            print(f"  [<<] Previous: {self._current}")

    # -- Queue -------------------------------------------------

    def request_song(self, title):
        songs = self.playlist.to_list()
        found, _ = Searching.linear_search_by_title(songs, title)
        if found:
            self.req_queue.enqueue(found.title)
            print(f"  [Q] '{title}' added to request queue.")
        else:
            print(f"  [!] '{title}' not in playlist.")

    def play_next_requested(self):
        title = self.req_queue.dequeue()
        if title is None:
            print("  [!] Request queue empty. Playing next normally.")
            self.next_song()
        else:
            songs = self.playlist.to_list()
            found, _ = Searching.linear_search_by_title(songs, title)
            if found:
                self._current = found
                print(f"  [>] Playing requested: {self._current}")
            else:
                print(f"  [!] Requested song '{title}' no longer in playlist.")

    # -- Searching ---------------------------------------------

    def search_by_title_linear(self, title):
        songs        = self.playlist.to_list()
        found, comps = Searching.linear_search_by_title(songs, title)
        print(f"\n  Linear Search | title='{title}' | comparisons={comps}")
        print(f"  {'[FOUND] ' + str(found) if found else '[NOT FOUND]'}")
        return found

    def search_by_title_binary(self, title):
        songs          = self.playlist.to_list()
        sorted_s, _, _ = Sorting.bubble_sort_by_title(songs)
        found, comps   = Searching.binary_search_by_title(sorted_s, title)
        print(f"\n  Binary Search (title) | '{title}' | comparisons={comps}")
        print(f"  {'[FOUND] ' + str(found) if found else '[NOT FOUND]'}")
        return found

    def search_by_genre(self, genre):
        songs          = self.playlist.to_list()
        results, comps = Searching.linear_search_by_genre(songs, genre)
        print(f"\n  Genre Search | genre='{genre}' | comparisons={comps}")
        if results:
            for s in results:
                print(f"    [+] {s}")
        else:
            print(f"  [NOT FOUND] No songs in genre '{genre}'.")

    def search_by_duration_binary(self, duration):
        songs          = self.playlist.to_list()
        ds, _, _       = Sorting.insertion_sort_by_duration(songs)
        found, comps   = Searching.binary_search_by_duration(ds, duration)
        print(f"\n  Binary Search (duration) | {duration} min | comparisons={comps}")
        print(f"  {'[FOUND] ' + str(found) if found else '[NOT FOUND]'}")

    # -- Sorting -----------------------------------------------

    def sort_by_title(self):
        songs            = self.playlist.to_list()
        s, swaps, comps  = Sorting.bubble_sort_by_title(songs)
        self.playlist.rebuild_from_list(s); self._current = self.playlist.head
        print(f"\n  [OK] Bubble Sort by Title | comps={comps} | swaps={swaps}")
        self.playlist.display()

    def sort_by_duration(self):
        songs            = self.playlist.to_list()
        s, swaps, comps  = Sorting.insertion_sort_by_duration(songs)
        self.playlist.rebuild_from_list(s); self._current = self.playlist.head
        print(f"\n  [OK] Insertion Sort by Duration | comps={comps} | swaps={swaps}")
        self.playlist.display()

    def sort_by_artist(self):
        songs            = self.playlist.to_list()
        s, swaps, comps  = Sorting.selection_sort_by_artist(songs)
        self.playlist.rebuild_from_list(s); self._current = self.playlist.head
        print(f"\n  [OK] Selection Sort by Artist | comps={comps} | swaps={swaps}")
        self.playlist.display()

    # -- Statistics --------------------------------------------

    def show_statistics(self):
        songs = self.playlist.to_list()
        if not songs:
            print("  [!] Playlist is empty."); return
        total    = sum(s.duration for s in songs)
        avg      = total / len(songs)
        longest  = max(songs, key=lambda s: s.duration)
        shortest = min(songs, key=lambda s: s.duration)
        genres   = {}
        for s in songs:
            genres[s.genre] = genres.get(s.genre, 0) + 1
        print(f"\n  {'='*60}")
        print(f"  STATISTICS  -  {self.name}")
        print(f"  {'='*60}")
        print(f"  Total Songs      : {self.playlist.size}")
        print(f"  Total Duration   : {total:.2f} min")
        print(f"  Average Duration : {avg:.2f} min")
        print(f"  Longest Song     : {longest.title} ({longest.duration:.2f} min)")
        print(f"  Shortest Song    : {shortest.title} ({shortest.duration:.2f} min)")
        print(f"  Undo Stack Size  : {self.undo_stack.size()}")
        print(f"  Request Queue    : {self.req_queue.size()}")
        print(f"  {'-'*60}")
        print(f"  Genre Breakdown:")
        for g, c in sorted(genres.items()):
            print(f"    {g:<20}: {'#'*c} ({c})")
        print(f"  {'='*60}\n")


# =============================================================
#  SECTION 8 - INTERACTIVE CLI MENU
# =============================================================

SAMPLE_DATA = [
    ("Blinding Lights",        "The Weeknd",       "Pop",      3.20),
    ("Hotel California",       "Eagles",            "Rock",     6.30),
    ("Bohemian Rhapsody",      "Queen",             "Rock",     5.55),
    ("Shape of You",           "Ed Sheeran",        "Pop",      3.53),
    ("Believer",               "Imagine Dragons",   "Pop Rock", 3.24),
    ("Lose Yourself",          "Eminem",            "Hip-Hop",  5.26),
    ("Perfect",                "Ed Sheeran",        "Pop",      4.23),
    ("Stairway to Heaven",     "Led Zeppelin",      "Rock",     8.02),
    ("Rolling in the Deep",    "Adele",             "Soul",     3.48),
    ("Smells Like Teen Spirit","Nirvana",           "Grunge",   5.01),
]


def clr():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print("""
  ============================================================
        MUSIC PLAYLIST MANAGEMENT SYSTEM
        Data Structure  :  Circular Linked List
        Stack (Undo)  |  Queue (Requests)
        Linear & Binary Search  |  3 Sorting Algorithms
  ============================================================
""")


def menu():
    print("""
  --- PLAYLIST -------------------------------------------
   [1] Add Song (end)          [2] Add Song (beginning)
   [3] Add Song (at position)  [4] Remove Song
   [5] Display Playlist
  --- PLAYBACK --------------------------------------------
   [6] Now Playing             [7] Next Song
   [8] Previous Song
  --- SEARCH ----------------------------------------------
   [9] Search by Title (Linear)  [10] Search by Title (Binary)
  [11] Search by Genre          [12] Search by Duration (Binary)
  --- SORT ------------------------------------------------
  [13] Sort by Title (Bubble)   [14] Sort by Duration (Insertion)
  [15] Sort by Artist (Selection)
  --- QUEUE & STACK ---------------------------------------
  [16] Request Song (Enqueue)   [17] Play Next Requested
  [18] View Request Queue       [19] Undo Last Operation
  [20] View Undo History
  --- INFO ------------------------------------------------
  [21] Statistics               [0] Exit
  ---------------------------------------------------------
""")


def get_song():
    t = input("    Title    : ").strip()
    a = input("    Artist   : ").strip()
    g = input("    Genre    : ").strip()
    while True:
        try:
            d = float(input("    Duration (min): ").strip())
            break
        except ValueError:
            print("    [!] Enter a valid number.")
    return t, a, g, d


def run_interactive():
    clr(); banner()
    name = input("  Playlist name (Enter = 'My Playlist'): ").strip() or "My Playlist"
    ctrl = PlaylistController(name)
    if input("  Load sample songs? (y/n): ").strip().lower() == "y":
        print()
        for t, a, g, d in SAMPLE_DATA:
            ctrl.add_song(t, a, g, d)
        print("  [OK] Sample data loaded!\n")

    while True:
        menu()
        opt = input("  Enter option: ").strip()

        if   opt == "1":
            print("\n  -- Add at End --")
            t, a, g, d = get_song(); ctrl.add_song(t, a, g, d)
        elif opt == "2":
            print("\n  -- Add at Beginning --")
            t, a, g, d = get_song(); ctrl.add_song(t, a, g, d, position=0)
        elif opt == "3":
            print("\n  -- Add at Position --")
            t, a, g, d = get_song()
            while True:
                try:
                    p = int(input("    Position: ").strip()); break
                except ValueError:
                    print("    [!] Integer required.")
            ctrl.add_song(t, a, g, d, position=p)
        elif opt == "4":
            ctrl.remove_song(input("\n  Title to remove: ").strip())
        elif opt == "5":
            ctrl.playlist.display()
        elif opt == "6":
            ctrl.now_playing()
        elif opt == "7":
            ctrl.next_song()
        elif opt == "8":
            ctrl.prev_song()
        elif opt == "9":
            ctrl.search_by_title_linear(input("\n  Title (Linear): ").strip())
        elif opt == "10":
            ctrl.search_by_title_binary(input("\n  Title (Binary): ").strip())
        elif opt == "11":
            ctrl.search_by_genre(input("\n  Genre: ").strip())
        elif opt == "12":
            while True:
                try:
                    d = float(input("\n  Duration (min): ").strip()); break
                except ValueError:
                    print("  [!] Number required.")
            ctrl.search_by_duration_binary(d)
        elif opt == "13":
            ctrl.sort_by_title()
        elif opt == "14":
            ctrl.sort_by_duration()
        elif opt == "15":
            ctrl.sort_by_artist()
        elif opt == "16":
            ctrl.request_song(input("\n  Title to request: ").strip())
        elif opt == "17":
            ctrl.play_next_requested()
        elif opt == "18":
            ctrl.req_queue.display()
        elif opt == "19":
            ctrl.undo_last()
        elif opt == "20":
            ctrl.undo_stack.display()
        elif opt == "21":
            ctrl.show_statistics()
        elif opt == "0":
            print("\n  Goodbye!\n"); break
        else:
            print("  [!] Invalid option.")

        input("\n  Press Enter to continue...")
        clr(); banner()


# =============================================================
#  SECTION 9 - AUTOMATED TEST SUITE
# =============================================================

def run_tests():
    passed = 0; failed = 0

    def t(desc, cond):
        nonlocal passed, failed
        tag = "[PASS]" if cond else "[FAIL]"
        if cond: passed += 1
        else:    failed += 1
        print(f"  {tag}  {desc}")

    sep = "=" * 65
    print(f"\n{sep}")
    print("  AUTOMATED TEST SUITE")
    print(sep)

    # A. Circular Linked List
    print("\n  [A] Circular Linked List")
    c = CircularLinkedList()
    s1 = Song("Alpha","A1","Pop",3.0)
    s2 = Song("Beta", "A2","Rock",4.0)
    s3 = Song("Gamma","A3","Jazz",2.5)

    c.insert_end(s1)
    t("TC-A1  insert_end size==1",       c.size == 1)
    t("TC-A2  single-node self-loop",    c.head.next == c.head)
    c.insert_end(s2)
    t("TC-A3  tail.next==head after 2",  c.tail.next == c.head)
    c.insert_beginning(s3)
    t("TC-A4  insert_beginning head=Gamma", c.head.title == "Gamma")
    t("TC-A5  size==3",                  c.size == 3)
    t("TC-A6  tail still circular",      c.tail.next == c.head)
    d = c.delete_by_title("Beta")
    t("TC-A7  delete returns node",      d is not None)
    t("TC-A8  deleted title correct",    d.title == "Beta")
    t("TC-A9  size==2 after delete",     c.size == 2)
    t("TC-A10 delete missing -> None",   c.delete_by_title("X") is None)
    t("TC-A11 total_duration==5.5",      abs(c.total_duration()-5.5)<0.001)

    c2 = CircularLinkedList()
    for x in ["A","B","D"]: c2.insert_end(Song(x,"X","Pop",1.0))
    c2.insert_at_position(Song("C","X","Pop",1.0), 3)
    t("TC-A12 insert_at_position 3",
      [s.title for s in c2.to_list()] == ["A","B","C","D"])

    # B. Stack
    print("\n  [B] Stack (Undo History)")
    st = Stack(3)
    st.push(("ADD","T1","ADD END: 'T1'"))
    st.push(("ADD","T2","ADD END: 'T2'"))
    t("TC-B1  peek == last pushed",     st.peek()[1] == "T2")
    t("TC-B2  size==2",                 st.size() == 2)
    v = st.pop()
    t("TC-B3  pop returns T2",          v[1] == "T2")
    t("TC-B4  size==1 after pop",       st.size() == 1)
    st.pop()
    t("TC-B5  pop empty -> None",       st.pop() is None)
    t("TC-B6  is_empty after all pops", st.is_empty())

    # C. Queue
    print("\n  [C] Queue (Request Queue)")
    q = Queue(3)
    t("TC-C1  new queue is_empty",      q.is_empty())
    q.enqueue("Song A"); q.enqueue("Song B")
    t("TC-C2  peek front == Song A",    q.peek() == "Song A")
    t("TC-C3  size==2",                 q.size() == 2)
    v = q.dequeue()
    t("TC-C4  dequeue -> Song A",       v == "Song A")
    t("TC-C5  size==1 after dequeue",   q.size() == 1)
    q.enqueue("Song C"); q.enqueue("Song D")
    t("TC-C6  is_full",                 q.is_full())
    t("TC-C7  enqueue full -> False",   q.enqueue("X") == False)
    q.dequeue(); q.dequeue(); q.dequeue()
    t("TC-C8  dequeue empty -> None",   q.dequeue() is None)

    # D. Searching
    print("\n  [D] Searching Algorithms")
    songs = [Song("Apple","A1","Pop",2.0), Song("Banana","A2","Rock",3.0), Song("Cherry","A3","Pop",4.0)]
    f, c = Searching.linear_search_by_title(songs, "Banana")
    t("TC-D1  linear finds Banana",     f is not None)
    t("TC-D2  comparisons==2",          c == 2)
    nf, c2 = Searching.linear_search_by_title(songs, "Mango")
    t("TC-D3  linear miss -> None",     nf is None)
    t("TC-D4  miss scans all (3)",      c2 == 3)
    gr, _ = Searching.linear_search_by_genre(songs, "Pop")
    t("TC-D5  genre search 2 Pop",      len(gr) == 2)
    ss, _, _ = Sorting.bubble_sort_by_title(songs[:])
    fb, _ = Searching.binary_search_by_title(ss, "Cherry")
    t("TC-D6  binary finds Cherry",     fb is not None)
    t("TC-D7  binary miss -> None",     Searching.binary_search_by_title(ss,"Zebra")[0] is None)
    ds, _, _ = Sorting.insertion_sort_by_duration(songs[:])
    fd, _ = Searching.binary_search_by_duration(ds, 3.0)
    t("TC-D8  binary duration 3.0",     fd is not None and fd.duration == 3.0)

    # E. Sorting
    print("\n  [E] Sorting Algorithms")
    songs2 = [Song("Mango","Charlie","Pop",5.0), Song("Apple","Alice","Rock",2.0), Song("Banana","Bob","Jazz",3.5)]
    bs, sw, _ = Sorting.bubble_sort_by_title(songs2)
    t("TC-E1  bubble sort title order",  [s.title for s in bs]==["Apple","Banana","Mango"])
    t("TC-E2  bubble sort swaps>0",      sw > 0)
    ins, _, _ = Sorting.insertion_sort_by_duration(songs2)
    t("TC-E3  insertion sort duration",  [s.duration for s in ins]==[2.0,3.5,5.0])
    sel, _, _ = Sorting.selection_sort_by_artist(songs2)
    t("TC-E4  selection sort artist",    [s.artist for s in sel]==["Alice","Bob","Charlie"])

    # F. Integration
    print("\n  [F] Integration (PlaylistController)")
    ctrl = PlaylistController("Test")
    ctrl.add_song("T1","A1","Pop",3.0); ctrl.add_song("T2","A2","Rock",4.0)
    t("TC-F1  size==2 after 2 adds",         ctrl.playlist.size == 2)
    ctrl.undo_last()
    t("TC-F2  undo add -> size==1",           ctrl.playlist.size == 1)
    ctrl.add_song("T3","A3","Jazz",5.0)
    ctrl.remove_song("T1")
    t("TC-F3  remove T1 -> size==1",          ctrl.playlist.size == 1)
    ctrl.undo_last()
    t("TC-F4  undo delete -> size==2",        ctrl.playlist.size == 2)
    ctrl.request_song("T3")
    t("TC-F5  request queue size==1",         ctrl.req_queue.size() == 1)
    ctrl.play_next_requested()
    t("TC-F6  queue empty after play",        ctrl.req_queue.is_empty())
    ctrl.sort_by_title()
    lst = ctrl.playlist.to_list()
    t("TC-F7  sorted by title ascending",     lst[0].title <= lst[1].title)
    ctrl.sort_by_duration()
    lst2 = ctrl.playlist.to_list()
    t("TC-F8  sorted by duration ascending",  lst2[0].duration <= lst2[1].duration)

    # Result summary
    total = passed + failed
    print(f"\n{sep}")
    print(f"  RESULTS: {passed}/{total} passed  |  {failed} failed")
    print(f"{sep}\n")
    return passed, failed


# =============================================================
#  ENTRY POINT
# =============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        run_interactive()
