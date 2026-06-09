const API = 'http://127.0.0.1:8000';

export async function getRecentActions() {
    try {
        const res = await fetch(`${API}/api/recent-actions`);
        if (!res.ok) throw new Error('API error');
        return await res.json();
    } catch {
        return null;
    }
}

export async function getLiveStats() {
    try {
        const res = await fetch(`${API}/api/stats`);
        if (!res.ok) throw new Error('API error');
        return await res.json();
    } catch {
        return null;
    }
}