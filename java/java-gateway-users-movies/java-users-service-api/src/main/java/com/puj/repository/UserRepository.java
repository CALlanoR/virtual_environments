package com.puj.repository;

import org.springframework.data.repository.CrudRepository;

import com.puj.domain.User;


public interface UserRepository extends CrudRepository<User, Integer> {
    public User findByUsernameAndPassword(String username, String password);
}
