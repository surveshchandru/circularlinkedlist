# 🎵 Music Playlist Manager (Circular Linked List)

A full-stack interactive Data Structures project implementing a **Music Playlist Manager** powered by:
- **Circular Linked List**: Core playlist data structure with (1)$ loop wrap-around (	ail.next = head).
- **Circular Array Queue**: Song request queue adhering to FIFO (First-In, First-Out) scheduling.
- **LIFO Stack**: Dedicated undo history buffer enabling 1-click restore of deleted songs.
- **Searching Algorithms**: Linear Search ((n)$) and Binary Search ((\log n)$) across Title, Artist, and Genre.
- **Sorting Algorithms**: Bubble Sort, Insertion Sort, and Selection Sort with automatic sequential rebuild of Circular Linked List pointers.
- **Web UI & Synthesizer**: Modern dark-theme glassmorphism interface with real-time Web Audio API chord synthesis, live CLL pointer inspector, and a guided interactive tour.

---

## 🚀 Quick Start

### 1. Install Dependencies
`ash
pip install -r requirements.txt
`

### 2. Launch the Application
`ash
python app.py
`

### 3. Open in Browser
- **Web Application**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Project Report**: [http://127.0.0.1:5000/report.html](http://127.0.0.1:5000/report.html)
- **CLI Terminal Mode**: python music_playlist.py

---

## 📂 Project Structure

`
├── app.py              # Flask REST API connecting data structures to web endpoints
├── music_playlist.py   # Pure Python Data Structures implementation (CLL, Stack, Queue, Algorithms)
├── index.html          # Interactive frontend with live CLL visualizer & Web Audio synthesizer
├── report.html         # Comprehensive lab project report with code snippets and metrics
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
`

---

## 💡 Key Data Structures & Algorithms

| Feature | Data Structure / Algorithm | Time Complexity | Role in System |
| :--- | :--- | :--- | :--- |
| **Playlist Traversal** | Circular Linked List | (1)$ Forward / (n)$ Backward | Seamless infinite looping playback from Tail to Head |
| **Song Insertion** | Circular Linked List | (1)$ Head/Tail, (n)$ Position | Dynamic node insertion with pointer relinking |
| **Undo Operations** | LIFO Stack | (1)$ Push / Pop | Restores removed tracks back to Circular Linked List |
| **Song Requests** | Circular Array Queue | (1)$ Enqueue / Dequeue | Fair FIFO queueing transitioning into live playback |
| **Title Lookup** | Binary Search | (\log n)$ | Divide-and-conquer search on sorted collection |
| **Filter & Browse** | Linear Search | (n)$ | Substring search across title, artist, and genre |
| **Playlist Reorder** | Bubble / Insertion Sort | (n^2)$ | In-place sorting and sequential circular pointer rebuild |
