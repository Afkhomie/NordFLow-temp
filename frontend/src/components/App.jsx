import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container, Typography } from '@mui/material';
import DeviceControl from './DeviceControl';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const ws = new WebSocket(`${protocol}://${window.location.host}/ws`);

      ws.onopen = () => {
        setConnected(true);
        setError(null);
      };

      ws.onclose = () => {
        setConnected(false);
        setTimeout(connectWebSocket, 5000); // Retry connection
      };

      ws.onerror = (error) => {
        setError('Connection error');
        console.error('WebSocket error:', error);
      };

      return ws;
    };

    const ws = connectWebSocket();
    return () => ws.close();
  }, []);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="sm">
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            NodeFlow Control Panel
          </Typography>
          <Typography variant="subtitle1" color={connected ? 'success.main' : 'error.main'}>
            Status: {connected ? 'Connected' : 'Disconnected'}
          </Typography>
          {error && (
            <Typography variant="body2" color="error.main">
              {error}
            </Typography>
          )}
          <DeviceControl connected={connected} />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
