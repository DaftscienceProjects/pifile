import os
from tinydb import TinyDB, where
import inspect
from tinyrecord import transaction
from time import time, mktime, strftime, localtime
import datetime
from global_variables import DATABASE_SETTINGS, ROWS
from pprintpp import pprint
from sqlitedict import SqliteDict
from prettytable import PrettyTable


from metrics import profile, print_prof_data


class tiny_db():

    def __init__(self):
        self.debug = True
        self.dict_db = SqliteDict('./racks.sqlite', autocommit=True)
        self.days_to_keep = 5
        self._define_mem_db()
        # SET UP DATABASE VARIABLES
        self.row_height = DATABASE_SETTINGS['rows']
        self.column_width = DATABASE_SETTINGS['columns']
        self.get_last_filed()
        self.rack_day = self._today()
        self.next = {}
        self._today()
        self.next_location()
        self._db_info()
        # if self.last_filed is None:
            # try:
                # self._convert_to_sqlitedb()
            # except:
                # print "Database is Empty"


    # @profile
    def _define_mem_db(self):
        self.mem_db = []
        for item in self.dict_db.iteritems():
            self.mem_db.append(item[1])

    # @profile
    def _db_info(self):
        if len(self.mem_db) > 3:
            x = PrettyTable([" ", "size"])
            x.add_row(["DB Size", len(self.dict_db)])
            x = PrettyTable(["stats", "accn", "Date", "Timestamp"])
            readable = self._conv_timestamp(self.last_filed['time'])
            x.add_row(["Last",
                       self.last_filed['accn'],
                       readable,
                       self.last_filed['time']])
            first_filed = self.get_first_filed()
            other_readable = self._conv_timestamp(first_filed['time'])
            x.add_row(["First",
                       first_filed['accn'],
                       other_readable,
                       first_filed['time']])
            # print x
            return x

    def _list_size(self):
        size = {'memory': len(self.mem_db), 'disk': len(self.dict_db)}
        return  size
    def _print_database(self):
        if len(self.mem_db) < 2:
            return none
        x = PrettyTable(["Accn", "Rack", "Position", "Time", "Timestamp"])
        for item in self.mem_db:
            x.add_row(self._make_entry_row(item))
        f = open('_database_info.txt', 'w')
        f.write(x.get_string(sortby="Timestamp"))
        f.write(self._db_info().get_string())
        f.close()
        print x.get_string(fields=["Accn", "Rack", "Position"])

    def _make_entry_row(self, item):
        readable = self._conv_timestamp(item['time'])
        x = [item['accn'],
             item['rackDay'] + ' ' + str(item['rack']),
             ROWS[str(item['row'])] + ' ' + str(item['column']),
             readable,
             item['time']]
        return x

    def _conv_timestamp(self, ts):
        dt = datetime.datetime.fromtimestamp(float(ts))
        return dt.strftime("%H:%M - %m.%d.%Y")

    def _today(self):
        self.purge_date = int(
            mktime(
                (datetime.date.today() -
                 datetime.timedelta(
                    self.days_to_keep)).timetuple()))
        return strftime('%a', localtime(time()))

    # @profile
    def file_accn(self, accn):
        insert = {
            'accn': accn,
            'rack': self.next['rack'],
            'rackDay': self.next['rackDay'],
            'column': self.next['column'],
            'row': self.next['row'],
            'time': str(time())
        }
        self.mem_db.append(insert)
        self.last_filed = insert
        self.dict_db[insert['time']] = insert
        self.next_location()

    # @profile
    def get_last_filed(self):
        _last_filed_id = None
        self.last_filed = None
        for item in self.mem_db:
            if _last_filed_id < item['time']:
                _last_filed_id = item['time']
                self.last_filed = item
        return self.last_filed

    # @profile
    def get_first_filed(self):
        # if len(self.mem_db) == 1:
            # return self.last_filed
        # else:
        # print self.last_filed
        if self.last_filed is None:
            return self.last_filed
        else:
            _smallest_id = self.last_filed['time']
            first_filed = None
            for item in self.mem_db:
                if item:
                    # print item
                    if _smallest_id > item['time']:
                        # print "smaller"
                        _smallest_id = item['time']
                        first_filed = item
                # print first_filed
                return first_filed

    # @profile
    def new_day(self):
        self.next['column'] = 1
        self.next['rack'] = 1
        self.next['row'] = 1
        self.next['rackDay'] = self._today()

    # @profile
    def next_location(self):
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

    # @profile
    def find_accn(self, accn):
        result = []
        for item in self.mem_db:
            if item['accn'] == accn:
                result.append(item)
        return result

    # # @profile
    # def _convert_to_sqlitedb(self):
    #     old_db = TinyDB(DATABASE_SETTINGS['database'])
    #     self.mem_db = []
    #     total = 0
    #     for table in old_db.tables():
    #         for item in old_db.table(table).all():
    #             total += 1
    #     print "MIGRATING DATABASE"
    #     print "--OLD DATABASE: " + str(total)
    #     i = 0
    #     for table in old_db.tables():
    #         for item in old_db.table(table).all():
    #             if len(item['accn']) < 15:
    #                 if int(item['time']) > self.purge_date:
    #                     self.mem_db.append(item)
    #                     print "   Converted:   " + str(i) + " of " + str(total)
    #                     i += 1
    #                     self.dict_db[str(item['time'])] = item
    #                 else:
    #                     print "REMOVING OLD THING"
    #     print "DATABASE MIGRATION COMPLETE"
    #     print "COMMITING CHANGES"
    #     self.get_last_filed()

    # @profile
    def clean(self):
        print "HARD STORAGE: " + str(len(self.dict_db))
        print "Mem:  " +str(len(self.mem_db))
        self.mem_db = []
        for item in self.dict_db.iteritems():
            # print int(item[1]['time'][:-3])
            # print self.purge_date
            if float(item[1]['time']) < self.purge_date:
                print "---"
                print float(item[1]['time'])
                # print "---"
                print self.purge_date
                del self.dict_db[item[0]]

        self._define_mem_db()
        print self.purge_date
        print "HARD STORAGE: " + str(len(self.dict_db))
        print "Mem:  " +str(len(self.mem_db))

RACK_DB = tiny_db()

if __name__ == '__main__':
    import random

    def populate(n):
        while n > 0:
            for x in range(1, 8):
                for y in range(100):
                    fake = "%02d%05d" % (x, y,)
                    if n > 0:
                        n -= 1
                        RACK_DB.file_accn(fake)
                    else:
                        return

    def find_random(n):
        sample = []
        for item in RACK_DB.mem_db:
            sample.append(item)
        mem_nf = 0
        nf = 0
        for item in random.sample(sample, n):
            if len(RACK_DB.find_accn(item)) > 0:
                print "found in memory"
            else:
                nf += 1
            if len(RACK_DB.find_accn_mem(item)) > 0:
                print "found with database"
            else:
                mem_nf += 1
        print "mem_nf: " + str(mem_nf)
        print "nf: " + str(nf)

    # RACK_DB._convert_to_sqlitedb()
    # populate(50)
    # find_random(10)
    RACK_DB._print_database()
    RACK_DB._db_info()
    print_prof_data()
    RACK_DB.clean()
    print int(
            mktime(
                (datetime.date.today() -
                 datetime.timedelta(
                    RACK_DB.days_to_keep)).timetuple()))
    # pprint(RACK_DB.mem_db)
