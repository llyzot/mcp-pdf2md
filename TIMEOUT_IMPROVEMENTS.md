# 超时断开连接问题修复

## 问题分析

原始代码存在以下超时和连接稳定性问题：

1. **HTTP客户端超时设置不一致**：不同请求使用了不同的硬编码超时值
2. **任务状态检查缺乏灵活性**：固定的重试次数和间隔，无法适应不同规模的文件
3. **异常处理不完善**：简单的异常捕获，没有区分不同类型的错误
4. **缺乏进度通知**：长时间任务可能导致客户端因无响应而断开连接
5. **没有连续错误检测**：可能在持续失败的情况下无限重试

## 解决方案

### 1. 统一的超时配置系统

添加了可通过环境变量配置的超时参数：

- `HTTP_CLIENT_TIMEOUT`: HTTP客户端总超时（默认10分钟）
- `API_REQUEST_TIMEOUT`: API请求超时（默认5分钟）
- `DOWNLOAD_TIMEOUT`: 文件下载超时（默认10分钟）
- `STATUS_CHECK_TIMEOUT`: 状态检查超时（默认1分钟）
- `TASK_MAX_RETRIES`: 任务轮询最大重试次数（默认120次）
- `TASK_RETRY_INTERVAL`: 重试间隔（默认5秒）

### 2. 改进的错误处理

- 区分不同类型的异常（超时、网络错误、其他错误）
- 连续错误检测，防止无限重试
- 详细的错误信息，便于调试

### 3. 进度通知机制

- 添加了进度回调函数，在长时间任务中定期发送进度
- 防止MCP客户端因长时间无响应而断开连接
- 可扩展为实际的进度通知

### 4. 智能重试逻辑

- 指数退避算法用于下载失败重试
- 连续错误计数器，避免无限循环
- 可配置的重试参数

## 配置示例

### 大文件处理配置
```bash
HTTP_CLIENT_TIMEOUT=1800  # 30分钟
DOWNLOAD_TIMEOUT=1800     # 30分钟
TASK_MAX_RETRIES=360      # 30分钟轮询
```

### 快速网络配置
```bash
HTTP_CLIENT_TIMEOUT=300   # 5分钟
API_REQUEST_TIMEOUT=120   # 2分钟
TASK_MAX_RETRIES=60       # 5分钟轮询
```

## 技术改进细节

### 1. 超时配置统一化
```python
# 之前：硬编码超时
async with httpx.AsyncClient(timeout=300.0) as client:
    response = await client.post(url, timeout=60.0)

# 现在：可配置超时
async with httpx.AsyncClient(timeout=HTTP_CLIENT_TIMEOUT) as client:
    response = await client.post(url, timeout=API_REQUEST_TIMEOUT)
```

### 2. 错误处理改进
```python
# 之前：简单异常捕获
except Exception as e:
    retry_count += 1
    continue

# 现在：分类错误处理
except httpx.TimeoutException:
    consecutive_errors += 1
    # 特定处理逻辑
except httpx.RequestError as e:
    consecutive_errors += 1
    # 网络错误处理
```

### 3. 进度通知
```python
async def progress_notification_callback(current_attempt, max_attempts, batch_id):
    progress_percent = min(100, int((current_attempt / max_attempts) * 100))
    logger.debug(f"Task progress: {progress_percent}%")
```

## 测试验证

创建了完整的测试套件 `test_timeout_config.py` 来验证：

- ✅ 超时配置正确加载
- ✅ 进度回调正常工作
- ✅ HTTP客户端超时生效
- ✅ 连续错误检测机制

## 使用建议

1. **根据文件大小调整配置**：大文件需要更长的超时时间
2. **根据网络条件优化**：慢速网络需要更多的重试次数
3. **监控日志输出**：注意连续错误和超时警告
4. **定期更新配置**：根据实际使用情况调整参数

## 预期效果

- **减少连接断开**：通过进度通知保持连接活跃
- **提高成功率**：智能重试和错误处理
- **更好的用户体验**：详细的错误信息和可配置的参数
- **系统稳定性**：防止无限循环和资源泄漏

这些改进应该能够显著减少超时导致的连接断开问题，提高整体系统的稳定性和可靠性。