import os
from tinydb import TinyDB, where
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage, JSONStorage
from tinyrecord import transaction
from time import time, mktime, strftime, localtime
import datetime
from global_variables import DATABASE_SETTINGS
from pprint import pprint


from metrics import profile, print_prof_data

class tiny_db():

    def __init__(self):
        self.days_to_keep = int(mktime((datetime.date.today() - datetime.timedelta(3)).timetuple()))

        self.db = TinyDB(DATABASE_SETTINGS['database'])
        # SET UP A MEMORY VERSION OF THE DATABASE
        self.mem_db = []
        for item in self.db.all():
            # if item['time'] > self.days_to_keep:
                # print (item.eid)
                self.mem_db.append(item)

        self.table = self.db.table('_default', smart_cache=True)
        self.CACHE_SIZE = 1
        # self.purge_old()

        # CREATE A CACHE FOR TINYRECORD
        self.cache = []


        # SET UP DATABASE VARIABLES
        self.row_height = DATABASE_SETTINGS['rows']
        self.column_width = DATABASE_SETTINGS['columns']
        self.get_last_filed()

        self.rack_day = None
        self.next={}
        self.next_location()

        self.db.purge_tables()
        self.table = self.db.table('_default', smart_cache=True)

        with transaction(self.table) as tr:
                for item in self.mem_db:
                    tr.insert(item)



        # self.table = self.db.table('table_name')
    @profile
    def file_accn(self, accn):
        # print('file_accn')
        insert = {
            'accn': accn,
            'rack': self.next['rack'],
            'rackDay': self.next['rackDay'],
            'column': self.next['column'],
            'row': self.next['row'],
            'time': time()
        }
        self.mem_db.append(insert)
        # self.cache.append(insert)
        self.table.insert(insert)
        self.last_filed = insert
        self.next_location()

    @profile
    def file_accn_tr_multi(self, accn):
        # print('file_accn')
        insert = {
            'accn': accn,
            'rack': self.next['rack'],
            'rackDay': self.next['rackDay'],
            'column': self.next['column'],
            'row': self.next['row'],
            'time': time()
        }
        self.mem_db.append(insert)
        self.cache.append(insert)
        if len(self.cache) == 5:
            with transaction(self.table) as tr:
                for item in self.cache:
                    tr.insert(item)
            # self.table.insert_multiple(self.cache)
            self.cache = []
        self.last_filed = insert
        self.next_location()

    @profile
    def file_accn_tr(self, accn):
        # print('file_accn')
        insert = {
            'accn': accn,
            'rack': self.next['rack'],
            'rackDay': self.next['rackDay'],
            'column': self.next['column'],
            'row': self.next['row'],
            'time': time()
        }
        self.mem_db.append(insert)
        with transaction(self.table) as tr:
            tr.insert(insert)
        self.last_filed = insert
        self.next_location()

    def get_last_filed(self):
        _last_id = None
        try:
            _last_id = self.db.table("_default")._last_id
        except:
            self.last_filed = None
            # print "Last Filed is None"
        else:
            self.last_filed = self.db.get(eid=_last_id)
        return self.last_filed

    def new_day(self):
        today = strftime('%a', localtime(time()))
        self.purge_old()

        self.next['column'] = 1
        self.next['rack'] = 1
        self.next['row'] = 1
        self.next['rackDay'] = today

    def next_location(self):
        # print "running next location"
        today = strftime('%a', localtime(time()))
        if self.last_filed is None:
            self.new_day()
            return
        if self.last_filed['rackDay'] != today:
            self.new_day()
        elif self.last_filed['column'] == self.column_width:
            if self.last_filed['row'] == self.row_height:
                self.next['column'] = 1
                self.next['row'] = 1
                self.next['rack'] = self.last_filed['rack'] + 1
            else:
                self.next['column'] = 1
                self.next['row'] = self.last_filed['row'] + 1
                self.next['rack'] = self.last_filed['rack']
        else:
            self.next['column'] = self.last_filed['column'] + 1
            self.next['rack'] = self.last_filed['rack']
            self.next['row'] = self.last_filed['row']
        self.next['rackDay'] = today

    def purge_old(self):
        self.days_to_keep = int(mktime((datetime.date.today() - datetime.timedelta(4)).timetuple()))
        purge = []
        for item in self.mem_db:
            if item['time'] < self.days_to_keep:
                purge.append(item)
        print "mem_db length" + str(len(self.mem_db))
        for item in purge:
            self.mem_db.remove(item)
        print "mem_db length" + str(len(self.mem_db))

        with transaction(self.table) as tr:
                for item in self.mem_db:
                    tr.insert(item)
        # with transaction(self.table) as tr:
            # tr.remove(where('time') < self.days_to_keep)
    
    @profile
    def find_accn(self, accn):
        print "---find memory ----"
        print "looking for: " + str(accn)
        print "found the date of two days ago"
        print "starting search"
        result = []
        for item in self.mem_db:
            if item['accn'] == accn:
                result.append(item)
        print "finished search"
        # pprint(result)
        return result

    def list_all(self):
        for item in self.db.all():
            pass
            print str(item.eid) + " " + str(item['accn'])
        return
        
RACK_DB = tiny_db()


if __name__ == '__main__':
    from metrics import profile, print_prof_data
    import random

    x = 0
    max_rand = 2000
    while x < 1000:
        # RACK_DB.file_accn(random.randint(1, 500329123))
        RACK_DB.file_accn_tr_multi(random.randint(1, 500329123))
        # RACK_DB.file_accn_tr(random.randint(1, 500329123))
        # print x
        x+=1



    # @profile
    # def search1():
        # RACK_DB.find_accn("4newer")
    # @profile
    # def search2():
        # RACK_DB.find_accn_td("4newer")
    # search1()
    # search2()
    print_prof_data()

