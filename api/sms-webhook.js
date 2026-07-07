export default async function handler(req, res) {
  res.setHeader('Content-Type', 'text/xml');
  try {
    const from = req.body.From || '';
    const body = req.body.Body || '';

    const SUPA_URL = process.env.SUPABASE_URL;
    const SUPA_KEY = process.env.SUPABASE_KEY;

    if (from && SUPA_URL && SUPA_KEY) {
      await fetch(`${SUPA_URL}/rest/v1/sms_messages`, {
        method: 'POST',
        headers: {
          'apikey': SUPA_KEY,
          'Authorization': `Bearer ${SUPA_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          company: 'alliance',
          phone: from,
          direction: 'in',
          body: body,
          status: 'received'
        })
      });
    }
  } catch (e) {
    console.error('sms-webhook error:', e);
  }
  res.status(200).send('<?xml version="1.0" encoding="UTF-8"?><Response></Response>');
}
