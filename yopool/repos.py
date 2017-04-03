"""
the repository of YOPO
"""
import datetime
from pymongo import MongoClient, DESCENDING, ASCENDING
from random import shuffle


class repos:
    def __init__(self):
        # ds063892.mlab.com:63892/yopodb -u yopo -p yopo666
        # mongodb://127.0.0.1/test
        #client = MongoClient("mongodb://yopo:yopo666@ds063892.mlab.com:63892/yopodb")
        client = MongoClient("mongodb://yopo:yopo666@ds063892.mlab.com:63892/yopodb")
        self.db = client.yopodb

    def save_account(self, m):
        username = m['name']
        om = self.find_account(username)
        if om is None:
            new_model = self.db.accounts.insert_one(m)
        else:
            new_model = self.db.accounts.replace_one({"name": username}, m)

        return new_model

    def find_account(self, name):
        new_model = self.db.accounts.find_one({"name": name})

        return new_model

    def delete_account(self, username):
        om = self.find_account(username)
        om['status'] = 'deleted'
        new_model = self.db.accounts.replace_one({"name": username}, om)

        return new_model

    def save_account_pics(self, m):
        username = m['user']
        om = self.find_account(username)
        if om is None:
            new_model = self.db.account_pics.insert_one(m)
        else:
            new_model = self.db.account_pics.replace_one({"user": username}, m)

        om['picid'] = m['picid']
        self.save_account(om)

        return new_model

    def find_pic_url(self, username):
        new_model = self.db.account_pics.find_one({"user": username})

        return new_model["url"]

    def find_pic_id(self, username):
        new_model = self.db.accounts.find_one({"name": username})

        return new_model.get("picid",'v1476794414/empty')

    def save_preference(self, m):
        username = m['user']
        om = self.find_preference(username)
        if om is None:
            new_model = self.db.account_pre.insert_one(m)
        else:
            new_model = self.db.account_pre.replace_one({"user": username}, m)
        return new_model

    def find_preference(self, username):
        new_model = self.db.account_pre.find_one({"user": username})

        return new_model

    def clear_preference(self):
        ps = self.db.account_pre.find()
        for p in ps:
            u = self.find_account(p['user'])
            if u is None:
                self.db.account_pre.remove(p)

        return ''


    def test_pic_id(self):
        users = self.db.accounts.find({"sex": "f"})

        for user in users:
            url = self.find_pic_url(user['name'])
            picid = url.replace("http://res.cloudinary.com/yopo/image/upload/", "")
            picid = picid[0:len(picid) - 4]
            user['picid'] = picid
            self.save_account(user)

        return users

    def query_accounts(self, current_user, p):
        users = self.db.accounts.find(p)
        result = []
        for user in users:
            #filter some users: 1. current user, 2. deleted user 3. someone you liked or disliked 4. someone who disliked you
            if user["name"] == current_user \
                    or user.get('status', '') == 'deleted' \
                    or self.is_liked(current_user, user["name"])=='yes' \
                    or self.is_disliked(current_user, user["name"])=='yes' \
                    or self.is_disliked(user["name"], current_user)=='yes':
                continue

            result.append(user)

        # shuffle data
        if(len(result)>3):
            oldpart = []
            newpart = []
            i = 0
            for user in result:
                if i < (len(result)-3):
                    oldpart.append(user)
                else:
                    newpart.append(user)
                i=i+1

            shuffle(oldpart)
            result = oldpart + newpart

        return result


    def find_all_accounts(self):
        users = self.db.accounts.find({})
        return users

    def save_like_result(self, current_user, liked_user):
        m = dict(current_user=current_user,
                 liked_user=liked_user,
                 create_date=datetime.datetime.utcnow())
        new_model = self.db.likes.insert_one(m)

        return new_model

    def is_liked(self, current_user, liked_user):
        m = self.db.likes.find_one({"current_user": current_user, "liked_user": liked_user})
        if m is None:
            return 'no'

        return 'yes'

    def save_dislike_result(self, current_user, disliked_user):
        m = dict(current_user=current_user,
                 disliked_user=disliked_user,
                 create_date=datetime.datetime.utcnow())
        new_model = self.db.dislikes.insert_one(m)

        return new_model

    def is_disliked(self, current_user, disliked_user):
        m = self.db.dislikes.find_one({"current_user": current_user, "disliked_user": disliked_user})
        if m is None:
            return 'no'

        return 'yes'

    def save_match_result(self, current_user, another_user):
        m1 = dict(u1=current_user,
                 u2=another_user,
                 create_date=datetime.datetime.utcnow())
        u1 = self.db.match.insert_one(m1)

        m2 = dict(u1=another_user,
                 u2=current_user,
                 create_date=datetime.datetime.utcnow())
        u2 = self.db.match.insert_one(m2)

        return (u1, u2)

    def is_matched(self, current_user, another_user):
        m = self.db.match.find_one({"u1": current_user, "u2": another_user})
        if m is None:
            return 'no'

        return 'yes'

    def find_match_list(self, current_user):
        list = self.db.match.find({"u1": current_user}).sort("create_date", DESCENDING)
        result = []
        for m in list:
            user = self.find_account(m["u2"])
            if user is not None:
                user["match_date"] = m["create_date"]
                result.append(user)

        return result

    def find_msg(self, current_user, chat_user):
        list = []
        list1 = self.db.messages.find({"current_user": current_user, 'chat_user': chat_user}).sort("create_date", DESCENDING).limit(20)
        for m in list1:
            msg = dict(current_user=m['current_user'],
                       chat_user=m['chat_user'],
                       create_date=m['create_date'],
                       msg=m['msg'],
                       message_side='right')
            list.append(msg)

        list2 = self.db.messages.find({"current_user": chat_user, 'chat_user': current_user}).sort("create_date", DESCENDING).limit(20)
        for m in list2:
            msg = dict(current_user=m['current_user'],
                       chat_user=m['chat_user'],
                       create_date=m['create_date'],
                       msg=m['msg'],
                       message_side='left')
            list.append(msg)

        result = sorted(list, key=lambda m: m['create_date'], reverse=True)[:20]
        result = sorted(result, key=lambda m: m['create_date'])

        return result

    def send_msg(self, current_user, chat_user, msg):
        m = dict(current_user=current_user,
                 chat_user=chat_user,
                 msg=msg,
                 create_date=datetime.datetime.utcnow())
        new_model = self.db.messages.insert_one(m)

        return new_model