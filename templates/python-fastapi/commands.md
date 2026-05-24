# Python FastAPI 命令示例

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
python -m pytest tests/test_target.py
python -m pytest -k keyword
python -m compileall app
uvicorn app.main:app --reload
```

## Local validation / 局部验证优先级

```powershell
python -m pytest tests/test_target.py
python -m pytest -k keyword
python -m compileall app
python -m py_compile app\main.py
```

注意：

- 创建虚拟环境、安装依赖先确认。
- `uvicorn --reload` 是长期运行服务，先确认。
- 优先跑相关 pytest；没有测试时至少运行 compileall 或 py_compile。
