import os
from tinydb import TinyDB, where
# from tinydb.middlewares import CachingMiddleware
# from tinydb.storages import MemoryStorage, JSONStorage
from tinyrecord import transaction
from time import time, mktime, strftime, localtime
import datetime
from global_variables import DATABASE_SETTINGS
from pprint import pprint
# from logger import log_with


from metrics import profile, print_prof_data


class tiny_db():

    def __init__(self):
        self.db = TinyDB(DATABASE_SETTINGS['database'])
        self.days_to_keep = 5
        self._define_range()
        self._migrate_db()


        self.mem_db = []
        self.todays_table = self.db.table(self._today())

        # SET UP DATABASE VARIABLES
        self.row_height = DATABASE_SETTINGS['rows']
        self.column_width = DATABASE_SETTINGS['columns']
        self.get_last_filed()

        self.rack_day = self._today()
        self.next = {}
        self.next_location()

    def _today(self):
        return strftime('%a', localtime(time()))

    def _days_stored(self):
        return

    @profile
    def _define_range(self):
        self.list_of_days = []
        for x in range(self.days_to_keep):
            day = datetime.datetime.now() - datetime.timedelta(days=x)
            self.list_of_days.append(day.strftime('%a'))
        self.list_of_days.append('_default')
    @profile
    def _purge_old(self):
        for item in self.db.tables():
            if item not in self.list_of_days:
                print "Droping old table: " + item
                self.db.table(item).purge()

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
        self.todays_table.insert(insert)
        self.last_filed = insert
        self.next_location()

    @profile
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

    @profile
    def new_day(self):
        self._define_range()
        self._purge_old()
        self.todays_table = self.db.table((self._today()))
        self.next['column'] = 1
        self.next['rack'] = 1
        self.next['row'] = 1
        self.next['rackDay'] = self._today()

    @profile
    def next_location(self):
        # self.today = strftime('%a', localtime(time()))
        if self.last_filed is None:
            self.new_day()
            return
        if self.last_filed['rackDay'] != self._today():
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
        self.next['rackDay'] = self._today()

    @profile
    def find_accn(self, accn):
        result = []
        for item in self.mem_db:
            if item['accn'] == accn:
                result.append(item)
        return result

    @profile
    def _migrate_db(self):
        keep = []
        if len(self.db) > 0:
            print 'Merging information from _default table'
            keep = self.db.search((where('time') > self.days_to_keep))
            print "Found " + str(len(keep)) + "to merge"
        self.db.table('_default').purge()
        i = 0
        # print len(keep)
        for item in keep:
            print "Merged item " + str(i) + "of " + str(len(keep))
            self.db.table(item['rackDay']).insert(item)
            i += 1
    @profile
    def list_all(self):
        print len(self.db)
        print "Size of tables"
        for item in self.list_of_days:
            print item + ": " + str(len(self.db.table(item)))
        return

RACK_DB = tiny_db()


if __name__ == '__main__':
    from metrics import profile, print_prof_data
    # from random import random
    import random

    @profile
    def populate():
        for item in RACK_DB.db.tables():
            table = RACK_DB.db.table(item)
            for x in range(30):
                table.insert({'accn': str(x), 'test': "item"})
    # populate()

    RACK_DB.list_all()
    print_prof_data()
