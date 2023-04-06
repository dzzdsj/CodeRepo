package com.dzzdsj.code.databasedemo.mapper.dzzdsj;

import com.dzzdsj.code.databasedemo.entity.dzzdsj.Test;
import com.dzzdsj.code.databasedemo.entity.dzzdsj.TestExample;
import java.math.BigDecimal;
import java.util.List;
import org.apache.ibatis.annotations.Param;

public interface TestMapper {
    long countByExample(TestExample example);

    int deleteByExample(TestExample example);

    int deleteByPrimaryKey(BigDecimal id);

    int insert(Test row);

    int insertSelective(Test row);

    List<Test> selectByExample(TestExample example);

    Test selectByPrimaryKey(BigDecimal id);

    int updateByExampleSelective(@Param("row") Test row, @Param("example") TestExample example);

    int updateByExample(@Param("row") Test row, @Param("example") TestExample example);

    int updateByPrimaryKeySelective(Test row);

    int updateByPrimaryKey(Test row);
}