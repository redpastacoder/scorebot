#!/usr/bin/env python
'''
Created on Dec 18, 2011

@author: dichotomy@riseup.net

Blueteam.py is a module in the scorebot program.  It's purpose is to manage Blue Team assets and run scoring for services.

Copyright (C) 2011  Dichotomy

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import sys
import traceback
import threading
import time
import Queue
import globalvars
import dns.resolver
import dns.exception
from Host import Host
from Logger import Logger
from Scores import Scores
from FlagStore import FlagStore

del_host_blue_str = "Blueteam %s:  Deleting host %s\n"
del_host_blue_err_str = "Blueteam %s: No such host %s to delete\n"
add_host_blue_str = "Blueteam %s:  Adding host %s\n"
add_srvc_blue_str = "Blueteam %s:  Adding service %s/%s with value %s to host %s\n"
add_srvc_blue_err_str = "Blueteam %s:  Failed adding service %s/%s with value %s to host %s\n"
clobber_host_blue_str = "Blueteam %s:  clobbering host %s!\n"

class BlueTeam(threading.Thread):
   '''
   classdocs
   '''

   def __init__(self, teamname, start_time, flags, queue=None, interval=300):
      '''
      Constructor
      '''
      threading.Thread.__init__(self)
      self.queue_obj = queue
      now = time.strftime("%Y %b %d %H:%M:%S", time.localtime(time.time()))
      self.dns = dns.resolver.Resolver()
      self.del_dns("8.8.8.8")
      #self.add_dns("10.0.1.50")
      self.teamname = teamname
      self.logger = Logger(self.teamname)
      self.logger.err("\n" + globalvars.sep + "\n")
      self.logger.err("| Starting run for Blueteam %s\n" % self.teamname)
      self.logger.err("| Start time: %s\n" % now)
      self.logger.out(globalvars.sep + "\n")
      self.logger.out("| Starting run for Blueteam %s\n" % self.teamname)
      self.logger.out("| Start time: %s\n" % now)
      self.hosts = {}
      self.scores = Scores() 
      self.start_time = start_time
      self.go_time = self.start_time
      self.interval = interval
      self.did_time = None
      # Number of rounds finished
      self.this_round = 1 
      self.flag_store = flags

   def add_flag(self, name, value):
      self.flag_store.add(self.teamname, name, value)

   def run(self):
      print "Firing up Blueteam %s, go time is %s" % \
                  (self.teamname, self.go_time)
      if globalvars.quick:
         self.go_time = time.time() + 5
      while True:
         go_time_lt = time.localtime(self.go_time)
         if self.did_time:
            did_time_lt = time.localtime(self.did_time)
            if go_time_lt.tm_min == did_time_lt.tm_min:
               continue
            else:
               pass
         else:
            pass
         rightnow = time.time()
         rightnow_lt = time.localtime(rightnow)
         if go_time_lt.tm_mday == rightnow_lt.tm_mday:
            if go_time_lt.tm_hour == rightnow_lt.tm_hour:
               if go_time_lt.tm_min == rightnow_lt.tm_min:
                  try:      
                     print "Now is %s" % rightnow
                     self.did_time = self.go_time
                     self.check()
                     queue_str = self.teamname+"|"+str(self.this_round)
                     self.queue_obj.put(queue_str)
                     self.go_time += self.interval
                     self.set_score(self.this_round)
                     self.this_round += 1      
                  except:   
                     traceback.print_exc(file=self.logger)
               elif go_time_lt.tm_min == (rightnow_lt.tm_min + 1):
                  print "Counting down for %s: %s to %s..." % \
                        (self.teamname, self.go_time, rightnow)
                  time.sleep(1)
               else:
                  print "Counting down for %s: %s to %s..." % \
                        (self.teamname, self.go_time, rightnow)
                  time.sleep(60)
            else:
               print "Counting down for %s: %s to %s..." % \
                     (self.teamname, self.go_time, rightnow)
               time.sleep(60)
         else:
            time.sleep(60)

   def add_dns(self, dnssvr):
      if self.dns.nameservers.count(dnssvr):
         pass
      else:
         self.logger.out("Adding DNS %s to %s\n" % (dnssvr, self.teamname))
         self.dns.nameservers.append(dnssvr)

   def del_dns(self, dnssvr):
      if self.dns.nameservers.count(dnssvr):
         index = self.dns.nameservers.index(dnssvr)
         self.dns.nameservers.pop(index)
      else:
         pass

   def add_queue(self, queue):
      self.queue_obj = queue

   def check(self):
      hostlist = self.hosts.keys()
      for host in hostlist:
         hostscore = self.hosts[host].check(self.this_round)

   def add_host(self, hostname, value):
      if self.hosts.has_key(hostname):
         self.logger.err(clobber_host_blue_str % (self.teamname, hostname))
      else:   
         self.logger.err(add_host_blue_str % (self.teamname, hostname))
      self.hosts[hostname] = Host(hostname, value, self.logger, self.dns)

   def del_host(self, hostname):
      if self.hosts.has_key(hostname):
         self.logger.err(del_host_blue_str % (self.teamname, hostname))
         del(self.hosts[hostname])
      else:   
         self.logger.err(del_host_blue_err_str % (self.teamname, hostname))

   def add_service(self, hostname, port, proto, value, app=None):
      if self.hosts.has_key(hostname):
         self.logger.err(add_srvc_blue_str % \
               (self.teamname, port, proto, value, hostname))
         self.hosts[hostname].add_service(port, proto, app, value)
      else:   
         self.logger.err(add_srvc_blue_err_str % \
               (self.teamname, port, proto, hostname))

   def del_service(self, host, port, proto):
      if self.hosts.has_key(hostname):
         self.logger.err(add_srvc_blue_str % \
               (self.teamname, port, proto, hostname))
         self.hosts[hostname].del_service(port, proto, app, value)
      else:   
         self.logger.err(add_srvc_blue_err_str % \
               (self.teamname, port, proto, hostname))

   def tally(self):      
      this_round = self.this_round - 1
      this_score = self.scores.total()
      flag_score = self.flag_store.score(self.teamname, this_round)
      final_score = this_score * flag_score
      return [this_round, final_score]

   def set_score(self, this_round, value=None):
      if value == None:
         myscore = self.get_score(this_round)
      else:
         myscore = value
      print "Blueteam %s round %s scored %s\n" % \
              (self.teamname, this_round, myscore)
      self.scores.set_score(this_round, myscore)
      print "Blueteam %s tally: %s\n" % (self.teamname, self.tally())
          

   def get_score(self, this_round):
      score = 0
      hostlist = self.hosts.keys()
      for host in hostlist:
         score += self.hosts[host].get_score(this_round)
      return score

def main():
   '''
   unit tests for classes and their functions
   '''
   globalvars.verbose = True
   globalvars.quick = True
   queue_obj = Queue.Queue()
   hostname = "atlas.arnothde.net"
   score = 100
   mylog = Logger("blueteam_py_test")
   rightnow = time.time()+5
   blueteam = BlueTeam("Test", rightnow, interval=120)
   blueteam.add_host(hostname, score)
   blueteam.add_service(hostname, 80, "tcp", score)
   blueteam.add_queue(queue_obj)
   blueteam.start()



if __name__ == "__main__":
   main()