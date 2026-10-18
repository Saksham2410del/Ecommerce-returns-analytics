// Sends the daily return summary email to the marketing and product teams.
//
// Setup:
//   1. Run `python return_summary.py` and import return_summary.csv into a
//      Google Sheet tab named "Return Analytics".
//   2. Open Extensions > Apps Script, paste this file, and run setupDailyTrigger() once.
//
// The email numbers are read from the sheet, so they update whenever the sheet does.

const RECIPIENT_EMAILS = "marketing@ecommerce.com, product@ecommerce.com";
const ALERT_RETURN_RATE = 15; // categories above this return rate (%) get flagged

function sendReturnSummary() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Return Analytics");
  const data = sheet.getDataRange().getValues();
  if (data.length < 2) return;

  // Find columns by header name so the column order in the sheet doesn't matter
  const header = data[0];
  const col = name => header.indexOf(name);
  const rows = data.slice(1);

  let emailHtml = "<h2>Daily Return Rate Summary</h2>";
  emailHtml += "<table border='1' cellpadding='6' style='border-collapse: collapse; font-family: Arial, sans-serif;'>";
  emailHtml += "<tr style='background-color: #f2f2f2;'><th>Category</th><th>Purchases</th><th>Returns</th>"
             + "<th>Return Rate</th><th>Refunds (Rs.)</th><th>Share of Refunds</th></tr>";

  const flagged = [];
  rows.forEach(row => {
    const category = row[col("product_category")];
    const rate = Number(row[col("return_rate_pct")]);
    const isHigh = rate > ALERT_RETURN_RATE;
    if (isHigh) flagged.push(row);

    emailHtml += `<tr style="background-color: ${isHigh ? "#ffebee" : "#ffffff"};">`
               + `<td>${category}</td>`
               + `<td>${row[col("total_purchases")]}</td>`
               + `<td>${row[col("total_returns")]}</td>`
               + `<td>${rate.toFixed(1)}%</td>`
               + `<td>${Number(row[col("total_refund_inr")]).toLocaleString("en-IN")}</td>`
               + `<td>${Number(row[col("share_of_refunds_pct")]).toFixed(1)}%</td>`
               + "</tr>";
  });
  emailHtml += "</table><br/>";

  let subject = "Daily Return Summary: all categories normal";

  if (flagged.length > 0) {
    const names = flagged.map(row => row[col("product_category")]).join(", ");
    subject = `Return Alert: high return rate in ${names}`;

    flagged.forEach(row => {
      emailHtml += `<p><strong>${row[col("product_category")]}</strong> has a `
                 + `${Number(row[col("return_rate_pct")]).toFixed(1)}% return rate and makes up `
                 + `${Number(row[col("share_of_returns_pct")]).toFixed(0)}% of all returns and `
                 + `${Number(row[col("share_of_refunds_pct")]).toFixed(0)}% of all refunds.</p>`;
    });
    emailHtml += "<p style='color: #c0392b;'><strong>Suggested action:</strong> review paid ads "
               + "for these categories and check product size guides.</p>";
  }

  MailApp.sendEmail({ to: RECIPIENT_EMAILS, subject: subject, htmlBody: emailHtml });
}

function setupDailyTrigger() {
  // Remove any old trigger first so the email isn't sent twice
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === "sendReturnSummary") {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger("sendReturnSummary")
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
}
