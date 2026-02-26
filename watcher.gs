var SPREADSHEET_ID = '1GuiICjRn7netb9fThkwiDm_6YgBbNKOYY7ck5D_yLiI';
var BINANCE_API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT';
var TELEGRAM_TOKEN = PropertiesService.getScriptProperties().getProperty('TELEGRAM_TOKEN');
var TELEGRAM_CHAT_ID = PropertiesService.getScriptProperties().getProperty('TELEGRAM_CHAT_ID');

/**
 * Hàm chạy mỗi phút để kiểm tra trạng thái các tín hiệu.
 */
function watchSignals() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName('signals');
  var data = sheet.getDataRange().getValues();
  
  // Lấy giá hiện tại từ Binance
  var currentPrice = getBinancePrice();
  if (!currentPrice) return;
  
  var now = new Date();
  
  // Duyệt qua dữ liệu (bỏ dòng tiêu đề)
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    var state = row[7]; // Cột State (0-indexed: ID=0, Time=1, ..., State=7)
    
    if (state === 'WAITING_FOR_ENTRY') {
      checkEntry(sheet, i + 1, row, currentPrice, now);
    } else if (state === 'ENTRY_HIT') {
      checkExit(sheet, i + 1, row, currentPrice, now);
    }
  }
}

function checkEntry(sheet, rowIdx, rowData, currentPrice, now) {
  var direction = rowData[3];
  var entryPrice = rowData[4];
  
  var hit = false;
  if (direction === 'BUY' && currentPrice <= entryPrice) hit = true;
  if (direction === 'SELL' && currentPrice >= entryPrice) hit = true;
  
  if (hit) {
    sheet.getRange(rowIdx, 8).setValue('ENTRY_HIT'); // Cột State
    sheet.getRange(rowIdx, 11).setValue(now);       // Cột EntryTime
    sendTelegram('✅ *Entry Hit: ' + rowData[0] + '*\n' + direction + ' EURUSDT tại ' + currentPrice);
  } else {
    // Kiểm tra hết hạn (ví dụ > 90 phút không khớp)
    var createdAt = new Date(rowData[8]); // Cột CreatedAt
    if ((now - createdAt) / (1000 * 60) > 90) {
      sheet.getRange(rowIdx, 8).setValue('EXPIRED');
    }
  }
}

function checkExit(sheet, rowIdx, rowData, currentPrice, now) {
  var direction = rowData[3];
  var tp = rowData[5];
  var sl = rowData[6];
  
  var closed = false;
  var outcome = '';
  
  if (direction === 'BUY') {
    if (currentPrice >= tp) { closed = true; outcome = 'CLOSED_WIN'; }
    else if (currentPrice <= sl) { closed = true; outcome = 'CLOSED_LOSS'; }
  } else { // SELL
    if (currentPrice <= tp) { closed = true; outcome = 'CLOSED_WIN'; }
    else if (currentPrice >= sl) { closed = true; outcome = 'CLOSED_LOSS'; }
  }
  
  if (closed) {
    sheet.getRange(rowIdx, 8).setValue(outcome);
    sheet.getRange(rowIdx, 12).setValue(now); // Cột CloseTime
    var emoji = outcome === 'CLOSED_WIN' ? '💰' : '❌';
    sendTelegram(emoji + ' *Signal Closed: ' + rowData[0] + '*\nKết quả: ' + outcome + '\nGiá đóng: ' + currentPrice);
    
    // Đồng bộ sang sheet model_results
    syncToModelResults(rowData[0], outcome, now);
  }
}

function syncToModelResults(id, outcome, closeTime) {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var resSheet = ss.getSheetByName('model_results');
  var data = resSheet.getDataRange().getValues();
  
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] === id) {
      resSheet.getRange(i + 1, 10).setValue(outcome); // Cột State (giả định cột 10)
      resSheet.getRange(i + 1, 11).setValue(closeTime); 
      resSheet.getRange(i + 1, 12).setValue(outcome === 'CLOSED_WIN' ? 'win' : 'loss'); // Cột Outcome
      break;
    }
  }
}

function getBinancePrice() {
  try {
    var response = UrlFetchApp.fetch(BINANCE_API_URL);
    var json = JSON.parse(response.getContentText());
    return parseFloat(json.price);
  } catch (e) {
    console.error('Lỗi lấy giá Binance: ' + e);
    return null;
  }
}

function sendTelegram(text) {
  if (!TELEGRAM_TOKEN) return;
  var url = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/sendMessage';
  var payload = {
    'chat_id': TELEGRAM_CHAT_ID,
    'text': text,
    'parse_mode': 'Markdown'
  };
  UrlFetchApp.fetch(url, {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  });
}
