import os
from tinydb import TinyDB, where
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage, JSONStorage
from tinyrecord import transaction
from time import time, mktime, strftime, localtime
import datetime
from global_variables import DATABASE_SETTINGS
from pprint import pprint


class tiny_db():

    def __init__(self):
        # days_to_keep = int(mktime((datetime.date.today() - datetime.timedelta(3)).timetuple()))
        # tempDB = TinyDB(DATABASE_SETTINGS['database'])
        self.db = TinyDB(DATABASE_SETTINGS['database'])
        # self.db = TinyDB(DATABASE_SETTINGS['database'], storage=CachingMiddleware(JSONStorage))
        # self.storage = CachingMiddleware(MemoryStorage)
        # self.storage()  # Initialization


        # self.db.WRITE_CACHE_SIZE = 3



        # self.db.close()

        # for item in tempDB.all():
            # if item['time'] > days_to_keep:
            # self.db.insert(item)
        # self.db.close()
        # del self.db
        self.cache = []

        self.row_height = DATABASE_SETTINGS['rows']
        self.column_width = DATABASE_SETTINGS['columns']
        self.get_last_filed()
        self.mem_db = []
        # self.list_all()
        self.accn_batch = []
        self.rack_day = None
        self.next={}
        self.next_location()



        # self.table = self.db.table('table_name')

    def file_accn(self, accn):
        insert = {
            'accn': accn,
            'rack': self.next['rack'],
            'rackDay': self.next['rackDay'],
            'column': self.next['column'],
            'row': self.next['row'],
            'time': time()
        }
        # this does a few thigns:
        # 	First it inserts he item, and returns an eid
        # 	that eid is used to then get what it just inserted.
        # 	then that dict is put into last filed
        print "-----------------------"
        print "starting to file accn"
        self.mem_db.append(insert)
        print "written to memory"
        self.cache.append(insert)
        # self.db.insert(insert)
        table = self.db.table()
        if len(self.cache) < 5:
            for item in self.cache:
                with transaction(table) as tr:
            # tr.insert({})
                    tr.insert(item)
            self.cache = []
        

        print "stored"
        self.last_filed = insert
        print "last filed updated"
        self.next_location()
        print "next location updated"
        print "======================="

    def get_last_filed(self):
        # db.all returns a list of every tube,
        # the [-1] will print the last item in the list,
        # which should be the last tube filed
        try:
            self.last_filed = self.db.all()[-1]
            pprint(self.last_filed)
        except:
            self.last_filed = None
            # print "Last Filed is None"
        return self.last_filed

    def new_day(self):
        # print('creating new rack')
        today = strftime('%a', localtime(time()))
        self.next['column'] = 1
        self.next['rack'] = 1
        self.next['row'] = 1
        self.next['rackDay'] = today

    def next_location(self):
        # print "running next location"
        today = strftime('%a', localtime(time()))
        # print today
        if self.last_filed is None:
            self.new_day()
            return
        # pprint (self.last_filed)
        if self.last_filed['rackDay'] != today:
            # print "creating new day"
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


    def print_properties(self):
        print self.last_filed
        print self.next_column
        print self.next_row
        print self.next_rack
        print self.rack_day

    def purge_old(self):
        purge = []
        keep = []
        twoDaysAgo = int(mktime((datetime.date.today() - datetime.timedelta(2)).timetuple()))
        for item in self.db.all():
            print item.eid
            if item['time'] < twoDaysAgo:
                print "removing: " + str(item['accn'])
                purge.append(item.eid)
            else:
                self.mem_db.append(item)
                keep.append(item.eid)
        # self.db.remove(eids=purge)
        # self.last_filed = self.db.get(eid=max(keep))
        print "last id " + str(max(keep))
        return self.mem_db
            
        
    def find_accn(self, accn):
        print "looking for: " + str(accn)
        # testTime = 1422225306.907
        twoDaysAgo = int(
            mktime(
                (datetime.date.today() - datetime.timedelta(2)).timetuple()))
        print "found the date of two days ago"
        # So this will check for accn and compare time
        # Returning only values that after two days ago
        print "starting search"
        result = []
        for item in self.mem_db:
            if item['accn'] == accn:
                result.append(item)
        
        # result = self.db.search((where('accn') == accn))
        print "finished search"
        pprint(result)
        return result

    def list_all(self):
        for item in self.db.all():
            print str(item.eid) + " " + str(item['accn'])
            self.mem_db.append(item)
        return self.mem_db
        
RACK_DB = tiny_db()


if __name__ == '__main__':
    import timeit
    # RACK_DB.purge_old()
    # path = "test.json"

    # tempDB = TinyDB(path)
    # db = TinyDB(path, storage=CachingMiddleware(JSONStorage))
    # db.WRITE_CACHE_SIZE = 3
    # for item in tempDB.all():
        # db.insert(item)
    # storage = CachingMiddleware(MemoryStorage)
    # storage()  # Initialization

    # x = 0
    # while x < 20:
            # db.insert({'fuck': x})
            # x +=1

    # storage.write({'key': 'value'})
    # test = db.all()
    # print len(test)
    # db.close()
    # x = 0
    # while x < 20:
            # db.insert({'Second': x})
            # x +=1


    # assert statinfo.st_size != 0

    # Assert JSON file has been closed
    # assert db._storage._handle.closed

    # del db

    # Repoen database
    # db = TinyDB(path, storage=CachingMiddleware(JSONStorage))
    # assert db.all() == [{'key': 'value'}]


    # element = {'none': [None, None], 'int': 42, 'float': 3.1415899999999999,
           # 'list': ['LITE', 'RES_ACID', 'SUS_DEXT'],
           # 'dict': {'hp': 13, 'sp': 5},
           # 'bool': [True, False, True, False]}

    x=0
    while x < 120:
        RACK_DB.file_accn(x)
        x += 1
        # RACK_DB.db.close()

    # RACK_DB.list_all()
    pprint(RACK_DB.get_last_filed())

