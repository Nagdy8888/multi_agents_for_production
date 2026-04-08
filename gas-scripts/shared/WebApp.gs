/**
 * Web App: POST JSON from Python callback.
 * Dispatches based on payload.type: "po_result" or "image_result".
 */

function doPost(e) {
  try {
    if (!e.postData || !e.postData.contents) {
      return jsonResponse({ status: 'error', message: 'Empty body' });
    }
    var payload = JSON.parse(e.postData.contents);
    var expected = getConfig('GAS_WEBAPP_SECRET');
    if (!payload.secret || payload.secret !== expected) {
      return jsonResponse({ status: 'error', message: 'Invalid secret' });
    }

    var type = payload.type || 'po_result';

    if (type === 'po_result') {
      return handlePOResult(payload);
    } else if (type === 'image_result') {
      return handleImageResult(payload);
    } else {
      return jsonResponse({ status: 'error', message: 'Unknown type: ' + type });
    }
  } catch (err) {
    Logger.log('doPost error: ' + err);
    return jsonResponse({ status: 'error', message: String(err) });
  }
}

function handlePOResult(payload) {
  if (payload.status === 'success') {
    writePOData(payload);
    var poNum = (payload.po_data && payload.po_data.po_number) || '';
    writePOItems(payload.items || [], poNum);
    writeMonitoringLog(payload, 'success');
    sendPONotification(payload);
    labelMessage(payload.message_id, LABEL_PROCESSED);
  } else {
    writeMonitoringLog(payload, 'error');
    if (payload.message_id) {
      labelMessage(payload.message_id, LABEL_FAILED);
    }
    sendErrorAlert(payload);
  }
  return jsonResponse({ status: 'ok' });
}

function handleImageResult(payload) {
  if (payload.status === 'success') {
    writeImageData(payload);
    writeImageMonitoringLog(payload, 'success');
  } else {
    writeImageMonitoringLog(payload, 'error');
  }
  return jsonResponse({ status: 'ok' });
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
