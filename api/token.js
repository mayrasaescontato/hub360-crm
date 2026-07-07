import twilio from 'twilio';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const AccessToken = twilio.jwt.AccessToken;
  const VoiceGrant = AccessToken.VoiceGrant;

  const accountSid = process.env.TWILIO_ACCOUNT_SID;
  const apiKeySid = process.env.TWILIO_API_KEY_SID;
  const apiKeySecret = process.env.TWILIO_API_KEY_SECRET;
  const appSid = process.env.TWILIO_APP_SID;

  if (!accountSid || !apiKeySid || !apiKeySecret || !appSid) {
    return res.status(500).json({ error: 'Twilio API Key/App SID não configurados no Vercel' });
  }

  try {
    const identity = 'mayra';
    const token = new AccessToken(accountSid, apiKeySid, apiKeySecret, { identity, ttl: 3600 });
    const grant = new VoiceGrant({
      outgoingApplicationSid: appSid,
      incomingAllow: false
    });
    token.addGrant(grant);
    return res.status(200).json({ token: token.toJwt(), identity });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
