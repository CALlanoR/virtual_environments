sudo docker build -t my_website_httpd_image .
sudo docker images
sudo docker run -di -p 80:80 --name=mywebsitehttpd my_website_httpd_image
sudo docker ps -a
sudo docker logs mywebsitehttpd

# Create another container with the same image but with different port
sudo docker run -di -p 8080:80 --name=mywebsitehttp2 my_website_httpd_image
sudo docker ps -a
sudo docker logs mywebsitehttp2