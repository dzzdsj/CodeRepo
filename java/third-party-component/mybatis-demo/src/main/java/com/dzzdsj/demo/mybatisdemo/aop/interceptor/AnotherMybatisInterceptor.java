package com.dzzdsj.demo.mybatisdemo.aop.interceptor;

import com.alibaba.druid.sql.ast.statement.*;
import com.alibaba.druid.sql.dialect.postgresql.ast.stmt.PGSelectQueryBlock;
import com.alibaba.druid.sql.dialect.postgresql.parser.PGSQLStatementParser;
import com.alibaba.druid.sql.dialect.postgresql.visitor.PGOutputVisitor;
import org.apache.ibatis.binding.MapperMethod;
import org.apache.ibatis.javassist.bytecode.analysis.Executor;
import org.apache.ibatis.mapping.BoundSql;
import org.apache.ibatis.mapping.MappedStatement;
import org.apache.ibatis.mapping.ParameterMapping;
import org.apache.ibatis.mapping.SqlSource;
import org.apache.ibatis.plugin.*;
import org.apache.ibatis.session.ResultHandler;
import org.apache.ibatis.session.RowBounds;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Objects;
import java.util.Properties;

/*
Mybatis 允许在以映射SQL语句执行过程中的某一点进行拦截调用。默认情况下，Mybatis允许使用插件来拦截的接口和方法有以下几个

Executor(update、query、flushStatements、commit、rollback、getTransaction、clos、isClosed)
ParameterHandler(getParameterObject、setParameters)
ResultSetHandler(handlerResultSets、handleCursorResultSets、handleOutPutParameters)
StatementHandler(prepare、parameterize、batch、update、query)
 */
//@Component
@Intercepts(@Signature(type = Executor.class, method = "query",
        args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class}))
public class AnotherMybatisInterceptor implements Interceptor {

    static int MAPPED_STATEMENT_INDEX = 0;// 这是对应上面的args的序号

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        // 获取拦截方法的参数
        Object[] args = invocation.getArgs();
        MappedStatement mappedStatement = (MappedStatement) args[0];
        // 拦截方法参数
        MapperMethod.ParamMap method = (MapperMethod.ParamMap)args[1];

        Integer customerId = (Integer)method.get(("customerId"));
        if (!filterObject(customerId)) {
            //只处理拦截SQL
            return invocation.proceed();
        }
        // 通过StatementHandler 获取执行SQL
        BoundSql boundSql = mappedStatement.getBoundSql(args[1]);
        String sql = boundSql.getSql();
//        System.out.println("获取到的SQL: " + sql);
        String newSql = updateSql(sql);
        BoundSql newBoundSql = new BoundSql(mappedStatement.getConfiguration(), newSql,
                boundSql.getParameterMappings(), boundSql.getParameterObject());
        // 把新的查询放到statement里
        MappedStatement newMs = copyFromMappedStatement(mappedStatement, new BoundSqlSqlSource(newBoundSql));
        for (ParameterMapping mapping : boundSql.getParameterMappings()) {
            String prop = mapping.getProperty();
            if (boundSql.hasAdditionalParameter(prop)) {
                newBoundSql.setAdditionalParameter(prop, boundSql.getAdditionalParameter(prop));
            }
        }
        final Object[] queryArgs = invocation.getArgs();
        queryArgs[MAPPED_STATEMENT_INDEX] = newMs;
        return invocation.proceed();
    }


    private MappedStatement copyFromMappedStatement(MappedStatement ms, SqlSource newSqlSource) {
        MappedStatement.Builder builder = new MappedStatement.Builder(ms.getConfiguration(), ms.getId(), newSqlSource, ms.getSqlCommandType());
        builder.resource(ms.getResource());
        builder.fetchSize(ms.getFetchSize());
        builder.statementType(ms.getStatementType());
        builder.keyGenerator(ms.getKeyGenerator());
        if (ms.getKeyProperties() != null && ms.getKeyProperties().length > 0) {
            builder.keyProperty(ms.getKeyProperties()[0]);
        }
        builder.timeout(ms.getTimeout());
        builder.parameterMap(ms.getParameterMap());
        builder.resultMaps(ms.getResultMaps());
        builder.resultSetType(ms.getResultSetType());
        builder.cache(ms.getCache());
        builder.flushCacheRequired(ms.isFlushCacheRequired());
        builder.useCache(ms.isUseCache());
        return builder.build();
    }

    public static class BoundSqlSqlSource implements SqlSource {

        private final BoundSql boundSql;

        public BoundSqlSqlSource(BoundSql boundSql) {
            this.boundSql = boundSql;
        }
        public BoundSql getBoundSql(Object parameterObject) {
            return boundSql;
        }
    }


    /**
     * SQL改写
     * @param sql
     * @return java.lang.String
     * @author wh
     * @date 2021/1/21
     */
    private String updateSql(String sql) {

//        String convertedSql = sql.replaceAll("t_order", "order_detail final");
        StringBuilder newSql = new StringBuilder("select ");
        PGSQLStatementParser mySqlStatementParser = new PGSQLStatementParser(sql);
        SQLSelectStatement sqlSelectStatement = mySqlStatementParser.parseSelect();
        SQLSelect sqlSelect = sqlSelectStatement.getSelect();
        SQLSelectQuery sqlSelectQuery = sqlSelect.getQuery();
        if (sqlSelectQuery instanceof PGSelectQueryBlock) {
            PGSelectQueryBlock pgSelectQueryBlock = (PGSelectQueryBlock) sqlSelectQuery;
            List<SQLSelectItem> coulums = pgSelectQueryBlock.getSelectList();
            for (int i = 0; i < coulums.size(); i++) {
                if (i == coulums.size() - 1) {
                    newSql.append(coulums.get(i));
                } else {
                    newSql.append(coulums.get(i)).append(",");
                }
            }
            new PGOutputVisitor(new StringBuilder());
            PGOutputVisitor tableName = new PGOutputVisitor(new StringBuilder());
            pgSelectQueryBlock.getFrom().accept(tableName);
//            System.out.println(tableName.getAppender());
            newSql.append(" from ").append(tableName.getAppender()).append(" final");
            PGOutputVisitor where = new PGOutputVisitor(new StringBuilder());
            // 获取where 条件
            pgSelectQueryBlock.getWhere().accept(where);
            newSql.append(" where ").append(where.getAppender());
            PGOutputVisitor groupBy = new PGOutputVisitor(new StringBuilder());
            SQLSelectGroupByClause sqlGroup = pgSelectQueryBlock.getGroupBy();
            if (Objects.nonNull(sqlGroup)) {
                sqlGroup.accept(groupBy);
                newSql.append(" ").append(groupBy.getAppender());
            }
        }
        return newSql.toString();
    }


    /**
     * 要拦截的对象
     * @param target
     * @return java.lang.Object
     * @author wh
     * @date 2021/1/21
     */
    @Override
    public Object plugin(Object target) {
        return Plugin.wrap(target, this);
    }

    /**
     * 插件属性传递
     * @param properties
     * @return void
     * @author wh
     * @date 2021/1/21
     */
    @Override
    public void setProperties(Properties properties) {

    }

    /**
     * 默认拦截所有SQL
     * @param
     * @return boolean
     * @author wh
     * @date 2021/1/21
     */
    public boolean filterObject(Integer customerId) {
        return true;
    }

}

