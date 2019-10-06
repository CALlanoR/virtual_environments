package com.puj.cotroller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

import com.puj.domain.Token;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.AuthorityUtils;

import com.puj.service.UserService;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

@Controller
@RequestMapping(path="/login")
public class LoginController {

	@Autowired
	private UserService userService;

    Logger logger = LogManager.getLogger(LoginController.class);

    @PostMapping
    public @ResponseBody Token login(@RequestParam("username") String username,
                                     @RequestParam("password") String password) {
        Token token = new Token();
        // Validate username and password with the UserService
        //logger.info("username: " + username + " password: " + password);
        if(userService.existsUsernameAndPassword(username, password)){
            String jwtToken = getJWTToken(username);
		    token.setToken(jwtToken);
        } else {
            token.setToken("");
        }
        return token;
	}

	private String getJWTToken(String username) {
		String secretKey = "mySecretKey";
		List<GrantedAuthority> grantedAuthorities = AuthorityUtils
				.commaSeparatedStringToAuthorityList("ROLE_USER");
        
        Claims claims = Jwts.claims()
                .setSubject(username);
        claims.put("identity", username);

		String token = Jwts
				.builder()
				.setId("softtekJWT")
                .setClaims(claims)
				.claim("authorities",
						grantedAuthorities.stream()
								.map(GrantedAuthority::getAuthority)
								.collect(Collectors.toList()))
				.setIssuedAt(new Date(System.currentTimeMillis()))
				.setExpiration(new Date(System.currentTimeMillis() + 600000))
				.signWith(SignatureAlgorithm.HS512,
						  secretKey.getBytes()).compact();

		return "Bearer " + token;
	}
}
