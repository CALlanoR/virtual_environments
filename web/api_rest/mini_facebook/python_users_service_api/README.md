Install packages:
python3.7 -m pip install flask Flask flask-cors PyMySQL flask-mysql PyJWT

In mysql database execute this:

-- create database
CREATE DATABASE IF NOT EXISTS `UsersDB`;

USE UsersDB;

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--
INSERT INTO `UsersDB`.`user` (`id`, `email`, `name`, `password`, `username`) VALUES ('1', 'mrblue@javerianacali.edu.co', 'Blue Perez', '123456', 'blue');


Execute the service with this command:
in one console execute this: python3.7 main.py

Execute the test with this command:
in another console execute:
cd manual_tests
python3.7 consumer.py

-- Generate swagger doc
http://localhost:5010/swagger