import express from 'express';
import cors from 'cors';
import multer from 'multer';
import sqlite3 from 'sqlite3';
import path from 'path';
import fs from 'fs';

const app = express();
const PORT = 4000;
const IMAGE_DIR = './data/images';

app.use(cors());
app.use(express.json());
app.use('/images', express.static(IMAGE_DIR));

if (!fs.existsSync(IMAGE_DIR)) fs.mkdirSync(IMAGE_DIR, { recursive: true });

const db = new sqlite3.Database('./data/inventory.db', (err) => {
  if (err) throw err;
  db.run(`CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    gtin TEXT,
    category TEXT,
    image TEXT
  )`);
});

const upload = multer({ dest: IMAGE_DIR });

app.get('/api/items', (req, res) => {
  const { search = '', category = '' } = req.query;
  let query = 'SELECT * FROM items WHERE 1=1';
  let params = [];
  if (search) {
    query += ' AND (title LIKE ? OR gtin LIKE ?)';
    params.push(`%${search}%`, `%${search}%`);
  }
  if (category) {
    query += ' AND category = ?';
    params.push(category);
  }
  db.all(query, params, (err, items) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(items);
  });
});

app.post('/api/items', upload.single('image'), (req, res) => {
  const { title, gtin, category } = req.body;
  const image = req.file ? req.file.filename : null;
  db.run(
    'INSERT INTO items (title, gtin, category, image) VALUES (?, ?, ?, ?)',
    [title, gtin, category, image],
    function (err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ id: this.lastID });
    }
  );
});

app.get('/api/items/:gtin', (req, res) => {
  const { gtin } = req.params;
  db.get('SELECT * FROM items WHERE gtin = ?', [gtin], (err, item) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!item) return res.status(404).json({ error: 'Not found' });
    res.json(item);
  });
});

app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
