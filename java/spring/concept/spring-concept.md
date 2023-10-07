# spring 重要概念

。Spring是为了
解决企业级应用开发的复杂性而创建的，使用Spring可以让简单的
JavaBean实现之前只有EJB才能完成的事情。但Spring不仅仅局限于服
务器端开发，任何Java应用都能在简单性、可测试性和松耦合等方面
从Spring中获益。



为了降低Java开发的复杂性，Spring采取了以下4种关键策略：
基于POJO的轻量级和最小侵入性编程；
通过依赖注入和面向接口实现松耦合；
基于切面和惯例进行声明式编程；
通过切面和模板减少样板式代码。

就是DI所带来的最大收益
——松耦合。如果一个对象只通过接口（而不是具体实现或初始化过
程）来表明依赖关系，那么这种依赖就能够在对象本身毫不知情的情
况下，用不同的具体实现进行替换。

而面向切面编程
（aspect-oriented programming，AOP）允许你把遍布应用各处的功能
分离出来形成可重用的组件。诸如日志、事务管理和安全，这些系统服务通常被称为横切关注点，因为它
们会跨越系统的多个组件



容器是Spring框架的核心。Spring容器使用DI管理构成应用的组件，
它会创建相互协作的组件之间的关联



## spring包结构

aop

该模块包含在应用程序中使用Spring的 AOP功能时所需的所有类.如果打算在Spring中使用其他使用了AOP的功能，例如声明式事务管理，则需要在应用程序中包含此JAR文件。此外，支持与AspeactJ集成的类也封装在此模块中

aspects

该模块包含与AspectJ AOP库进行高级集成的所有类。例如,如果为完成Spring配置而使用Java类，并且需要Aspectl风格的注解驱动的事务管理，则需要使用此模块

beans

该模块包含所有支持Spring对 Spring bean进行操作的类。该模块中的大多数类都支持 Spring的 bean 工厂实现。例如,处理 Spring XML配置文件和 Java注解所需的类被封装到此模块中

beans-groovy

此模块包含用于支持 Spring对 Spring bean进行操作的Groovy类

context

该模块包含为Spring Core提供许多扩展的类。你会发现所有类都需要使用 Spring的 ApplicationContext 功能(将在第5章介绍)以及Enterprise JavaBeans(EJB)、Java Naming and Directory

context-indexer

该模块包含一个索引器实现，它提供对 META-INF/spring.components 中定义的候选项的访问功能。但核心类CandidateComponentsIndex并不能在外部使用

context-support

该模块包含对spring-context 模块的进一步扩展。在用户界面方面，有一些用于支持邮件并与模板引擎(例如Velocity、FreeMarker和 JasperReports)集成的类。此外，还包括与各种任务执行和调度库(包括CommonJ和 Quartz)的集成这是每个Spring应用程序都需要的主要模块。在该JAR文件中，可以找到所有其他Spring模块(例如，用于访问配置文件的类)所共享的所有类。另外，在该JAR文件中，会发现在整个Spring 代码库中都使用的非常有用的实用程序类，可以在自己的应用程序中使用它们

expression

该模块包含Spring Expression Language(SpEL)的所有支持类

instrument

该模块包含用于JVM启动的Spring 工具代理。如果在Spring应用程序中使用Aspectl'实现加载时织入，那么该模块是必需的

jdbc

该模块包含所有的 JDBC支持类。对于需要数据库访问的所有应用程序，都需要此模块。支持数据源、JDBC 数据类型、JDBC模板、本地JDBC连接等的类都被打包在此模块中

jms

该模块包含JMS支持的所有类

orm

该模块扩展了Spring的标准JDBC功能集,支持流行的ORM.工具，包括Hibernate.JDO、JPA和数据映射器iBATIS.该JAR文件中的许多类都依赖于spring-jdbc JAR文件中所包含的类，因此也需要把它包含在应用程序中

oxm

该模块扩展了Spring的标准JDBC功能集,支持流行的ORM.工具，包括Hibermnate.JDO.JPA和数据映射器iBATIS.该JAR文件中的许多类都依赖于spring-jdbc JAR文件中所包含的类，因此也需要把它包含在应用程序中

test

Spring 提供一-组模拟类来帮助测试应用程序，并且许多模拟类都在Spring 测试套件中使用，所以它们都经过了很好的测试;从而使测试应用程序变得更简单。在对Web应用程序进行单元测试时会发现模拟HttpServletRequest和HttpServletResponse类所带来的好处。另一方面，Spring 提供了与JUnit单元测试框架的紧密集成，并且在该模块中提供了许多支持JUnit测试用例开发的类;例如，SpringJUnit4ClassRunner-提供了一种在单元测试环境中引导SpringApplicationContext的简单方法

tx

该模块提供支持Spring事务基础架构的所有类。可以从事务抽象层找到相应的类来支持Java Transaction API(JTA)以及与主要供应商的应用程序服务器的集成

web

此模块包含在Web应用程序中使用Spring所需的核心类，包括用于自动加载ApplicationContext功能的类、文件上传支持类以及一些用于执行重复任务(比如从查询字符串中解析整数值)的有用类

web-reactive

该模块包含Spring Web Reactive模型的核心接口和类

web-mvc

该模块包含Spring自己的MVC框架的所有类。如果想要为应用程序使用单独的MVC框架，则不需要此JAR文件中的任何类。Spring MVC在第16章中有更详细的介绍

webfsocket

该模块提供对JSR-356(WebSocket的 Java API)的支持





## bean的装配

### 装配机制

Spring具有非常大的灵活性，它提供了三种主要的装配机制：

- 在XML中进行显式配置。
- 在Java中进行显式配置。
- 隐式的bean发现机制和自动装配。

#### 选用原则

自动化装配 >java代码装配 > xml装配

1. 尽可能地使用自动配置的机制。显式配置越少越好。

2. 当你必须要显式配置bean的时候（比如，有些源码不是由你来维护的，而当你需要为这些代码配置bean的时候），使用类型安全并且比XML更加强大的JavaConfig。

3. 最后，只有当你想要使用便利的XML命名空间，并且在JavaConfig中没有同样的实现时，才应该使用XML

#### **自动化装配**

Spring从两个角度来实现自动化装配：
**组件扫描**（component scanning）：Spring会自动发现应用上下文中所创建的bean。
**自动装配**（autowiring）：Spring自动满足bean之间的依赖。

##### 注解

```java
//@ComponentScan用于配置类,在Spring中启用组件扫描,默认会扫描与配置类相同的包。会扫描这个包以及这个包下的所有子包，查找带有@Component注解的类,在Spring中自动为其创建一个bean
@ComponentScan
xml   <context:component-scan>


//@Component注解。这个简单的注解表明该类会作为组件类，并告知Spring要为这个类创建bean
@Component

    /**
   *@Bean注解会告诉Spring这个方法将会返回一个对象，该对象要注册
   * 为Spring应用上下文中的bean。方法体中包含了最终产生bean实例的逻辑
   * Spring将会拦截所有对它的调用，并确保直接返回该方法所创建的
   * bean，而不是每次都对其进行实际的调用
   * 。默认情况下，Spring中的bean都是单例的
   */
//@Bean

```





#### java代码装配



#### xml装配









