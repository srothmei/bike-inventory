import express from 'express';
import cors from 'cors';
import multer from 'multer';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';
import fs from 'fs';

const app = express();
const PORT = 4000;
const IMAGE_DIR = './data/images';

app.use(cors());
app.use(express.json());
app.use('/images', express.static(IMAGE_DIR));

if (!fs.existsSync(IMAGE_DIR)) fs.mkdirSync(IMAGE_DIR, { recursive: true });

let db;
(async () => {
  db = await open({
    filename: './data/inventory.db',
    driver: sqlite3.Database
  });
  await db.run(`CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    gtin TEXT,
    category TEXT,
    image TEXT
  )`);
})();

const upload = multer({ dest: IMAGE_DIR });

app.get('/api/items', async (req, res) => {
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
  const items = await db.all(query, params);
  res.json(items);
});

app.post('/api/items', upload.single('image'), async (req, res) => {
  const { title, gtin, category } = req.body;
  const image = req.file ? req.file.filename : null;
  const result = await db.run(
    'INSERT INTO items (title, gtin, category, image) VALUES (?, ?, ?, ?)',
    [title, gtin, category, image]
  );
  res.json({ id: result.lastID });
});

app.get('/api/items/:gtin', async (req, res) => {
  const { gtin } = req.params;
  const item = await db.get('SELECT * FROM items WHERE gtin = ?', [gtin]);
  if (!item) return res.status(404).json({ error: 'Not found' });
  res.json(item);
});

app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
