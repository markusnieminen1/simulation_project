// src/components/NavBar.js
import React from 'react';
import { Link } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import AccountMenu from './Accountmenu';
import { useAuth } from '../../context/AuthContext';

const DynamicAccountMenu = () => {
  const { isLoggedIn, logout } = useAuth();

  return (
    <>
      {isLoggedIn ? (
        <AccountMenu />
      ) : (
        <Button color="inherit" component={Link} to="/login">
          Login 
        </Button>
      )}
    </>
  );
};

const NavBarComponent = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <IconButton edge="start" color="inherit" aria-label="menu">
        </IconButton>
        <Typography variant="h6" style={{ flexGrow: 1 }}>
          My App
        </Typography>
        <Button color="inherit">Home</Button>
        <Button color="inherit">About</Button>
        <Button color="inherit">Contact</Button>
        <DynamicAccountMenu />
      </Toolbar>
    </AppBar>
  );
};

export default NavBarComponent;
