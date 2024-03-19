import datetime
import random
import time

from src import db, app
from src.models import Post, Branch, Thread_, User
from sqlalchemy import text
import multiprocessing
import requests
import random
import string


def create_triggers(ses):
    create_ddl_queries = [
        '''
        CREATE OR REPLACE FUNCTION trg_decrem_branch_count()
        RETURNS TRIGGER AS $$
        BEGIN
          UPDATE threads
          SET branch_count = branch_count - 1
          WHERE thread_id = OLD.thread_id
                AND EXISTS (SELECT 1 FROM branches WHERE id = OLD.thread_id);
          RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER decrem_branch_count
        AFTER DELETE ON branches
        FOR EACH ROW
        EXECUTE FUNCTION trg_decrem_branch_count();
        ''',
        '''
        CREATE OR REPLACE FUNCTION trg_decrem_post_count()
        RETURNS TRIGGER AS $$
        BEGIN
          UPDATE branches
          SET message_count = message_count - 1
          WHERE id = OLD.branch_id
                AND EXISTS (SELECT 1 FROM branches WHERE id = OLD.branch_id);
          RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER decrem_post_count
        AFTER DELETE ON posts
        FOR EACH ROW
        EXECUTE FUNCTION trg_decrem_post_count();
        ''',
        '''
        CREATE OR REPLACE FUNCTION trg_increm_branches_count()
        RETURNS TRIGGER AS $$
        BEGIN
          UPDATE threads
          SET branch_count = branch_count + 1
          WHERE thread_id = NEW.thread_id
                AND EXISTS (SELECT 1 FROM branches WHERE thread_id = NEW.thread_id);
          RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER increm_branches_count
        AFTER INSERT ON branches
        FOR EACH ROW
        EXECUTE FUNCTION trg_increm_branches_count();
        ''',
        '''
        CREATE OR REPLACE FUNCTION trg_set_into_branch_id()
        RETURNS TRIGGER AS $$
        DECLARE
            TEMP INTEGER;
        BEGIN
            SELECT COALESCE(MAX(into_branch_id), 0) INTO TEMP
            FROM posts
            WHERE branch_id = NEW.branch_id;
        
            IF TEMP >= (SELECT message_count FROM branches WHERE id = NEW.branch_id) THEN
                NEW.into_branch_id := TEMP + 1;
            ELSE
                NEW.into_branch_id := (SELECT message_count FROM branches WHERE id = NEW.branch_id) + 1;
            END IF;
        
            UPDATE branches
            SET message_count = message_count + 1
            WHERE id = NEW.branch_id
            AND EXISTS (SELECT 1 FROM branches WHERE id = NEW.branch_id);
        
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER set_into_branch_id
        BEFORE INSERT ON posts
        FOR EACH ROW
        EXECUTE FUNCTION trg_set_into_branch_id();
        ''',
           ]

    for query in create_ddl_queries:
        ses.execute(text(query))
        ses.commit()


def drop_triggers(ses):
    drop_ddl_queries = [
        'DROP TRIGGER IF EXISTS decrem_branch_count ON branches',
        'DROP TRIGGER IF EXISTS decrem_post_count ON posts',
        'DROP TRIGGER IF EXISTS increm_branches_count ON branches',
        'DROP TRIGGER IF EXISTS increm_post_count ON posts',
        'DROP TRIGGER IF EXISTS set_into_branch_id ON posts'
    ]
    for query in drop_ddl_queries:
        ses.execute(text(query))
        ses.commit()


def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def reset_start_id(ses):
    a = [
        "SELECT setval(pg_get_serial_sequence('branches', 'id'), 1, false);",
        "SELECT setval(pg_get_serial_sequence('threads', 'thread_id'), 1, false);",
        "SELECT setval(pg_get_serial_sequence('posts', 'u_id'), 1, false);",
        "SELECT setval(pg_get_serial_sequence('users', 'user_id'), 1, false);"
    ]
    for query in a:
        ses.execute(text(query))
        ses.commit()


