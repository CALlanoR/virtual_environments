sudo docker build -t my_website_image .
sudo docker images
sudo docker run -di -p 80:80 --name=mywebsite my_website_image
sudo docker ps -a
sudo docker logs mywebsite

# Create another container with the same image but with different port
sudo docker run -di -p 8080:80 --name=mywebsite my_website_image
sudo docker ps -a
sudo docker logs mywebsite2