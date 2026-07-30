function sendDailyReport() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Return Analytics");
  if (!sheet) return;

  const data = sheet.getRange("A1:C5").getValues(); 
  
  let body = "<h2>Daily E-Commerce Return Rate Report</h2>";
  body += "<p>Please review the automated return metrics below. Note the spike in Apparel returns.</p>";
  body += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>";
  
  data.forEach((row, index) => {
    body += "<tr>";
    row.forEach(cell => {
      if (index === 0) {
        body += `<th style="background-color: #f2f2f2;">${cell}</th>`;
      } else {
        body += `<td>${cell}</td>`;
      }
    });
    body += "</tr>";
  });
  
  body += "</table>";
  body += "<p><em>Action Required: Marketing team to pause Apparel ad spend.</em></p>";

  MailApp.sendEmail({
    to: "marketing-team@ecommerce.com, product-team@ecommerce.com",
    subject: "URGENT: Daily Product Return Analytics",
    htmlBody: body
  });
}
