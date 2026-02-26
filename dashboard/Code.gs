/**
 * Quantix AI Core - Terminal Dashboard Server
 * Copy code này vào Apps Script của bạn.
 */

var SPREADSHEET_ID = '1GuiICjRn7netb9fThkwiDm_6YgBbNKOYY7ck5D_yLiI';

function doGet(e) {
  // Nếu có parameter cmd=data, trả về JSON cho Dashboard ngoài (GitHub Pages)
  if (e && e.parameter && e.parameter.cmd === 'data') {
    var data = getDashboardData();
    return ContentService.createTextOutput(JSON.stringify(data))
      .setMimeType(ContentService.MimeType.JSON);
  }

  // Mặc định trả về giao diện HTML nếu mở trực tiếp
  return HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setTitle('Quantix Terminal')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function getDashboardData() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  
  return {
    active: getActiveSignals(ss),
    history: getSignalHistory(ss),
    logs: getSystemLogs(ss),
    stats: getQuickStats(ss)
  };
}

function getActiveSignals(ss) {
  var sheet = ss.getSheetByName('signals');
  var data = sheet.getDataRange().getValues();
  var active = [];
  
  // Lọc lấy các tín hiệu chưa đóng
  for (var i = 1; i < data.length; i++) {
    var state = data[i][7];
    if (state === 'WAITING_FOR_ENTRY' || state === 'ENTRY_HIT') {
      active.push({
        id: data[i][0],
        pair: data[i][2],
        direction: data[i][3],
        entry: data[i][4],
        tp: data[i][5],
        sl: data[i][6],
        state: state
      });
    }
  }
  return active.slice(-10); // Lấy 10 cái mới nhất
}

function getSignalHistory(ss) {
  var sheet = ss.getSheetByName('signals');
  var data = sheet.getDataRange().getValues();
  var history = [];
  
  for (var i = data.length - 1; i >= 1; i--) {
    var state = data[i][7];
    if (state.includes('CLOSED') || state === 'EXPIRED') {
      history.push({
        time: Utilities.formatDate(new Date(data[i][1]), "GMT+7", "yyyy-MM-dd HH:mm"),
        id: data[i][0],
        pair: data[i][2],
        direction: data[i][3],
        price: data[i][4],
        outcome: state
      });
    }
    if (history.length >= 20) break;
  }
  return history;
}

function getSystemLogs(ss) {
  var sheet = ss.getSheetByName('logs');
  var data = sheet.getDataRange().getValues();
  var logs = [];
  
  for (var i = data.length - 1; i >= Math.max(1, data.length - 30); i--) {
    logs.push({
      time: Utilities.formatDate(new Date(data[i][0]), "GMT+7", "HH:mm:ss"),
      msg: data[i][1],
      type: data[i][1].toLowerCase().includes('error') ? 'error' : 'info'
    });
  }
  return logs;
}

function getQuickStats(ss) {
  var signalsSheet = ss.getSheetByName('signals');
  var configSheet = ss.getSheetByName('config');
  
  // Đọc config
  var configData = configSheet.getDataRange().getValues();
  var currentModel = 'UNKNOWN';
  for(var i=1; i<configData.length; i++) {
    if(configData[i][0] == 'active_model') currentModel = configData[i][1];
  }

  // Tính Win Rate sơ bộ
  var data = signalsSheet.getDataRange().getValues();
  var wins = 0;
  var closed = 0;
  for (var i = 1; i < data.length; i++) {
    if (data[i][7] === 'CLOSED_WIN') { wins++; closed++; }
    else if (data[i][7] === 'CLOSED_LOSS') { closed++; }
  }
  
  var wr = closed > 0 ? ((wins / closed) * 100).toFixed(1) : 0;

  return {
    active_count: 0, // Sẽ tính ở client
    win_rate: wr,
    model: currentModel
  };
}
