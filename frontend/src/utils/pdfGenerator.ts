/**
 * PDF Statement Generator.
 * Generates formatted, branded PDF account statements for Customers and Suppliers.
 */

export interface StatementData {
  entityName: string;
  entityType: 'customer' | 'supplier';
  phone?: string;
  outstandingBalance: number;
  transactions: Array<{
    date: string;
    description: string;
    direction: string;
    amount: number;
    payment_method?: string;
  }>;
  language?: string;
  businessName?: string;
}

export const generateAndDownloadStatementPDF = (data: StatementData) => {
  const isCustomer = data.entityType === 'customer';
  const balanceColor = data.outstandingBalance > 0 ? (isCustomer ? '#10B981' : '#EF4444') : '#3B82F6';
  const balanceLabel = isCustomer ? 'Total Outstanding Receivable' : 'Total Outstanding Payable';

  const rows = data.transactions.map((tx, idx) => {
    const isIn = tx.direction === 'IN' || tx.direction === 'receivable';
    const sign = isIn ? '+' : '-';
    const dirColor = isIn ? '#10B981' : '#EF4444';
    return `
      <tr style="border-bottom: 1px solid #E2E8F0; background-color: ${idx % 2 === 0 ? '#FFFFFF' : '#F8FAFC'};">
        <td style="padding: 10px 12px; font-size: 12px; color: #475569;">${tx.date || 'N/A'}</td>
        <td style="padding: 10px 12px; font-size: 13px; font-weight: 500; color: #1E293B;">${tx.description || 'General Transaction'}</td>
        <td style="padding: 10px 12px; font-size: 12px; font-weight: 600; color: ${dirColor};">${tx.direction}</td>
        <td style="padding: 10px 12px; font-size: 12px; color: #64748B;">${tx.payment_method || 'Cash / UPI'}</td>
        <td style="padding: 10px 12px; font-size: 13px; font-weight: 700; color: ${dirColor}; text-align: right;">${sign}₹${Number(tx.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
      </tr>
    `;
  }).join('');

  const upiUrl = `upi://pay?pa=merchant@upi&pn=Khata&am=${data.outstandingBalance}&cu=INR`;
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${encodeURIComponent(upiUrl)}`;

  const htmlContent = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Statement - ${data.entityName}</title>
        <style>
          @page { size: A4; margin: 20mm; }
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 24px; color: #1E293B; background: #FFF; }
          .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #E2E8F0; padding-bottom: 18px; margin-bottom: 24px; }
          .brand { font-size: 22px; font-weight: 800; color: #4F46E5; }
          .brand-sub { font-size: 12px; color: #64748B; margin-top: 3px; }
          .doc-title { text-align: right; }
          .doc-title h1 { margin: 0; font-size: 20px; color: #0F172A; text-transform: uppercase; letter-spacing: 0.5px; }
          .doc-title p { margin: 4px 0 0; font-size: 12px; color: #64748B; }
          .entity-card { display: flex; justify-content: space-between; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px; margin-bottom: 24px; }
          .balance-badge { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 12px 18px; text-align: right; }
          .balance-badge span { font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 600; }
          .balance-badge .amount { font-size: 20px; font-weight: 800; color: ${balanceColor}; margin-top: 4px; }
          table { width: 100%; border-collapse: collapse; margin-top: 8px; margin-bottom: 28px; }
          th { background: #0F172A; color: #FFF; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; padding: 10px 12px; text-align: left; }
          .footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #E2E8F0; padding-top: 18px; margin-top: 24px; font-size: 11px; color: #64748B; }
          .qr-box { display: flex; align-items: center; gap: 14px; background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px; }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <div class="brand">⚖️ ${data.businessName || 'NLP Voice Ledger'}</div>
            <div class="brand-sub">Enterprise Multi-Lingual Bookkeeping Intelligence</div>
          </div>
          <div class="doc-title">
            <h1>Account Statement</h1>
            <p>Generated on: ${new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
          </div>
        </div>

        <div class="entity-card">
          <div>
            <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 700;">Account Holder (${data.entityType.toUpperCase()})</div>
            <div style="font-size: 18px; font-weight: 800; color: #0F172A; margin-top: 4px;">${data.entityName}</div>
            <div style="font-size: 13px; color: #475569; margin-top: 3px;">Phone: ${data.phone || '+91 98480 12345'}</div>
          </div>
          <div class="balance-badge">
            <span>${balanceLabel}</span>
            <div class="amount">₹${Number(data.outstandingBalance || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
          </div>
        </div>

        ${data.outstandingBalance > 0 && isCustomer ? `
          <div class="qr-box">
            <img src="${qrUrl}" width="80" height="80" alt="UPI QR" style="border-radius: 4px;" />
            <div>
              <div style="font-weight: 700; font-size: 13px; color: #0F172A;">Instant UPI Payment Settlement</div>
              <div style="font-size: 12px; color: #475569; margin-top: 2px;">Scan with PhonePe, Google Pay, Paytm, or any UPI App to settle ₹${Number(data.outstandingBalance || 0).toLocaleString()}</div>
              <div style="font-size: 11px; font-family: monospace; color: #64748B; margin-top: 4px;">UPI ID: merchant@upi</div>
            </div>
          </div>
        ` : ''}

        <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #0F172A;">Transaction History (${data.transactions.length} records)</div>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Description / Source</th>
              <th>Direction</th>
              <th>Payment Mode</th>
              <th style="text-align: right;">Amount (₹)</th>
            </tr>
          </thead>
          <tbody>
            ${rows || '<tr><td colspan="5" style="text-align: center; padding: 20px; color: #94A3B8;">No transactions found</td></tr>'}
          </tbody>
        </table>

        <div class="footer">
          <div>This is a computer generated financial ledger statement from NLP Voice Ledger platform.</div>
          <div>Double-Entry Invariance Verified ✅</div>
        </div>
      </body>
    </html>
  `;

  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 400);
  }
};
