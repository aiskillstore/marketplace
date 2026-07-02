# Tutorial 4: Full Project — Notes App

Build a complete notes application with dark mode, localStorage persistence, and modal editing.

## Features

- Create, edit, delete notes
- localStorage persistence
- Dark mode toggle
- Modal editing with `<dialog>`
- Responsive grid layout

## HTML

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quick Notes</title>
  <style>/* CSS below */</style>
</head>
<body>
  <header>
    <h1>Quick Notes</h1>
    <button id="dark-toggle">🌙</button>
  </header>

  <main>
    <div class="input-row">
      <input type="text" id="note-input" placeholder="New note...">
      <button onclick="addNote()">Add</button>
    </div>
    <div class="notes-grid" id="notes-grid"></div>
  </main>

  <dialog id="edit-dialog">
    <form method="dialog">
      <h2>Edit Note</h2>
      <textarea id="edit-text" rows="4"></textarea>
      <div class="dialog-actions">
        <button type="button" onclick="this.closest('dialog').close()">Cancel</button>
        <button type="submit" onclick="saveEdit()">Save</button>
      </div>
    </form>
  </dialog>

  <script>/* JS below */</script>
</body>
</html>
```

## CSS

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root { --bg: #ffffff; --bg-card: #f5f5f5; --text: #1a1a1a; --primary: #667eea; }
[data-theme="dark"] { --bg: #121212; --bg-card: #1e1e1e; --text: #e0e0e0; }

body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); padding: 2rem; max-width: 800px; margin: 0 auto; transition: background 0.3s, color 0.3s; }

header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }

#dark-toggle { background: none; border: none; font-size: 1.5rem; cursor: pointer; }

.input-row { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
.input-row input { flex: 1; padding: 0.75rem; border: 1px solid #ddd; border-radius: 8px; font-size: 1rem; background: var(--bg-card); color: var(--text); }
.input-row button { padding: 0.75rem 1.25rem; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; }

.notes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }

.note { background: var(--bg-card); border-radius: 8px; padding: 1rem; position: relative; }
.note p { line-height: 1.5; margin-bottom: 0.75rem; }
.note-actions { display: flex; gap: 0.5rem; }
.note-actions button { background: none; border: none; cursor: pointer; font-size: 0.8rem; color: var(--primary); }

dialog { border: none; border-radius: 12px; padding: 2rem; max-width: 400px; width: 90%; }
dialog textarea { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 8px; font-family: inherit; font-size: 1rem; margin: 1rem 0; resize: vertical; }
.dialog-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
.dialog-actions button { padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; border: none; }
.dialog-actions button:first-child { background: transparent; color: #666; }
.dialog-actions button:last-child { background: var(--primary); color: white; }
```

## JavaScript

```javascript
let notes = JSON.parse(localStorage.getItem('notes') || '[]');
let editingId = null;

function save() { localStorage.setItem('notes', JSON.stringify(notes)); }

function render() {
  document.getElementById('notes-grid').innerHTML = notes.map(n => `
    <div class="note">
      <p>${n.text}</p>
      <div class="note-actions">
        <button onclick="editNote('${n.id}')">Edit</button>
        <button onclick="deleteNote('${n.id}')">Delete</button>
      </div>
    </div>
  `).join('');
}

function addNote() {
  const input = document.getElementById('note-input');
  if (!input.value.trim()) return;
  notes.push({ id: Date.now().toString(), text: input.value.trim() });
  input.value = '';
  save(); render();
}

function editNote(id) {
  editingId = id;
  const note = notes.find(n => n.id === id);
  document.getElementById('edit-text').value = note.text;
  document.getElementById('edit-dialog').showModal();
}

function saveEdit() {
  const note = notes.find(n => n.id === editingId);
  note.text = document.getElementById('edit-text').value.trim();
  save(); render();
}

function deleteNote(id) {
  notes = notes.filter(n => n.id !== id);
  save(); render();
}

// Dark mode
const toggle = document.getElementById('dark-toggle');
const root = document.documentElement;
function setTheme(t) { root.setAttribute('data-theme', t); localStorage.setItem('theme', t); toggle.textContent = t === 'dark' ? '☀️' : '🌙'; }
const saved = localStorage.getItem('theme') || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light');
setTheme(saved);
toggle.addEventListener('click', () => setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'));

document.getElementById('note-input').addEventListener('keydown', e => { if (e.key === 'Enter') addNote(); });

render();
```
