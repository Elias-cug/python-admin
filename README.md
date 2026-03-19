## 目录结构

backend-admin/
│
├── app/ # 主应用目录
│
│ ├── main.py # 应用入口
│ ├── config.py # 配置文件
│
│ ├── api/ # API 层（路由）
│ │ ├── **init**.py
│ │ ├── deps.py # 依赖注入
│ │ │
│ │ └── v1/ # API 版本
│ │ ├── **init**.py
│ │ ├── api.py # 路由聚合
│ │ ├── auth.py # 登录接口
│ │ ├── user.py
│ │ └── role.py
│
│ ├── models/ # 数据库模型
│ │ ├── **init**.py
│ │ ├── user.py
│ │ ├── role.py
│ │ └── menu.py
│
│ ├── schemas/ # 数据验证(Pydantic)
│ │ ├── user.py
│ │ ├── auth.py
│ │ └── role.py
│
│ ├── crud/ # 数据库操作层
│ │ ├── base.py
│ │ ├── user.py
│ │ └── role.py
│
│ ├── services/ # 业务逻辑层
│ │ ├── auth_service.py
│ │ ├── user_service.py
│ │ └── role_service.py
│
│ ├── core/ # 核心组件
│ │ ├── security.py # JWT
│ │ ├── database.py # DB连接
│ │ ├── config.py
│ │ └── logger.py
│
│ ├── middleware/ # 中间件
│ │ ├── auth.py
│ │ └── request_log.py
│
│ ├── utils/ # 工具类
│ │ ├── jwt.py
│ │ ├── response.py
│ │ └── pagination.py
│
│ └── tasks/ # 异步任务
│ └── celery_worker.py
│
├── migrations/ # 数据库迁移
│
├── tests/ # 测试
│
├── scripts/ # 脚本
│
├── requirements.txt
├── .env
├── Dockerfile
└── README.md

## 架构分层

API层
↓
Service层
↓
CRUD层
↓
Model层
↓
Database
