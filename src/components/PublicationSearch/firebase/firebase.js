import { initializeApp } from "firebase/app";
import { getDatabase, set, ref, get, child } from "firebase/database";

// Validate Firebase configuration
const requiredEnvVars = {
  REACT_APP_FIREBASE_API_KEY: process.env.REACT_APP_FIREBASE_API_KEY,
  REACT_APP_FIREBASE_AUTH_DOMAIN: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  REACT_APP_FIREBASE_PROJECT_ID: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  REACT_APP_FIREBASE_DATABASE_URL: process.env.REACT_APP_FIREBASE_DATABASE_URL,
};

// Check for missing required environment variables
const missingVars = Object.entries(requiredEnvVars)
  .filter(([_, value]) => !value)
  .map(([key]) => key);

if (missingVars.length > 0) {
  throw new Error(
    `Missing required Firebase configuration variables: ${missingVars.join(', ')}`
  );
}

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: requiredEnvVars.REACT_APP_FIREBASE_API_KEY,
  authDomain: requiredEnvVars.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: requiredEnvVars.REACT_APP_FIREBASE_PROJECT_ID,
  databaseURL: requiredEnvVars.REACT_APP_FIREBASE_DATABASE_URL,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  measurementId: process.env.REACT_APP_FIREBASE_APP_MEASUREMENT_ID,
};

const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

export { database, set, ref, get, child };
