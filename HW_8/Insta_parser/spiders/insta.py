def parse_user_info(self, response: HtmlResponse, username, user_id, variables,
                cb_kwargs={
                    'username': username,
                    'user_id': user_id,
                    'variables': deepcopy(variables)
                    'variables': variables
                }
            )

def parse_user_data(self, response: HtmlResponse, username):
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables': deepcopy(variables),
                'variables': variables,
                'followed_by': True
            }
        )
def parse_user_data(self, response: HtmlResponse, username):
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables': deepcopy(variables),
                'variables': variables,
                'followed_by': False
            }
        )