/**
 * Script Properties keys (set in GAS editor: Project Settings > Script properties):
 *   WEBHOOK_URL          - Python POST /webhook/email URL
 *   WEBHOOK_SECRET       - Shared secret; sent as x-webhook-secret header
 *   GAS_WEBAPP_SECRET    - Secret Python must send in callback JSON body
 *   SPREADSHEET_ID       - Google Sheet ID for PO Data / Items / Monitoring
 *   NOTIFICATION_RECIPIENTS - Comma-separated emails for notifications
 *   IMAGE_WEBHOOK_URL    - Python POST /webhook/drive-image URL
 *   IMAGE_DRIVE_FOLDER_ID - Google Drive folder ID for new images
 *   IMAGE_SPREADSHEET_ID - Separate Google Sheet for image tagging results
 */

function getConfig(key) {
  var value = PropertiesService.getScriptProperties().getProperty(key);
  if (!value) {
    throw new Error('Missing Script Property: ' + key);
  }
  return value;
}

/** Gmail search: unread PO-like subjects, exclude already labeled and own notifications */
var SEARCH_QUERY =
  'subject:(PO OR "Purchase Order") is:unread -label:PO-Processed -label:PO-Processing-Failed -subject:"PO Processed:" -subject:"PO Processing FAILED:" -from:me';

var LABEL_PROCESSED = 'PO-Processed';
var LABEL_FAILED = 'PO-Processing-Failed';

var TAB_PO_DATA = 'PO Data';
var TAB_PO_ITEMS = 'PO Items';
var TAB_MONITORING = 'Monitoring Logs';

/** Script property key names (values set in Project Settings) */
var IMAGE_WEBHOOK_URL_KEY = 'IMAGE_WEBHOOK_URL';
var IMAGE_DRIVE_FOLDER_ID_KEY = 'IMAGE_DRIVE_FOLDER_ID';
var IMAGE_SPREADSHEET_ID_KEY = 'IMAGE_SPREADSHEET_ID';

var LABEL_IMAGE_PROCESSED = 'Image-Processed';
var LABEL_IMAGE_FAILED = 'Image-Processing-Failed';

var TAB_IMAGE_DATA = 'Image Tags';
var TAB_IMAGE_MONITORING = 'Image Monitoring';
