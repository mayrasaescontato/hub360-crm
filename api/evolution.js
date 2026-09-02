// Proxy para a Evolution API. A EVOLUTION_KEY nunca mais fica no navegador:
// fica só aqui, em variável de ambiente do Vercel. O frontend manda o path
// e o payload, esse arquivo valida a sessão do usuário logado no Supabase
// e só então repassa a chamada pra Evolution com a chave real.

const EVOLUTION_URL = 'https://evolution-api-production-7eff.up.railway.app';
const SUPA_URL = 'https://mvktoymgeapkpsvfmbfl.supabase.co';

// Chave anon do Supabase: é segura ficar aqui, ela é pública por design
// (o Supabase espera que ela apareça em código-cliente). O que protege de
// verdade é o RLS no banco e, aqui, a validação do token de sessão abaixo.
const SUPA_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12a3RveW1nZWFwa3BzdmZtYmZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkyMjA4NTEsImV4cCI6MjA5NDc5Njg1MX0._RQsWc2jR4kSuALw5jHl7T2Q-bgjvDrSQdmjwCD8dWA';

async function isValidSession(accessToken) {
  if (!accessToken) return false;
  try {
    const res = await fetch(`${SUPA_URL}/auth/v1/user`, {
      headers: {
        'apikey': SUPA_ANON_KEY,
        'Authorization': `Bearer ${accessToken}`
      }
    });
    return res.ok;
  } catch (e) {
    return false;
  }
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const authHeader = req.headers.authorization || '';
  const accessToken = authHeader.replace('Bearer ', '');
  const authorized = await isValidSession(accessToken);
  if (!authorized) return res.status(401).json({ error: 'Sessão inválida ou expirada. Faça login novamente.' });

  const evolutionKey = process.env.EVOLUTION_KEY;
  if (!evolutionKey) return res.status(500).json({ error: 'EVOLUTION_KEY não configurada no Vercel' });

  const { path, method, payload } = req.body || {};
  if (!path) return res.status(400).json({ error: 'path é obrigatório' });

  try {
    const evoRes = await fetch(EVOLUTION_URL + path, {
      method: method || 'POST',
      headers: { 'apikey': evolutionKey, 'Content-Type': 'application/json' },
      body: payload ? JSON.stringify(payload) : undefined
    });
    const data = await evoRes.json().catch(() => null);
    return res.status(evoRes.status).json(data);
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
