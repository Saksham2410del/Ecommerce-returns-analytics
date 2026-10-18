// Sends the daily return summary email to the marketing and product teams.
//
// Setup:
//   1. Run `python return_summary.py` and import return_summary.csv into a
//      Google Sheet tab named "Return Analytics".
//   2. Open Extensions > Apps Script, paste this file, and run setupDailyTrigger() once.
//
// Sheet columns (same order as return_summary.csv):
//   0 product_category | 1 total_purchases | 2 total_returns | 3 total_refund_inr
//   4 return_rate_pct  | 5 share_of_returns_pct | 6 share_of_refunds_pct

var RECIPIENT_EMAILS = "marketing@ecommerce.com, product@ecommerce.com";
var ALERT_RETURN_RATE = 15;   // flag any category with a return rate above 15%

function sendReturnSummary() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Return Analytics");
  var data = sheet.getDataRange().getValues();

  var table = "<table border='1' cellpadding='6' style='border-collapse: collapse;'>";
  table += "<tr><th>Category</th><th>Purchases</th><th>Returns</th><th>Return Rate</th><th>Refunds (Rs.)</th></tr>";

  var alerts = "";
  var flaggedCategories = [];

  // row 0 is the header, so start from 1
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    var category = row[0];
    var returnRate = Number(row[4]);

    var color = "#ffffff";
    if (returnRate > ALERT_RETURN_RATE) {
      color = "#ffebee";
      flaggedCategories.push(category);
      alerts += "<p><b>" + category + "</b> has a " + returnRate.toFixed(1) + "% return rate. "
              + "It makes up " + Math.round(row[5]) + "% of all returns and "
              + Math.round(row[6]) + "% of all refunds.</p>";
    }

    table += "<tr style='background-color: " + color + ";'>"
           + "<td>" + category + "</td>"
           + "<td>" + row[1] + "</td>"
           + "<td>" + row[2] + "</td>"
           + "<td>" + returnRate.toFixed(1) + "%</td>"
           + "<td>" + Math.round(row[3]) + "</td>"
           + "</tr>";
  }
  table += "</table>";

  var subject = "Daily Return Summary: all categories normal";
  var body = "<h2>Daily Return Rate Summary</h2>" + table;

  if (flaggedCategories.length > 0) {
    subject = "Return Alert: high return rate in " + flaggedCategories.join(", ");
    body += alerts;
    body += "<p style='color: #c0392b;'><b>Suggested action:</b> review paid ads for these "
          + "categories and check the product size guides.</p>";
  }

  MailApp.sendEmail({
    to: RECIPIENT_EMAILS,
    subject: subject,
    htmlBody: body
  });
}

// Run this once to send the email every day at 9 AM
function setupDailyTrigger() {
  // delete the old trigger first so the email isn't sent twice
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() == "sendReturnSummary") {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }

  ScriptApp.newTrigger("sendReturnSummary")
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
}
