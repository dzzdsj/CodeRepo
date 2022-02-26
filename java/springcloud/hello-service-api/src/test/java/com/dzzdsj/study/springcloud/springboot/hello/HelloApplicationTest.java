//package com.dzzdsj.study.springcloud.springboot.hello;
//
//import org.hamcrest.Matchers;
//import org.junit.Before;
//import org.junit.Test;
//import org.junit.runner.RunWith;
//import org.springframework.boot.test.SpringApplicationConfiguration;
//import org.springframework.http.MediaType;
//import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
//import org.springframework.test.context.web.WebAppConfiguration;
//import org.springframework.test.web.servlet.MockMvc;
//import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
//import org.springframework.test.web.servlet.result.MockMvcResultMatchers;
//import org.springframework.test.web.servlet.setup.MockMvcBuilders;
//
//@RunWith(SpringJUnit4ClassRunner.class)
//@SpringApplicationConfiguration(classes = HelloApplication.class)
//@WebAppConfiguration
//public class HelloApplicationTest {
//    private MockMvc mockMvc;
//
//    @Before
//    public void setUp() throws Exception{
//        mockMvc = MockMvcBuilders.standaloneSetup(new HelloController()).build();
//    }
//    @Test
//    public void hello() throws Exception{
//        mockMvc.perform(MockMvcRequestBuilders.get("/hello").accept(MediaType.APPLICATION_JSON))
//                .andExpect(MockMvcResultMatchers.status().isOk())
//                .andExpect(MockMvcResultMatchers.content().string(Matchers.equalTo("hello")));
//    }
//}
