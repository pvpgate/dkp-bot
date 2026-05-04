from .menu import router as menu_router
from .clan.create_clan import router as create_clan_router
from .clan.show_clans import router as my_clans_router
from .help import router as help_router
from .clan.delete_clan import router as delete_clan_router
from .clan.join_clan import router as join_clan_router
from .clan.leave_clan import router as leave_clan_router
from .clan.manage_requests import router as manage_requests_router
from .clan.dismiss_member import router as dismiss_member_router
from .clan.set_role import router as set_role_router
from .clan.clan_members import router as clan_members_router
from .clan.change_dkp import router as change_dkp_router
routers = [
    menu_router,
    create_clan_router,
    my_clans_router,
    help_router,
    delete_clan_router,
    join_clan_router,
    leave_clan_router,
    manage_requests_router,
    dismiss_member_router,
    set_role_router,
    clan_members_router,
    change_dkp_router
]