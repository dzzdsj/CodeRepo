package com.dzzdsj.demo.mvn;

import org.apache.maven.plugin.AbstractMojo;
import org.apache.maven.plugin.MojoExecutionException;
import org.apache.maven.plugin.MojoFailureException;
import org.apache.maven.plugins.annotations.Mojo;
import org.apache.maven.plugins.annotations.Parameter;

@Mojo(name = "hello")//goal name
public class HelloPlugin extends AbstractMojo {
    @Parameter(property = "pluginName",defaultValue = "defaultPluginName")
    private String pluginName;
    @Override
    public void execute() throws MojoExecutionException, MojoFailureException {
        getLog().info("========This is HelloPlugin");
        getLog().info("========pluginName is:" + pluginName);
    }
}
