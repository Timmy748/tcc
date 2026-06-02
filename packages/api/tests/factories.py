import factory

from api.models.ai_agent import AiAgent
from api.models.chat_session import ChatSession
from api.models.message import Message
from api.models.permission import Permission
from api.models.project import Project
from api.models.role import Role
from api.models.user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


class RoleFactory(factory.Factory):
    class Meta:
        model = Role

    name = factory.Sequence(lambda n: f'ROLE_{n}')


class PermissionFactory(factory.Factory):
    class Meta:
        model = Permission

    name = factory.Sequence(lambda n: f'permission_{n}')


class ProjectFactory(factory.Factory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f'Project Artificial Intelligence {n}')
    created_by = 1


class AiAgentFactory(factory.Factory):
    class Meta:
        model = AiAgent

    name = factory.Sequence(lambda n: f'Agent_Branding_{n}')
    profile_pic = factory.Sequence(
        lambda n: f'https://avatar.com/agent_{n}.png'
    )
    description = 'Agente especialista em semiótica e identidades visuais.'
    system_prompt = 'Você é um Agente de design.'


class ChatSessionFactory(factory.Factory):
    class Meta:
        model = ChatSession

    title = factory.Sequence(lambda n: f'Sessão de Brainstorming #{n}')
    started_by = 1
    project_id = 1


class MessageFactory(factory.Factory):
    class Meta:
        model = Message

    content = 'Olá!'
    sender_type = Message.SenderType.AI
    chat_session_id = 1
    sender_user_id = None
    sender_ai_id = 1
