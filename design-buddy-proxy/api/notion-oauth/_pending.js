const TTL_MS = 10 * 60 * 1000;

function pendingMap() {
  if (!globalThis.__notionOAuthPending) {
    globalThis.__notionOAuthPending = new Map();
  }
  return globalThis.__notionOAuthPending;
}

function pruneExpired(map) {
  const now = Date.now();
  map.forEach((entry, key) => {
    if (!entry || entry.expiresAt <= now) {
      map.delete(key);
    }
  });
}

export function setPendingOAuth(state, data) {
  if (!state) return;
  const map = pendingMap();
  pruneExpired(map);
  map.set(state, {
    ...data,
    expiresAt: Date.now() + TTL_MS,
  });
}

export function takePendingOAuth(state) {
  if (!state) return null;
  const map = pendingMap();
  pruneExpired(map);
  const entry = map.get(state);
  if (!entry) return null;
  map.delete(state);
  if (entry.expiresAt <= Date.now()) return null;
  return entry;
}
