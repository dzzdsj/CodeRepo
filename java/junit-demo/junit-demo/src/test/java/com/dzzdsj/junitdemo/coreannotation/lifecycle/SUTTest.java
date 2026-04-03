package com.dzzdsj.junitdemo.coreannotation.lifecycle;

import com.dzzdsj.junitdemo.ResourceForAllTests;
import com.dzzdsj.junitdemo.SUT;
import org.junit.jupiter.api.*;

import static org.junit.jupiter.api.Assertions.assertTrue;
/**
 * mvn -Dtest=SUTTest.java clean install
 * */
public class SUTTest {
    private static ResourceForAllTests resourceForAllTests;
    private SUT systemUnderTest;

    @BeforeAll
    static void setUpClass() {
        resourceForAllTests = new ResourceForAllTests("Our resource for all tests");
    }

    @AfterAll
    static void tearDownClass() {
        resourceForAllTests.close();
    }

    @BeforeEach
    void setUp() {
        systemUnderTest = new SUT("Our system under test");
    }

    @AfterEach
    void tearDown() {
        systemUnderTest.close();
    }
    @Test
    void testRegularWord() {
        System.out.println("Testing regular work");
        boolean canReceiveRegularWork =
                systemUnderTest.canReceiveRegularWork();
        assertTrue(canReceiveRegularWork);
    }
    @Test
    void testAdditionalWord() {
        System.out.println("Testing additional work");
        boolean canReceiveAdditionalWork =
                systemUnderTest.canReceiveAdditionalWork();
        assertTrue(canReceiveAdditionalWork);
    }
}
