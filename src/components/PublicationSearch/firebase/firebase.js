// Firebase connection has been severed - this site is deprecated
// All exports are stubs that prevent any Firebase requests

console.warn(
  "Firebase connection disabled: This application is deprecated and no longer connects to Firebase."
);

// Stub database object
const database = null;

// Stub ref function - returns a mock reference
const ref = () => ({});

// Stub get function - returns a snapshot with no data
const get = async () => ({
  exists: () => false,
  val: () => null,
});

// Stub set function - logs warning and rejects
const set = async () => {
  console.warn("Firebase write operations are disabled - this site is deprecated.");
  return Promise.reject(new Error("Firebase connection disabled - site is deprecated"));
};

// Stub child function - returns empty object
const child = () => ({});

export { database, set, ref, get, child };
