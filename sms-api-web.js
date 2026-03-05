// KimiAxe SMS Gateway API
// Add to your Express server

// In-memory storage (use database in production)
const pendingMessages = [];
const receivedMessages = [];
const devices = new Map();

// API Key for Fast2SMS (get from https://www.fast2sms.com)
const FAST2SMS_API_KEY = "YOUR_FAST2SMS_KEY"; // Replace with actual key

// SMS Routes
app.post('/api/sms/send', async (req, res) => {
  try {
    const { to, message, device_id } = req.body;
    
    if (!to || !message) {
      return res.status(400).json({ error: "Missing to or message" });
    }
    
    // If device_id provided, queue for phone
    if (device_id) {
      const msg = {
        id: Date.now(),
        to,
        message,
        device_id,
        status: 'pending',
        created_at: new Date()
      };
      pendingMessages.push(msg);
      return res.json({ success: true, queued: true, message_id: msg.id });
    }
    
    // Otherwise send via API
    const result = await sendViaFast2SMS(to, message);
    
    res.json({ success: true, ...result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/sms/pending', (req, res) => {
  const { device } = req.query;
  const pending = pendingMessages.filter(m => m.device_id === device && m.status === 'pending');
  res.json(pending);
});

app.post('/api/sms/status', (req, res) => {
  const { message_id, status } = req.body;
  const msg = pendingMessages.find(m => m.id === message_id);
  if (msg) {
    msg.status = status;
  }
  res.json({ success: true });
});

app.post('/api/sms/receive', (req, res) => {
  const { device, from, message, timestamp } = req.body;
  receivedMessages.push({ device, from, message, timestamp, received_at: new Date() });
  res.json({ success: true });
});

app.get('/api/sms/messages', (req, res) => {
  res.json(receivedMessages.slice(-50)); // Last 50 messages
});

// Device registration
app.post('/api/device/register', (req, res) => {
  const { device_id, name, phone } = req.body;
  devices.set(device_id, { name, phone, online: true, last_seen: new Date() });
  res.json({ success: true, device_id });
});

app.get('/api/devices', (req, res) => {
  res.json(Array.from(devices.values()));
});

// Fast2SMS function
async function sendViaFast2SMS(to, message) {
  const url = "https://www.fast2sms.com/dev/bulkV2";
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': FAST2SMS_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        route: 'v3',
        sender_id: 'KIMIAX',
        message: message,
        language: 'english',
        numbers: to.replace(/\D/g, '')
      })
    });
    
    const data = await response.json();
    return data;
  } catch (err) {
    return { return: false, error: err.message };
  }
}

// Health check
app.get('/api/sms/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    pending: pendingMessages.length,
    received: receivedMessages.length,
    devices: devices.size 
  });
});