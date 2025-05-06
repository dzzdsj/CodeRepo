package com.dzzdsj.demo.mybatisdemo.aop.interceptor;

import com.dzzdsj.demo.mybatisdemo.entity.Student;
import com.dzzdsj.demo.mybatisdemo.mapper.StudentMapper;
import jakarta.annotation.Resource;
import org.apache.ibatis.binding.MapperMethod;
import org.apache.ibatis.executor.parameter.ParameterHandler;
import org.apache.ibatis.executor.statement.StatementHandler;
import org.apache.ibatis.mapping.BoundSql;
import org.apache.ibatis.mapping.MappedStatement;
import org.apache.ibatis.plugin.*;
import org.apache.ibatis.reflection.DefaultReflectorFactory;
import org.apache.ibatis.reflection.MetaObject;
import org.apache.ibatis.reflection.SystemMetaObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;

import java.lang.reflect.Field;
import java.sql.Connection;
import java.util.Map;
import java.util.Properties;

//	标志该类是一个拦截器
//@Intercepts({
//        //指明该拦截器需要拦截哪一个接口的哪一个方法
//        @Signature(
//                type = Executor.class, //	四种类型接口中的某一个接口，如Executor.class。
//                method = "query", //对应接口中的某一个方法名，比如Executor的query方法。
//                //对应接口中的某一个方法的参数，比如Executor中query方法因为重载原因，有多个，args就是指明参数类型，从而确定是具体哪一个方法。
//                args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class, CacheKey.class, BoundSql.class}
//        )
//@Component
@Intercepts({@Signature(type = StatementHandler.class, method = "prepare", args = {Connection.class, Integer.class})})
public class MybatisInterceptor implements Interceptor {
//    @Autowired
//    private ApplicationContext applicationContext;

    /**
     * 进行拦截的时候要执行的方法
     * @param invocation
     * @return
     * @throws Throwable
     */
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        System.out.println("====intercept======");
        StatementHandler statementHandler = (StatementHandler) invocation.getTarget();
        //通过MetaObject优雅访问对象的属性，这里是访问statementHandler的属性;：MetaObject是Mybatis提供的一个用于方便、
        //优雅访问对象属性的对象，通过它可以简化代码、不需要try/catch各种reflect异常，同时它支持对JavaBean、Collection、Map三种类型对象的操作。
        MetaObject metaObject = MetaObject
                .forObject(statementHandler, SystemMetaObject.DEFAULT_OBJECT_FACTORY, SystemMetaObject.DEFAULT_OBJECT_WRAPPER_FACTORY,
                        new DefaultReflectorFactory());
        //先拦截到RoutingStatementHandler，里面有个StatementHandler类型的delegate变量，其实现类是BaseStatementHandler，然后就到BaseStatementHandler的成员变量mappedStatement
        MappedStatement mappedStatement = (MappedStatement) metaObject.getValue("delegate.mappedStatement");
        //id为执行的mapper方法的全路径名，如com.uv.dao.UserMapper.insertUser
        String id = mappedStatement.getId();
        //sql语句类型 select、delete、insert、update
        String sqlCommandType = mappedStatement.getSqlCommandType().toString();
        //数据库连接信息
//        Configuration configuration = mappedStatement.getConfiguration();
//        ComboPooledDataSource dataSource = (ComboPooledDataSource)configuration.getEnvironment().getDataSource();
//        dataSource.getJdbcUrl();

        //获取参数
        ParameterHandler parameterHandler = (ParameterHandler) metaObject.getValue("parameterHandler");
        // 获取参数对象
        Map parameters = (MapperMethod.ParamMap) parameterHandler.getParameterObject();
        if (parameters != null) {
            System.out.println("SQL Parameters: " + parameters);
        }

        BoundSql boundSql = statementHandler.getBoundSql();
        //获取到原始sql语句
        String sql = boundSql.getSql();
        String mSql = "select * from t_student where sid=?";
        //通过反射修改sql语句
        Field field = boundSql.getClass().getDeclaredField("sql");
        field.setAccessible(true);
        field.set(boundSql, mSql);

//        StudentMapper studentMapper = applicationContext.getBean(StudentMapper.class);
//        Student student = studentMapper.selectByPrimaryKey(1L);
//        System.out.println(student);
//        return student;
        //执行结果
        return invocation.proceed();
    }

    @Override
    public Object plugin(Object target) {
//        return Interceptor.super.plugin(target);
        System.out.println("-----------------------------plugin-------------------------");
        return Plugin.wrap(target, this);
    }

    @Override
    public void setProperties(Properties properties) {
        Interceptor.super.setProperties(properties);
        System.out.println("====setProperties======");
    }
}
