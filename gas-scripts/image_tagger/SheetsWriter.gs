var _cachedImageSpreadsheetId = null;
var _cachedImageSpreadsheet = null;

function getImageSpreadsheet() {
  var id = getConfig(IMAGE_SPREADSHEET_ID_KEY);
  if (_cachedImageSpreadsheetId === id && _cachedImageSpreadsheet) {
    return _cachedImageSpreadsheet;
  }
  _cachedImageSpreadsheetId = id;
  _cachedImageSpreadsheet = SpreadsheetApp.openById(id);
  return _cachedImageSpreadsheet;
}

/**
 * Image Tags tab: Image ID, Filename, Drive File ID, Tags JSON, Confidence, Processing Status, Timestamp
 */
function writeImageData(payload) {
  var sheet = getImageSpreadsheet().getSheetByName(TAB_IMAGE_DATA);
  if (!sheet) {
    Logger.log('Sheet tab "' + TAB_IMAGE_DATA + '" not found');
    return;
  }
  sheet.appendRow([
    payload.image_id || '',
    payload.filename || '',
    payload.drive_file_id || '',
    JSON.stringify(payload.tag_record || {}),
    payload.confidence != null ? payload.confidence : '',
    payload.processing_status || '',
    cairoNowString(),
  ]);
}

/**
 * Image Monitoring tab: Timestamp, Image ID, Filename, Status, Processing Time (ms), Errors
 */
function writeImageMonitoringLog(payload, status) {
  var sheet = getImageSpreadsheet().getSheetByName(TAB_IMAGE_MONITORING);
  if (!sheet) {
    Logger.log('Sheet tab "' + TAB_IMAGE_MONITORING + '" not found');
    return;
  }
  sheet.appendRow([
    cairoNowString(),
    payload.image_id || '',
    payload.filename || '',
    status,
    payload.processing_time_ms != null ? payload.processing_time_ms : '',
    JSON.stringify(payload.errors || []),
  ]);
}
