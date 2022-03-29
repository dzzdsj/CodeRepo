# springboot 重要概念

## 四大核心

1. 自动配置
2. 起步依赖
3. 命令行界面Spring Boot CLI
4. actuator

## 探究@SpringBootApplication

```java
/**
 * 开启组件扫描和自动配置
 * @SpringBootApplication 整合了下列几大注释=
 * @SpringBootConfiguration (@Configuration) 使用spring基于java的配置+
 * @EnableAutoConfiguration 开启自动配置+
 * @ComponentScan 开启组件扫描。--组件被自动发现并注册为spring上下文里的bean。
 */
```

## 查看maven依赖树

```shell
mvn dependency:tree
```

## Spring Framework的核心工作

Spring Framework的核心工作是将所有组件编织在一起，构成一个应用程序。整个过程就是
读取配置说明（可以是XML、基于Java的配置、基于Groovy的配置或其他类型的配置），在应用程序上下文里初始化Bean，将Bean注入依赖它们的其他Bean中。