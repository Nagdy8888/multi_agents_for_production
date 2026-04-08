/**
 * Gmail labels apply to threads, not individual messages.
 */

function getOrCreateLabel(labelName) {
  var label = GmailApp.getUserLabelByName(labelName);
  if (!label) {
    label = GmailApp.createLabel(labelName);
  }
  return label;
}

/**
 * @param {string} messageId - Gmail message id
 * @param {string} labelName - label name to apply
 */
function labelMessage(messageId, labelName) {
  var label = getOrCreateLabel(labelName);
  var message = GmailApp.getMessageById(messageId);
  var thread = message.getThread();
  label.addToThread(thread);
}
