/**
 * Quantix AI Core - Terminal Dashboard Server
 * Copy code này vào Apps Script của bạn.
 */

var SPREADSHEET_ID = '1GuiICjRn7netb9fThkwiDm_6YgBbNKOYY7ck5D_yLiI';

function doGet(e) {
  if (e && e.parameter && e.parameter.cmd === 'data') {
    var data = getDashboardData();
    return ContentService.createTextOutput(JSON.stringify(data))
      .setMimeType(ContentService.MimeType.JSON);
  }

  if (e && e.parameter && e.parameter.cmd === 'save_bt') {
    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    saveBacktestResult(ss, e.parameter);
    return ContentService.createTextOutput(JSON.stringify({status: 'ok'}))
      .setMimeType(ContentService.MimeType.JSON);
  }

  return HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setTitle('Quantix Terminal')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function getDashboardData() {
  try {
    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    return {
      active: getActiveSignals(ss),
      history: getSignalHistory(ss),
      logs: getSystemLogs(ss),
      stats: getQuickStats(ss),
      learning: getLearningHistory(ss),
      market: getMarketData(ss)
    };
  } catch (e) {
    return { error: e.toString() };
  }
}

function getMarketData(ss) {
  var sheet = ss.getSheetByName('market_data');
  if (!sheet) return [];
  try {
    var data = sheet.getDataRange().getValues();
    var market = [];
    if (data.length <= 1) return [];
    
    var start = Math.max(1, data.length - 300);
    for (var i = start; i < data.length; i++) {
        market.push({
            time: data[i][0], open: data[i][2], high: data[i][3],
            low: data[i][4], close: data[i][5]
        });
    }
    return market;
  } catch(e) { return []; }
}

function getLearningHistory(ss) {
  var sheet = ss.getSheetByName('learning_history');
  if (!sheet) return [];
  try {
    var data = sheet.getDataRange().getValues();
    var learn = [];
    if (data.length <= 1) return [];
    
    for (var i = data.length - 1; i >= 1; i--) {
        learn.push({
            time: Utilities.formatDate(new Date(data[i][0]), "GMT+7", "yyyy-MM-dd"),
            ema: data[i][1], rsi: data[i][2], wr: data[i][3],
            total: data[i][4], score: data[i][5]
        });
        if (learn.length >= 15) break;
    }
    return learn;
  } catch(e) { return []; }
}

function getActiveSignals(ss) {
  var sheet = ss.getSheetByName('signals');
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var active = [];
  if (data.length <= 1) return [];
  
  for (var i = 1; i < data.length; i++) {
    var state = data[i][7];
    if (state === 'WAITING_FOR_ENTRY' || state === 'ENTRY_HIT') {
      active.push({
        id: data[i][0], pair: data[i][2], direction: data[i][3],
        entry: data[i][4], tp: data[i][5], sl: data[i][6], state: state
      });
    }
  }
  return active;
}

function getSignalHistory(ss) {
  var sheet = ss.getSheetByName('signals');
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var history = [];
  if (data.length <= 1) return [];
  
  for (var i = data.length - 1; i >= 1; i--) {
    var state = data[i][7];
    if (state.includes('CLOSED') || state === 'EXPIRED') {
      history.push({
        time: Utilities.formatDate(new Date(data[i][1]), "GMT+7", "yyyy-MM-dd HH:mm"),
        closeTime: data[i][11] ? Utilities.formatDate(new Date(data[i][11]), "GMT+7", "HH:mm") : '---',
        id: data[i][0], pair: data[i][2], direction: data[i][3],
        price: data[i][4], outcome: state
      });
    }
    if (history.length >= 20) break;
  }
  return history;
}

function getSystemLogs(ss) {
  var sheet = ss.getSheetByName('logs');
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var logs = [];
  if (data.length <= 1) return [];
  
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
  
  var currentModel = 'UNKNOWN';
  if (configSheet) {
    var configData = configSheet.getDataRange().getValues();
    for(var i=1; i<configData.length; i++) {
      if(configData[i][0] == 'active_model') currentModel = configData[i][1];
    }
  }

  var wr = 0;
  if (signalsSheet) {
    var data = signalsSheet.getDataRange().getValues();
    var wins = 0;
    var closed = 0;
    for (var i = 1; i < data.length; i++) {
      if (data[i][7] === 'CLOSED_WIN') { wins++; closed++; }
      else if (data[i][7] === 'CLOSED_LOSS') { closed++; }
    }
    wr = closed > 0 ? ((wins / closed) * 100).toFixed(1) : 0;
  }

  return { active_count: 0, win_rate: wr, model: currentModel };
}

function saveBacktestResult(ss, p) {
  var archiveSheet = ss.getSheetByName('backtest_archive');
  var configSheet = ss.getSheetByName('config');
  
  // Archiving
  archiveSheet.appendRow([
    new Date(), p.ema, p.rsi, p.wr, p.total, p.score, 'DASHBOARD_MANUAL'
  ]);
  
  // Update Config
  var configData = configSheet.getDataRange().getValues();
  for (var i = 1; i < configData.length; i++) {
    if (configData[i][0] == 'ema_period') configSheet.getRange(i+1, 2).setValue(p.ema);
    if (configData[i][0] == 'rsi_period') configSheet.getRange(i+1, 2).setValue(p.rsi);
  }
}
