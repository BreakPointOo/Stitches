# Stitches(缝合怪)————Blender建模工具包

## 更新信息



2020.9.6	0.3.0	修复大量bug 重新梳理文件结构

2020.10.24	0.5.12	修复已知bug 第一个稳定版本



## **使用说明**



缝合怪分为三大模块

Object Mode下的Mesh模块

![image-20201025001234268](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001234268.png)

Edit Mode下的Edit模块（点线面模式下面板略有改动）

![image-20201025001308300](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001308300.png)

还有UV Editor下的UV模块

![image-20201025001401324](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001401324.png)

### 功能详解

#### 导入导出FBX

![image-20201025001459074](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001459074.png)

导出时使用导出选择物体并删除动画节点的设置

#### 特殊材质

![image-20201025001512780](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001512780.png)

背面黑色材质可以在Shading视图下将模型背面改为黑色 同时提高高光效果 便于观察模型平滑情况和反转面

#### 镜像

![image-20201025001528327](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001528327.png)

沿轴方向镜像



#### 批量重命名

![image-20201025001545818](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001545818.png)

![image-20201025001600828](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001600828.png)

批量重命名选择物体 具有批量前缀后缀替换等常用功能

#### 添加物体

![image-20201025001615287](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001615287.png)

点击创建常用mesh、曲线或添加修改器

#### 编辑

![image-20201025001633704](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001633704.png)

SmartDel:点击按钮删除所选物体

UVIslandToHardEdges:UV壳边界自动划分硬边

CenterPivot:居中轴

EditPivot:编辑轴的位置

PivotToBoundingBOX:在物体中心建立包裹物体的3 * 3 * 3的包裹框 点击其中一个点后将轴移动至该点的位置

UnblockNormal:解锁法线

FreezeTransformations:冻结变换

ShadeSmooth:平滑所选物体 在该命令执行后可以按角度自动分光滑组

#### 点法线工具

![image-20201025001652194](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001652194.png)

点或面模式下激活该工具 Get:获取所选点/面法线信息 	Set:将编辑框中的坐标信息输出至所选点/面 Reset:重置法线恢复至默认

#### 删除工具

![image-20201025001714764](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001714764.png)

![image-20201025001726112](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001726112.png)

![image-20201025001741873](https://raw.githubusercontent.com/BreakPointOo/FigureBed/main/img/image-20201025001741873.png)

根据点/线/面模式自动切换	删除点/线/面	溶解点/线/面

## License

Just use it as you like.