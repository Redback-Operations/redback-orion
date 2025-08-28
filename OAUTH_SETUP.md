# OAuth Authentication Setup

This guide will help you set up Google and Apple OAuth authentication for your AFL Analytics application.

## Prerequisites

You need to create OAuth applications with Google and Apple to get the required credentials.

## Google OAuth Setup

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google OAuth2 API

### 2. Configure OAuth Consent Screen

1. In the Google Cloud Console, go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in the required information:
   - App name: AFL Analytics
   - User support email: your email
   - Developer contact information: your email
4. Add scopes: `userinfo.email` and `userinfo.profile`
5. Add test users if needed

### 3. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Set authorized redirect URIs:
   - Development: `http://localhost:8080/api/auth/google/callback`
   - Production: `https://yourdomain.com/api/auth/google/callback`
5. Save and copy the Client ID and Client Secret

### 4. Update Environment Variables

Set these environment variables in your application:

```bash
GOOGLE_CLIENT_ID=your-actual-google-client-id
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
```

## Apple OAuth Setup

### 1. Apple Developer Account

You need an active Apple Developer Account to set up Sign In with Apple.

### 2. Create an App ID

1. Go to [Apple Developer Portal](https://developer.apple.com/account/)
2. Navigate to "Certificates, Identifiers & Profiles" > "Identifiers"
3. Create a new App ID with Sign In with Apple capability enabled

### 3. Create a Services ID

1. Create a new Services ID in the Apple Developer Portal
2. Enable "Sign In with Apple"
3. Configure the service:
   - Primary App ID: Select the App ID you created
   - Web Domain: Your domain (e.g., `localhost` for development)
   - Return URLs:
     - Development: `http://localhost:8080/api/auth/apple/callback`
     - Production: `https://yourdomain.com/api/auth/apple/callback`

### 4. Create a Private Key

1. Go to "Keys" section in Apple Developer Portal
2. Create a new key with "Sign In with Apple" enabled
3. Download the private key file (.p8)
4. Note the Key ID

### 5. Update Environment Variables

Set these environment variables in your application:

```bash
APPLE_CLIENT_ID=your-services-id
APPLE_TEAM_ID=your-team-id
APPLE_KEY_ID=your-key-id
APPLE_PRIVATE_KEY=your-private-key-content
```

## Setting Environment Variables in Builder.io

To set these environment variables in your Builder.io project:

1. **Important**: Use the DevServerControl tool to set environment variables (they won't be committed to git)
2. Or manually set them in your deployment environment

Example for setting via DevServerControl:

```
GOOGLE_CLIENT_ID=your-actual-google-client-id
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
APPLE_CLIENT_ID=your-services-id
JWT_SECRET=your-super-secure-jwt-secret
```

## Testing OAuth

### Google OAuth Test Flow

1. Click "Continue with Google" button
2. You'll be redirected to Google's OAuth consent screen
3. Choose your Google account and grant permissions
4. You'll be redirected back and automatically logged in

### Apple OAuth Test Flow

1. Click "Continue with Apple" button
2. You'll be redirected to Apple's Sign In page
3. Enter your Apple ID credentials
4. Choose to share or hide your email
5. You'll be redirected back and automatically logged in

## Security Notes

- Never commit OAuth secrets to your repository
- Use different OAuth applications for development and production
- Regularly rotate your JWT secret
- Implement proper token expiration and refresh logic for production

## Troubleshooting

### Common Google OAuth Issues

- **Invalid redirect_uri**: Ensure the redirect URI in Google Console matches exactly
- **Access blocked**: Add your domain to authorized domains in OAuth consent screen
- **API not enabled**: Enable Google+ API and OAuth2 API in Google Cloud Console

### Common Apple OAuth Issues

- **Invalid client**: Verify your Services ID is correctly configured
- **Invalid redirect**: Ensure redirect URIs match in Apple Developer Portal
- **Private key issues**: Ensure the private key is properly formatted

### Debug Mode

Set `NODE_ENV=development` to see detailed OAuth error logs in the server console.

## Production Considerations

1. Set up proper error handling for OAuth failures
2. Implement token refresh mechanisms
3. Add rate limiting to OAuth endpoints
4. Use HTTPS in production
5. Set secure cookie flags
6. Implement proper session management
