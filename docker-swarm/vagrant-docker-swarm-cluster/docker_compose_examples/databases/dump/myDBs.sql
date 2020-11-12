
-- create databases
CREATE DATABASE IF NOT EXISTS `UsersDB`;

USE UsersDB;

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--
INSERT INTO `UsersDB`.`user` (`id`, `email`, `name`, `password`, `username`) VALUES ('1', 'mrblue@javerianacali.edu.co', 'Blue Perez', '123456', 'blue');
INSERT INTO `UsersDB`.`user` (`id`, `email`, `name`, `password`, `username`) VALUES ('2', 'mrwhite@gmail.com', 'White Mejia', 'qwerty', 'white');


DROP TABLE IF EXISTS `friend_requests`;
CREATE TABLE `friend_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id_origin` int(11) DEFAULT NULL,
  `user_id_target` int(11) DEFAULT NULL,
  `status` char(30) DEFAULT NULL,
  `create_date` datetime NOT NULL,
  `update_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_friend_requests_1_idx` (`user_id_origin`),
  KEY `fk_friend_requests_2_idx` (`user_id_target`),
  CONSTRAINT `fk_friend_requests_1` FOREIGN KEY (`user_id_origin`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_friend_requests_2` FOREIGN KEY (`user_id_target`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;