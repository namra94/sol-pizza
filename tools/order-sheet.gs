/* Sol Hanoi — the Order Sheet's Order Guide, for the back office's purchase requests
   (sol.pizza/backoffice/purchase/; worker/backoffice.js in the sol-pizza repo).
   A web app bound to the "Sol Hanoi — Order Sheet" Google Sheet. The Worker fetches
   it (the secret ORDER_GUIDE_URL: this web app's address with ?token=…) and gets the
   suppliers, the items with their prices, the approval settings and the staff's
   names, as JSON. It answers only to the token in the script property TOKEN; to
   anything else, {"error":"forbidden"}. It finds every column by its header in row
   1, never by its position, so columns can be moved or added; and it never sends the
   contact, terms or price-list columns. Rows with no supplier are left out.
   Setting it up, and changing the token: README-DEPLOY.md in the repo, "The back
   office: purchase requests". Paste this file as it is: nothing in it is secret.
   Every name below is the sheet's own; if a tab or a header is renamed, rename it
   here too, or the Worker gets an error (and keeps its last good copy). */

const TABS = { items: 'Order Guide', suppliers: 'Suppliers', settings: 'Settings' };

// The Order Guide tab: [header, key in the JSON, must it be there?]
const ITEM_COLUMNS = [
  ['Supplier', 'supplier', true], ['Item (EN)', 'en', true], ['Item (VN)', 'vn', false],
  ['Unit', 'unit', true], ['Unit (VN)', 'unit_vn', false], ['Pack / size', 'pack', false],
  ['Price before VAT (VND)', 'price', true], ['VAT', 'vat', false], ['Par', 'par', false],
  ['Category', 'category', false], ['Notes / MOQ', 'notes', false], ['Code', 'code', false],
];
// The Suppliers tab: only these go out, never Contact / Zalo, Terms / VAT, Price list or Notes
const SUPPLIER_COLUMNS = [
  ['Supplier', 'name', true], ['Supplies', 'supplies', false], ['Station', 'station', true],
  ['Status', 'status', true], ['Owner (places the order)', 'owner', false], ['Order days', 'order_days', false],
  ['Cut-off', 'cutoff', false], ['Delivery', 'delivery', false], ['Min order', 'min_order', false],
];
// The Settings tab: a label in column A, its value in column B
const SETTINGS = [
  ['Approval limit (VND, before VAT)', 'limit'], ['Kitchen approver', 'kitchen_approver'],
  ['Bar & FOH approver', 'barfoh_approver'], ['Big orders / new suppliers', 'owner'],
];
// …and the staff's names for "Requested by", down column A from the row under this one
// to the first empty cell
const STAFF_LABEL = "Staff — 'Requested by' list";

function doGet(e) {
  const token = PropertiesService.getScriptProperties().getProperty('TOKEN');
  const given = (e && e.parameter && e.parameter.token) || '';
  if (!token || given !== token) return json_({ error: 'forbidden' });
  try {
    return json_(orderGuide_(SpreadsheetApp.getActiveSpreadsheet()));
  } catch (err) {
    return json_({ error: String((err && err.message) || err) });
  }
}

// The JSON the Worker reads (the contract is in worker/backoffice.js and README-DEPLOY.md)
function orderGuide_(book) {
  const settings = settings_(book);
  return {
    updated: Utilities.formatDate(new Date(), 'Asia/Ho_Chi_Minh', "yyyy-MM-dd'T'HH:mm:ssXXX"),
    settings: settings.values,
    staff: settings.staff,
    suppliers: rows_(book, TABS.suppliers, SUPPLIER_COLUMNS).filter((r) => r.name !== ''),
    items: rows_(book, TABS.items, ITEM_COLUMNS).filter((r) => r.supplier !== ''),
  };
}

// A tab's rows as objects. Text as the sheet shows it; price and par as numbers (a blank
// cell, or one that isn't a number, is null).
function rows_(book, tab, columns) {
  const range = sheet_(book, tab).getDataRange();
  const values = range.getValues(), shown = range.getDisplayValues();
  const headers = shown[0].map(same_);
  const at = {};
  columns.forEach(([header, key, needed]) => {
    at[key] = headers.indexOf(same_(header));
    if (at[key] < 0 && needed) throw new Error(tab + ': no "' + header + '" column in row 1');
  });
  return values.slice(1).map((row, r) => {
    const out = {};
    columns.forEach(([, key]) => {
      const i = at[key];
      if (key === 'price') out[key] = i < 0 ? null : number_(row[i], true);
      else if (key === 'par') out[key] = i < 0 ? null : number_(row[i], false);
      else out[key] = i < 0 ? '' : String(shown[r + 1][i]).trim();
    });
    return out;
  });
}

function settings_(book) {
  const range = sheet_(book, TABS.settings).getDataRange();
  const values = range.getValues(), shown = range.getDisplayValues();
  const labels = shown.map((row) => same_(row[0]));
  const out = {};
  SETTINGS.forEach(([label, key]) => {
    const i = labels.indexOf(same_(label));
    const cell = i < 0 ? '' : (values[i] || [])[1], text = i < 0 ? '' : String((shown[i] || [])[1] || '').trim();
    out[key] = key === 'limit' ? (i < 0 ? null : number_(cell, true)) : text;
  });
  const staff = [];
  const start = labels.indexOf(same_(STAFF_LABEL));
  for (let i = start + 1; start >= 0 && i < shown.length && String(shown[i][0]).trim(); i++) {
    staff.push(String(shown[i][0]).trim());
  }
  return { values: out, staff: staff };
}

function sheet_(book, tab) {
  const sheet = book.getSheetByName(tab);
  if (!sheet) throw new Error('no "' + tab + '" tab');
  return sheet;
}

// A cell as a number: as it is if it is one; typed as text, dong are whole
// ("95.000", "95,000 đ" are 95000) and a par may have a decimal ("1,5" is 1.5)
function number_(v, whole) {
  if (typeof v === 'number') return isFinite(v) && v >= 0 ? v : null;
  const s = String(v).trim();
  if (!s) return null;
  const n = whole ? Number(s.replace(/[^\d]/g, '')) : parseFloat(s.replace(',', '.'));
  return s.replace(/[^\d]/g, '') !== '' && isFinite(n) && n >= 0 ? n : null;
}

// Headers and labels compared without case, curly quotes, long dashes or extra spaces
function same_(s) {
  return String(s).toLowerCase().replace(/[‘’`´]/g, "'").replace(/[–—]/g, '-').replace(/\s+/g, ' ').trim();
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
