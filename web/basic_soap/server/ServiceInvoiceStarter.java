package wsserver;

import javax.xml.ws.Endpoint;

public class ServiceInvoiceStarter {
	public static void main(String[] args) {
		String url = "http://localhost:1212/get_invoice_date_by_id";
		Endpoint.publish(url, new Invoice());
		System.out.println("Service started @ " + url);
	}

}
