const twilio = require('twilio');

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { to } = req.body;
  if (!to) return res.status(400).json({ error: 'Número de destino obrigatório' });

  const accountSid = process.env.TWILIO_ACCOUNT_SID;
  const authToken = process.env.TWILIO_AUTH_TOKEN;
  const from = process.env.WILIO_PHONE_NUMBER || process.env.TWILIO_PHONE_NUMBER;

  try {
    const client = twilio(accountSid, authToken);
    const call = await client.calls.create({
      to,
      from,
      twiml: `<Response><Say language="pt-BR">Conectando sua ligação.</Say><Dial>${to}</Dial></Response>`
    });
    return res.status(200).json({ success: true, callSid: call.sid, status: call.status });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
