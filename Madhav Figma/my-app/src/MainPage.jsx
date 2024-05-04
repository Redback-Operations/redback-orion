// MainPage.js

import React, { useState } from 'react';
import './MainPage.css'; // Import the CSS file for styles

function MainPage() {
    const [collapsed, setCollapsed] = useState(false);

    const toggleSidebar = () => {
        setCollapsed(!collapsed);
    };

    const sidebarStyle = {
        width: collapsed ? '80px' : '297px',
        height: '100vh',
        background: 'black',
        color: 'white',
        padding: '20px',
        position: 'relative',
        transition: 'width 0.3s ease'
    };

    const headingStyle = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '24px',
        fontWeight: '700',
        marginBottom: '60px',
        cursor: 'pointer',
        color: 'white' // Setting color to white for the heading
    };

    const operationsStyle = {
        color: '#CA6D00' // Setting color to orange for "Operations"
    };

    const menuStyle = {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        gap: '40px' // Increased gap between menu items
    };

    const menuItemStyle = {
        display: 'flex',
        alignItems: 'center',
        gap: '35px' // Increased gap between icon and text
    };

    const logoutContainerStyle = {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        marginTop: 'auto',
        gap: '20px'
    };

    const logoutStyle = {
        cursor: 'pointer',
        backgroundColor: 'black',
        padding: '10px 20px',
        borderRadius: '20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'background-color 0.3s ease',
        border: '2px solid white',
        color: 'white',
        // New: Apply hover effect
        ':hover': {
            backgroundColor: 'red', // Change background color to red on hover
        }
    };

    const userAvatarStyle = {
        width: '48px',
        height: '48px',
        borderRadius: '50%',
        border: '3px solid #CA6D00'
    };

    const crowdImageStyle = {
        position: 'absolute',
        top: 0,
        right: collapsed ? '80px' : '297px', // Align with the collapsed sidebar
        width: 'auto',
        height: '100vh',
        zIndex: '-1'
    };

    const iconStyle = {
        marginRight: '10px',
        marginLeft: '10px' // Adjusted margin to move the icons to the right
    };

    return (
        <div style={{ display: 'flex' }}>
            <div style={sidebarStyle}>
                <div style={headingStyle} onClick={toggleSidebar}>
                    <span style={{ display: collapsed ? 'none' : 'block' }}>
                        <span style={{ color: 'red' }}>Red</span>back <span style={operationsStyle}>Operations</span>
                    </span>
                    <i className={collapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'}></i>
                </div>
                <div style={menuStyle}>
                    <div style={menuItemStyle}>
                        <i className="fas fa-chart-bar" style={iconStyle}></i>
                        <div style={{ marginLeft: '10px', display: collapsed ? 'none' : 'block' }}>Statistics</div>
                    </div>
                    <div style={menuItemStyle}>
                        <i className="fas fa-bell" style={iconStyle}></i>
                        <div style={{ marginLeft: '10px', display: collapsed ? 'none' : 'block' }}>Notifications</div>
                    </div>
                    <div style={menuItemStyle}>
                        <i className="fas fa-cog" style={iconStyle}></i>
                        <div style={{ marginLeft: '10px', display: collapsed ? 'none' : 'block' }}>Settings</div>
                    </div>
                    <div style={menuItemStyle}>
                        <i className="fas fa-upload" style={iconStyle}></i>
                        <div style={{ marginLeft: '10px', display: collapsed ? 'none' : 'block' }}>Files Upload</div>
                    </div>
                    <div style={menuItemStyle}>
                        <i className="fas fa-question-circle" style={iconStyle}></i>
                        <div style={{ marginLeft: '10px', display: collapsed ? 'none' : 'block' }}>Help!</div>
                    </div>
                </div>
                <div style={logoutContainerStyle}>
                    <div className="user-info">
                        <img style={userAvatarStyle} src="logo.png" alt="User Avatar" />
                        <div className="user-name" style={{ display: collapsed ? 'none' : 'block', marginTop: '10px' }}>Madhav</div>
                    </div>
                    <div style={logoutStyle} onClick={() => console.log("Logout clicked")}>
                        <i className="fas fa-sign-out-alt" style={iconStyle}></i>
                        <div style={{ marginLeft: '10px', display: collapsed ? 'none' : 'block' }}>LogOut</div>
                    </div>
                </div>
            </div>
            <img className="crowd-image" id="crowd-image" src="crowd.png" alt="Crowd Image" style={crowdImageStyle} />
        </div>
    );
}

export default MainPage;
