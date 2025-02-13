import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const HomePage = () => {
  return (
    <Container>
      <Box mt={5}>
        <Typography variant="h4">Home Page</Typography>
        <Typography>Welcome to the Home Page!</Typography>
      </Box>
    </Container>
  );
};

export default HomePage;