package com.puj.admincenter.repository.users

import com.puj.admincenter.domain.users.User

import org.springframework.stereotype.Repository
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.JpaSpecificationExecutor
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import java.util.*

import org.springframework.transaction.annotation.Transactional
import org.springframework.data.jpa.repository.Modifying

@Repository
interface UserRepository : JpaRepository<User, Int>,
                           JpaSpecificationExecutor<User> {

    @Query("""
        SELECT user
        FROM User user
        WHERE user.username = :username
        AND user.password = :password
    """)
    fun findUserByUserAndPassword(username: String,
                                  password: String): User?

    @Query("""
        SELECT COUNT(user) > 0
        FROM User user
        WHERE user.email = :email
    """)
    fun existsByEmail(@Param("email") email: String): Boolean

    @Transactional
    @Modifying
    @Query("""
        DELETE
        FROM User user
        WHERE user.id = :id
    """)
    fun deleteUserById(@Param("id") id: Int): Int
}