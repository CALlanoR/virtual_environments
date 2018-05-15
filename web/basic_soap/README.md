1. Create image with java installed
sudo docker build -t java_soap_image .

2. Verify images
sudo docker images

3. Create server and client containers
sudo docker run -di -p 127.0.0.1:1212:1212 --name=server_soap_java java_soap_image

4. Verify ip address of each container
sudo docker ps -a
sudo docker exec -it server_soap_java bash

5. Create the Invoice service:
In server_soap_java container:
- cd home/server
- The service is Invoice.java
- The starter service is ServiceInvoiceStarter.java
- Compile the code:
  - javac -d . *.java
- Start the service:
  - java wsserver/ServiceInvoiceStarter
- Check Running Service (The output is the WSDL file):
  - curl http://localhost:1212/get_invoice_date_by_id?wsdl

In the same container (open another terminal sudo docker exec -it <<ID>> bash):
- Create the client:
  - cd home/client
  - wsimport -d . -p wsclient -keep http://localhost:1212/get_invoice_date_by_id?wsdl
-  Invoke the Web Service:
  - ls -la
  - javac -d . *.java
  - java wsclient.InvoiceClient
