const http = require('http');

// Simple Next.js API endpoint smoke tests running directly against isolated file logic
const assert = (condition, message) => {
  if (!condition) {
    console.error(`❌ FAIL: ${message}`);
    process.exit(1);
  } else {
    console.log(`✅ PASS: ${message}`);
  }
};

// Mock Next.js request/response handlers to test the page handlers directly
const mockReq = (method, headers = {}, body = {}) => ({
  method,
  headers,
  body,
});

const mockRes = () => {
  const res = {
    statusCode: 200,
    headers: {},
    body: null,
    status: function (code) {
      this.statusCode = code;
      return this;
    },
    json: function (obj) {
      this.body = obj;
      return this;
    },
    send: function (str) {
      this.body = str;
      return this;
    },
    setHeader: function (name, value) {
      this.headers[name] = value;
      return this;
    }
  };
  return res;
};

async function testHealthProxy() {
  const handler = require('../pages/api/health.js').default;
  const req = mockReq('GET');
  const res = mockRes();
  
  handler(req, res);
  assert(res.statusCode === 200, 'Health proxy endpoint returns status 200');
  assert(res.body.status === 'healthy', 'Health proxy endpoint reports healthy');
}

async function testModelsProxyMethodNotAllowed() {
  const handler = require('../pages/api/models.js').default;
  const req = mockReq('POST');
  const res = mockRes();
  
  await handler(req, res);
  assert(res.statusCode === 405, 'Models proxy rejects non-GET requests with 405 Method Not Allowed');
  assert(res.body.detail === 'Method Not Allowed', 'Models proxy method details');
}

async function testModelsProxyConnectionFailure() {
  // Test connection error state (when no backend is running)
  process.env.DRIFTGUARD_API_URL = 'http://localhost:9999'; // Invalid port
  const handler = require('../pages/api/models.js').default;
  const req = mockReq('GET', { 'x-api-key': 'test-key' });
  const res = mockRes();
  
  await handler(req, res);
  assert(res.statusCode === 500, 'Models proxy returns 500 when backend is unreachable');
  assert(res.body.detail === 'Cannot connect to DriftGuard API', 'Unreachable backend error details match');
}

async function run() {
  console.log('Starting Dashboard API proxy routes smoke tests...');
  try {
    await testHealthProxy();
    await testModelsProxyMethodNotAllowed();
    await testModelsProxyConnectionFailure();
    console.log('All smoke tests completed successfully.');
  } catch (err) {
    console.error('Smoke tests crashed:', err);
    process.exit(1);
  }
}

run();
