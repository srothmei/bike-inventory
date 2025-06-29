import React from 'react';
import { Container, Typography, AppBar, Toolbar, Box } from '@mui/material';
import Inventory from './Inventory';
import BarcodeScanner from './BarcodeScanner';

function App() {
  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">Bike Parts Inventory</Typography>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>
        <Inventory />
        <BarcodeScanner />
      </Container>
    </Box>
  );
}

export default App;
