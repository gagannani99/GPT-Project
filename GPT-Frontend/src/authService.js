import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig } from "./microsoftConfig";

export const msalInstance = new PublicClientApplication(msalConfig);
let isInitialized = false;

export const loginWithMicrosoft = async () => {
  try {
    if (!isInitialized && typeof msalInstance.initialize === "function") {
      await msalInstance.initialize();
      isInitialized = true;
    }

    const loginResponse = await msalInstance.loginPopup({
      scopes: ["user.read"],
    });

    let account = loginResponse?.account;
    if (!account) {
      const accounts = msalInstance.getAllAccounts();
      account = accounts.length > 0 ? accounts[0] : null;
    }

    if (!account) {
      throw new Error("No account information found after login.");
    }

    return {
      success: true,
      account,
    };
  } catch (error) {
    console.error("Microsoft login failed", error);
    return {
      success: false,
      error,
    };
  }
};
