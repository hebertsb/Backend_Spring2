import os
import sys
import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Permission

def inspect(token_key):
    try:
        t = Token.objects.get(key=token_key)
    except Token.DoesNotExist:
        print('Token not found')
        return
    u = t.user
    print('User id:', u.id)
    print('username:', u.username)
    print('email:', u.email)
    print('is_staff:', u.is_staff)
    print('is_superuser:', u.is_superuser)
    print('is_active:', u.is_active)
    print('\nExplicit user permissions:')
    for p in u.user_permissions.all():
        print(' -', p.content_type.app_label, p.codename)
    print('\nGroup permissions (via groups):')
    for g in u.groups.all():
        print('Group:', g.name)
        for p in g.permissions.all():
            print('  -', p.content_type.app_label, p.codename)
    print('\nhas auth.change_user?:', u.has_perm('auth.change_user'))

    # Try to inspect roles via UserRole relation if present
    try:
        from authz.models import UserRole
        roles = UserRole.objects.filter(user=u)
        print('\nUserRoles:')
        for r in roles:
            print(' -', r.rol.id, r.rol.slug, r.rol.nombre)
    except Exception:
        print('\nUserRole model not available')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: inspect_user_by_token.py <token>')
        sys.exit(2)
    inspect(sys.argv[1])