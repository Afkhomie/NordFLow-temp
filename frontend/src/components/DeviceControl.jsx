import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
} from '@mui/material';
import {
  Videocam,
  VideocamOff,
  Mic,
  MicOff,
  VolumeUp,
  VolumeOff,
} from '@mui/icons-material';

const DeviceControl = ({ connected }) => {
  const [activeDevices, setActiveDevices] = useState({
    webcam: false,
    microphone: false,
    speaker: false,
  });

  const handleDeviceToggle = async (device) => {
    const newState = !activeDevices[device];
    const command = newState ? 'start' : 'stop';

    try {
      const response = await fetch(`/api/device/${device}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command }),
      });

      if (response.ok) {
        setActiveDevices((prev) => ({
          ...prev,
          [device]: newState,
        }));
      } else {
        console.error(`Failed to ${command} ${device}`);
      }
    } catch (error) {
      console.error('Error controlling device:', error);
    }
  };

  const devices = [
    {
      name: 'Webcam',
      id: 'webcam',
      ActiveIcon: Videocam,
      InactiveIcon: VideocamOff,
    },
    {
      name: 'Microphone',
      id: 'microphone',
      ActiveIcon: Mic,
      InactiveIcon: MicOff,
    },
    {
      name: 'Speaker',
      id: 'speaker',
      ActiveIcon: VolumeUp,
      InactiveIcon: VolumeOff,
    },
  ];

  return (
    <Box sx={{ mt: 4 }}>
      <Grid container spacing={3}>
        {devices.map((device) => {
          const isActive = activeDevices[device.id];
          const Icon = isActive ? device.ActiveIcon : device.InactiveIcon;

          return (
            <Grid item xs={12} sm={4} key={device.id}>
              <Card>
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 2,
                    }}
                  >
                    <Icon
                      sx={{
                        fontSize: 40,
                        color: isActive ? 'success.main' : 'error.main',
                      }}
                    />
                    <Typography variant="h6">{device.name}</Typography>
                    <Button
                      variant="contained"
                      color={isActive ? 'error' : 'success'}
                      onClick={() => handleDeviceToggle(device.id)}
                      disabled={!connected}
                    >
                      {isActive ? 'Stop' : 'Start'}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};

export default DeviceControl;
