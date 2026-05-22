# Python FastAPI 命令示例

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
python -m compileall app
uvicorn app.main:app --reload
```

注意：

- 创建虚拟环境、安装依赖先确认。
- `uvicorn --reload` 是长期运行服务，先确认。
