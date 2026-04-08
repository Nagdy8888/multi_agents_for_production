function parseRecipients() {
  var raw = getConfig('NOTIFICATION_RECIPIENTS');
  return raw
    .split(',')
    .map(function (e) {
      return e.trim();
    })
    .filter(function (e) {
      return e.length > 0;
    })
    .join(',');
}

function sendPONotification(payload) {
  var recipients = parseRecipients();
  if (!recipients) {
    return;
  }
  var pd = payload.po_data || {};
  var poNum = pd.po_number || '(unknown)';
  var customer = pd.customer || '';
  var val = payload.validation || {};
  var subject = 'PO Processed: ' + poNum + ' - ' + customer;
  var htmlBody =
    '<p><b>PO Number:</b> ' +
    escapeHtml(poNum) +
    '</p>' +
    '<p><b>Customer:</b> ' +
    escapeHtml(customer) +
    '</p>' +
    '<p><b>Status:</b> ' +
    escapeHtml(String(val.status || '')) +
    '</p>' +
    '<p><b>Confidence:</b> ' +
    escapeHtml(String(payload.confidence != null ? payload.confidence : '')) +
    '</p>' +
    '<p><b>Source type:</b> ' +
    escapeHtml(String(pd.source_type || '')) +
    '</p>' +
    '<p><b>Airtable:</b> ' +
    (payload.airtable_url
      ? '<a href="' + escapeHtml(payload.airtable_url) + '">' + escapeHtml(payload.airtable_url) + '</a>'
      : '') +
    '</p>';
  GmailApp.sendEmail(recipients, subject, '', { htmlBody: htmlBody });
}

function sendErrorAlert(payload) {
  var recipients = parseRecipients();
  if (!recipients) {
    return;
  }
  var mid = payload.message_id || '(unknown)';
  var subject = 'PO Processing FAILED: ' + mid;
  var htmlBody =
    '<p><b>Message ID:</b> ' +
    escapeHtml(mid) +
    '</p>' +
    '<p><b>Errors:</b> ' +
    escapeHtml(JSON.stringify(payload.errors || [])) +
    '</p>';
  GmailApp.sendEmail(recipients, subject, '', { htmlBody: htmlBody });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
