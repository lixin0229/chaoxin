# 学习通实习打卡脚本

一个支持多用户的学习通（超星）实习自动打卡脚本。
部分学校可能失效

## 项目信息

- 作者：十号 (https://shihao520.top)
- 参考项目：[WAADRI/ChaoXingshixidaka](https://github.com/WAADRI/ChaoXingshixidaka)

## 功能特点

- ✅ 支持多用户配置
- ✅ 自动定时打卡
- ✅ 支持自定义打卡地点和时间
- ✅ 支持手动/自动打卡模式
- ✅ 完整的日志记录
- ✅ 用户状态管理（启用/禁用）
- ✅ 支持图片上传

## 使用说明

### 1. 环境要求

- Python 3.12
- Windows 系统

### 2. 快速开始

1. 双击运行 `start.bat`，脚本会自动：
   - 检查 Python 环境
   - 创建虚拟环境
   - 安装必要的依赖包
   - 启动主程序

### 3. 功能菜单

程序提供以下功能：

- `0.手动打卡`: 选择用户进行手动打卡
- `1.上传打卡图片`: 上传打卡需要的图片
- `2.启动自动打卡`: 为所有启用的用户开启自动打卡
- `3.用户管理`: 管理用户配置
- `4.退出`: 退出程序

### 4. 用户管理

在用户管理菜单中可以：

1. 添加用户
2. 修改用户信息
3. 删除用户
4. 启用/禁用用户

### 5. 配置说明

用户配置存储在 `users.json` 文件中，包含以下字段：

```json
{
    "username": "手机号/学号",
    "password": "密码",
    "schoolid": "学校ID（可选）",
    "address": "打卡地址",
    "location": "经纬度坐标",
    "clock_in_time": "打卡时间（HH:MM格式）",
    "remark": "备注",
    "enabled": true,
    "clockin_version": "old2"
}
```

#### 配置字段说明：
- `username`: 学习通账号（手机号或学号）
- `password`: 账号密码
- `schoolid`: 学校ID，使用手机号登录时可为空
- `address`: 打卡地址文字描述
- `location`: 打卡位置的经纬度坐标
- `clock_in_time`: 自动打卡时间，24小时制（如："09:00"）
- `remark`: 用户备注信息
- `enabled`: 是否启用自动打卡（true/false）
- `clockin_version`: 打卡版本选择，可选值：
  - `"new"`: 使用新版打卡接口
  - `"old1"`: 使用旧版打卡接口1
  - `"old2"`: 使用旧版打卡接口2（默认推荐）

### 6. 获取经纬度坐标

1. 访问 [百度地图坐标拾取系统](http://api.map.baidu.com/lbsapi/getpoint/index.html)
2. 搜索或定位到需要打卡的位置
3. 点击获取坐标
4. 复制经纬度信息到配置文件

## 注意事项

1. 首次使用需要配置用户信息
2. 打卡时间格式必须是 "HH:MM"（如 "09:00"）
3. 程序运行时会生成 `clockin.log` 日志文件
4. 确保电脑不会进入睡眠状态，以免影响自动打卡
5. 使用自动打卡功能时，可以按 Ctrl+C 终止

## 常见问题

1. **Q: 如何修改打卡时间？**  
   A: 在用户管理中选择修改用户信息，输入新的打卡时间。

2. **Q: 如何确认打卡是否成功？**  
   A: 查看 `clockin.log` 日志文件，会记录所有打卡操作和结果。

3. **Q: 如何暂停某个用户的自动打卡？**  
   A: 在用户管理中选择启用/禁用用户功能。

4. **Q: 如何选择合适的打卡版本？**  
   A: 默认使用 "old2" 版本，如果打卡失败可以尝试切换到其他版本。不同学校可能支持的版本不同。

5. **Q: 打卡版本有什么区别？**  
   A: 
   - new: 新版打卡接口，支持部分新系统
   - old1: 旧版打卡接口1，支持大部分学校
   - old2: 旧版打卡接口2，默认推荐，兼容性最好

6. **Q: 如何修改打卡版本？**  
   A: 在用户管理中修改用户信息，或直接编辑 users.json 文件的 clockin_version 字段。

## 免责声明

本脚本仅供学习交流使用，使用本脚本所产生的任何后果由使用者自行承担。

## 更新日志

### v1.0.0 (2024-01-04)
- 支持多用户配置
- 添加自动打卡功能
- 添加用户管理系统
- 添加日志记录功能
- 支持多版本打卡接口选择

## 致谢

本项目基于 [WAADRI/ChaoXingshixidaka](https://github.com/WAADRI/ChaoXingshixidaka) 项目进行了重构和功能扩展，
增加了多用户支持、自动打卡、日志记录等功能。感谢原作者的开源贡献。

## 许可证

本项目仅供学习交流使用，请勿用于商业用途。

