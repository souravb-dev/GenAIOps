from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG  # Enable SQL logging in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    """Create all database tables"""
    from app.models.user import Base as UserBase
    from app.models.remediation import Base as RemediationBase
    from app.models.chatbot import Base as ChatbotBase
    
    # Create all tables from all models
    UserBase.metadata.create_all(bind=engine)
    RemediationBase.metadata.create_all(bind=engine)
    ChatbotBase.metadata.create_all(bind=engine)

# Initialize default roles
def init_default_roles():
    """Initialize default roles in database"""
    from sqlalchemy.orm import Session
    from app.models.user import Role, RoleEnum
    
    db = SessionLocal()
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        if existing_roles > 0:
            return
        
        # Create default roles
        default_roles = [
            Role(
                name=RoleEnum.ADMIN,
                display_name="Administrator",
                description="Full access to all features and user management",
                can_view_dashboard=True,
                can_view_alerts=True,
                can_approve_remediation=True,
                can_execute_remediation=True,
                can_manage_users=True,
                can_manage_roles=True,
                can_view_access_analyzer=True,
                can_view_pod_analyzer=True,
                can_view_cost_analyzer=True,
                can_use_chatbot=True
            ),
            Role(
                name=RoleEnum.OPERATOR,
                display_name="Operator",
                description="Can view, analyze and approve/execute remediations",
                can_view_dashboard=True,
                can_view_alerts=True,
                can_approve_remediation=True,
                can_execute_remediation=True,
                can_manage_users=False,
                can_manage_roles=False,
                can_view_access_analyzer=True,
                can_view_pod_analyzer=True,
                can_view_cost_analyzer=True,
                can_use_chatbot=True
            ),
            Role(
                name=RoleEnum.VIEWER,
                display_name="Viewer",
                description="Read-only access to dashboards and analytics",
                can_view_dashboard=True,
                can_view_alerts=True,
                can_approve_remediation=False,
                can_execute_remediation=False,
                can_manage_users=False,
                can_manage_roles=False,
                can_view_access_analyzer=True,
                can_view_pod_analyzer=True,
                can_view_cost_analyzer=True,
                can_use_chatbot=True
            )
        ]
        
        for role in default_roles:
            db.add(role)
        
        db.commit()
        print("Default roles initialized successfully")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing roles: {e}")
    finally:
        db.close() 