def create_test_data():
    with app.app_context():
        ses = db.session

        thread1 = Thread_(delta_time=15000000)
        thread2 = Thread_(delta_time=14000000)
        thread3 = Thread_(delta_time=13000000)
        posts_list = []
        post_dict = {}
        branches = []
        threads = []
        print("Creating threads to insert")
        for i in range(42):
            # print(i,"=",(120*100000)-(i+1)*100000)
            tname = generate_random_string(random.randint(20, 28))
            threads.append(Thread_(delta_time=(120 * 100000) - (i + 1) * 100000, name=tname))
        print(f"Created {len(threads)} threads to insert")
        branch1 = Branch(
            # b_id=1,
            thread_id=1,
            creator=1,

        )
        branch2 = Branch(
            thread_id=1,
            creator=1,
        )

        branch3 = Branch(
            thread_id=1,
            creator=1,

        )
        print("Creating branches to insert")
        for i in range(40 * 5):
            random_number = random.randint(1, 42)
            random_creator = random.randint(1, 4)
            bname = generate_random_string(random.randint(20, 28))
            branches.append(Branch(thread_id=random_number, creator=random_creator,
                                   name=bname))
        print(f"Created {len(branches)} branches to insert")
        post1 = Post(
            b_id=3,
            creator=1,
            delta_time=5 * (10 ** 6),
            content="its first post"
        )

        post2 = Post(
            b_id=1,
            creator=1,
            delta_time=4 * (10 ** 6),
            content="post"
        )

        post3 = Post(
            b_id=1,
            creator=1,
            delta_time=3 * (10 ** 6),
            content="post"
        )

        post4 = Post(
            b_id=1,
            creator=2,
            delta_time=2 * (10 ** 6),
            content="post"
        )
        post5 = Post(
            b_id=2,
            creator=2,
            delta_time=0,
            content="post"
        )
        # for i in range(1, 120 * 5+1):
        #     post_dict[i] = []

        # for i in range(120 * 5 * 36 * 5):
        #     random_branch = random.randint(1, 120 * 5)
        #     random_creator = random.randint(1, 4)
        #
        #     post_dict[random_branch].append(Post(
        #         b_id=random_branch,
        #         ib_id=6 + i,
        #         creator=random_creator,
        #         delta_time=0,
        #         content=generate_random_string(random.randint(1, 30)) + generate_random_string(
        #             random.randint(1, 30)) + generate_random_string(random.randint(1, 30))
        #     ))
        print("Creating post to insert")
        for i in range(120 * 5 * 50):# * 10):
            random_branch = random.randint(1, 200)
            random_creator = random.randint(1, 4)

            posts_list.append(Post(
                b_id=random_branch,

                creator=random_creator,
                delta_time=0,
                content=generate_random_string(random.randint(1, 30)) + " " + generate_random_string(
                    random.randint(1, 30)) + " " + generate_random_string(random.randint(1, 30))
            ))
        print(f"Created {len(posts_list)} post to insert")
        drop_triggers(ses)

        ses.execute(text('DELETE FROM posts'))
        print("Deleting entries posts.... ")

        ses.execute(text('DELETE FROM branches'))
        print("Deleting entries branches.... ")

        ses.execute(text('DELETE FROM threads'))
        print("Deleting entries threads.... ")

        ses.execute(text('DELETE FROM users'))
        print("Deleting entries users.... ")

        print("Dropped. ")

        db.session.commit()

        create_triggers(ses)
        reset_start_id(ses)
        # return
        print("Creating data....")

        user1 = User("admin", "123456", "seurs@gmai.com", 3)
        db.session.add(user1)
        user2 = User("s1", "123456", "s1kek@gmai.com", 3)
        db.session.add(user2)
        user3 = User("s2", "123456", "s2meme1@mail.com", 3)
        db.session.add(user3)
        user4 = User("s3", "123456", "s2me3me@mail.com", 3)
        db.session.add(user4)
        user5 = User("s4", "123456", "s2m2eme@mail.com", 3)
        db.session.add(user5)

        ses.commit()
        db.session.add(thread1)
        db.session.add(thread2)
        db.session.add(thread3)

        db.session.add(branch1)
        db.session.add(branch2)
        db.session.add(branch3)
        db.session.commit()

        db.session.add(post1)
        ses.commit()
        db.session.add(post2)
        ses.commit()
        db.session.add(post3)
        ses.commit()
        db.session.add(post4)
        ses.commit()
        db.session.add(post5)
        ses.commit()

        # chunk_size = len(posts_list) // 4
        # chunks = [tuple(posts_list[i:i + chunk_size]) for i in range(0, len(posts_list), chunk_size)]

        print("post count:", len(posts_list))

        for itm in threads:
            db.session.add(itm)
        db.session.commit()
        print("save threads")
        for itm in branches:
            db.session.add(itm)
        db.session.commit()
        print("save branches")
        print()
        print("saving posts")
        for itm in posts_list:
            db.session.add(itm)
        db.session.commit()
        print("saved posts")


# requests.get("http://127.0.0.1:5062/drop_hashes/fkojnsdihf9u8sd7f8sdf")





def test___1():
    import datetime
    import time

    delta_time = 3600  # Replace this with your desired delta time in seconds

    # Calculate the new time
    new_time = time.time() - delta_time
    print(new_time)

    created_date = datetime.datetime.fromtimestamp(new_time)
    print(created_date)


if __name__ == '__main__':
    # test___1()
    print("Start_script", datetime.datetime.now().time())
    s = time.time()
    create_test_data()
    print(f"Spend: {time.time() - s}")
