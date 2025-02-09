import React from 'react';


function Header() {
    return (
        <header className="App-header">
            <div className="logo">
                <a href='/'><img src="text_logo.png" alt="Company Logo"/></a>
            </div>
            <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/simulation">Simulation</a></li>
                    <li><a href="/settings">Settings</a></li>
                </ul>
            </nav>
        </header>
    );
}

export default Header;
