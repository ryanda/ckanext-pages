import ckan.plugins as p

try:
    import ckan.authz as authz
except ImportError:
    import ckan.new_authz as authz

from ckanext.pages import db


def sysadmin(context, data_dict):
    return {'success':  False}

def anyone(context, data_dict):
    return {'success': True}

def only_moderator(context, data_dict=None):
    # Get the user name of the logged-in user.
    user_name = context['user']

    # Have logged-in user's user name, get their user id
    convert_user_name_or_id_to_id = p.toolkit.get_converter('convert_user_name_or_id_to_id')
    user_id = convert_user_name_or_id_to_id(user_name, context)

    # Check current user organization list with manage_group permission
    param = {
        'id': user_id,
        'permission': 'manage_group',
    }
    orgs = p.toolkit.get_action('organization_list_for_user')(data_dict=param)

    # Test whether the user is a admin of an organization
    if len(orgs) > 1:
        return {'success': True}
    else:
        return {
            'success': False,
            'msg': 'Only moderator are allowed'
        }

# Starting from 2.2 you need to explicitly flag auth functions that allow
# anonymous access
if p.toolkit.check_ckan_version(min_version='2.2'):
    anyone = p.toolkit.auth_allow_anonymous_access(anyone)


def group_admin(context, data_dict):
    return {
        'success': p.toolkit.check_access('group_update', context, data_dict)
    }


def org_admin(context, data_dict):
    return {
        'success': p.toolkit.check_access('group_update', context, data_dict)
    }


def page_group_admin(context, data_dict):
    group_id = data_dict.get('org_id')
    if not group_id:
        id = data_dict.get('id')
        page = data_dict.get('page') or db.Page.get(id=id)
        if page:
            group_id = page.group_id
    return group_admin(context, {'id': group_id})


def page_privacy(context, data_dict):
    if db.pages_table is None:
        db.init_db(context['model'])
    org_id = data_dict.get('org_id')
    page = data_dict.get('page')
    out = db.Page.get(group_id=org_id, name=page)
    if out and out.private == False:
        return {'success':  True}
    # no org_id means it's a universal page
    if not org_id:
        if out and out.private:
            return {'success': False}
        return {'success': True}
    group = context['model'].Group.get(org_id)
    user = context['user']
    authorized = authz.has_user_permission_for_group_or_org(group.id,
                                                                user,
                                                                'read')
    if not authorized:
        return {'success': False,
                'msg': p.toolkit._(
                    'User %s not authorized to read this page') % user}
    else:
        return {'success': True}


# Starting from 2.2 you need to explicitly flag auth functions that allow
# anonymous access
if p.toolkit.check_ckan_version(min_version='2.2'):
    anyone = p.toolkit.auth_allow_anonymous_access(anyone)
    page_privacy = p.toolkit.auth_allow_anonymous_access(page_privacy)


pages_show = anyone
pages_update = only_moderator
pages_delete = only_moderator
pages_list = anyone
pages_upload = only_moderator
org_pages_show = anyone
org_pages_update = only_moderator
org_pages_delete = only_moderator
org_pages_list = anyone
group_pages_show = anyone
group_pages_update = only_moderator
group_pages_delete = only_moderator
group_pages_list = anyone
