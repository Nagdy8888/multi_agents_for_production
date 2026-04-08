/**
 * Time-driven entry: search Gmail, POST each message to Python webhook, mark read on success.
 * Max 10 threads per run (6-minute execution limit).
 */

function processNewEmails() {
  try {
    var webhookUrl = getConfig('WEBHOOK_URL');
    var secret = getConfig('WEBHOOK_SECRET');
    var threads = GmailApp.search(SEARCH_QUERY, 0, 10);

    for (var i = 0; i < threads.length; i++) {
      var thread = threads[i];
      var messages = thread.getMessages();
      for (var j = 0; j < messages.length; j++) {
        var message = messages[j];
        if (!message.isUnread()) {
          continue;
        }
        postMessageToWebhook(message, webhookUrl, secret);
      }
    }
  } catch (err) {
    Logger.log('processNewEmails error: ' + err);
  }
}

function postMessageToWebhook(message, webhookUrl, secret) {
  var attachments = message.getAttachments();
  var attachmentPayload = [];
  for (var a = 0; a < attachments.length; a++) {
    var att = attachments[a];
    attachmentPayload.push({
      filename: att.getName(),
      content_type: att.getContentType(),
      data_base64: Utilities.base64Encode(att.getBytes()),
    });
  }

  Logger.log('Processing email: ' + message.getSubject());

  var payload = {
    subject: message.getSubject(),
    body: message.getPlainBody(),
    sender: message.getFrom(),
    timestamp: message.getDate().toISOString(),
    message_id: message.getId(),
    attachments: attachmentPayload,
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
      'Webhook failed for ' +
        message.getId() +
        ' HTTP ' +
        code +
        ' ' +
        response.getContentText()
    );
    labelMessage(message.getId(), LABEL_FAILED);
    return;
  }

  message.markRead();
}

/**
 * Install a time-driven trigger every 5 minutes. Run once from the GAS editor after deploy.
 */
function installFiveMinuteTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'processNewEmails') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  ScriptApp.newTrigger('processNewEmails').timeBased().everyMinutes(5).create();
}
