from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = '<!-- QR CODE ONIBUS LEADS PAGE -->'
if marker in s:
    print('Already patched')
    raise SystemExit(0)

page_anchor = '        <!-- EZ MONEY DASHBOARD -->'
if page_anchor not in s:
    raise SystemExit('Page anchor not found')

qr_page = '''        <!-- QR CODE ONIBUS LEADS PAGE -->
        <div class="page" id="page-qrcode">
          <div class="contacts-page">
            <div class="contacts-header">
              <div>
                <div class="contacts-header-title">QR Code do Ônibus</div>
                <div style="font-size:12px;color:var(--gray-500);margin-top:3px">Leads enviados pelo formulário da landing page da Alliance</div>
              </div>
              <span class="contacts-count" id="qrLeadsTotalLabel">— Leads</span>
              <div style="flex:1"></div>
              <button class="btn btn-outline" style="font-size:12px;padding:5px 10px" onclick="loadQrLeads()"><i class="fas fa-sync"></i> Atualizar</button>
            </div>
            <div class="contacts-toolbar">
              <div class="search-wrap">
                <i class="fas fa-search"></i>
                <input class="search-input" type="text" id="qrLeadSearch" placeholder="Buscar por nome, aluno, telefone ou email..." oninput="renderQrLeads()">
              </div>
            </div>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Responsável</th><th>Telefone</th><th>E-mail</th><th>Aluno</th><th>Idade</th><th>Nível</th><th>Status</th><th>Recebido em</th><th style="width:78px">Ação</th>
                  </tr>
                </thead>
                <tbody id="qrLeadsBody">
                  <tr><td colspan="9"><div class="loading"><div class="spinner"></div></div></td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

'''
s = s.replace(page_anchor, qr_page + page_anchor, 1)

nav_anchor = '''    <div class="sb-item" onclick="showPage('pipeline',this);changePipeline('leads')"><i class="fas fa-columns"></i> Oportunidades</div>'''
if nav_anchor not in s:
    raise SystemExit('Nav anchor not found')
nav_insert = nav_anchor + '''
    <div class="sb-item" onclick="showPage('qrcode',this)"><i class="fas fa-qrcode"></i> QR Code Ônibus</div>'''
s = s.replace(nav_anchor, nav_insert, 1)

title_anchor = "    alunos:'Cadastro de Alunos'"
if title_anchor not in s:
    raise SystemExit('Title anchor not found')
s = s.replace(title_anchor, "    alunos:'Cadastro de Alunos', qrcode:'QR Code Ônibus'", 1)

loader_anchor = "  if (name === 'alunos') loadAlunos();"
if loader_anchor not in s:
    raise SystemExit('Loader anchor not found')
s = s.replace(loader_anchor, loader_anchor + "\n  if (name === 'qrcode') loadQrLeads();", 1)

js_anchor = '// ===== CALENDAR ====='
if js_anchor not in s:
    raise SystemExit('JS anchor not found')

qr_js = r'''// ===== QR CODE ONIBUS / LEADS =====
let qrLeadsData = [];

function qrEscape(value) {
  return String(value ?? '')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&#039;');
}

async function loadQrLeads() {
  const tbody = document.getElementById('qrLeadsBody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="9"><div class="loading"><div class="spinner"></div></div></td></tr>';
  try {
    const rows = await supaFetch('qr_code_leads?select=*&order=created_at.desc&limit=1000');
    qrLeadsData = rows || [];
    const lbl = document.getElementById('qrLeadsTotalLabel');
    if (lbl) lbl.textContent = `${qrLeadsData.length.toLocaleString()} Lead${qrLeadsData.length===1?'':'s'}`;
    renderQrLeads();
  } catch(e) {
    tbody.innerHTML = `<tr><td colspan="9"><div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Erro ao carregar leads do QR Code.</p></div></td></tr>`;
    toast('Erro ao carregar leads do QR Code: ' + e.message, 'error');
  }
}

function renderQrLeads() {
  const tbody = document.getElementById('qrLeadsBody');
  if (!tbody) return;
  const q = (document.getElementById('qrLeadSearch')?.value || '').trim().toLowerCase();
  let rows = qrLeadsData;
  if (q) {
    rows = rows.filter(r => [r.name,r.phone,r.email,r.student_name,r.student_age,r.experience_level,r.message,r.status]
      .some(v => String(v ?? '').toLowerCase().includes(q)));
  }
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="9"><div class="empty-state"><i class="fas fa-qrcode"></i><p>Nenhum lead do QR Code encontrado.</p></div></td></tr>';
    return;
  }
  tbody.innerHTML = rows.map(r => {
    const created = r.created_at ? new Date(r.created_at).toLocaleString('pt-BR') : '—';
    const statusRaw = String(r.status || 'new').toLowerCase();
    const statusLabel = statusRaw === 'new' ? 'NOVO' : (r.status || 'NOVO');
    const statusClass = statusRaw === 'new' ? 'badge-blue' : statusRaw === 'contacted' ? 'badge-yellow' : 'badge-gray';
    const phone = qrEscape(r.phone || '');
    const digits = String(r.phone || '').replace(/\D/g,'');
    const message = r.message ? `<div style="font-size:11px;color:var(--gray-500);margin-top:3px;max-width:240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="${qrEscape(r.message)}">${qrEscape(r.message)}</div>` : '';
    return `<tr>
      <td><div class="contact-name">${qrEscape(r.name || 'Sem nome')}</div>${message}</td>
      <td>${phone || '<span style="color:var(--gray-300)">—</span>'}</td>
      <td style="font-size:12px;color:var(--gray-500)">${qrEscape(r.email || '') || '<span style="color:var(--gray-300)">—</span>'}</td>
      <td><strong>${qrEscape(r.student_name || '—')}</strong></td>
      <td>${qrEscape(r.student_age || '—')}</td>
      <td>${qrEscape(r.experience_level || '—')}</td>
      <td><span class="badge ${statusClass}">${qrEscape(statusLabel)}</span></td>
      <td style="font-size:12px;color:var(--gray-500);white-space:nowrap">${created}</td>
      <td>${digits ? `<button class="contact-action-btn" style="opacity:1" onclick="window.open('https://wa.me/${digits}','_blank')" title="Abrir WhatsApp"><i class="fab fa-whatsapp"></i></button>` : '—'}</td>
    </tr>`;
  }).join('');
}

setInterval(function(){
  const pg = document.getElementById('page-qrcode');
  if (pg && pg.classList.contains('active')) loadQrLeads();
}, 15000);

'''
s = s.replace(js_anchor, qr_js + js_anchor, 1)

p.write_text(s, encoding='utf-8')
print('Patched index.html')
