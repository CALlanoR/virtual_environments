package wsserver;

import javax.jws.WebMethod;
import javax.jws.WebParam;
import javax.jws.WebService;
import javax.jws.soap.SOAPBinding;
import java.text.SimpleDateFormat;
import java.util.Date;

@WebService
@SOAPBinding(style=SOAPBinding.Style.RPC)
public class Invoice {
	public String get_invoice_date_by_id(String id) {
		// Simulate the service
		SimpleDateFormat format_date = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
    	Date now = new Date();
    	return format_date.format(now);
	}
}
