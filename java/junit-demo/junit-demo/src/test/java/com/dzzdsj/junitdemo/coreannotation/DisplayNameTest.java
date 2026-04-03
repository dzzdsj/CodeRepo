package com.dzzdsj.junitdemo.coreannotation;

import com.dzzdsj.junitdemo.SUT;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
@DisplayName("test @DisplayName annotation")
public class DisplayNameTest {
    private SUT systemUnderTest = new SUT();

    @Test
    @DisplayName("test hello")
    void testHello() {
        assertEquals("Hello", systemUnderTest.hello());
    }
}
