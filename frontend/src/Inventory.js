import React, { useState, useEffect } from 'react';
import { TextField, Button, Grid, Card, CardContent, CardMedia, Typography, Select, MenuItem } from '@mui/material';

const API_URL = process.env.REACT_APP_API_URL || 'https://localhost:4000';

const categories = ['brakes', 'frame', 'tires', 'drivetrain', 'other'];

export default function Inventory() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');

  useEffect(() => {
    fetch(`${API_URL}/api/items?search=${search}&category=${category}`)
      .then(res => res.json())
      .then(setItems);
  }, [search, category]);

  return (
    <div>
      <Typography variant="h5" sx={{ mb: 2 }}>Inventory</Typography>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={6}>
          <TextField label="Search" value={search} onChange={e => setSearch(e.target.value)} fullWidth />
        </Grid>
        <Grid item xs={6}>
          <Select value={category} onChange={e => setCategory(e.target.value)} displayEmpty fullWidth>
            <MenuItem value="">All Categories</MenuItem>
            {categories.map(cat => <MenuItem key={cat} value={cat}>{cat}</MenuItem>)}
          </Select>
        </Grid>
      </Grid>
      <Grid container spacing={2} sx={{ mt: 2 }}>
        {items.map(item => (
          <Grid item xs={12} sm={6} md={4} key={item.id}>
            <Card>
              {item.image && <CardMedia component="img" height="140" image={`${API_URL}/images/${item.image}`} alt={item.title} />}
              <CardContent>
                <Typography variant="h6">{item.title}</Typography>
                <Typography variant="body2">GTIN: {item.gtin}</Typography>
                <Typography variant="body2">Category: {item.category}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}
