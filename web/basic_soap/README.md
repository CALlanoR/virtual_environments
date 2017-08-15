1. Create image with java installed
sudo docker build -t java_soap_image .

2. Verify images
sudo docker images

3. Create server container
sudo docker run -di -p 127.0.0.1:1212:1212 --name=server_soap_1 java_soap_image

4. Verify ip address of each container
sudo docker ps -a
sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' <<ID>>
sudo docker exec -it <<ID>> bash

5. Create the Invoice service:
In server_soap_1 container:
- In /home/workdir are:
  - The service is Invoice.java
  - The starter service is ServiceInvoiceStarter.java
- Compile the code to generate the soap service:
  - javac -d . *.java
  - Verify the creation of the folder called wsserver
- Start the service:
  - java wsserver/ServiceInvoiceStarter
- Check Running Service (The output is the WSDL file):
  - curl http://localhost:1212/get_invoice_date_by_id?wsdl

6. - Create the client:
- open another terminal:
  - Execute sudo docker exec -it <<ID>> bash
- Copy the file InvoiceClient.java in another folder
- wsimport -d . -p wsclient -keep http://localhost:1212/get_invoice_date_by_id?wsdl
-  Invoke the Web Service:
  - cd wsclient/
  - Create InvoiceClient.java
  - javac -d . *.java
  - java wsclient.InvoiceClient
