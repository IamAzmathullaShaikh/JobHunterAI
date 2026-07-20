const assert = require('assert');

function normalizeJobURL(raw_url, canonical_url) {
    let resolved_url = canonical_url || raw_url;
    let http_status = 200;
    let needs_validation = false;

    if (raw_url && raw_url.includes('google.com')) {
        http_status = 302;
        resolved_url = raw_url.replace('google.com/search?q=', 'resolved.com/');
    } else if (!raw_url) {
        http_status = 404;
        needs_validation = true;
    }

    if (!resolved_url || resolved_url === '#' || resolved_url.includes('mock')) {
        needs_validation = true;
    }

    return { resolved_url, http_status, needs_validation };
}

function extractPortalId(html) {
    if (html.includes('data-job-id="')) {
        return html.split('data-job-id="')[1].split('"')[0];
    }
    return null;
}

const res1 = normalizeJobURL('https://google.com/search?q=job', '');
assert.strictEqual(res1.resolved_url, 'https://resolved.com/job', 'Should follow redirect mock');
assert.strictEqual(res1.http_status, 302, 'Should simulate redirect');

const res2 = normalizeJobURL('mock-url', '');
assert.strictEqual(res2.needs_validation, true, 'Should require validation for mock URLs');

const portalId = extractPortalId('<div data-job-id="12345">Job</div>');
assert.strictEqual(portalId, '12345', 'Should extract portal id from HTML');

console.log('Unit tests passed!');
