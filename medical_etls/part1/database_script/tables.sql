CREATE TABLE `myDB`.`vocabularies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ref` char(20) NOT NULL,
  `name` char(255) NOT NULL,
  `url` char(255) NOT NULL,
  `version` char(100) NOT NULL,
  `description` varchar(500) NOT NULL,
  `status` char(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
