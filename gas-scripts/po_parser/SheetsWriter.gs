/**
 * Column layouts must match docs/setup/09_GOOGLE_SHEETS_SETUP.md (row 1 headers in each tab).
 */

var _cachedSpreadsheetId = null;
var _cachedSpreadsheet = null;

function getSpreadsheet() {
  var id = getConfig('SPREADSHEET_ID');
  if (_cachedSpreadsheetId === id && _cachedSpreadsheet) {
    return _cachedSpreadsheet;
  }
  _cachedSpreadsheetId = id;
  _cachedSpreadsheet = SpreadsheetApp.openById(id);
  return _cachedSpreadsheet;
}

function cairoNowString() {
  return Utilities.formatDate(new Date(), 'Africa/Cairo', 'yyyy-MM-dd HH:mm:ss');
}

/**
 * PO Data: PO Number, Customer, PO Date, Ship Date, Status, Source Type,
 * Email Subject, Sender, Confidence, Validation Status, Processing Timestamp, Airtable Link
 */
function writePOData(payload) {
  var pd = payload.po_data || {};
  var val = payload.validation || {};
  var sheet = getSpreadsheet().getSheetByName(TAB_PO_DATA);
  sheet.appendRow([
    pd.po_number || '',
    pd.customer || '',
    pd.po_date || '',
    pd.ship_date || '',
    val.status || '',
    pd.source_type || '',
    '',
    '',
    payload.confidence != null ? payload.confidence : '',
    val.status || '',
    cairoNowString(),
    payload.airtable_url || '',
  ]);
}

/**
 * PO Items: PO Number, SKU, Description, Quantity, Unit Price, Total Price, Destination/DC, Processing Timestamp
 */
function writePOItems(items, poNumber) {
  if (!items || !items.length) {
    return;
  }
  var sheet = getSpreadsheet().getSheetByName(TAB_PO_ITEMS);
  for (var i = 0; i < items.length; i++) {
    var item = items[i];
    sheet.appendRow([
      poNumber || '',
      item.sku || '',
      item.description || '',
      item.quantity != null ? item.quantity : '',
      item.unit_price != null ? item.unit_price : '',
      item.total_price != null ? item.total_price : '',
      item.destination || '',
      cairoNowString(),
    ]);
  }
}

/**
 * Monitoring: Timestamp (Cairo), Email ID, Subject, Sender, Classification Result,
 * Confidence, Parse Status, Processing Time (ms), Errors, Node
 */
function writeMonitoringLog(payload, status) {
  var sheet = getSpreadsheet().getSheetByName(TAB_MONITORING);
  sheet.appendRow([
    cairoNowString(),
    payload.message_id || '',
    '',
    '',
    status,
    payload.confidence != null ? payload.confidence : '',
    status,
    payload.processing_time_ms != null ? payload.processing_time_ms : '',
    JSON.stringify(payload.errors || []),
    '',
  ]);
}
