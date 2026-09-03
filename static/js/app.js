const api = {
    async _parse(res) {
        const text = await res.text();
        let body = {};
        try { body = text ? JSON.parse(text) : {}; } catch (_) { body = { error: text || 'Request failed' }; }
        if (!res.ok) throw new Error(body.error || 'Request failed');
        return body;
    },
    get(url) {
        return fetch(url).then(this._parse);
    },
    post(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data || {}),
        }).then(this._parse);
    },
    put(url, data) {
        return fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data || {}),
        }).then(this._parse);
    },
    del(url) {
        return fetch(url, { method: 'DELETE' }).then(this._parse);
    },
};
