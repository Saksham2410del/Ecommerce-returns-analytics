const RECIPIENT_EMAILS = "marketing@ecommerce.com, product@ecommerce.com";

function sendReturnSummary() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Return Analytics") 
                || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  const data = sheet.getDataRange().getValues();
  if (!data || data.length < 2) return;

  let emailHtml = "<h2>Automated Return Rate Alert</h2>";
  emailHtml += "<p>Summary generated from the return analytics data pipeline.</p>";
  emailHtml += "<table border='1' cellpadding='6' style='border-collapse: collapse; font-family: Arial, sans-serif;'>";

  data.forEach((row, i) => {
    let isApparel = row.some(cell => String(cell).toLowerCase().includes("apparel"));
    let bgColor = (i === 0) ? "#f2f2f2" : (isApparel ? "#ffebee" : "#ffffff");
    emailHtml += `<tr style="background-color: ${bgColor};">`;
    row.forEach(cell => {
      emailHtml += (i === 0) ? `<th><b>${cell}</b></th>` : `<td>${cell}</td>`;
    });
    emailHtml += "</tr>";
  });

  emailHtml += "</table>";
  emailHtml += "<br/>";
  emailHtml += "<p><strong>Observation:</strong> Apparel accounts for 66% of all returns and Rs. 16.6 Lakh in refunds, driven entirely by size issues.</p>";
  emailHtml += "<p style='color: #c0392b;'><strong>Action Required:</strong> Marketing team advised to pause paid ad spend on high-return Apparel SKUs.</p>";

  MailApp.sendEmail({
    to: RECIPIENT_EMAILS,
    subject: "Return Alert: Elevated Apparel Return Rate (31.7%)",
    htmlBody: emailHtml
  });
}

function setupDailyTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(t => {
    if (t.getHandlerFunction() === 'sendReturnSummary') {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger('sendReturnSummary')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
}
