from tinydb import TinyDB, where
from time import time, mktime, strftime, localtime
import datetime
from global_variables import DATABASE_SETTINGS
from pprint import pprint


class tiny_db():

    def __init__(self):
        self.db = TinyDB(DATABASE_SETTINGS['database'])
        self.row_height = DATABASE_SETTINGS['rows']
        self.column_width = DATABASE_SETTINGS['columns']
        self.get_last_filed()
        self.rack_day = None
        self.next={}
        self.next_location()
        self.mem_db = []
        self.list_all()
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
        self.mem_db.append(insert)
        self.last_filed = self.db.get(eid=self.db.insert(insert))
        self.next_location()

    def get_last_filed(self):
        # db.all returns a list of every tube,
        # the [-1] will print the last item in the list,
        # which should be the last tube filed
        try:
            self.last_filed = self.db.all()[-1]
            # pprint(self.last_filed)
        except:
            self.last_filed = None
            # print "Last Filed is None"

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



    # def next_location(self):
    #     today = strftime('%a', localtime(time()))
    #     self.next = 
    #     # print today
    #     if self.last_filed is None:
    #         self.new_day()
    #         return
    #     # pprint (self.last_filed)
    #     if self.last_filed['rackDay'] != today:
    #         # print "creating new day"
    #         self.new_day()
    #     elif self.last_filed['column'] == self.column_width:
    #         if self.last_filed['row'] == self.row_height:
    #             self.next_column = 1
    #             self.next_row = 1
    #             self.next_rack = self.last_filed['rack'] + 1
    #         else:
    #             self.next_column = 1
    #             self.next_row = self.last_filed['row'] + 1
    #             self.next_rack = self.last_filed['rack']
    #     else:
    #         self.next_column = self.last_filed['column'] + 1
    #         self.next_rack = self.last_filed['rack']
    #         self.next_row = self.last_filed['row']
    #     self.rack_day = today

    def print_properties(self):
        print self.last_filed
        print self.next_column
        print self.next_row
        print self.next_rack
        print self.rack_day

    def old_find_accn(self, accn):
        print "looking for: " + str(accn)
        # testTime = 1422225306.907
        twoDaysAgo = int(
            mktime(
                (datetime.date.today() - datetime.timedelta(2)).timetuple()))
        print "found the date of two days ago"
        # So this will check for accn and compare time
        # Returning only values that after two days ago
        print "starting search"
        result = self.db.search(
            (where('accn') == accn) & (
                where('time') > twoDaysAgo))
        print "finished search"
        pprint(result)
        return result
    def purge_old(self):
        twoDaysAgo = int(
            mktime(
                (datetime.date.today() - datetime.timedelta(2)).timetuple()))
        for item in self.mem_db:
            if item['date'] > twoDaysAgo:
                print "still valid " +item['date']
            else:
                print "old " + item['date']
            
        
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
        # result = self.db.search((where('accn') == accn) & (where('time') > twoDaysAgo))
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
            self.mem_db.append(item)
            print "found: rack  " + str(item['rack']) + " " + str(item['column']) + " " + str(item['row']+ " " + str(item['date'])
        return self.mem_db
        
RACK_DB = tiny_db()


if __name__ == '__main__':
    import timeit
    # for x in xrange(100):
        # print x
        # RACK_DB.file_accn(x)

    # rack_db.find_accn(8)
    # rack_db.list_all()
    # print RACK_DB.next_row
    # print RACK_DB.next_column
    # print RACK_DB.next_rack

    # start = localtime()
    RACK_DB.find_accn('050065740')
    # RACK_DB.new_find_accn('050065740')
    # stamp = localtime()
    # delta = start - stamp
    # pprint(delta)

    # RACK_DB.list_all()

    # rack_db.next_location()
