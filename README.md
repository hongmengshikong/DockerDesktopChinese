# DockerDesktopChinese

Docker汉化版 DockerDesktop汉化版 Docker Windows汉化版 Docker中文版

## 更新
由于个人精力问题，无法继续开发该仓库
如果需要DockerDesktop汉化版请转到

Docker Desktop汉化包

https://github.com/asxez/DockerDesktop-CN.git

Docker汉化脚本

https://github.com/asxez/DDCS.git

##### 介绍



> 本项目由本人自行汉化, 且只翻译了一部分, ~~后续会不断修补~~
>
> 该汉化版本是Docker Desktop 4.28.0 (139021) 版本差太多的话可能出现白屏情况请先做好备份

![image-20240408165111592.png](https://github.com/hongmengshikong/DockerDesktopChinese/blob/main/Pictuer/image-20240408165111592.png?raw=true)

![image-20240408165150965.png](https://github.com/hongmengshikong/DockerDesktopChinese/blob/main/Pictuer/image-20240408165150965.png?raw=true)

![image-20240408165204476.png](https://github.com/hongmengshikong/DockerDesktopChinese/blob/main/Pictuer/image-20240408165204476.png?raw=true)



##### 汉化方法

1. Docker安装目录(一般是`C:\Program Files\Docker\Docker\frontend\resources`)中找到app.asar并备份
2. 将本仓库提供的app.asar替换上述文件

### 工具准备

在实际开发中，有这样子的需求，就是需要解压asar结尾的文件。这里会涉及到两个基础环境的安装，node.js和npm有对应的配置。

app.asar文件是Electron加密打包时的中间产物，electron.exe调用resources文件夹下的app.asar从而实现不用解压缩而直接读取文件内容的高效。

在网上的一些教程中，对asar文件的解压和打包主要是执行以下命令：

```
1、安装asar 
npm install -g asar
2、cmd窗口中解压文件
asar extract app.asar ./app
3、没有表示成功
在文件夹系统中可以查看
```

2 报错提示
执行安装命令中，实际会报错以下消息：

```
npm WARN deprecated asar@3.2.0: Please use @electron/asar moving forward. There is no API change, just a package name change
```


原因是在新版本的框架中，已经有包含了asar的支持，不需要在额外下载对应的模块，只需要更更换执行的命令即可。

根据警告消息所示，官方建议改用 @electron/asar。这是一个针对 Electron 应用程序中的数据和文件管理的模块，它支持读取和打包应用内的文件，可以在命令行中使用。 您可以按照下面的步骤来更新 asar 版本：

```
1. 卸载旧版 asar： npm uninstall asar
2. 安装新版 @electron/asar： npm install -g @electron/asar
3. 使用 @electron/asar 打包应用程序： npx asar pack <app_directory> <output_file>
4. 读取 asar 文件： npx asar extract <input_file> <output_directory>
```

3 执行成功
按照上一步的操作，更换了执行命令以后，就能正常把文件解压。

所以，在执行软件的使用中，有时候需要注意版本更换以后带来的问题，及时调整对应的执行和使用命令。

### 如何汉化？

因为我们没有客户端软件的源码，所以我们就需要将被汉化的客户端进行一次反编译，因为我们只是汉化所以不涉及到功能的使用，也不需要将被压缩的代码进行还原，只要找到需要替换的关键字进行替换就可以，替换完后再进行二次打包就完成了整体的工作，将我们二次打包的内容替换到原客户端对应的文件（注意备份）即可。

### 如何解包？

那我们需要解开哪个包呢？总不能一个一个去试吧？网上可以搜索到的汉化包的使用流程，需要我们替换名为app.asar的文件。那好吧，我们就把这个文件解开来看看

- **第一步：**找到app.asar的目录；
- **第二步：**我们需要使用到`asar`的一个`Node`包，我们这里就不用再进行安装了使用npx执行运行即可；
  - 解包命令：`npx asar extract ./app.asar ./output`

下图是我们解压后得到的目录：

![image-20240408165610007.png](https://github.com/hongmengshikong/DockerDesktopChinese/blob/main/Pictuer/image-20240408165610007.png?raw=true)

### 关键字替换：

**第一步：**我们还是通过使用文字识别工具来帮助我们提取页面的关键字

**第二步：**这一步的操作就简单很多了，我们只需要将关键字进行替换就可以了，那就使用我们的必备技能（CV大法）吧，因为毕竟没有源码通过脚本还是不太方便。

### 如何二次打包？

通过执行`asar`的命令来进行打包：`npx asar pack ./output ./app1.asar`，将打包后的内容替换原文件即可



