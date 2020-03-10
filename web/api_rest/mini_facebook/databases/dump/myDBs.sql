
-- create databases
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
