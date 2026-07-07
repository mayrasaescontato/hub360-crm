export default async function handler(req, res) {
  res.setHeader('Content-Type', 'text/xml');
  const to = req.query.to || req.body?.To || '';
  res.status(200).send(`<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="pt-BR">Conectando.</Say>
  <Dial callerId="${process.env.WILIO_PHONE_NUMBER || process.env.TWILIO_PHONE_NUMBER || ''}">
    <Number>${to}</Number>
  </Dial>
</Response>`);
}
