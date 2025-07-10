export const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_MSAL_CLIENT_ID,
    authority: import.meta.env.VITE_MSAL_AUTHORITY,
    redirectUri: import.meta.env.VITE_MSAL_REDIRECT_URI,
    postLogoutRedirectUri: '/',
    navigateToLoginRequestUrl: false
  },

  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false
  }
};
