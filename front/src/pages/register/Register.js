import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Container, Box, Typography, TextField, Button, Alert } from '@mui/material';

const API_URL = process.env.REACT_APP_API_URL;

const RegisterPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleRegister = async () => {
        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username,
                    password: password,
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                setError(errorData.detail || 'Registration failed');
                return;
            }

            const data = await response.json();
            setSuccess('Registration successful! Redirecting...');
            setTimeout(() => {
                login(data.access_token, data.refresh_token);
                navigate('/');
            }, 2000);
        } catch (error) {
            console.error('Registration error:', error);
            setError('An unexpected error occurred. Please try again.');
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            setError(null);
            setSuccess(null);
            handleRegister();
        }
    };

    return (
        <Container maxWidth="sm">
            <Box mt={5}>
                <Typography variant="h4" gutterBottom>
                    Register
                </Typography>
                {error && (
                    <Alert severity="error" onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}
                {success && (
                    <Alert severity="success" onClose={() => setSuccess(null)}>
                        {success}
                    </Alert>
                )}
                <TextField
                    label="Username"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <TextField
                    label="Password"
                    type="password"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={() => { setError(null); setSuccess(null); handleRegister(); }}
                >
                    Register
                </Button>
            </Box>
        </Container>
    );
};

export default RegisterPage;