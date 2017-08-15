package wsclient;

public class InvoiceClient {
  public static void main(String[] args) {
		InvoiceService service = new InvoiceService();
		Invoice invoice = service.getInvoicePort();
		String date_format = invoice.getInvoiceDateById("12345A");
		System.out.println(date_format);
	}
}
