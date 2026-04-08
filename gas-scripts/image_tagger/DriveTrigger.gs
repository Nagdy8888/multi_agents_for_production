/**
 * Time-driven: check a Drive folder for new images, POST each to Python webhook.
 * "New" = created after last run timestamp (stored in Script Properties as LAST_IMAGE_CHECK).
 */

function processNewImages() {
  try {
    var webhookUrl = getConfig(IMAGE_WEBHOOK_URL_KEY);
    var secret = getConfig('WEBHOOK_SECRET');
    var folderId = getConfig(IMAGE_DRIVE_FOLDER_ID_KEY);
    var folder = DriveApp.getFolderById(folderId);

    var lastCheck = PropertiesService.getScriptProperties().getProperty('LAST_IMAGE_CHECK');
    var since = lastCheck ? new Date(lastCheck) : new Date(0);
    var now = new Date();

    var files = folder.getFiles();
    var count = 0;
    while (files.hasNext() && count < 10) {
      var file = files.next();
      if (file.getDateCreated() <= since) {
        continue;
      }
      var mimeType = file.getMimeType();
      if (mimeType.indexOf('image/') !== 0) {
        continue;
      }
      postImageToWebhook(file, webhookUrl, secret);
      count++;
    }

    PropertiesService.getScriptProperties().setProperty('LAST_IMAGE_CHECK', now.toISOString());
  } catch (err) {
    Logger.log('processNewImages error: ' + err);
  }
}

function postImageToWebhook(file, webhookUrl, secret) {
  var blob = file.getBlob();
  var payload = {
    filename: file.getName(),
    content_type: file.getMimeType(),
    drive_file_id: file.getId(),
    image_base64: Utilities.base64Encode(blob.getBytes()),
  };

  var options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'x-webhook-secret': secret,
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  var response = UrlFetchApp.fetch(webhookUrl, options);
  var code = response.getResponseCode();

  if (code < 200 || code >= 300) {
    Logger.log(
      'Image webhook failed for ' + file.getName() + ' HTTP ' + code + ' ' + response.getContentText()
    );
  }
}

/**
 * Install a time-driven trigger every 5 minutes for image processing.
 */
function installImageTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'processNewImages') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  ScriptApp.newTrigger('processNewImages').timeBased().everyMinutes(5).create();
}
